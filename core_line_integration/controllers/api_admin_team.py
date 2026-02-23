# -*- coding: utf-8 -*-
"""
Admin Team Management API
Manager-only endpoints for inviting/revoking admin team members.
"""
import json
import logging
from ast import literal_eval

from odoo import http, fields, SUPERUSER_ID
from odoo.http import request

from .main import success_response, error_response
from .admin_main import (
    require_admin, require_manager,
    format_team_member, OFFICER_GROUP, MANAGER_GROUP,
)

_logger = logging.getLogger(__name__)


class AdminTeamController(http.Controller):

    # ==================== Team List ====================

    @http.route('/api/line-admin/team', type='http', auth='none',
                methods=['GET'], csrf=False)
    @require_manager
    def get_team(self, **kwargs):
        """List admin team members. Filter by state (active/revoked)."""
        try:
            state = kwargs.get('state', 'active')
            page = int(kwargs.get('page', 1))
            limit = min(int(kwargs.get('limit', 20)), 50)
            offset = (page - 1) * limit

            domain = []
            if state and state != 'all':
                domain.append(('state', '=', state))

            TeamMember = request.env['admin.team.member'].sudo()
            total = TeamMember.search_count(domain)
            records = TeamMember.search(domain, offset=offset, limit=limit, order='invite_date desc')

            return success_response({
                'members': [format_team_member(r) for r in records],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': max(1, (total + limit - 1) // limit),
                },
                'counts': {
                    'active': TeamMember.search_count([('state', '=', 'active')]),
                    'revoked': TeamMember.search_count([('state', '=', 'revoked')]),
                },
            })
        except Exception as e:
            _logger.error('Get team error: %s', e)
            return error_response(str(e), 500)

    # ==================== Team Member Detail ====================

    @http.route('/api/line-admin/team/<int:member_id>', type='http', auth='none',
                methods=['GET'], csrf=False)
    @require_manager
    def get_team_member(self, member_id, **kwargs):
        """Get detail of a specific admin team member."""
        try:
            record = request.env['admin.team.member'].sudo().browse(member_id)
            if not record.exists():
                return error_response('Admin team member not found', 404, 'NOT_FOUND')

            return success_response(format_team_member(record))
        except Exception as e:
            _logger.error('Get team member error: %s', e)
            return error_response(str(e), 500)

    # ==================== Candidates Search ====================

    @http.route('/api/line-admin/team/candidates', type='http', auth='none',
                methods=['GET'], csrf=False)
    @require_manager
    def get_candidates(self, **kwargs):
        """Search LINE members that can be invited as admin."""
        try:
            search = kwargs.get('search', '').strip()
            limit = min(int(kwargs.get('limit', 20)), 50)

            if len(search) < 2:
                return success_response({'candidates': []})

            # Find LINE members matching search
            Member = request.env['line.channel.member'].sudo()
            domain = [
                ('is_following', '=', True),
                ('partner_id', '!=', False),
                '|',
                ('display_name', 'ilike', search),
                ('partner_id.name', 'ilike', search),
            ]
            members = Member.search(domain, limit=limit)

            # Exclude partners who already have active admin membership
            active_admin_partner_ids = set(
                request.env['admin.team.member'].sudo().search([
                    ('state', '=', 'active'),
                ]).mapped('partner_id.id')
            )

            # Exclude current user's partner (can't invite self)
            my_partner_id = request.line_partner.id

            # Also check who already has officer/manager group
            officer_group = request.env.ref(OFFICER_GROUP, raise_if_not_found=False)
            manager_group = request.env.ref(MANAGER_GROUP, raise_if_not_found=False)

            candidates = []
            for m in members:
                pid = m.partner_id.id
                if pid == my_partner_id:
                    continue
                if pid in active_admin_partner_ids:
                    continue

                # Check if already manager (can't invite via LIFF)
                user = request.env['res.users'].sudo().search([
                    ('partner_id', '=', pid),
                ], limit=1)
                if user and manager_group and manager_group in user.groups_id:
                    continue

                partner = m.partner_id
                candidates.append({
                    'partner_id': pid,
                    'name': partner.name or '',
                    'phone': partner.phone or partner.mobile or '',
                    'email': partner.email or '',
                    'picture_url': m.picture_url or '',
                    'line_display_name': m.display_name or '',
                    'is_seller': bool(partner.seller and getattr(partner, 'state', '') == 'approved'),
                    'has_profile': bool(partner.name and (partner.phone or partner.mobile)),
                })

            return success_response({'candidates': candidates})
        except Exception as e:
            _logger.error('Get candidates error: %s', e)
            return error_response(str(e), 500)

    # ==================== Invite ====================

    @http.route('/api/line-admin/team/invite', type='http', auth='none',
                methods=['POST'], csrf=False)
    @require_manager
    def invite_admin(self, **kwargs):
        """Invite a LINE member as Officer."""
        try:
            data = json.loads(request.httprequest.data or '{}')
            partner_id = data.get('partner_id')
            notes = data.get('notes', '').strip()

            if not partner_id:
                return error_response('partner_id is required', 400, 'MISSING_FIELD')

            sudo = lambda model: request.env[model].with_user(SUPERUSER_ID)
            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )

            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner.exists():
                return error_response('Partner not found', 404, 'NOT_FOUND')

            my_partner = request.line_partner

            # ── Validations ──

            if partner.id == my_partner.id:
                return error_response('ไม่สามารถเชิญตัวเองได้', 400, 'SELF_INVITE')

            if not partner.name or not (partner.phone or partner.mobile):
                return error_response(
                    'กรุณาให้ผู้ใช้กรอกชื่อและเบอร์โทรก่อน',
                    400, 'INCOMPLETE_PROFILE'
                )

            # Check LINE member is following
            member = request.env['line.channel.member'].sudo().search([
                ('partner_id', '=', partner.id),
                ('is_following', '=', True),
            ], limit=1)
            if not member:
                return error_response(
                    'ผู้ใช้ต้อง follow LINE OA ก่อน',
                    400, 'NOT_FOLLOWING'
                )

            # Check not already active admin
            existing = request.env['admin.team.member'].sudo().search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'active'),
            ], limit=1)
            if existing:
                return error_response('ผู้ใช้นี้เป็นแอดมินอยู่แล้ว', 400, 'ALREADY_ADMIN')

            # Check not already Manager
            user = sudo('res.users').search([
                ('partner_id', '=', partner.id),
            ], limit=1)
            manager_group = request.env.ref(MANAGER_GROUP, raise_if_not_found=False)
            if user and manager_group and manager_group in user.groups_id:
                return error_response('ผู้ใช้นี้เป็น Manager อยู่แล้ว', 400, 'ALREADY_MANAGER')

            # ── Step 1: Ensure res.users exists ──

            if not user:
                if not partner.email:
                    partner.with_user(SUPERUSER_ID).with_context(**ctx).write({
                        'email': f'{member.line_user_id}@line.marketplace.local'
                    })

                IrConfigParam = sudo('ir.config_parameter')
                template_user_id = literal_eval(
                    IrConfigParam.get_param('base.template_portal_user_id', 'False')
                )
                if template_user_id:
                    template_user = sudo('res.users').browse(template_user_id)
                    if template_user.exists():
                        user = template_user.with_context(
                            no_reset_password=True, **ctx
                        ).copy({
                            'name': partner.name,
                            'login': partner.email,
                            'partner_id': partner.id,
                            'active': True,
                        })

                if not user:
                    user = sudo('res.users').with_context(**ctx).create({
                        'name': partner.name,
                        'login': partner.email or f'{member.line_user_id}@line.local',
                        'partner_id': partner.id,
                        'active': True,
                        'groups_id': [(4, request.env.ref('base.group_user').id)],
                    })

            # ── Step 2: Move portal → internal group (if needed) ──

            portal_group = request.env.ref('base.group_portal', raise_if_not_found=False)
            internal_group = request.env.ref('base.group_user', raise_if_not_found=False)
            if portal_group and internal_group:
                portal_group.with_user(SUPERUSER_ID).write({"users": [(3, user.id, 0)]})
                internal_group.with_user(SUPERUSER_ID).write({"users": [(4, user.id, 0)]})

            # ── Step 3: Add to marketplace_officer_group ──

            officer_group_id = sudo('ir.model.data')._xmlid_to_res_id(OFFICER_GROUP)
            if officer_group_id:
                officer_grp = sudo('res.groups').browse(officer_group_id)
                officer_grp.write({"users": [(4, user.id, 0)]})

            # ── Step 4: Update config-wise groups ──

            user.with_user(SUPERUSER_ID).update_groups_for_mp_user(user)

            # ── Step 5: Create admin.team.member record ──

            team_record = sudo('admin.team.member').with_context(**ctx).create({
                'partner_id': partner.id,
                'user_id': user.id,
                'role': 'officer',
                'state': 'active',
                'invited_by': my_partner.id,
                'invite_date': fields.Datetime.now(),
                'invite_notes': notes,
                'line_member_id': member.id,
            })

            # ── Step 6: Sync member type + rich menu + notification ──

            member.sync_member_type_from_partner()
            member.assign_role_rich_menu()
            member.send_role_change_notification(
                member.member_type, 'admin', seller_state='admin_promoted'
            )

            # ── Step 7: Log notification ──

            request.env['line.notify.log'].sudo().with_context(**ctx).create({
                'channel_id': member.channel_id.id,
                'line_user_id': member.line_user_id,
                'partner_id': partner.id,
                'notify_type': 'admin_team',
                'message': f'Admin invite: {partner.name} as officer by {my_partner.name}',
                'state': 'sent',
                'sent_date': fields.Datetime.now(),
            })

            _logger.info(
                'Admin team invite: %s (partner=%d) invited as officer by %s',
                partner.name, partner.id, my_partner.name,
            )

            return success_response({
                'member': format_team_member(team_record),
                'message': f'เชิญ {partner.name} เป็น Officer สำเร็จ',
            })

        except Exception as e:
            _logger.error('Invite admin error: %s', e)
            return error_response(str(e), 500)

    # ==================== Revoke ====================

    @http.route('/api/line-admin/team/<int:member_id>/revoke', type='http', auth='none',
                methods=['POST'], csrf=False)
    @require_manager
    def revoke_admin(self, member_id, **kwargs):
        """Revoke Officer access from an admin team member."""
        try:
            data = json.loads(request.httprequest.data or '{}')
            reason = data.get('reason', '').strip()

            record = request.env['admin.team.member'].sudo().browse(member_id)
            if not record.exists():
                return error_response('Admin team member not found', 404, 'NOT_FOUND')

            if record.state != 'active':
                return error_response('สมาชิกนี้ถูกเพิกถอนแล้ว', 400, 'ALREADY_REVOKED')

            my_partner = request.line_partner
            target_partner = record.partner_id

            # Cannot revoke self
            if target_partner.id == my_partner.id:
                return error_response('ไม่สามารถเพิกถอนตัวเองได้', 400, 'SELF_REVOKE')

            # Cannot revoke Manager
            target_user = record.user_id
            manager_group = request.env.ref(MANAGER_GROUP, raise_if_not_found=False)
            if target_user and manager_group and manager_group in target_user.groups_id:
                return error_response(
                    'ไม่สามารถเพิกถอน Manager ผ่าน LIFF ได้',
                    400, 'CANNOT_REVOKE_MANAGER'
                )

            ctx = dict(
                tracking_disable=True,
                mail_create_nosubscribe=True,
                mail_auto_subscribe_no_notify=True,
            )
            sudo = lambda model: request.env[model].with_user(SUPERUSER_ID)

            # ── Step 1: Remove from marketplace_officer_group ──

            officer_group_id = sudo('ir.model.data')._xmlid_to_res_id(OFFICER_GROUP)
            if officer_group_id and target_user:
                officer_grp = sudo('res.groups').browse(officer_group_id)
                officer_grp.write({"users": [(3, target_user.id, 0)]})

            # ── Step 2: Update record ──

            record.sudo().write({
                'state': 'revoked',
                'revoked_by': my_partner.id,
                'revoke_date': fields.Datetime.now(),
                'revoke_reason': reason,
            })

            # ── Step 3: Sync member type + rich menu + notification ──

            member = record.line_member_id
            if member:
                member.sync_member_type_from_partner()
                member.assign_role_rich_menu()
                member.send_role_change_notification(
                    'admin', member.member_type, seller_state='admin_revoked'
                )

            # ── Step 4: Log notification ──

            if member:
                request.env['line.notify.log'].sudo().with_context(**ctx).create({
                    'channel_id': member.channel_id.id,
                    'line_user_id': member.line_user_id,
                    'partner_id': target_partner.id,
                    'notify_type': 'admin_team',
                    'message': f'Admin revoke: {target_partner.name} by {my_partner.name}',
                    'state': 'sent',
                    'sent_date': fields.Datetime.now(),
                })

            _logger.info(
                'Admin team revoke: %s (partner=%d) revoked by %s. Reason: %s',
                target_partner.name, target_partner.id, my_partner.name, reason or 'N/A',
            )

            return success_response({
                'member': format_team_member(record),
                'message': f'เพิกถอนสิทธิ์ {target_partner.name} สำเร็จ',
            })

        except Exception as e:
            _logger.error('Revoke admin error: %s', e)
            return error_response(str(e), 500)

    # ==================== My Status ====================

    @http.route('/api/line-admin/team/my-status', type='http', auth='none',
                methods=['GET'], csrf=False)
    @require_admin
    def get_my_status(self, **kwargs):
        """Check if the current user is a Manager."""
        try:
            user = request.admin_user
            manager_group = request.env.ref(MANAGER_GROUP, raise_if_not_found=False)
            is_manager = bool(manager_group and manager_group in user.groups_id)

            officer_group = request.env.ref(OFFICER_GROUP, raise_if_not_found=False)
            is_officer = bool(officer_group and officer_group in user.groups_id)

            return success_response({
                'is_manager': is_manager,
                'is_officer': is_officer,
                'role': 'manager' if is_manager else ('officer' if is_officer else 'none'),
                'name': user.partner_id.name,
            })
        except Exception as e:
            _logger.error('Get my status error: %s', e)
            return error_response(str(e), 500)
