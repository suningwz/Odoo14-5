# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    project_id = fields.Many2one('project.project', string='Project', states=READONLY_STATES, tracking=True)
    select_sale_order_ids = fields.Many2many('sale.order', string='Sale Orders')
    rfq = fields.Char(string='RFQ', compute='_compute_rfq_po', store=True)
    payment_ids = fields.One2many('account.payment', 'purchase_order_id', string='Account Payment')
    payment_count = fields.Integer(compute='_compute_account_payment_count', string='Purchase Order')
    advance_payment = fields.Float(string='Advance Payment', compute='_compute_advance_payment', store=True)
    remaining_amount = fields.Float(string='Unpaid Balance', compute='_compute_remaining_amount', store=True)
    percentage_paid = fields.Integer(string="Percentage of total PO paid", compute='_compute_percentage_paid')

    @api.depends('state')
    def _compute_rfq_po(self):
        for record in self:
            if record.state not in ('draft', 'sent'):
                record.rfq = record.name.replace("RFQ", "P")
                record.name = record.rfq 
            if record.state in ('draft', 'sent'):
                record.rfq = record.name.replace("P", "RFQ")
                record.name = record.rfq

    @api.depends('advance_payment', 'amount_total', 'invoice_status')
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.amount_total - record.advance_payment if record.invoice_status != 'invoiced' else 0

    @api.depends('payment_ids','payment_ids.amount')
    def _compute_advance_payment(self):
        for record in self:
            total_amount = 0
            if record.payment_ids:
                for line in record.payment_ids:
                    total_amount += line.amount
            record.advance_payment = total_amount

    @api.depends('advance_payment', 'amount_total', 'invoice_status')
    def _compute_percentage_paid(self):
        for record in self:
            if record.invoice_status != 'invoiced':
                record.percentage_paid = (record.advance_payment / record.amount_total)*100
            else :
                record.percentage_paid = 0
    
    @api.depends('payment_ids')
    def _compute_account_payment_count(self):
        for order in self:
            order.payment_count = len(order.payment_ids)

    def action_view_advance_payment(self):
        action = self.env.ref('account.action_account_payments_payable').read()[0]
        advance_payment = self.mapped('payment_ids')
        if len(advance_payment) > 1:
            action['domain'] = [('id', 'in', advance_payment.ids)]
        elif advance_payment:
            form_view = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = advance_payment.id
        return action

    def action_advance_payment(self):
        ctx = dict(
            default_partner_id=self.partner_id.id,
            default_purchase_order_id=self.id,
            default_payment_type='outbound',
            default_partner_type='supplier',
            default_communication=self.name,
            default_currency_id = self.currency_id.id
        )
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('cortex_products.view_account_payment_form_custom').id,
            'context': ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
