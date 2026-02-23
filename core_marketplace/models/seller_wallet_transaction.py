# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SellerWalletTransaction(models.Model):
    _name = 'seller.wallet.transaction'
    _description = 'Seller Wallet Transaction'
    _order = 'create_date desc, id desc'
    _rec_name = 'reference'

    wallet_id = fields.Many2one(
        'seller.wallet',
        string='Wallet',
        required=True,
        ondelete='restrict',
        index=True,
    )
    seller_id = fields.Many2one(
        related='wallet_id.seller_id',
        string='Seller',
        store=True,
        index=True,
    )
    type = fields.Selection([
        ('commission_credit', 'Commission Credit'),
        ('order_refund_debit', 'Order Refund'),
        ('withdrawal', 'Withdrawal'),
        ('adjustment_credit', 'Adjustment (Credit)'),
        ('adjustment_debit', 'Adjustment (Debit)'),
    ], string='Type', required=True, index=True)
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        required=True,
    )
    balance_after = fields.Monetary(
        string='Balance After',
        currency_field='currency_id',
        required=True,
    )
    currency_id = fields.Many2one(
        related='wallet_id.currency_id',
        string='Currency',
        store=True,
    )
    reference = fields.Char(
        string='Reference',
        index=True,
    )
    description = fields.Text(string='Description')
    date = fields.Datetime(
        string='Transaction Date',
        default=fields.Datetime.now,
        required=True,
    )
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line',
    )
    seller_payment_id = fields.Many2one(
        'seller.payment',
        string='Seller Payment',
    )
    withdrawal_request_id = fields.Many2one(
        'seller.withdrawal.request',
        string='Withdrawal Request',
    )
    company_id = fields.Many2one(
        related='wallet_id.company_id',
        string='Company',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('allow_wallet_transaction_create'):
            raise ValidationError(
                _('Wallet transactions can only be created through wallet credit/debit methods.')
            )
        return super().create(vals_list)

    def write(self, vals):
        raise ValidationError(
            _('Wallet transactions are immutable and cannot be modified.')
        )

    def unlink(self):
        raise ValidationError(
            _('Wallet transactions cannot be deleted.')
        )
