# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GrottoCortes(models.Model):
    _name = 'grotto.cortes'
    _description = 'Cortes'
    
    name = fields.Char('Name')
    codigo_de_reparto = fields.Char('Codigo de Reparto')
    diario = fields.Char('Diario')
    factura = fields.Integer('Factura')
    factura_id = fields.Integer('Factura Id')
    picking_ids = fields.Many2many('stock.picking',string='Albaran')
    piking_id = fields.Many2one('stock.picking',string='Albaran')
    repartidor = fields.Integer('Repartidor')
    repartidor_1 = fields.Integer('Repartidor')
    vendedor = fields.Integer('Vendedor')
    
    """
    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100
        """


