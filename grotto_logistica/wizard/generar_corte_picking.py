# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _name = "stock.picking.corte"
    _description = "Asignar Repartidor a Albaran"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    name = fields.Char('Corte',)

    @api.multi
    def generar_corte(self):
        picking_orders = self.env['stock.picking'].browse(self._context.get('active_ids', []))
        data = {'name':self.name,
                'picking_ids': [(6, 0, picking_orders.ids)] }
        self.env['grotto.cortes'].create(data)
        return {'type': 'ir.actions.act_window_close'}

