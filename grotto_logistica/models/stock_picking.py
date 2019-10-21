# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking' 

    """
    @api.multi
    def create_invoice(self):
        super(StockPicking,self).create_invoice()
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        for picking_id in picking_ids.filtered(lambda l:l.state == 'done'):
            for invoice_id in picking_id.invoice_ids:
                invoice_id.action_invoice_open()
                """