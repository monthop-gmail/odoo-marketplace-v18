# -*- coding: utf-8 -*-
"""
Seller Dashboard & Reports API endpoints
"""
import logging
from datetime import datetime, timedelta

from odoo import http
from odoo.http import request

from .main import success_response, error_response
from .seller_main import require_seller, format_seller_order_line

_logger = logging.getLogger(__name__)


class SellerDashboardController(http.Controller):
    """Seller Dashboard & Reports API"""

    @http.route('/api/line-seller/dashboard', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_dashboard(self, **kwargs):
        """
        Get seller dashboard overview with stats and recent orders.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            seller = request.seller_partner
            seller_id = seller.id

            # Date range for today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            SOL = request.env['sale.order.line'].sudo()
            Product = request.env['product.template'].sudo()

            # Base domain for seller's order lines (exclude drafts)
            base_domain = [
                ('marketplace_seller_id', '=', seller_id),
                ('order_id.state', 'not in', ('draft', 'sent', 'cancel')),
            ]

            # Today's orders
            today_lines = SOL.search(base_domain + [
                ('order_id.date_order', '>=', today_start),
            ])
            today_orders = len(set(today_lines.mapped('order_id').ids))
            today_revenue = sum(today_lines.mapped('price_subtotal'))

            # Pending shipment (pending or approved but not yet shipped)
            pending_ship = SOL.search_count(base_domain + [
                ('marketplace_state', 'in', ('pending', 'approved')),
            ])

            # Active products (approved)
            active_products = Product.search_count([
                ('marketplace_seller_id', '=', seller_id),
                ('status', '=', 'approved'),
            ])

            # Recent orders (last 5)
            recent_lines = SOL.search(base_domain + [
                ('marketplace_state', '!=', 'new'),
            ], order='create_date desc', limit=5)

            # Currency
            currency = seller.seller_currency_id.symbol if hasattr(seller, 'seller_currency_id') and seller.seller_currency_id else '฿'

            return success_response({
                'stats': {
                    'today_orders': today_orders,
                    'pending_ship': pending_ship,
                    'today_revenue': today_revenue,
                    'active_products': active_products,
                    'currency': currency,
                },
                'recent_orders': [format_seller_order_line(l) for l in recent_lines],
            })

        except Exception as e:
            _logger.error(f'Error in seller dashboard: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/reports', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_reports(self, **kwargs):
        """
        Get sales reports for a given period.

        Query params:
        - period: today | week | month (default: today)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            seller = request.seller_partner
            seller_id = seller.id
            period = kwargs.get('period', 'today')

            # Calculate date range
            now = datetime.now()
            if period == 'week':
                date_from = now - timedelta(days=now.weekday())
            elif period == 'month':
                date_from = now.replace(day=1)
            else:  # today
                date_from = now
            date_from = date_from.replace(hour=0, minute=0, second=0, microsecond=0)

            SOL = request.env['sale.order.line'].sudo()

            # Query order lines in period
            domain = [
                ('marketplace_seller_id', '=', seller_id),
                ('order_id.state', 'not in', ('draft', 'sent', 'cancel')),
                ('marketplace_state', 'not in', ('new', 'cancel')),
                ('order_id.date_order', '>=', date_from),
            ]

            lines = SOL.search(domain)

            # Aggregate stats
            total_sales = sum(lines.mapped('price_subtotal'))
            order_ids = list(set(lines.mapped('order_id').ids))
            order_count = len(order_ids)
            items_sold = sum(lines.mapped('product_uom_qty'))
            avg_order = total_sales / order_count if order_count > 0 else 0

            # Top products (group by product, sum qty)
            product_stats = {}
            for line in lines:
                pid = line.product_id.id
                if pid not in product_stats:
                    product_stats[pid] = {
                        'id': pid,
                        'name': line.product_id.name,
                        'image_url': get_product_image_url_safe(line.product_id),
                        'qty_sold': 0,
                        'revenue': 0,
                    }
                product_stats[pid]['qty_sold'] += line.product_uom_qty
                product_stats[pid]['revenue'] += line.price_subtotal

            top_products = sorted(
                product_stats.values(),
                key=lambda x: x['qty_sold'],
                reverse=True,
            )[:5]

            currency = seller.seller_currency_id.symbol if hasattr(seller, 'seller_currency_id') and seller.seller_currency_id else '฿'

            return success_response({
                'period': period,
                'total_sales': total_sales,
                'order_count': order_count,
                'items_sold': items_sold,
                'avg_order': round(avg_order, 2),
                'top_products': top_products,
                'currency': currency,
            })

        except Exception as e:
            _logger.error(f'Error in seller reports: {str(e)}')
            return error_response(str(e), 500)


def get_product_image_url_safe(product):
    """Get product image URL safely (handles product.product)"""
    try:
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        tmpl = product.product_tmpl_id if hasattr(product, 'product_tmpl_id') else product
        if tmpl.image_256:
            return f"{base_url}/web/image/product.template/{tmpl.id}/image_256"
    except Exception:
        pass
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    return f"{base_url}/web/static/img/placeholder.png"
