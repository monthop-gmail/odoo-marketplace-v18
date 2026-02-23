# -*- coding: utf-8 -*-
"""
Address Management API for LIFF

Endpoints for managing shipping addresses:
- GET /api/line-buyer/addresses - List shipping addresses
- POST /api/line-buyer/addresses - Create new address
- PUT /api/line-buyer/addresses/<id> - Update address
- DELETE /api/line-buyer/addresses/<id> - Delete address
- POST /api/line-buyer/addresses/<id>/set-default - Set as default
- GET /api/line-buyer/provinces - List Thai provinces
"""
import json
import logging
from odoo import http, SUPERUSER_ID
from odoo.http import request

from .main import success_response, error_response, require_auth

_logger = logging.getLogger(__name__)


class AddressApiController(http.Controller):
    """API Controller for shipping address management"""

    # =========================================
    # Address List
    # =========================================
    @http.route('/api/line-buyer/addresses', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_auth
    def list_addresses(self, **kwargs):
        """List all shipping addresses for the current user."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        partner = request.line_partner
        if not partner:
            return error_response('Profile required', 400, 'PROFILE_REQUIRED')

        addresses = partner.with_user(SUPERUSER_ID).get_shipping_addresses()

        result = []
        for addr in addresses:
            result.append(addr.get_shipping_address_dict())

        result.sort(key=lambda x: (not x['is_default'], x['id']))

        return success_response({'addresses': result})

    # =========================================
    # Create Address
    # =========================================
    @http.route('/api/line-buyer/addresses', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def create_address(self, **kwargs):
        """Create a new shipping address."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        partner = request.line_partner
        if not partner:
            return error_response('Profile required', 400, 'PROFILE_REQUIRED')

        try:
            data = json.loads(request.httprequest.data or '{}')
        except json.JSONDecodeError:
            return error_response('Invalid JSON', 400)

        if not data.get('name'):
            return error_response('Name is required', 400)
        if not data.get('phone'):
            return error_response('Phone is required', 400)
        if not data.get('street'):
            return error_response('Street address is required', 400)

        try:
            address = partner.with_user(SUPERUSER_ID).create_shipping_address(data)
            return success_response({
                'address': address.get_shipping_address_dict(),
            })
        except Exception as e:
            _logger.exception('Error creating address')
            return error_response(str(e), 500)

    # =========================================
    # Update Address
    # =========================================
    @http.route('/api/line-buyer/addresses/<int:address_id>', type='http',
                auth='none', methods=['PUT', 'OPTIONS'], csrf=False)
    @require_auth
    def update_address(self, address_id, **kwargs):
        """Update an existing shipping address."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        partner = request.line_partner
        if not partner:
            return error_response('Profile required', 400, 'PROFILE_REQUIRED')

        try:
            data = json.loads(request.httprequest.data or '{}')
        except json.JSONDecodeError:
            return error_response('Invalid JSON', 400)

        address = partner.with_user(SUPERUSER_ID).update_shipping_address(address_id, data)

        if not address:
            return error_response('Address not found', 404)

        return success_response({
            'address': address.get_shipping_address_dict(),
        })

    # =========================================
    # Delete Address
    # =========================================
    @http.route('/api/line-buyer/addresses/<int:address_id>', type='http',
                auth='none', methods=['DELETE', 'OPTIONS'], csrf=False)
    @require_auth
    def delete_address(self, address_id, **kwargs):
        """Delete a shipping address."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        partner = request.line_partner
        if not partner:
            return error_response('Profile required', 400, 'PROFILE_REQUIRED')

        result = partner.with_user(SUPERUSER_ID).delete_shipping_address(address_id)

        if not result:
            return error_response('Address not found', 404)

        return success_response()

    # =========================================
    # Set Default Address
    # =========================================
    @http.route('/api/line-buyer/addresses/<int:address_id>/set-default',
                type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    @require_auth
    def set_default_address(self, address_id, **kwargs):
        """Set an address as the default shipping address."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        partner = request.line_partner
        if not partner:
            return error_response('Profile required', 400, 'PROFILE_REQUIRED')

        result = partner.with_user(SUPERUSER_ID).set_default_shipping_address(address_id)

        if not result:
            return error_response('Address not found', 404)

        return success_response()

    # =========================================
    # List Thai Provinces
    # =========================================
    @http.route('/api/line-buyer/provinces', type='http', auth='public',
                methods=['GET'], csrf=False, cors='*')
    def list_provinces(self, **kwargs):
        """List all Thai provinces."""
        thailand = request.env.ref('base.th')
        states = request.env['res.country.state'].sudo().search([
            ('country_id', '=', thailand.id),
        ], order='name')

        provinces = []
        for state in states:
            provinces.append({
                'id': state.id,
                'name': state.name,
                'code': state.code or '',
            })

        return success_response({'provinces': provinces})

    # =========================================
    # Calculate Shipping Cost
    # =========================================
    @http.route('/api/line-buyer/shipping-cost', type='http', auth='public',
                methods=['POST'], csrf=False, cors='*')
    def calculate_shipping_cost(self, **kwargs):
        """Calculate shipping cost based on address and order."""
        try:
            data = json.loads(request.httprequest.data or '{}')
        except json.JSONDecodeError:
            return error_response('Invalid JSON', 400)

        ICP = request.env['ir.config_parameter'].sudo()

        threshold = float(ICP.get_param('core_line_integration.free_shipping_threshold', '1000'))
        order_total = float(data.get('order_total', 0))

        if order_total >= threshold:
            return success_response({
                'shipping_cost': 0,
                'free_shipping': True,
                'free_shipping_remaining': 0,
            })

        zip_code = data.get('zip', '')
        zone = self._get_zone_from_zip(zip_code)
        rate = float(ICP.get_param(f'core_line_integration.shipping_rate_zone{zone}', '70'))

        return success_response({
            'shipping_cost': rate,
            'free_shipping': False,
            'free_shipping_remaining': threshold - order_total,
        })

    def _get_zone_from_zip(self, zip_code):
        """Determine shipping zone from zip code"""
        if not zip_code:
            return 2

        try:
            prefix = int(zip_code[:2])
        except (ValueError, IndexError):
            return 2

        ICP = request.env['ir.config_parameter'].sudo()

        zones = {
            1: ICP.get_param('core_line_integration.zone_bangkok', '10,11,12,13'),
            2: ICP.get_param('core_line_integration.zone_central', ''),
            3: ICP.get_param('core_line_integration.zone_north', ''),
            4: ICP.get_param('core_line_integration.zone_northeast', ''),
            5: ICP.get_param('core_line_integration.zone_south', ''),
        }

        for zone, prefixes in zones.items():
            if prefixes:
                prefix_list = [int(p.strip()) for p in prefixes.split(',') if p.strip()]
                if prefix in prefix_list:
                    return zone

        return 2
