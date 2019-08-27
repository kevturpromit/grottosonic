# -*- coding: utf-8 -*-
# © 2009 Albert Cervera i Areny <http://www.nan-tic.com)>
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# © 2011 Pexego Sistemas Informáticos.
#        Alberto Luengo Cabanillas <alberto@pexego.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models, api, _
from datetime import datetime
import time


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cash_credit = fields.Boolean('Allow Over Credit?')
    max_invoice_credit = fields.Integer(string='Maximum amount of pending invoices', default=2)
    max_dias_credit = fields.Integer(string='Maximum amount of credit days', default=15)    
    unpayed_amount = fields.Float(compute='_unpayed_amount',
                                  string='Expired Unpaid Payments')
    pending_amount = fields.Float(compute='_pending_amount',
                                  string='Unexpired Pending Payments')
    draft_invoices_amount = fields.Float(compute='_draft_invoices_amount',
                                         string='Draft Invoices')
    circulating_amount = fields.Float(compute='_circulating_amount',
                                      string='Payments Sent to Bank')
    pending_orders_amount = fields.Float(compute='_pending_orders_amount',
                                         string='Uninvoiced Orders')
    total_debt = fields.Float(compute='_total_debt',
                              string='Total Debt')
    available_risk = fields.Float(compute='_available_risk',
                                  string='Available Credit')
    total_risk_percent = fields.Float(compute='_total_risk_percent',
                                      string='Credit Usage (%)')
    pending_docum_debi = fields.Integer(compute='_pending_docum',
                                  string='Document Debit Pending')
    pending_docum_cred = fields.Integer(compute='_pending_docum',
                                  string='Document Credit Pending')
    pending_docum_draft = fields.Integer(compute='_draft_invoices_amount',
                                  string='Document Draft Pending')
    pending_credit_days = fields.Integer(compute='_pending_docum',
                                  string='Credit Days Pending')            

    @api.multi
    def _unpayed_amount(self):
        today = time.strftime('%Y-%m-%d')
        for partner in self:
            accounts = []
            if partner.property_account_receivable_id:
                accounts.append(partner.property_account_receivable_id.id)
            if partner.property_account_payable_id:
                accounts.append(partner.property_account_payable_id.id)
            line_ids = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('account_id', 'in', accounts),
                ('full_reconcile_id', '=', False),
                ('date_maturity', '<', today)])
            # Those that have amount_residual == 0,
            # will mean that they're circulating. #
            # The payment request has been sent
            # to the bank but have not yet been reconciled #
            # (or the date_maturity has not been reached).
            amount = 0.0
            for line in line_ids:
                if line.currency_id:
                    sign = line.amount_currency < 0 and -1 or 1
                else:
                    sign = (line.debit - line.credit) < 0 and -1 or 1
                # if line.reconcile_partial_id:
                #     amount += line.debit - line.credit
                # else:
                #     amount += sign * line.amount_residual
                amount += sign * line.amount_residual
            partner.unpayed_amount = amount

    @api.multi
    def _pending_amount(self):
        today = time.strftime('%Y-%m-%d')
        for partner in self:
            accounts = []
            if partner.property_account_receivable_id:
                accounts.append(partner.property_account_receivable_id.id)
            if partner.property_account_payable_id:
                accounts.append(partner.property_account_payable_id.id)
            line_ids = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('account_id', 'in', accounts),
                ('full_reconcile_id', '=', False),
                '|', ('date_maturity', '>=', today),
                ('date_maturity', '=', False)
            ])
            # Those that have amount_residual == 0,
            # will mean that they're circulating. #
            # The payment request has been sent
            # to the bank but have not yet been reconciled #
            # (or the date_maturity has not been reached).
            amount = 0.0
            for line in line_ids:
                if line.currency_id:
                    sign = line.amount_currency < 0 and -1 or 1
                else:
                    sign = (line.debit - line.credit) < 0 and -1 or 1
                # ???
                # if line.reconcile_partial_id:
                #     amount += line.debit - line.credit
                # else:
                #     amount += sign * line.amount_residual

                amount += sign * line.amount_residual
            partner.pending_amount = amount

    @api.multi
    def _draft_invoices_amount(self):
        today = time.strftime('%Y-%m-%d')
        for partner in self:
            invids = self.env['account.invoice'].search([
                ('partner_id', 'child_of', [partner.id]),
                ('state', '=', 'draft'),
                '|', ('date_due', '>=', today), ('date_due', '=', False)
            ])
            val = 0.0
            doc = 0
            for invoice in invids:
                # Note that even if the invoice is in 'draft' state it can
                # have an account.move because it
                # may have been validated and brought back to draft.
                # Here we'll only consider invoices with
                # NO account.move as those will be added in other fields.
                if invoice.move_id:
                    continue
                if invoice.type in ('out_invoice', 'in_refund'):
                    val += invoice.amount_total
                    doc += 1
                else:
                    val -= invoice.amount_total
                    doc -= 1
            partner.draft_invoices_amount = val
            partner.pending_docum_draft = doc

    @api.multi
    def _circulating_amount(self):
        for partner in self:
            amount = 0.0
            move_ids = self.env['account.move.line'].\
                search([('partner_id', 'child_of', [partner.id]),
                        ('account_id.circulating', '=', True),
                        ('full_reconcile_id', '=', False)])

            for line in move_ids:
                if line.currency_id:
                    sign = line.amount_currency < 0 and -1 or 1
                else:
                    sign = (line.debit - line.credit) < 0 and -1 or 1
                # if line.reconcile_partial_id:
                #     amount += line.debit - line.credit
                # else:
                #     amount += sign * line.amount_residual
                amount += sign * line.amount_residual
            partner.circulating_amount = amount

    @api.multi
    def _pending_orders_amount(self):
        for partner in self:
            total = 0.0
            # mids = self.env['stock.move'].search([
            #     ('partner_id', 'child_of', [partner.id]),
            #     ('state', 'not in', ['draft', 'cancel']),
            #     ('procurement_id.sale_line_id', '!=', False),
            #     ('invoice_state', '=', '2binvoiced')])

            # for move in mids:
            #     line = move.procurement_id.sale_line_id
            #     sign = move.picking_id.picking_type_code == "outgoing" and \
            #         1 or -1
            #     total += sign * \
            #         (move.product_uom_qty *
            #          (line.price_unit * (1 - (line.discount or 0.0) / 100.0)))

            sids = self.env['sale.order.line'].search([
                ('order_id.partner_id', 'child_of', [partner.id]),
                ('order_id.state', 'not in',
                    ['draft', 'cancel', 'wait_risk', 'sent']),
                ('invoice_status', '!=', 'invoiced'),
                '|', ('product_id', '=', False),
                ('product_id.type', '=', 'service')])
            for sline in sids:
                total += sline.price_subtotal

            partner.pending_orders_amount = total

    @api.multi
    def _total_debt(self):
        for partner in self:
            pending_orders = partner.pending_orders_amount or 0.0
            unpayed = partner.unpayed_amount or 0.0
            pending = partner.pending_amount or 0.0
            draft_invoices = partner.draft_invoices_amount or 0.0
            circulating = partner.circulating_amount or 0.0
            partner.total_debt = pending_orders + unpayed + pending + \
                draft_invoices + circulating

    @api.multi
    def _available_risk(self):
        for partner in self:
            partner.available_risk = partner.credit_limit - partner.total_debt

    @api.multi
    def _total_risk_percent(self):
        for partner in self:
            if partner.credit_limit:
                partner.total_risk_percen = \
                    100.0 * partner.total_debt / partner.credit_limit
            else:
                partner.total_risk_percen = 100
                
    @api.multi
    def _pending_docum(self):
        today = time.strftime('%Y-%m-%d')
        for partner in self:
            accounts = []
            if partner.property_account_receivable_id:
                accounts.append(partner.property_account_receivable_id.id)
            if partner.property_account_payable_id:
                accounts.append(partner.property_account_payable_id.id)
            line_ids = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('account_id', 'in', accounts),
                ('full_reconcile_id', '=', False),
                '|','|', ('date_maturity', '>=', today),
                ('date_maturity', '=', False),
                ('date_maturity', '<', today)
            ])
            # Those that have amount_residual == 0,
            # will mean that they're circulating. #
            # The payment request has been sent
            # to the bank but have not yet been reconciled #
            # (or the date_maturity has not been reached).
            amount = 0.0
            docum_debi = 0
            docum_cred = 0
            credit_days = 0
            for line in line_ids:
                if line.currency_id:
                    sign = line.amount_currency < 0 and -1 or 1
                else:
                    sign = (line.debit - line.credit) < 0 and -1 or 1

                if sign:                    
                    docum_debi += 1
                    fmt = '%Y-%m-%d'
                    d1 = datetime.strptime(today, fmt)
                    d2 = datetime.strptime(str(line.date_maturity), fmt)
                    days = (d2-d1).days
                    if days>credit_days:
                        credit_days = days
                else:
                    docum_cred += 1
            partner.pending_docum_debi = docum_debi
            partner.pending_docum_cred = docum_cred
            partner.pending_credit_days = credit_days                
