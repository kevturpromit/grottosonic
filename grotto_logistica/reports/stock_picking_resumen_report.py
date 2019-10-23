# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class StockPickingResumenReport(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.grotto_logistica.stock_picking_despacho'

    @api.model
    def get_report_values(self, docids, data=None):

        docs = []
        
        picking_ids = self.env['stock.picking'].search([('id','in',self._context('active_ids'))], order='name asc')
        for picking in pikcing_ids:            
            docs.append({
                'name': pikcing.name,
                'date': picking.date,
                'partner_id': picking.partner_id.name,
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
        }