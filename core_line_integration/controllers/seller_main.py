# -*- coding: utf-8 -*-
"""
Seller API base utilities - decorator and formatters
"""
import logging
from functools import wraps

from odoo.http import request

from .main import (
    require_auth, success_response, error_response,
    get_product_image_url, _get_stock_status
)

_logger = logging.getLogger(__name__)


def require_seller(func):
    """
    Decorator that wraps require_auth and additionally verifies
    that the authenticated LINE user is an approved seller OR an active shop staff.

    Sets on request:
    - seller_partner: the shop OWNER's partner (for both owner and staff)
    - is_shop_owner: True if the user is the shop owner
    - is_shop_staff: True if the user is a shop staff member
    - staff_record: the seller.shop.staff record (or None)
    """
    @wraps(func)
    @require_auth
    def wrapper(*args, **kwargs):
        partner = request.line_partner

        # Case 1: Shop owner (approved seller)
        if partner and partner.seller and partner.state == 'approved':
            request.seller_partner = partner
            request.is_shop_owner = True
            request.is_shop_staff = False
            request.staff_record = None
            return func(*args, **kwargs)

        # Case 2: Shop staff (not a seller, but linked to a shop)
        if partner:
            staff = request.env['seller.shop.staff'].sudo().search([
                ('staff_partner_id', '=', partner.id),
                ('is_active', '=', True),
            ], limit=1)
            if staff and staff.seller_id and staff.seller_id.seller and staff.seller_id.state == 'approved':
                request.seller_partner = staff.seller_id  # Shop owner's partner
                request.is_shop_owner = False
                request.is_shop_staff = True
                request.staff_record = staff
                return func(*args, **kwargs)

        # Neither owner nor staff
        if not partner or not partner.seller:
            return error_response('Not a seller or shop staff', 403, 'NOT_SELLER')
        return error_response(
            f'Seller account is {partner.state}, not approved',
            403, 'SELLER_NOT_APPROVED'
        )
    return wrapper


def owner_only(func):
    """
    Decorator to block shop staff from owner-only operations.
    Must be used AFTER @require_seller.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if getattr(request, 'is_shop_staff', False):
            return error_response(
                'This action is restricted to shop owners only',
                403, 'OWNER_ONLY'
            )
        return func(*args, **kwargs)
    return wrapper


def format_seller_product(product):
    """Format product for seller API response"""
    stock_status, qty_available, is_service = _get_stock_status(product)
    return {
        'id': product.id,
        'name': product.name,
        'status': product.status,
        'status_display': dict(product._fields['status'].selection).get(product.status, ''),
        'price': product.list_price,
        'currency': product.currency_id.symbol if product.currency_id else '฿',
        'image_url': get_product_image_url(product),
        'category': {
            'id': product.categ_id.id,
            'name': product.categ_id.name,
        } if product.categ_id else None,
        'qty_available': qty_available,
        'stock_status': stock_status,
        'is_service': is_service,
        'is_published': product.is_published if hasattr(product, 'is_published') else False,
        'create_date': product.create_date.isoformat() if product.create_date else None,
        'mp_qty': product.mp_qty,
    }


def format_seller_order_line(line):
    """Format sale order line for seller API response"""
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    return {
        'id': line.id,
        'order_name': line.order_id.name,
        'order_id': line.order_id.id,
        'order_date': line.order_id.date_order.isoformat() if line.order_id.date_order else None,
        'customer_name': line.order_id.partner_id.name,
        'product': {
            'id': line.product_id.id,
            'name': line.product_id.name,
            'image_url': get_product_image_url(line.product_id.product_tmpl_id) if line.product_id.product_tmpl_id else None,
        },
        'quantity': line.product_uom_qty,
        'price_unit': line.price_unit,
        'subtotal': line.price_subtotal,
        'total': line.price_total,
        'marketplace_state': line.marketplace_state,
        'marketplace_state_display': dict(line._fields['marketplace_state'].selection).get(line.marketplace_state, ''),
        'seller_amount': line.seller_amount,
        'admin_commission': line.admin_commission,
    }


def format_seller_order_detail(line):
    """Format sale order line with full details for seller"""
    data = format_seller_order_line(line)
    order = line.order_id

    # Customer info
    data['customer'] = {
        'name': order.partner_id.name,
        'phone': order.partner_id.phone or order.partner_id.mobile or '',
        'email': order.partner_id.email or '',
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

    # Order summary
    data['order_total'] = order.amount_total
    data['order_currency'] = order.currency_id.symbol if order.currency_id else '฿'

    # All lines in this order belonging to this seller
    seller_lines = order.order_line.filtered(
        lambda l: l.marketplace_seller_id.id == line.marketplace_seller_id.id
    )
    data['seller_lines'] = [format_seller_order_line(l) for l in seller_lines]

    return data
