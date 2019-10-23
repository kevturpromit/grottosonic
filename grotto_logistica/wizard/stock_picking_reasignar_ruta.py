# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _name = "stock.picking.repartidor"
    _description = "Asignar Repartidor a Albaran"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    count = fields.Integer(default=_count, string='Order Count')
    repartidor_id = fields.Many2one("x_reparto", string="Repartidor", help="Asignar nuevo repartido o ruta")

    @api.multi
    def update_repartidor(self):
        picking_orders = self.env['stock.picking'].browse(self._context.get('active_ids', []))
        for picking in picking_orders:
            data = {'x_studio_field_ogKKX': self.repartidor_id.id,
                    }
            picking.write(data)
        return {'type': 'ir.actions.act_window_close'}

