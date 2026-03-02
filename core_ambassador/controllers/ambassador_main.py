# -*- coding: utf-8 -*-
"""
Ambassador API base utilities - decorator and formatters
"""
import logging
from functools import wraps

from odoo.http import request

from odoo.addons.core_line_integration.controllers.main import (
    require_auth, success_response, error_response, get_product_image_url
)

_logger = logging.getLogger(__name__)


def require_ambassador(func):
    """
    Decorator that wraps require_auth and verifies
    the authenticated LINE user is an approved ambassador.

    Sets on request:
    - ambassador_partner: the ambassador's partner record
    """
    @wraps(func)
    @require_auth
    def wrapper(*args, **kwargs):
        partner = request.line_partner

        if partner and partner.is_ambassador and partner.ambassador_state == 'approved':
            request.ambassador_partner = partner
            return func(*args, **kwargs)

        if not partner or not partner.is_ambassador:
            return error_response('Not an ambassador', 403, 'NOT_AMBASSADOR')

        return error_response(
            f'Ambassador account is {partner.ambassador_state}',
            403, 'AMBASSADOR_NOT_APPROVED'
        )
    return wrapper


def format_ambassador(partner):
    """Format ambassador for API response"""
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    return {
        'id': partner.id,
        'name': partner.name,
        'tier': partner.ambassador_tier,
        'commission_rate': partner.ambassador_commission_rate,
        'bio': partner.ambassador_bio or '',
        'specialties': [{
            'id': s.id,
            'name': s.name,
            'code': s.code,
            'icon': s.icon or '',
        } for s in partner.ambassador_specialty_ids],
        'social': {
            'youtube': partner.ambassador_social_youtube or '',
            'facebook': partner.ambassador_social_facebook or '',
            'tiktok': partner.ambassador_social_tiktok or '',
            'instagram': partner.ambassador_social_instagram or '',
        },
        'endorsement_count': partner.endorsement_count,
        'image_url': f"{base_url}/web/image/res.partner/{partner.id}/image_256"
            if partner.image_256 else '',
        'approved_date': partner.ambassador_approved_date.isoformat()
            if partner.ambassador_approved_date else None,
    }


def format_endorsement(endorsement):
    """Format endorsement for API response"""
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    product = endorsement.product_id
    return {
        'id': endorsement.id,
        'ambassador': {
            'id': endorsement.ambassador_id.id,
            'name': endorsement.ambassador_id.name,
            'tier': endorsement.ambassador_id.ambassador_tier,
            'image_url': f"{base_url}/web/image/res.partner/{endorsement.ambassador_id.id}/image_256"
                if endorsement.ambassador_id.image_256 else '',
        },
        'product': {
            'id': product.id,
            'name': product.name,
            'price': product.list_price,
            'image_url': get_product_image_url(product),
            'seller': {
                'id': endorsement.seller_id.id,
                'name': endorsement.seller_id.name,
            } if endorsement.seller_id else None,
        },
        'state': endorsement.state,
        'endorsement_text': endorsement.endorsement_text or '',
        'video_url': endorsement.endorsement_video_url or '',
        'rating': endorsement.rating,
        'endorsed_date': endorsement.endorsed_date.isoformat()
            if endorsement.endorsed_date else None,
        'expiry_date': endorsement.expiry_date.isoformat()
            if endorsement.expiry_date else None,
    }


def format_endorsement_request(req):
    """Format endorsement request for API response"""
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    product = req.product_id
    return {
        'id': req.id,
        'name': req.name,
        'seller': {
            'id': req.seller_id.id,
            'name': req.seller_id.name,
        },
        'ambassador': {
            'id': req.ambassador_id.id,
            'name': req.ambassador_id.name,
            'tier': req.ambassador_id.ambassador_tier,
        },
        'product': {
            'id': product.id,
            'name': product.name,
            'price': product.list_price,
            'image_url': get_product_image_url(product),
        },
        'message': req.message or '',
        'response_message': req.response_message or '',
        'state': req.state,
        'requested_date': req.requested_date.isoformat()
            if req.requested_date else None,
        'responded_date': req.responded_date.isoformat()
            if req.responded_date else None,
        'endorsement_id': req.endorsement_id.id if req.endorsement_id else None,
    }
