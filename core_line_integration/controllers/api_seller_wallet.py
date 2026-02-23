# -*- coding: utf-8 -*-
"""
Seller Wallet API endpoints for LIFF Seller App
"""
import json
import logging

from odoo import http, _
from odoo.http import request

from .seller_main import require_seller, owner_only
from .main import success_response, error_response

_logger = logging.getLogger(__name__)


class SellerWalletController(http.Controller):

    # ==================== Wallet Overview ====================

    @http.route('/api/line-seller/wallet', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_wallet(self, **kwargs):
        """Get seller's wallet overview with balance and withdrawal limits."""
        seller = request.seller_partner
        wallet = request.env['seller.wallet'].sudo().search([
            ('seller_id', '=', seller.id),
        ], limit=1)

        if not wallet:
            # Auto-create wallet if seller is approved but has no wallet
            wallet = request.env['seller.wallet'].sudo().get_or_create_wallet(seller.id)

        if not wallet:
            return error_response('Wallet not available', 404, 'WALLET_NOT_FOUND')

        # Get withdrawal limits
        min_amount = int(
            request.env['ir.config_parameter'].sudo().get_param(
                'core_marketplace.mp_min_withdrawal_amount', '0'
            )
        )
        has_pending = request.env['seller.withdrawal.request'].sudo().search_count([
            ('seller_id', '=', seller.id),
            ('state', 'in', ['pending', 'approved', 'processing']),
        ]) > 0

        return success_response({
            'wallet': {
                'id': wallet.id,
                'name': wallet.name,
                'balance': wallet.balance,
                'total_earned': wallet.total_earned,
                'total_withdrawn': wallet.total_withdrawn,
                'state': wallet.state,
                'currency': wallet.currency_id.symbol or '฿',
            },
            'withdrawal_limits': {
                'min_amount': min_amount,
                'has_pending_request': has_pending,
                'can_withdraw': (
                    wallet.state == 'active'
                    and wallet.balance > 0
                    and not has_pending
                ),
            },
        })

    # ==================== Transaction History ====================

    @http.route('/api/line-seller/wallet/transactions', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_transactions(self, **kwargs):
        """Get wallet transaction history with pagination and type filter."""
        seller = request.seller_partner
        wallet = request.env['seller.wallet'].sudo().search([
            ('seller_id', '=', seller.id),
        ], limit=1)
        if not wallet:
            return error_response('Wallet not found', 404, 'WALLET_NOT_FOUND')

        page = int(kwargs.get('page', 1))
        limit = min(int(kwargs.get('limit', 20)), 100)
        offset = (page - 1) * limit
        tx_type = kwargs.get('type', 'all')

        domain = [('wallet_id', '=', wallet.id)]
        if tx_type == 'credits':
            domain.append(('amount', '>', 0))
        elif tx_type == 'debits':
            domain.append(('amount', '<', 0))
        elif tx_type != 'all':
            domain.append(('type', '=', tx_type))

        Transaction = request.env['seller.wallet.transaction'].sudo()
        total = Transaction.search_count(domain)
        transactions = Transaction.search(domain, limit=limit, offset=offset, order='create_date desc, id desc')

        return success_response({
            'transactions': [_format_transaction(tx) for tx in transactions],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': max(1, (total + limit - 1) // limit),
            },
        })

    @http.route('/api/line-seller/wallet/transactions/<int:tx_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_transaction_detail(self, tx_id, **kwargs):
        """Get transaction detail."""
        seller = request.seller_partner
        tx = request.env['seller.wallet.transaction'].sudo().browse(tx_id)
        if not tx.exists() or tx.seller_id.id != seller.id:
            return error_response('Transaction not found', 404, 'TX_NOT_FOUND')

        data = _format_transaction(tx)
        data['description'] = tx.description or ''
        if tx.sale_order_line_id:
            data['order_line'] = {
                'id': tx.sale_order_line_id.id,
                'order_name': tx.sale_order_line_id.order_id.name,
            }
        return success_response(data)

    # ==================== Withdrawal Requests ====================

    @http.route('/api/line-seller/wallet/withdraw', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    @owner_only
    def request_withdrawal(self, **kwargs):
        """Create a new withdrawal request."""
        seller = request.seller_partner
        wallet = request.env['seller.wallet'].sudo().search([
            ('seller_id', '=', seller.id),
        ], limit=1)
        if not wallet:
            return error_response('Wallet not found', 404, 'WALLET_NOT_FOUND')

        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')

        amount = float(body.get('amount', 0))
        payment_method_id = int(body.get('payment_method_id', 0))
        if amount <= 0:
            return error_response('Amount must be positive', 400, 'INVALID_AMOUNT')
        if not payment_method_id:
            return error_response('Payment method is required', 400, 'MISSING_PAYMENT_METHOD')

        # Validate payment method exists
        pm = request.env['seller.payment.method'].sudo().browse(payment_method_id)
        if not pm.exists():
            return error_response('Invalid payment method', 400, 'INVALID_PAYMENT_METHOD')

        try:
            wd_request = request.env['seller.withdrawal.request'].sudo().create({
                'wallet_id': wallet.id,
                'amount': amount,
                'payment_method_id': payment_method_id,
                'bank_name': body.get('bank_name', ''),
                'bank_account_name': body.get('bank_account_name', ''),
                'bank_account_number': body.get('bank_account_number', ''),
                'bank_branch': body.get('bank_branch', ''),
                'note': body.get('note', ''),
            })
            # Auto-submit
            wd_request.action_submit()

            return success_response({
                'request_id': wd_request.id,
                'name': wd_request.name,
                'amount': wd_request.amount,
                'state': wd_request.state,
                'requested_date': wd_request.requested_date.isoformat() if wd_request.requested_date else None,
            }, message='Withdrawal request submitted')
        except Exception as e:
            _logger.warning('Withdrawal request failed: %s', str(e))
            return error_response(str(e), 400, 'WITHDRAWAL_FAILED')

    @http.route('/api/line-seller/wallet/withdrawals', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_withdrawals(self, **kwargs):
        """Get seller's withdrawal request history."""
        seller = request.seller_partner
        page = int(kwargs.get('page', 1))
        limit = min(int(kwargs.get('limit', 20)), 100)
        offset = (page - 1) * limit
        state = kwargs.get('state', 'all')

        domain = [('seller_id', '=', seller.id)]
        if state != 'all':
            domain.append(('state', '=', state))

        WdRequest = request.env['seller.withdrawal.request'].sudo()
        total = WdRequest.search_count(domain)
        requests_list = WdRequest.search(domain, limit=limit, offset=offset, order='create_date desc')

        return success_response({
            'withdrawals': [_format_withdrawal(r) for r in requests_list],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': max(1, (total + limit - 1) // limit),
            },
        })

    @http.route('/api/line-seller/wallet/withdrawals/<int:wd_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_withdrawal_detail(self, wd_id, **kwargs):
        """Get withdrawal request detail."""
        seller = request.seller_partner
        wd = request.env['seller.withdrawal.request'].sudo().browse(wd_id)
        if not wd.exists() or wd.seller_id.id != seller.id:
            return error_response('Request not found', 404, 'REQUEST_NOT_FOUND')

        data = _format_withdrawal(wd)
        data['bank_name'] = wd.bank_name or ''
        data['bank_account_name'] = wd.bank_account_name or ''
        data['bank_account_number'] = wd.bank_account_number or ''
        data['bank_branch'] = wd.bank_branch or ''
        data['rejection_reason'] = wd.rejection_reason or ''
        data['note'] = wd.note or ''
        return success_response(data)

    @http.route('/api/line-seller/wallet/withdrawals/<int:wd_id>/cancel', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def cancel_withdrawal(self, wd_id, **kwargs):
        """Cancel a pending withdrawal request."""
        seller = request.seller_partner
        wd = request.env['seller.withdrawal.request'].sudo().browse(wd_id)
        if not wd.exists() or wd.seller_id.id != seller.id:
            return error_response('Request not found', 404, 'REQUEST_NOT_FOUND')

        try:
            wd.action_cancel()
            return success_response({
                'request_id': wd.id,
                'state': wd.state,
            }, message='Withdrawal cancelled')
        except Exception as e:
            return error_response(str(e), 400, 'CANCEL_FAILED')


# ==================== Format Helpers ====================

def _format_transaction(tx):
    """Format wallet transaction for API response."""
    type_labels = {
        'commission_credit': 'Commission Credit',
        'order_refund_debit': 'Order Refund',
        'withdrawal': 'Withdrawal',
        'adjustment_credit': 'Adjustment (Credit)',
        'adjustment_debit': 'Adjustment (Debit)',
    }
    return {
        'id': tx.id,
        'type': tx.type,
        'type_display': type_labels.get(tx.type, tx.type),
        'amount': tx.amount,
        'balance_after': tx.balance_after,
        'reference': tx.reference or '',
        'description': tx.description or '',
        'date': tx.date.isoformat() if tx.date else None,
        'currency': tx.currency_id.symbol or '฿',
    }


def _format_withdrawal(wd):
    """Format withdrawal request for API response."""
    state_labels = {
        'draft': 'Draft',
        'pending': 'Pending Approval',
        'approved': 'Approved',
        'processing': 'Processing',
        'completed': 'Completed',
        'rejected': 'Rejected',
        'cancelled': 'Cancelled',
    }
    return {
        'id': wd.id,
        'name': wd.name,
        'amount': wd.amount,
        'currency': wd.currency_id.symbol or '฿',
        'state': wd.state,
        'state_display': state_labels.get(wd.state, wd.state),
        'payment_method': wd.payment_method_id.name if wd.payment_method_id else '',
        'requested_date': wd.requested_date.isoformat() if wd.requested_date else None,
        'approved_date': wd.approved_date.isoformat() if wd.approved_date else None,
        'completed_date': wd.completed_date.isoformat() if wd.completed_date else None,
        'approved_by': wd.approved_by.name if wd.approved_by else '',
    }
