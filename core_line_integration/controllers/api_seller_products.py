# -*- coding: utf-8 -*-
"""
Seller Product CRUD API endpoints
"""
import json
import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request

from .main import success_response, error_response, get_product_image_url
from .seller_main import require_seller, format_seller_product

_logger = logging.getLogger(__name__)


class SellerProductsController(http.Controller):
    """Seller Product Management API"""

    @http.route('/api/line-seller/products', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_products(self, **kwargs):
        """
        List seller's products with filtering and pagination.

        Query params:
        - page, limit: Pagination
        - status: draft | pending | approved | rejected | all
        - search: Search by name
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            seller_id = request.seller_partner.id
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 100)
            offset = (page - 1) * limit
            status = kwargs.get('status', 'all')
            search = kwargs.get('search', '').strip()

            domain = [('marketplace_seller_id', '=', seller_id)]

            if status and status != 'all':
                domain.append(('status', '=', status))

            if search:
                domain.append(('name', 'ilike', search))

            Product = request.env['product.template'].sudo()
            total = Product.search_count(domain)
            products = Product.search(domain, limit=limit, offset=offset, order='create_date desc')

            return success_response({
                'items': [format_seller_product(p) for p in products],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit if limit > 0 else 0,
                },
            })

        except Exception as e:
            _logger.error(f'Error in get_products: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products/<int:product_id>', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_product_detail(self, product_id, **kwargs):
        """Get product detail for seller"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            if product.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            data = format_seller_product(product)
            # Add extra detail fields
            data['description'] = product.description_sale or ''
            data['description_short'] = product.description or ''
            data['weight'] = product.weight if hasattr(product, 'weight') else 0
            data['type'] = product.type
            data['is_published'] = product.is_published if hasattr(product, 'is_published') else False

            # Extra images gallery
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            data['images'] = []
            if hasattr(product, 'product_template_image_ids'):
                for img in product.product_template_image_ids:
                    data['images'].append({
                        'id': img.id,
                        'name': img.name or '',
                        'url': f"{base_url}/web/image/product.image/{img.id}/image_1920",
                        'thumbnail': f"{base_url}/web/image/product.image/{img.id}/image_256",
                        'sequence': img.sequence,
                        'video_url': img.video_url or '',
                    })
            data['images'].sort(key=lambda x: x['sequence'])

            return success_response(data)

        except Exception as e:
            _logger.error(f'Error in get_product_detail: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def create_product(self, **kwargs):
        """
        Create a new product for the seller.

        JSON body:
        - name (required)
        - list_price (required)
        - categ_id: Category ID
        - description_sale: Product description
        - type: product type (consu, service)
        - mp_qty: Initial quantity
        - image_1920: Base64 encoded image
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            body = json.loads(request.httprequest.data or '{}')

            name = body.get('name', '').strip()
            if not name:
                return error_response('Product name is required', 400, 'VALIDATION_ERROR')

            list_price = body.get('list_price', 0)
            if not list_price or float(list_price) <= 0:
                return error_response('Price must be greater than 0', 400, 'VALIDATION_ERROR')

            seller = request.seller_partner

            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            vals = {
                'name': name,
                'list_price': float(list_price),
                'marketplace_seller_id': seller.id,
                'type': body.get('type', 'consu'),
                'sale_ok': False,
                'purchase_ok': False,
                'status': 'draft',
            }

            if body.get('categ_id'):
                vals['categ_id'] = int(body['categ_id'])
            elif body.get('categ_name'):
                # Create new category if name provided
                categ_name = body['categ_name'].strip()
                Categ = request.env['product.category'].with_user(SUPERUSER_ID)
                existing = Categ.search([('name', '=ilike', categ_name)], limit=1)
                if existing:
                    vals['categ_id'] = existing.id
                else:
                    new_categ = Categ.create({'name': categ_name})
                    vals['categ_id'] = new_categ.id

            if body.get('description_sale'):
                vals['description_sale'] = body['description_sale']

            if body.get('description'):
                vals['description'] = body['description']

            if body.get('mp_qty'):
                vals['mp_qty'] = float(body['mp_qty'])

            if body.get('image_1920'):
                vals['image_1920'] = body['image_1920']

            product = request.env['product.template'].sudo().with_context(**ctx).create(vals)

            return success_response(
                format_seller_product(product),
                message='Product created successfully'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error creating product: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products/<int:product_id>', type='http', auth='none',
                methods=['PUT', 'OPTIONS'], csrf=False)
    @require_seller
    def update_product(self, product_id, **kwargs):
        """
        Update an existing product. Only allowed for draft/rejected products.

        JSON body: same fields as create (all optional)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            if product.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if product.status not in ('draft', 'rejected'):
                return error_response(
                    'Can only edit products in draft or rejected status',
                    400, 'INVALID_STATE'
                )

            body = json.loads(request.httprequest.data or '{}')

            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            # Only allow safe fields to be updated
            allowed_fields = {
                'name': str,
                'list_price': float,
                'description_sale': str,
                'description': str,
                'mp_qty': float,
            }

            vals = {}
            for field, cast in allowed_fields.items():
                if field in body and body[field] is not None:
                    vals[field] = cast(body[field])

            if 'categ_id' in body and body['categ_id']:
                vals['categ_id'] = int(body['categ_id'])
            elif body.get('categ_name'):
                categ_name = body['categ_name'].strip()
                Categ = request.env['product.category'].with_user(SUPERUSER_ID)
                existing = Categ.search([('name', '=ilike', categ_name)], limit=1)
                if existing:
                    vals['categ_id'] = existing.id
                else:
                    new_categ = Categ.create({'name': categ_name})
                    vals['categ_id'] = new_categ.id

            if 'image_1920' in body and body['image_1920']:
                vals['image_1920'] = body['image_1920']

            if vals:
                product.with_context(**ctx).write(vals)

            return success_response(
                format_seller_product(product),
                message='Product updated successfully'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error updating product: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products/<int:product_id>/submit', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def submit_product(self, product_id, **kwargs):
        """Submit product for approval: draft/rejected → pending"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            if product.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if product.status not in ('draft', 'rejected'):
                return error_response(
                    f'Cannot submit product in state: {product.status}',
                    400, 'INVALID_STATE'
                )

            # set_pending handles auto_approve logic too
            product.set_pending()

            return success_response(
                format_seller_product(product),
                message='Product submitted for approval'
            )

        except Exception as e:
            _logger.error(f'Error submitting product: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products/<int:product_id>', type='http', auth='none',
                methods=['DELETE', 'OPTIONS'], csrf=False)
    @require_seller
    def delete_product(self, product_id, **kwargs):
        """
        Delete a product. Only allowed for draft or rejected products.
        Approved/pending products cannot be deleted.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            if product.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if product.status not in ('draft', 'rejected'):
                return error_response(
                    'Can only delete products in draft or rejected status',
                    400, 'INVALID_STATE'
                )

            # Delete extra images first
            if hasattr(product, 'product_template_image_ids') and product.product_template_image_ids:
                product.product_template_image_ids.unlink()

            product_name = product.name
            product.unlink()

            return success_response(
                {'deleted': True, 'name': product_name},
                message='Product deleted successfully'
            )

        except Exception as e:
            _logger.error(f'Error deleting product: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products/<int:product_id>/toggle-publish', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def toggle_publish_product(self, product_id, **kwargs):
        """
        Toggle product published status. Only allowed for approved products.
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            if product.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if product.status != 'approved':
                return error_response(
                    'Can only toggle publish for approved products',
                    400, 'INVALID_STATE'
                )

            product.website_published = not product.website_published
            is_published = product.website_published

            return success_response(
                {'id': product.id, 'is_published': is_published},
                message=f'Product {"published" if is_published else "unpublished"} successfully'
            )

        except Exception as e:
            _logger.error(f'Error toggling product publish: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Restock ====================

    @http.route('/api/line-seller/products/<int:product_id>/restock', type='http', auth='none',
                methods=['POST', 'OPTIONS'], csrf=False)
    @require_seller
    def restock_product(self, product_id, **kwargs):
        """
        Restock a product: add inventory quantity via marketplace.stock.

        JSON body:
        - quantity: Amount to add (required, > 0)
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')

            if product.marketplace_seller_id.id != request.seller_partner.id:
                return error_response('Unauthorized', 403, 'UNAUTHORIZED')

            if product.status != 'approved':
                return error_response(
                    'Can only restock approved products',
                    400, 'INVALID_STATE'
                )

            if product.type == 'service':
                return error_response(
                    'Service products do not have stock',
                    400, 'SERVICE_PRODUCT'
                )

            body = json.loads(request.httprequest.data or '{}')
            quantity = float(body.get('quantity', 0))

            if quantity <= 0:
                return error_response('Quantity must be greater than 0', 400, 'VALIDATION_ERROR')

            # Get seller's stock location
            seller = request.seller_partner
            location_id = seller.get_seller_global_fields('location_id') if hasattr(seller, 'get_seller_global_fields') else False

            if not location_id:
                return error_response('Seller has no warehouse location configured', 400, 'NO_LOCATION')

            # Get product variant
            variant = product.product_variant_id
            if not variant:
                return error_response('No product variant available', 400, 'NO_VARIANT')

            # Create marketplace.stock record
            MpStock = request.env['marketplace.stock'].with_user(SUPERUSER_ID)
            stock_record = MpStock.create({
                'product_id': variant.id,
                'product_temp_id': product.id,
                'new_quantity': quantity,
                'location_id': location_id,
                'note': f'Restocked via LIFF ({int(quantity)} units)',
                'state': 'requested',
            })

            # Auto-approve the stock request
            stock_record.auto_approve()

            # Reload product to get updated qty
            product.invalidate_recordset(['qty_available'])

            return success_response(
                format_seller_product(product),
                message=f'เติมสต๊อก {int(quantity)} ชิ้นสำเร็จ'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error restocking product: {str(e)}')
            return error_response(str(e), 500)

    # ==================== Product Images Gallery ====================

    def _get_seller_product(self, product_id):
        """Helper: get product and verify seller ownership."""
        product = request.env['product.template'].sudo().browse(product_id)
        if not product.exists():
            return None, error_response('Product not found', 404, 'PRODUCT_NOT_FOUND')
        if product.marketplace_seller_id.id != request.seller_partner.id:
            return None, error_response('Unauthorized', 403, 'UNAUTHORIZED')
        return product, None

    def _format_product_image(self, img, base_url):
        """Format a product.image record for API response."""
        return {
            'id': img.id,
            'name': img.name or '',
            'url': f"{base_url}/web/image/product.image/{img.id}/image_1920",
            'thumbnail': f"{base_url}/web/image/product.image/{img.id}/image_256",
            'sequence': img.sequence,
            'video_url': img.video_url or '',
        }

    @http.route('/api/line-seller/products/<int:product_id>/images', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_product_images(self, product_id, **kwargs):
        """Get all extra images for a product."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product, err = self._get_seller_product(product_id)
            if err:
                return err

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            images = []
            if hasattr(product, 'product_template_image_ids'):
                for img in product.product_template_image_ids.sorted('sequence'):
                    images.append(self._format_product_image(img, base_url))

            return success_response({'images': images})

        except Exception as e:
            _logger.error(f'Error in get_product_images: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products/<int:product_id>/images', type='http', auth='none',
                methods=['POST'], csrf=False)
    @require_seller
    def upload_product_images(self, product_id, **kwargs):
        """
        Upload extra images for a product.

        JSON body:
        - images: array of {image_base64, name?, video_url?}
        """
        try:
            product, err = self._get_seller_product(product_id)
            if err:
                return err

            body = json.loads(request.httprequest.data or '{}')
            images_data = body.get('images', [])
            if not images_data:
                return error_response('No images provided', 400, 'VALIDATION_ERROR')

            if len(images_data) > 10:
                return error_response('Maximum 10 images per request', 400, 'VALIDATION_ERROR')

            # Get current max sequence
            existing = product.product_template_image_ids
            max_seq = max(existing.mapped('sequence') or [0])

            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            ProductImage = request.env['product.image'].sudo()
            created = []

            for i, img_data in enumerate(images_data):
                image_base64 = img_data.get('image_base64', '')
                if not image_base64 and not img_data.get('video_url'):
                    continue

                vals = {
                    'product_tmpl_id': product.id,
                    'name': img_data.get('name', '') or f"{product.name} - {len(existing) + i + 1}",
                    'sequence': max_seq + i + 1,
                }
                if image_base64:
                    vals['image_1920'] = image_base64
                if img_data.get('video_url'):
                    vals['video_url'] = img_data['video_url']

                img_record = ProductImage.create(vals)
                created.append(self._format_product_image(img_record, base_url))

            return success_response(
                {'images': created},
                message=f'{len(created)} image(s) uploaded successfully'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error uploading product images: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products/<int:product_id>/images/<int:image_id>', type='http', auth='none',
                methods=['DELETE', 'OPTIONS'], csrf=False)
    @require_seller
    def delete_product_image(self, product_id, image_id, **kwargs):
        """Delete a specific extra image from a product."""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product, err = self._get_seller_product(product_id)
            if err:
                return err

            img = request.env['product.image'].sudo().browse(image_id)
            if not img.exists() or img.product_tmpl_id.id != product.id:
                return error_response('Image not found', 404, 'IMAGE_NOT_FOUND')

            img.unlink()
            return success_response(message='Image deleted successfully')

        except Exception as e:
            _logger.error(f'Error deleting product image: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/products/<int:product_id>/images/reorder', type='http', auth='none',
                methods=['PUT', 'OPTIONS'], csrf=False)
    @require_seller
    def reorder_product_images(self, product_id, **kwargs):
        """
        Reorder extra images.

        JSON body:
        - image_ids: array of image IDs in desired order [3, 1, 2]
        """
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            product, err = self._get_seller_product(product_id)
            if err:
                return err

            body = json.loads(request.httprequest.data or '{}')
            image_ids = body.get('image_ids', [])
            if not image_ids:
                return error_response('image_ids is required', 400, 'VALIDATION_ERROR')

            # Verify all images belong to this product
            ProductImage = request.env['product.image'].sudo()
            product_image_ids = set(product.product_template_image_ids.ids)

            for seq, img_id in enumerate(image_ids):
                if img_id not in product_image_ids:
                    return error_response(
                        f'Image {img_id} does not belong to this product',
                        400, 'VALIDATION_ERROR'
                    )
                ProductImage.browse(img_id).write({'sequence': seq + 1})

            # Return updated images
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            images = []
            for img in product.product_template_image_ids.sorted('sequence'):
                images.append(self._format_product_image(img, base_url))

            return success_response(
                {'images': images},
                message='Images reordered successfully'
            )

        except json.JSONDecodeError:
            return error_response('Invalid JSON body', 400, 'INVALID_JSON')
        except Exception as e:
            _logger.error(f'Error reordering product images: {str(e)}')
            return error_response(str(e), 500)

    @http.route('/api/line-seller/categories', type='http', auth='none',
                methods=['GET', 'OPTIONS'], csrf=False)
    @require_seller
    def get_categories(self, **kwargs):
        """Get all product categories for seller to choose from"""
        if request.httprequest.method == 'OPTIONS':
            return success_response()

        try:
            categories = request.env['product.category'].sudo().search(
                [], order='complete_name'
            )

            result = [{
                'id': cat.id,
                'name': cat.name,
                'full_name': cat.complete_name,
                'parent_id': cat.parent_id.id if cat.parent_id else None,
            } for cat in categories]

            return success_response({'categories': result})

        except Exception as e:
            _logger.error(f'Error in get_categories: {str(e)}')
            return error_response(str(e), 500)
