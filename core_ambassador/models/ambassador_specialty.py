# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AmbassadorSpecialty(models.Model):
    _name = 'ambassador.specialty'
    _description = 'Ambassador Specialty'
    _order = 'sequence, name'

    name = fields.Char(string='Specialty Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    icon = fields.Char(string='Icon CSS Class', help='FontAwesome class, e.g. fa-bolt')
    ambassador_count = fields.Integer(
        string='Ambassador Count',
        compute='_compute_ambassador_count',
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Specialty code must be unique.'),
    ]

    def _compute_ambassador_count(self):
        for rec in self:
            rec.ambassador_count = self.env['res.partner'].search_count([
                ('is_ambassador', '=', True),
                ('ambassador_state', '=', 'approved'),
                ('ambassador_specialty_ids', 'in', [rec.id]),
            ])
