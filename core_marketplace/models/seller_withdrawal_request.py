# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SellerWithdrawalRequest(models.Model):
    _name = 'seller.withdrawal.request'
    _description = 'Seller Withdrawal Request'
    _inherit = ['mail.thread']
    _order = 'create_date desc, id desc'

    name = fields.Char(
        string='Request Reference',
        default='NEW',
        copy=False,
        readonly=True,
    )
    wallet_id = fields.Many2one(
        'seller.wallet',
        string='Wallet',
        required=True,
        ondelete='restrict',
    )
    seller_id = fields.Many2one(
        related='wallet_id.seller_id',
        string='Seller',
        store=True,
        index=True,
    )
    amount = fields.Monetary(
        string='Withdrawal Amount',
        currency_field='currency_id',
        required=True,
    )
    currency_id = fields.Many2one(
        related='wallet_id.currency_id',
        string='Currency',
        store=True,
    )
    payment_method_id = fields.Many2one(
        'seller.payment.method',
        string='Payment Method',
        required=True,
    )
    bank_name = fields.Char(string='Bank Name')
    bank_account_name = fields.Char(string='Account Holder Name')
    bank_account_number = fields.Char(string='Account Number')
    bank_branch = fields.Char(string='Branch')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, required=True, index=True)

    requested_date = fields.Datetime(string='Requested Date')
    approved_date = fields.Datetime(string='Approved Date')
    completed_date = fields.Datetime(string='Completed Date')
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
    )
    rejection_reason = fields.Text(string='Rejection Reason')
    note = fields.Text(string='Notes')
    seller_payment_id = fields.Many2one(
        'seller.payment',
        string='Seller Payment',
    )
    company_id = fields.Many2one(
        related='wallet_id.company_id',
        string='Company',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'NEW') == 'NEW':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'seller.withdrawal.request'
                ) or 'WDR/NEW'
        return super().create(vals_list)

    def action_submit(self):
        """Submit for approval: draft → pending."""
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(
                    _('Only draft requests can be submitted.')
                )
            if rec.amount <= 0:
                raise ValidationError(
                    _('Withdrawal amount must be positive.')
                )
            # Validate minimum amount
            min_amount = int(
                self.env['ir.config_parameter'].sudo().get_param(
                    'core_marketplace.mp_min_withdrawal_amount', '0'
                )
            )
            if min_amount > 0 and rec.amount < min_amount:
                raise ValidationError(
                    _('Minimum withdrawal amount is %s.') % min_amount
                )
            # Check for existing pending requests
            pending = self.search([
                ('seller_id', '=', rec.seller_id.id),
                ('state', 'in', ['pending', 'approved', 'processing']),
                ('id', '!=', rec.id),
            ], limit=1)
            if pending:
                raise ValidationError(
                    _('You already have a pending withdrawal request (%s).') % pending.name
                )
            # Validate balance
            if rec.amount > rec.wallet_id.balance:
                raise ValidationError(
                    _('Insufficient wallet balance. Available: %s') % rec.wallet_id.balance
                )
            rec.write({
                'state': 'pending',
                'requested_date': fields.Datetime.now(),
            })

    def action_approve(self):
        """Approve request: pending → approved."""
        for rec in self:
            if rec.state != 'pending':
                raise ValidationError(
                    _('Only pending requests can be approved.')
                )
            rec.write({
                'state': 'approved',
                'approved_date': fields.Datetime.now(),
                'approved_by': self.env.user.id,
            })

    def action_reject(self):
        """Reject request: pending/approved → rejected."""
        for rec in self:
            if rec.state not in ('pending', 'approved'):
                raise ValidationError(
                    _('Only pending or approved requests can be rejected.')
                )
            rec.state = 'rejected'

    def action_process(self):
        """Mark as processing: approved → processing."""
        for rec in self:
            if rec.state != 'approved':
                raise ValidationError(
                    _('Only approved requests can be processed.')
                )
            rec.state = 'processing'

    def action_complete(self):
        """
        Complete withdrawal: processing → completed.
        Debits wallet and creates seller.payment for accounting.
        """
        for rec in self:
            if rec.state != 'processing':
                raise ValidationError(
                    _('Only processing requests can be completed.')
                )
            # Debit wallet
            rec.wallet_id.debit(
                amount=rec.amount,
                transaction_type='withdrawal',
                description=_('Withdrawal: %s') % rec.name,
                reference=rec.name,
                withdrawal_request_id=rec.id,
            )
            # Create seller.payment for accounting
            payment_method_ids = rec.seller_id.payment_method.ids
            payment_vals = {
                'seller_id': rec.seller_id.id,
                'payment_method': rec.payment_method_id.id or (
                    payment_method_ids[0] if payment_method_ids else False
                ),
                'payment_type': 'dr',
                'payment_mode': 'seller_payment',
                'payable_amount': -rec.amount,
                'description': _('Wallet Withdrawal: %s') % rec.name,
                'memo': rec.name,
                'date': fields.Date.today(),
                'state': 'draft',
            }
            seller_payment = self.env['seller.payment'].with_context(
                pass_create_validation=True
            ).create(payment_vals)
            rec.write({
                'seller_payment_id': seller_payment.id,
                'state': 'completed',
                'completed_date': fields.Datetime.now(),
            })
            _logger.info(
                'Withdrawal %s completed: %.2f debited from wallet %s',
                rec.name, rec.amount, rec.wallet_id.name
            )

    def action_cancel(self):
        """Cancel request: draft/pending → cancelled."""
        for rec in self:
            if rec.state not in ('draft', 'pending'):
                raise ValidationError(
                    _('Only draft or pending requests can be cancelled.')
                )
            rec.state = 'cancelled'

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancelled'):
                raise ValidationError(
                    _('Only draft or cancelled requests can be deleted.')
                )
        return super().unlink()
