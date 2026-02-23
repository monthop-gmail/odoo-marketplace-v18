# -*- coding: utf-8 -*-
"""
LINE Rich Menu Model - Template system for LINE Rich Menus
"""
import json
import logging
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class LineRichMenu(models.Model):
    _name = 'line.rich.menu'
    _description = 'LINE Rich Menu Template'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)

    channel_id = fields.Many2one(
        'line.channel',
        string='LINE Channel',
        required=True,
        ondelete='cascade',
    )

    # Rich Menu ID from LINE (after creation)
    rich_menu_id = fields.Char(
        string='LINE Rich Menu ID',
        readonly=True,
        copy=False,
        help='Rich Menu ID assigned by LINE after creation',
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('uploaded', 'Uploaded to LINE'),
        ('active', 'Active (Default)'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', required=True)

    # Menu Type - role-based rich menus for dynamic single LINE OA
    menu_type = fields.Selection([
        ('general', 'General'),
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ], string='Menu Type', default='general',
       help='Type of rich menu. Determines which role gets this menu assigned.')

    # Rich Menu Settings
    size = fields.Selection([
        ('full', 'Full (2500x1686)'),
        ('half', 'Half (2500x843)'),
    ], string='Size', default='full', required=True)

    width = fields.Integer(
        string='Width',
        compute='_compute_dimensions',
        store=True,
    )
    height = fields.Integer(
        string='Height',
        compute='_compute_dimensions',
        store=True,
    )

    chat_bar_text = fields.Char(
        string='Chat Bar Text',
        default='Menu',
        required=True,
        help='Text shown on the menu bar',
    )

    selected = fields.Boolean(
        string='Menu Open by Default',
        default=True,
        help='Whether the rich menu is displayed by default',
    )

    # Rich Menu Image
    image = fields.Binary(
        string='Menu Image',
        attachment=True,
        help='Rich menu image (JPEG or PNG, max 1MB)',
    )
    image_filename = fields.Char(string='Image Filename')

    # Menu Areas (JSON config)
    area_ids = fields.One2many(
        'line.rich.menu.area',
        'rich_menu_id',
        string='Menu Areas',
    )

    # Target Users
    target_type = fields.Selection([
        ('all', 'All Users'),
        ('specific', 'Specific Users'),
    ], string='Target', default='all')

    target_member_ids = fields.Many2many(
        'line.channel.member',
        string='Target Members',
        help='Specific members to apply this rich menu to',
    )

    # Timing
    is_scheduled = fields.Boolean(string='Schedule Activation')
    schedule_start = fields.Datetime(string='Start Date')
    schedule_end = fields.Datetime(string='End Date')

    @api.depends('size')
    def _compute_dimensions(self):
        for record in self:
            if record.size == 'full':
                record.width = 2500
                record.height = 1686
            else:
                record.width = 2500
                record.height = 843

    def _build_rich_menu_object(self):
        """Build rich menu object for LINE API"""
        self.ensure_one()

        areas = []
        for area in self.area_ids:
            area_obj = {
                'bounds': {
                    'x': area.x,
                    'y': area.y,
                    'width': area.area_width,
                    'height': area.area_height,
                },
                'action': area._build_action(),
            }
            areas.append(area_obj)

        return {
            'size': {
                'width': self.width,
                'height': self.height,
            },
            'selected': self.selected,
            'name': self.name,
            'chatBarText': self.chat_bar_text,
            'areas': areas,
        }

    def action_create_on_line(self):
        """Create rich menu on LINE"""
        self.ensure_one()

        if not self.image:
            raise UserError('Please upload a menu image first.')

        if not self.area_ids:
            raise UserError('Please define at least one menu area.')

        if self.rich_menu_id:
            raise UserError('Rich menu already exists on LINE. Delete it first.')

        try:
            from ..services.line_api import LineApiService

            service = LineApiService(
                self.channel_id.channel_access_token,
                self.channel_id.channel_secret
            )

            # Create rich menu
            rich_menu_obj = self._build_rich_menu_object()
            result = service.create_rich_menu(rich_menu_obj)

            if 'richMenuId' in result:
                self.rich_menu_id = result['richMenuId']

                # Upload image
                image_data = base64.b64decode(self.image)
                service.upload_rich_menu_image(self.rich_menu_id, image_data)

                self.state = 'uploaded'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': f'Rich menu created: {self.rich_menu_id}',
                        'type': 'success',
                    }
                }
            else:
                raise UserError(f'Failed to create rich menu: {result}')

        except ImportError:
            raise UserError('LINE API service not available.')
        except Exception as e:
            _logger.error(f'Error creating rich menu: {e}')
            raise UserError(f'Error: {str(e)}')

    def action_set_default(self):
        """Set as default rich menu for all users"""
        self.ensure_one()

        if not self.rich_menu_id:
            raise UserError('Please create the rich menu on LINE first.')

        try:
            from ..services.line_api import LineApiService

            service = LineApiService(
                self.channel_id.channel_access_token,
                self.channel_id.channel_secret
            )

            service.set_default_rich_menu(self.rich_menu_id)

            # Update states
            self.search([
                ('channel_id', '=', self.channel_id.id),
                ('state', '=', 'active'),
            ]).write({'state': 'uploaded'})

            self.state = 'active'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Rich menu set as default',
                    'type': 'success',
                }
            }

        except Exception as e:
            _logger.error(f'Error setting default rich menu: {e}')
            raise UserError(f'Error: {str(e)}')

    def action_delete_on_line(self):
        """Delete rich menu from LINE"""
        self.ensure_one()

        if not self.rich_menu_id:
            return

        try:
            from ..services.line_api import LineApiService

            service = LineApiService(
                self.channel_id.channel_access_token,
                self.channel_id.channel_secret
            )

            service.delete_rich_menu(self.rich_menu_id)
            self.rich_menu_id = False
            self.state = 'draft'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Rich menu deleted from LINE',
                    'type': 'success',
                }
            }

        except Exception as e:
            _logger.error(f'Error deleting rich menu: {e}')
            raise UserError(f'Error: {str(e)}')

    def action_link_to_user(self, line_user_id):
        """Link rich menu to specific user"""
        self.ensure_one()

        if not self.rich_menu_id:
            raise UserError('Please create the rich menu on LINE first.')

        try:
            from ..services.line_api import LineApiService

            service = LineApiService(
                self.channel_id.channel_access_token,
                self.channel_id.channel_secret
            )

            service.set_user_rich_menu(line_user_id, self.rich_menu_id)
            return True

        except Exception as e:
            _logger.error(f'Error linking rich menu: {e}')
            return False

    def action_preview(self):
        """Show preview of rich menu layout"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rich Menu Preview',
            'res_model': 'line.rich.menu',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('core_line_integration.line_rich_menu_preview_form').id,
            'target': 'new',
        }


class LineRichMenuArea(models.Model):
    _name = 'line.rich.menu.area'
    _description = 'LINE Rich Menu Area'
    _order = 'sequence, id'

    rich_menu_id = fields.Many2one(
        'line.rich.menu',
        string='Rich Menu',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Area Name', required=True)

    # Bounds
    x = fields.Integer(string='X Position', default=0, required=True)
    y = fields.Integer(string='Y Position', default=0, required=True)
    area_width = fields.Integer(string='Width', default=833, required=True)
    area_height = fields.Integer(string='Height', default=843, required=True)

    # Action Type
    action_type = fields.Selection([
        ('uri', 'Open URL'),
        ('message', 'Send Message'),
        ('postback', 'Postback'),
        ('richmenuswitch', 'Switch Rich Menu'),
        ('liff', 'Open LIFF'),
    ], string='Action Type', default='uri', required=True)

    # Action Data
    action_uri = fields.Char(string='URL', help='URL to open (for uri action)')
    action_text = fields.Char(string='Message Text', help='Text to send (for message action)')
    action_data = fields.Char(string='Postback Data', help='Data to send (for postback action)')
    action_display_text = fields.Char(string='Display Text', help='Text shown to user (for postback)')

    # LIFF Reference
    liff_id = fields.Many2one(
        'line.liff',
        string='LIFF App',
        help='LIFF app to open',
    )

    # For rich menu switch
    target_rich_menu_id = fields.Many2one(
        'line.rich.menu',
        string='Target Rich Menu',
        help='Rich menu to switch to',
    )
    target_rich_menu_alias = fields.Char(
        string='Target Rich Menu Alias',
        help='Rich menu alias ID to switch to',
    )

    def _build_action(self):
        """Build action object for LINE API"""
        self.ensure_one()

        if self.action_type == 'uri':
            return {
                'type': 'uri',
                'uri': self.action_uri or '',
            }
        elif self.action_type == 'message':
            return {
                'type': 'message',
                'text': self.action_text or '',
            }
        elif self.action_type == 'postback':
            action = {
                'type': 'postback',
                'data': self.action_data or '',
            }
            if self.action_display_text:
                action['displayText'] = self.action_display_text
            return action
        elif self.action_type == 'liff':
            liff_url = f"https://liff.line.me/{self.liff_id.liff_id}" if self.liff_id else ''
            return {
                'type': 'uri',
                'uri': liff_url,
            }
        elif self.action_type == 'richmenuswitch':
            return {
                'type': 'richmenuswitch',
                'richMenuAliasId': self.target_rich_menu_alias or '',
                'data': self.action_data or 'switch',
            }
        return {'type': 'message', 'text': self.name}
