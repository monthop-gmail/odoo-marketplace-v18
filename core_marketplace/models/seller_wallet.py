# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SellerWallet(models.Model):
    _name = 'seller.wallet'
    _description = 'Seller Wallet'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    _sql_constraints = [
        ('seller_id_uniq', 'unique(seller_id)',
         'Each seller can only have one wallet.'),
    ]

    name = fields.Char(
        string='Wallet Reference',
        default='NEW',
        copy=False,
        readonly=True,
    )
    seller_id = fields.Many2one(
        'res.partner',
        string='Seller',
        required=True,
        domain=[('seller', '=', True)],
        ondelete='restrict',
        index=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self._default_currency(),
        required=True,
        readonly=True,
    )
    balance = fields.Monetary(
        string='Current Balance',
        currency_field='currency_id',
        default=0.0,
        tracking=True,
        readonly=True,
    )
    total_earned = fields.Monetary(
        string='Total Earned',
        currency_field='currency_id',
        default=0.0,
        readonly=True,
    )
    total_withdrawn = fields.Monetary(
        string='Total Withdrawn',
        currency_field='currency_id',
        default=0.0,
        readonly=True,
    )
    state = fields.Selection([
        ('active', 'Active'),
        ('frozen', 'Frozen'),
        ('closed', 'Closed'),
    ], string='Status', default='active', tracking=True, required=True)
    transaction_ids = fields.One2many(
        'seller.wallet.transaction',
        'wallet_id',
        string='Transactions',
    )
    withdrawal_request_ids = fields.One2many(
        'seller.withdrawal.request',
        'wallet_id',
        string='Withdrawal Requests',
    )
    transaction_count = fields.Integer(
        compute='_compute_transaction_count',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company.id,
        readonly=True,
    )

    def _default_currency(self):
        mp_currency = self.env['ir.default']._get(
            'res.config.settings', 'mp_currency_id'
        )
        if mp_currency:
            return mp_currency
        return self.env.company.currency_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'NEW') == 'NEW':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'seller.wallet'
                ) or 'WLT/NEW'
        return super().create(vals_list)

    def _compute_transaction_count(self):
        for rec in self:
            rec.transaction_count = self.env['seller.wallet.transaction'].search_count([
                ('wallet_id', '=', rec.id),
            ])

    def credit(self, amount, transaction_type, description='',
               reference='', sale_order_line_id=False,
               seller_payment_id=False):
        """Credit wallet balance atomically. Creates a transaction record."""
        self.ensure_one()
        if self.state != 'active':
            raise ValidationError(_('Cannot credit a non-active wallet.'))
        if amount <= 0:
            raise ValidationError(_('Credit amount must be positive.'))

        self.env.cr.execute("""
            UPDATE seller_wallet
            SET balance = balance + %s,
                total_earned = total_earned + %s,
                write_date = NOW() AT TIME ZONE 'UTC'
            WHERE id = %s
            RETURNING balance
        """, (amount, amount, self.id))
        new_balance = self.env.cr.fetchone()[0]
        self.invalidate_recordset(['balance', 'total_earned'])

        self.env['seller.wallet.transaction'].with_context(
            allow_wallet_transaction_create=True
        ).create({
            'wallet_id': self.id,
            'type': transaction_type,
            'amount': amount,
            'balance_after': new_balance,
            'reference': reference,
            'description': description,
            'sale_order_line_id': sale_order_line_id,
            'seller_payment_id': seller_payment_id,
        })
        _logger.info(
            'Wallet %s credited %.2f (%s), new balance: %.2f',
            self.name, amount, transaction_type, new_balance
        )
        return new_balance

    def debit(self, amount, transaction_type, description='',
              reference='', withdrawal_request_id=False,
              seller_payment_id=False):
        """Debit wallet balance atomically. Prevents overdraft."""
        self.ensure_one()
        if self.state != 'active':
            raise ValidationError(_('Cannot debit a non-active wallet.'))
        if amount <= 0:
            raise ValidationError(_('Debit amount must be positive.'))

        self.env.cr.execute("""
            UPDATE seller_wallet
            SET balance = balance - %s,
                total_withdrawn = total_withdrawn + %s,
                write_date = NOW() AT TIME ZONE 'UTC'
            WHERE id = %s AND balance >= %s
            RETURNING balance
        """, (amount, amount, self.id, amount))
        result = self.env.cr.fetchone()

        if not result:
            raise ValidationError(
                _('Insufficient wallet balance for this operation.')
            )
        new_balance = result[0]
        self.invalidate_recordset(['balance', 'total_withdrawn'])

        self.env['seller.wallet.transaction'].with_context(
            allow_wallet_transaction_create=True
        ).create({
            'wallet_id': self.id,
            'type': transaction_type,
            'amount': -amount,
            'balance_after': new_balance,
            'reference': reference,
            'description': description,
            'withdrawal_request_id': withdrawal_request_id,
            'seller_payment_id': seller_payment_id,
        })
        _logger.info(
            'Wallet %s debited %.2f (%s), new balance: %.2f',
            self.name, amount, transaction_type, new_balance
        )
        return new_balance

    @api.model
    def get_or_create_wallet(self, seller_id):
        """Get existing wallet or create one for an approved seller."""
        wallet = self.sudo().search([('seller_id', '=', seller_id)], limit=1)
        if not wallet:
            seller = self.env['res.partner'].sudo().browse(seller_id)
            if seller.exists() and seller.seller:
                wallet = self.sudo().create({'seller_id': seller_id})
                _logger.info(
                    'Created wallet %s for seller %s',
                    wallet.name, seller.name
                )
        return wallet

    def action_freeze(self):
        for rec in self:
            if rec.state == 'active':
                rec.state = 'frozen'

    def action_unfreeze(self):
        for rec in self:
            if rec.state == 'frozen':
                rec.state = 'active'

    def action_view_transactions(self):
        self.ensure_one()
        return {
            'name': _('Wallet Transactions'),
            'type': 'ir.actions.act_window',
            'res_model': 'seller.wallet.transaction',
            'view_mode': 'list',
            'domain': [('wallet_id', '=', self.id)],
            'context': {'default_wallet_id': self.id},
        }
