# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class StockPickingResumenReport(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.grotto_logistica.stock_picking_despacho'
        
    def get_data(self, data, pkids):

        sheet_search = self.env['stock.move'].search(
            [('picking_id', 'in', pkids)])
        
        _logger.info('Pickings :%s'%pkids)
        _logger.info('sheet_search :%s'%sheet_search)


        lst = []
        product = {}
        for sheet in sheet_search:
            if sheet.product_id:
                _logger.info('Producto:%s'%sheet.product_id.name)
                product[sheet.product_id.id] = {'product_id':sheet.product_id.id,
                                                'product_name':sheet.product_id.name,
                                                'cantidad':0.00}
        for sheet in sheet_search:
            if sheet.product_id:
                _logger.info('Cantidad:(%s)-%s'%(sheet.product_uom_qty,sheet.product_id.name))
                product[sheet.product_id.id]['cantidad'] += sheet.product_uom_qty

        for x in product:
            _logger.info('X: %s'%x)
            dic = {
                'product_name': product[x]['product_name'],
                'cantidad': product[x]['cantidad']
                }
            _logger.info('x:%s'%product[x])
            lst.append(dic)
        return [{'total': len(lst),
                 'line': lst}]
        
    """
    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('grotto_logistica.stock_picking_despacho')

        custom_data = self.get_data()

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
            'get_data': custom_data,
        }   
        return report_obj.render('grotto_logistica.stock_picking_despacho', docargs)                
       """ 
    
    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids') or False
        docs = self.env['stock.picking'].browse(docids)
        _logger.info('model:%s'%model)
        _logger.info('active_ids:%s'%active_ids)
        _logger.info('docids:%s'%docids)
        _logger.info('docs:%s'%docs)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'get_data': self.get_data(data, docids),
        }
        return docargs
        