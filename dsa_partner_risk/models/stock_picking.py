# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"
    
    state = fields.Selection(selection_add=[('wait_risk', 'Waiting Credit Approval')])
    
    def _search_picking_for_assignation(self):
        self.ensure_one()
        super(StockMove,self)._search_picking_for_assignation()
        picking = self.env['stock.picking'].search([
                ('group_id', '=', self.group_id.id),
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_dest_id.id),
                ('picking_type_id', '=', self.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned','wait_risk'])], limit=1)
        return picking    
         
    def write(self, vals):        
        new_state = self.env.context.get('new_state',False)
        if new_state and vals.get('state', ''):
            vals.update({'state':new_state})
            datos = {'state':new_state}
            if vals.get('picking_id'):
                datos.update({'picking_id':vals['picking_id']})
            return super(StockMove,self).write(datos)                 
        return super(StockMove,self).write(vals)
    
    def _action_wait_risk(self):
        if any(move.state == 'done' for move in self):
            raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))
        self.write({'state': 'assigned'})
        return True    
             
class Picking(models.Model):
    _inherit = "stock.picking"
    
    state = fields.Selection(selection_add=[('wait_risk', 'Waiting Credit Approval')])

    @api.depends('move_type', 'move_lines.state', 'move_lines.picking_id')
    @api.one                            
    def _compute_state(self):
        super(Picking,self)._compute_state()
        for picking in self:  
            _logger.info('Numero: %s'%(picking.name))
            for move in picking.move_lines:
                _logger.info('Line: ID(%s) %s-%s'%(move.id,move.state,move.name))                 
            if any(move.state == 'wait_risk' for move in picking.move_lines):  # TDE FIXME: should be all ?
                picking.state = 'wait_risk'
                    
    @api.one
    def _wait_risk_picking(self):
        if self.env.context.get('new_state',False):
            for move in self.move_line_ids:
                move.write({'state': 'wait_risk'})            
    
    """
    @api.multi
    def write(self, vals):
        res = super(Picking,self).write(vals)
        new_state = self.env.context.get('new_state',False)       
        if new_state:
            _logger.info('El Write new state: %s'%(new_state))        
            self._wait_risk_picking()
        return res
        """    
    
    @api.multi
    def action_wait_risk(self):
        for picking in self:
            if picking.state in ['cancel','done']:
                continue
            picking.mapped('move_lines')._action_wait_risk()
            picking.write({'is_locked': True})
        return True    