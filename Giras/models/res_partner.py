# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import logging

class ResPartner(models.Model):
    _inherit = "res.partner"

    user_id = fields.Many2one('res.users', compute="_compute_user_id",string='Salesperson',
      help='The internal user in charge of this contact.')

    @api.depends('x_studio_vendedor')
    def _compute_user_id(self):
        for record in self:
            record.user_id = record.x_studio_vendedor
