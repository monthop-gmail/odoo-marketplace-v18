# -*- coding: utf-8 -*-
"""
Compare API endpoints for LINE Marketplace
"""
import json
import logging

from odoo import http
from odoo.http import request

from .main import (
    success_response, error_response, require_auth,
    get_product_image_url
)

_logger = logging.getLogger(__name__)


class CompareApiController(http.Controller):
    """Product Compare API"""

    def _get_or_create_compare_list(self, partner):
        """Get existing compare list or create new one"""
        CompareList = request.env['line.compare.list'].sudo()
        compare_list = CompareList.search([
            ('partner_id', '=', partner.id),
        ], limit=1, order='create_date desc')

        if not compare_list:
            compare_list = CompareList.create({
                'partner_id': partner.id,
                'channel_id': request.line_channel.id if hasattr(request, 'line_channel') else False,
            })

        return compare_list

    def _format_compare_item(self, item):
        """Format compare item for API response"""
        product = item.product_id
        return {
            'id': item.id,
            'product_id': product.id,
            'name': product.name,
            'price': product.list_price,
            'currency': product.currency_id.symbol if product.currency_id else '',
            'image_url': get_product_image_url(product),
            'category': {
                'id': product.categ_id.id,
                'name': product.categ_id.name,
            } if product.categ_id else None,
            'description': product.description_sale or '',
            'weight': product.weight,
            'available': product.sale_ok and product.is_published,
        }

    def _format_compare_list(self, compare_list):
        """Format compare list for API response"""
        items = [self._format_compare_item(item) for item in compare_list.item_ids]

        # Build comparison attributes
        attributes = self._build_comparison_attributes(compare_list.item_ids)

        return {
            'id': compare_list.id,
            'items': items,
            'item_count': len(items),
            'max_items': compare_list.MAX_ITEMS,
            'attributes': attributes,
        }

    def _build_comparison_attributes(self, items):
        """Build attribute comparison matrix"""
        if not items:
            return []

        attributes = [
            {'name': 'Price', 'key': 'price', 'values': []},
            {'name': 'Category', 'key': 'category', 'values': []},
            {'name': 'Weight', 'key': 'weight', 'values': []},
            {'name': 'Available', 'key': 'available', 'values': []},
        ]

        for item in items:
            product = item.product_id
            attributes[0]['values'].append(f"{product.currency_id.symbol}{product.list_price:.2f}")
            attributes[1]['values'].append(product.categ_id.name if product.categ_id else '-')
            attributes[2]['values'].append(f"{product.weight} kg" if product.weight else '-')
            attributes[3]['values'].append('Yes' if product.sale_ok and product.is_published else 'No')

        # Add product-specific attributes if available
        if items and hasattr(items[0].product_id, 'attribute_line_ids'):
            attr_dict = {}
            for item in items:
                for attr_line in item.product_id.attribute_line_ids:
                    attr_name = attr_line.attribute_id.name
                    if attr_name not in attr_dict:
                        attr_dict[attr_name] = {'name': attr_name, 'key': attr_name.lower().replace(' ', '_'), 'values': []}

            for attr_name in attr_dict:
                for item in items:
                    value = '-'
                    for attr_line in item.product_id.attribute_line_ids:
                        if attr_line.attribute_id.name == attr_name:
                            value = ', '.join(attr_line.value_ids.mapped('name'))
                            break
                    attr_dict[attr_name]['values'].append(value)

            attributes.extend(attr_dict.values())

        return attributes

    @http.route('/api/line-buyer/compare', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def get_compare_list(self, **kwargs):
        """Get user's compare list with comparison data"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response({
                    'items': [],
                    'item_count': 0,
                    'max_items': 4,
                    'attributes': [],
                })

            compare_list = self._get_or_create_compare_list(request.line_partner)
            return success_response(self._format_compare_list(compare_list))

        except Exception as e:
            _logger.error(f'Error in get_compare_list: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/compare/add', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def add_to_compare(self, **kwargs):
        """
        Add product to compare list.

        POST body (JSON):
        - product_id: Product template ID (required)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            product_id = data.get('product_id')

            if not product_id:
                return error_response('product_id is required', 400)

            # Verify product exists
            product = request.env['product.template'].sudo().browse(int(product_id))
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            # Ensure partner exists
            if not request.line_partner:
                request.line_partner = request.env['res.partner'].sudo().get_or_create_from_line(
                    request.line_user_id,
                    request.line_channel.id,
                    {'display_name': request.line_member.display_name}
                )
                request.line_member.sudo().with_context(tracking_disable=True).partner_id = request.line_partner

            compare_list = self._get_or_create_compare_list(request.line_partner)
            result = compare_list.add_product(int(product_id))

            if 'error' in result:
                return error_response(result['error'], 400)

            return success_response(
                self._format_compare_list(compare_list),
                message='Product added to compare'
            )

        except Exception as e:
            _logger.error(f'Error in add_to_compare: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/compare/remove', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def remove_from_compare(self, **kwargs):
        """
        Remove product from compare list.

        POST body (JSON):
        - product_id: Product template ID (required)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            product_id = data.get('product_id')

            if not product_id:
                return error_response('product_id is required', 400)

            if not request.line_partner:
                return error_response('Compare list is empty', 404)

            compare_list = self._get_or_create_compare_list(request.line_partner)
            result = compare_list.remove_product(int(product_id))

            if 'error' in result:
                return error_response(result['error'], 404)

            return success_response(
                self._format_compare_list(compare_list),
                message='Product removed from compare'
            )

        except Exception as e:
            _logger.error(f'Error in remove_from_compare: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/compare/clear', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def clear_compare(self, **kwargs):
        """Clear compare list"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response(message='Compare list cleared')

            compare_list = self._get_or_create_compare_list(request.line_partner)
            compare_list.clear()

            return success_response(message='Compare list cleared')

        except Exception as e:
            _logger.error(f'Error in clear_compare: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-buyer/compare/check/<int:product_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def check_in_compare(self, product_id, **kwargs):
        """Check if product is in user's compare list"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            if not request.line_partner:
                return success_response({'in_compare': False})

            compare_list = self._get_or_create_compare_list(request.line_partner)
            in_compare = compare_list.item_ids.filtered(lambda i: i.product_id.id == product_id)

            return success_response({'in_compare': bool(in_compare)})

        except Exception as e:
            _logger.error(f'Error in check_in_compare: {str(e)}')
            return error_response(str(e), 500)
