# -*- coding: utf-8 -*-
"""
Product API endpoints for LINE Marketplace
"""
import logging

from odoo import http
from odoo.http import request

from .main import (
    success_response, error_response, require_auth,
    format_product
)

_logger = logging.getLogger(__name__)


class ProductApiController(http.Controller):
    """Product browsing API"""

    @http.route('/api/line-buyer/products', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    def get_products(self, **kwargs):
        """
        Get product list with filtering and pagination.

        Query params:
        - page: Page number (default 1)
        - limit: Items per page (default 20, max 100)
        - category_id: Filter by category
        - seller_id: Filter by seller (marketplace)
        - search: Search term
        - sort: Sort field (name, price, date)
        - order: Sort order (asc, desc)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            # Pagination
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 100)
            offset = (page - 1) * limit

            # Build domain
            domain = [
                ('is_published', '=', True),
                ('sale_ok', '=', True),
            ]

            # Category filter
            category_id = kwargs.get('category_id')
            if category_id:
                domain.append(('categ_id', '=', int(category_id)))

            # Seller filter (marketplace)
            seller_id = kwargs.get('seller_id')
            if seller_id and hasattr(request.env['product.template'], 'marketplace_seller_id'):
                domain.append(('marketplace_seller_id', '=', int(seller_id)))

            # Search
            search = kwargs.get('search', '').strip()
            if search:
                domain.append(('name', 'ilike', search))

            # Sort
            sort_field = kwargs.get('sort', 'create_date')
            sort_order = kwargs.get('order', 'desc')
            valid_sorts = ['name', 'list_price', 'create_date']
            if sort_field not in valid_sorts:
                sort_field = 'create_date'
            order = f'{sort_field} {sort_order}'

            # Query products
            Product = request.env['product.template'].sudo()
            total = Product.search_count(domain)
            products = Product.search(domain, limit=limit, offset=offset, order=order)

            return success_response({
                'items': [format_product(p) for p in products],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                }
            })

        except Exception as e:
            _logger.error(f'Error in get_products: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/products/<int:product_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    def get_product_detail(self, product_id, **kwargs):
        """
        Get product details by ID.

        Path params:
        - product_id: Product template ID
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product = request.env['product.template'].sudo().browse(product_id)

            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            if not product.is_published:
                return error_response('Product not available', 404, 'PRODUCT_NOT_AVAILABLE')

            return success_response(format_product(product, include_details=True))

        except Exception as e:
            _logger.error(f'Error in get_product_detail: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/categories', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    def get_categories(self, **kwargs):
        """
        Get product categories.

        Query params:
        - parent_id: Filter by parent category (optional)
        - with_products: Only return categories with published products (default true)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            domain = []

            # Parent filter
            parent_id = kwargs.get('parent_id')
            if parent_id:
                domain.append(('parent_id', '=', int(parent_id)))
            else:
                # Only root categories if no parent specified
                domain.append(('parent_id', '=', False))

            Category = request.env['product.category'].sudo()
            categories = Category.search(domain, order='name')

            # Filter to only categories with published products
            with_products = kwargs.get('with_products', 'true').lower() == 'true'
            if with_products:
                result = []
                Product = request.env['product.template'].sudo()
                for cat in categories:
                    count = Product.search_count([
                        ('categ_id', 'child_of', cat.id),
                        ('is_published', '=', True),
                        ('sale_ok', '=', True),
                    ])
                    if count > 0:
                        result.append({
                            'id': cat.id,
                            'name': cat.name,
                            'product_count': count,
                            'has_children': bool(cat.child_id),
                        })
            else:
                result = [{
                    'id': cat.id,
                    'name': cat.name,
                    'has_children': bool(cat.child_id),
                } for cat in categories]

            return success_response({'categories': result})

        except Exception as e:
            _logger.error(f'Error in get_categories: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/sellers', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    def get_sellers(self, **kwargs):
        """
        Get marketplace sellers list.
        Only available if core_marketplace module is installed.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            # Check if marketplace is installed
            Partner = request.env['res.partner'].sudo()
            if not hasattr(Partner, 'seller'):
                return error_response('Marketplace not installed', 404)

            sellers = Partner.search([
                ('seller', '=', True),
                ('state', '=', 'approved'),
            ], order='name')

            result = [{
                'id': s.id,
                'name': s.name,
                'shop_name': s.url_handler if hasattr(s, 'url_handler') else s.name,
                'image_url': f"{request.env['ir.config_parameter'].sudo().get_param('web.base.url')}/web/image/res.partner/{s.id}/image_128" if s.image_128 else None,
            } for s in sellers]

            return success_response({'sellers': result})

        except Exception as e:
            _logger.error(f'Error in get_sellers: {str(e)}')
            return error_response(str(e), 500)
