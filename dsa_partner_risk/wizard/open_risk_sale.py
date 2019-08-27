# -*- coding: utf-8 -*-
# © 2009 Albert Cervera i Areny <http://www.nan-tic.com)>
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# © 2011 Pexego Sistemas Informáticos.
#        Alberto Luengo Cabanillas <alberto@pexego.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class OpenRiskSale(models.TransientModel):
    """ Open Risk Window and show Partner relative information """

    _name = 'open.risk.sale'
    _description = "Credit Limit Exceeded"

    unpayed_amount = fields.Float(_('Expired Unpaid Payments'), readonly="True")
    pending_amount = fields.Float(_('Unexpired Unpaid Payments'), readonly="True")
    circulating_amount = fields.Float(_('Circulating amount'), readonly="True")
    draft_invoices_amount = fields.Float(_('Draft Invoices'), readonly="True")
    pending_orders_amount = fields.Float(_('Uninvoiced Orders'), readonly="True")
    total_debt = fields.Float(_('Total Debt'), readonly="True")
    credit_limit = fields.Float(_('Credit Limit'), readonly="True")
    available_risk = fields.Float(_('Available Credit'), readonly="True")
    total_risk_percent = fields.Float(_('Credit Usage (%)'), readonly="True")
    pending_docum_debi = fields.Integer(_('Document Debit Pending'), readonly="True")
    pending_docum_cred = fields.Integer(_('Document Credit Pending'), readonly="True")
    pending_docum_draft = fields.Integer(_('Document Draft Pending)'), readonly="True")
    pending_credit_days = fields.Integer(_('Credit Days Pending'), readonly="True")
    partner_id = fields.Many2one('res.partner', _('Customer'), readonly=True)
    max_invoice_credit = fields.Integer(_('Maximum amount of pending invoices'), readonly=True)
    max_dias_credit = fields.Integer(_('Maximum amount of credit days'), readonly=True)
    memo = fields.Text(_('Reason'), readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(OpenRiskSale, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        memo = self.env.context.get('memo')
        if active_id:
            active_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))  
            partner = self.env['res.partner'].browse(active_id.partner_id.id)
            unpayed_amount = partner.unpayed_amount
            pending_amount = partner.pending_amount
            draft_invoices_amount = partner.draft_invoices_amount
            pending_orders_amount = partner.pending_orders_amount
            total_debt = partner.total_debt
            credit_limit = partner.credit_limit
            available_risk = partner.available_risk
            total_risk_percent = partner.total_risk_percent
            circulating_amount = partner.circulating_amount
            pending_docum_debi = partner.pending_docum_debi
            pending_docum_cred = partner.pending_docum_cred
            pending_docum_draft = partner.pending_docum_draft
            pending_credit_days = partner.pending_credit_days
            partner_id = partner.id
            max_invoice_credit = partner.max_invoice_credit
            max_dias_credit = partner.max_dias_credit            
            res.update({
                'unpayed_amount': unpayed_amount,
                'pending_amount': pending_amount,
                'draft_invoices_amount': draft_invoices_amount,
                'pending_orders_amount': pending_orders_amount,
                'total_debt': total_debt,
                'credit_limit': credit_limit,
                'available_risk': available_risk,
                'total_risk_percent': total_risk_percent,
                'circulating_amount': partner.circulating_amount,
                'pending_docum_debi': circulating_amount,
                'pending_docum_cred':pending_docum_cred,
                'pending_docum_draft':pending_docum_draft,
                'pending_credit_days':pending_credit_days,
                'partner_id':partner_id,
                'max_invoice_credit':max_invoice_credit,
                'max_dias_credit':max_dias_credit,
                'memo':memo
            })
        return res
    
    @api.multi
    def draft_to_risk(self):
        active_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))    
        return active_id.write({'state': 'wait_risk'})