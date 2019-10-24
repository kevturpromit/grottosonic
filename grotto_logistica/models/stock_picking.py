# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking' 
    
    @api.model
    def get_data(self, picking_ids=None):
        
        picking_ids = self._context('active_ids',picking_ids)

        sheet_search = self.env['stock.move'].search(
            [('picking_id', 'in', picking_ids)])
        
        _logger.info('Pickings :%s'%picking_ids)
        _logger.info('sheet_search :%s'%sheet_search)


        lst = []
        product = []
        for sheet in sheet_search:
            _logger.info('Producto:%s'%sheet.product_id.name)
            product[sheet.product_id.id] = {'product_id':sheet.product_id.id,
                                            'product_name':sheet.product_id.name,
                                            'cantidad':0.00}
        for sheet in sheet_search:
            dic = {}
            _logger.info('Cantidad:(%s)-%s'%(sheet.product_uom_qty,sheet.product_id.name))
            product[sheet.product_id.id]['cantidad'] += sheet.product_uom_qty

        for x in product:
            dic = {
                'product_name': x['product_name'],
                'cantidad': x['cantidad']
                }
            _logger.info('x:%s'%x)
            lst.append(dic)
        return [{'total': len(lst),
                 'line': lst}]
        
    
class WizardStockPickingInvoice(models.TransientModel):
    _inherit = 'wizard.stock.picking.invoice'    

    @api.multi
    def create_invoice(self):
        super(WizardStockPickingInvoice,self).create_invoice()
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        for picking_id in picking_ids.filtered(lambda l:l.state == 'done'):
            for invoice_id in picking_id.invoice_ids:
                invoice_id.action_invoice_open()
                