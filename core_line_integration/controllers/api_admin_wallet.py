# -*- coding: utf-8 -*-
"""
Admin Wallet API endpoints for LIFF Admin App
"""
import json
import logging

from odoo import http, _
from odoo.http import request

from .admin_main import require_admin
from .main import success_response, error_response

_logger = logging.getLogger(__name__)


class AdminWalletController(http.Controller):

    # ==================== Wallets ====================

    @http.route('/api/line-admin/wallets', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_wallets(self, **kwargs):
        """List all seller wallets with balances."""
        page = int(kwargs.get('page', 1))
        limit = min(int(kwargs.get('limit', 20)), 100)
        offset = (page - 1) * limit
        search = kwargs.get('search', '').strip()

        domain = []
        if search:
            domain.append(('seller_id.name', 'ilike', search))

        Wallet = request.env['seller.wallet'].sudo()
        total = Wallet.search_count(domain)
        wallets = Wallet.search(domain, limit=limit, offset=offset, order='balance desc')

        return success_response({
            'wallets': [_format_admin_wallet(w) for w in wallets],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': max(1, (total + limit - 1) // limit),
            },
        })

    @http.route('/api/line-admin/wallets/<int:wallet_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_wallet_detail(self, wallet_id, **kwargs):
        """Get wallet detail with recent transactions."""
        wallet = request.env['seller.wallet'].sudo().browse(wallet_id)
        if not wallet.exists():
            return error_response('Wallet not found', 404, 'WALLET_NOT_FOUND')

        data = _format_admin_wallet(wallet)

        # Recent transactions (last 10)
        transactions = request.env['seller.wallet.transaction'].sudo().search([
            ('wallet_id', '=', wallet.id),
        ], limit=10, order='create_date desc')
        data['recent_transactions'] = [_format_admin_transaction(tx) for tx in transactions]

        # Pending withdrawal requests
        pending_wds = request.env['seller.withdrawal.request'].sudo().search([
            ('wallet_id', '=', wallet.id),
            ('state', 'in', ['pending', 'approved', 'processing']),
        ])
        data['pending_withdrawals'] = [_format_admin_withdrawal(wd) for wd in pending_wds]

        return success_response(data)

    # ==================== Withdrawal Requests ====================

    @http.route('/api/line-admin/withdrawals', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_admin
    def get_withdrawals(self, **kwargs):
        """List all withdrawal requests with filters."""
        page = int(kwargs.get('page', 1))
        limit = min(int(kwargs.get('limit', 20)), 100)
        offset = (page - 1) * limit
        state = kwargs.get('state', 'all')

        domain = []
        if state != 'all':
            domain.append(('state', '=', state))

        WdRequest = request.env['seller.withdrawal.request'].sudo()
        total = WdRequest.search_count(domain)
        requests_list = WdRequest.search(domain, limit=limit, offset=offset, order='create_date desc')

        return success_response({
            'withdrawals': [_format_admin_withdrawal(r) for r in requests_list],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': max(1, (total + limit - 1) // limit),
            },
        })

    @http.route('/api/line-admin/withdrawals/<int:wd_id>/approve', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def approve_withdrawal(self, wd_id, **kwargs):
        """Approve a pending withdrawal request."""
        wd = request.env['seller.withdrawal.request'].sudo().browse(wd_id)
        if not wd.exists():
            return error_response('Request not found', 404, 'REQUEST_NOT_FOUND')

        try:
            wd.action_approve()
            return success_response({
                'request_id': wd.id,
                'state': wd.state,
                'approved_by': request.admin_user.name,
            }, message='Withdrawal approved')
        except Exception as e:
            return error_response(str(e), 400, 'APPROVE_FAILED')

    @http.route('/api/line-admin/withdrawals/<int:wd_id>/reject', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def reject_withdrawal(self, wd_id, **kwargs):
        """Reject a withdrawal request with reason."""
        wd = request.env['seller.withdrawal.request'].sudo().browse(wd_id)
        if not wd.exists():
            return error_response('Request not found', 404, 'REQUEST_NOT_FOUND')

        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            body = {}

        reason = body.get('reason', '')
        try:
            wd.rejection_reason = reason
            wd.action_reject()
            return success_response({
                'request_id': wd.id,
                'state': wd.state,
            }, message='Withdrawal rejected')
        except Exception as e:
            return error_response(str(e), 400, 'REJECT_FAILED')

    @http.route('/api/line-admin/withdrawals/<int:wd_id>/complete', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_admin
    def complete_withdrawal(self, wd_id, **kwargs):
        """
        Mark withdrawal as completed.
        This will process payment if in 'approved' state,
        or complete if in 'processing' state.
        """
        wd = request.env['seller.withdrawal.request'].sudo().browse(wd_id)
        if not wd.exists():
            return error_response('Request not found', 404, 'REQUEST_NOT_FOUND')

        try:
            # Auto-advance through states if needed
            if wd.state == 'approved':
                wd.action_process()
            if wd.state == 'processing':
                wd.action_complete()

            return success_response({
                'request_id': wd.id,
                'state': wd.state,
                'completed_date': wd.completed_date.isoformat() if wd.completed_date else None,
            }, message='Withdrawal completed')
        except Exception as e:
            _logger.warning('Complete withdrawal %s failed: %s', wd_id, str(e))
            return error_response(str(e), 400, 'COMPLETE_FAILED')


# ==================== Format Helpers ====================

def _format_admin_wallet(wallet):
    """Format wallet for admin API response."""
    return {
        'id': wallet.id,
        'name': wallet.name,
        'seller': {
            'id': wallet.seller_id.id,
            'name': wallet.seller_id.name,
        },
        'balance': wallet.balance,
        'total_earned': wallet.total_earned,
        'total_withdrawn': wallet.total_withdrawn,
        'state': wallet.state,
        'currency': wallet.currency_id.symbol or '฿',
        'transaction_count': wallet.transaction_count,
    }


def _format_admin_transaction(tx):
    """Format transaction for admin API response."""
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
    }


def _format_admin_withdrawal(wd):
    """Format withdrawal request for admin API response."""
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
        'seller': {
            'id': wd.seller_id.id,
            'name': wd.seller_id.name,
        },
        'amount': wd.amount,
        'currency': wd.currency_id.symbol or '฿',
        'state': wd.state,
        'state_display': state_labels.get(wd.state, wd.state),
        'payment_method': wd.payment_method_id.name if wd.payment_method_id else '',
        'bank_name': wd.bank_name or '',
        'bank_account_name': wd.bank_account_name or '',
        'bank_account_number': wd.bank_account_number or '',
        'bank_branch': wd.bank_branch or '',
        'requested_date': wd.requested_date.isoformat() if wd.requested_date else None,
        'approved_date': wd.approved_date.isoformat() if wd.approved_date else None,
        'completed_date': wd.completed_date.isoformat() if wd.completed_date else None,
        'approved_by': wd.approved_by.name if wd.approved_by else '',
        'rejection_reason': wd.rejection_reason or '',
    }
