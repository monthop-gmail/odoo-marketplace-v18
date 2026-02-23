# -*- coding: utf-8 -*-
"""
Admin API base utilities - decorator and formatters
"""
import logging
from functools import wraps

from odoo.http import request

from .main import (
    require_auth, success_response, error_response,
    get_product_image_url
)

_logger = logging.getLogger(__name__)

OFFICER_GROUP = 'core_marketplace.marketplace_officer_group'
MANAGER_GROUP = 'core_marketplace.marketplace_manager_group'


def require_admin(func):
    """
    Decorator that wraps require_auth and additionally verifies
    that the authenticated LINE user is a platform officer or manager.
    Sets request.admin_user for convenience.
    """
    @wraps(func)
    @require_auth
    def wrapper(*args, **kwargs):
        partner = request.line_partner
        if not partner:
            return error_response('Authentication required', 401, 'AUTH_REQUIRED')

        # Find res.users linked to this partner
        user = request.env['res.users'].sudo().search([
            ('partner_id', '=', partner.id),
        ], limit=1)

        if not user:
            return error_response('No user account linked to this LINE profile', 403, 'NOT_ADMIN')

        # Check if user has officer or manager group
        officer_group = request.env.ref(OFFICER_GROUP, raise_if_not_found=False)
        manager_group = request.env.ref(MANAGER_GROUP, raise_if_not_found=False)

        is_admin = False
        if manager_group and manager_group in user.groups_id:
            is_admin = True
        elif officer_group and officer_group in user.groups_id:
            is_admin = True

        if not is_admin:
            return error_response(
                'Admin access required (officer or manager)',
                403, 'NOT_ADMIN'
            )

        request.admin_user = user
        return func(*args, **kwargs)
    return wrapper


def require_manager(func):
    """
    Decorator that wraps require_admin and additionally verifies
    that the authenticated user is a platform Manager (not just Officer).
    """
    @wraps(func)
    @require_admin
    def wrapper(*args, **kwargs):
        manager_group = request.env.ref(MANAGER_GROUP, raise_if_not_found=False)
        if not manager_group or manager_group not in request.admin_user.groups_id:
            return error_response(
                'Manager access required',
                403, 'NOT_MANAGER'
            )
        return func(*args, **kwargs)
    return wrapper


def format_member(member):
    """Format line.channel.member for admin API response"""
    return {
        'id': member.id,
        'line_user_id': member.line_user_id,
        'display_name': member.display_name,
        'picture_url': member.picture_url or '',
        'member_type': member.member_type,
        'registration_state': member.registration_state,
        'is_following': member.is_following,
        'follow_date': member.follow_date.isoformat() if member.follow_date else None,
        'last_activity_date': member.last_activity_date.isoformat() if member.last_activity_date else None,
        'order_count': member.order_count,
        'total_spent': member.total_spent,
        'partner': {
            'id': member.partner_id.id,
            'name': member.partner_id.name,
            'email': member.partner_id.email or '',
            'phone': member.partner_id.phone or member.partner_id.mobile or '',
        } if member.partner_id else None,
    }


def format_seller(partner):
    """Format res.partner seller for admin API response"""
    return {
        'id': partner.id,
        'name': partner.name,
        'email': partner.email or '',
        'phone': partner.phone or partner.mobile or '',
        'state': partner.state,
        'seller': partner.seller,
        'profile_image_url': partner.profile_image_url if hasattr(partner, 'profile_image_url') else '',
        'create_date': partner.create_date.isoformat() if partner.create_date else None,
        'approved_date': partner.approved_date.isoformat() if hasattr(partner, 'approved_date') and partner.approved_date else None,
        'product_count': partner.seller_product_count if hasattr(partner, 'seller_product_count') else 0,
        'shop': {
            'id': partner.seller_shop_id.id,
            'name': partner.seller_shop_id.name,
        } if hasattr(partner, 'seller_shop_id') and partner.seller_shop_id else None,
    }


def format_admin_order(order):
    """Format sale.order for admin API response"""
    return {
        'id': order.id,
        'name': order.name,
        'date': order.date_order.isoformat() if order.date_order else None,
        'state': order.state,
        'state_display': dict(order._fields['state'].selection).get(order.state, ''),
        'customer': {
            'id': order.partner_id.id,
            'name': order.partner_id.name,
        },
        'subtotal': order.amount_untaxed,
        'tax': order.amount_tax,
        'total': order.amount_total,
        'currency': order.currency_id.symbol if order.currency_id else '฿',
        'item_count': len(order.order_line),
    }


def format_admin_order_detail(order):
    """Format sale.order with full details for admin"""
    data = format_admin_order(order)

    # Customer details
    data['customer'] = {
        'id': order.partner_id.id,
        'name': order.partner_id.name,
        'email': order.partner_id.email or '',
        'phone': order.partner_id.phone or order.partner_id.mobile or '',
    }

    # Shipping address
    shipping = order.partner_shipping_id
    if shipping:
        data['shipping_address'] = {
            'name': shipping.name,
            'phone': shipping.phone or shipping.mobile or '',
            'street': shipping.street or '',
            'street2': shipping.street2 or '',
            'city': shipping.city or '',
            'state': shipping.state_id.name if shipping.state_id else '',
            'zip': shipping.zip or '',
            'country': shipping.country_id.name if shipping.country_id else '',
        }
    else:
        data['shipping_address'] = None

    # Order lines
    data['lines'] = []
    for line in order.order_line:
        line_data = {
            'id': line.id,
            'product': {
                'id': line.product_id.id,
                'name': line.product_id.name,
                'image_url': get_product_image_url(line.product_id.product_tmpl_id) if line.product_id.product_tmpl_id else None,
            },
            'quantity': line.product_uom_qty,
            'price_unit': line.price_unit,
            'subtotal': line.price_subtotal,
            'total': line.price_total,
        }
        # Add seller info if marketplace line
        if hasattr(line, 'marketplace_seller_id') and line.marketplace_seller_id:
            line_data['seller'] = {
                'id': line.marketplace_seller_id.id,
                'name': line.marketplace_seller_id.name,
            }
            line_data['marketplace_state'] = line.marketplace_state if hasattr(line, 'marketplace_state') else ''
        data['lines'].append(line_data)

    return data


def format_notify_log(log):
    """Format line.notify.log for admin API response"""
    return {
        'id': log.id,
        'notify_type': log.notify_type,
        'message_type': log.message_type,
        'message': log.message,
        'state': log.state,
        'sent_date': log.sent_date.isoformat() if log.sent_date else None,
        'create_date': log.create_date.isoformat() if log.create_date else None,
        'target_name': log.partner_id.name if log.partner_id else log.line_user_id,
        'error_message': log.error_message or '',
    }


def format_team_member(record):
    """Format admin.team.member for API response"""
    partner = record.partner_id
    member = record.line_member_id
    return {
        'id': record.id,
        'partner_id': partner.id,
        'name': partner.name or '',
        'email': partner.email or '',
        'phone': partner.phone or partner.mobile or '',
        'role': record.role,
        'state': record.state,
        'picture_url': member.picture_url if member else '',
        'line_display_name': member.display_name if member else '',
        'invite_date': record.invite_date.isoformat() if record.invite_date else None,
        'invite_notes': record.invite_notes or '',
        'invited_by_name': record.invited_by.name if record.invited_by else '',
        'revoke_date': record.revoke_date.isoformat() if record.revoke_date else None,
        'revoke_reason': record.revoke_reason or '',
        'revoked_by_name': record.revoked_by.name if record.revoked_by else '',
    }
