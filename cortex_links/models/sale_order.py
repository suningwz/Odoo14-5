# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"


    READONLY_STATES = {
        'draft': [('readonly', True)],
        'sent': [('readonly', True)],
        'sale': [('readonly', True)],
    }

    project_id = fields.Many2one('project.project', string='Project', states=READONLY_STATES, tracking=True)
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Order')
    purchase_count = fields.Integer(compute='_compute_purchase_count', string='Purchase Orders')
    manufacturing_count = fields.Integer(compute='_compute_manufacturing_count', string='Manufacturing Orders')
    pending_amount = fields.Float('Pending Amount', compute='_compute_pending_amount', store=True)
    has_knife_order = fields.Boolean(compute='_compute_has_knife_order', string='Has Knife Order', default=False, store=True)

    @api.depends('state', 'order_line.product_id', 'order_line.product_uom_qty', 'order_line.qty_delivered', 'order_line.net_price')
    def _compute_pending_amount(self):
        for record in self:
            line_pending_amount = 0
            pending_amounts = 0
            if record.state not in ('draft', 'sent'):
                for line in record.order_line:
                    if line.is_downpayment == True:
                        advance_payment = line.product_uom_qty * line.net_price
                        qty = line.product_uom_qty - line.qty_delivered
                        line_pending_amount = (qty * line.net_price) - advance_payment
                    else:
                        qty = line.product_uom_qty - line.qty_delivered
                        line_pending_amount = qty * line.net_price
                    pending_amounts += line_pending_amount
                record.pending_amount = pending_amounts
            else:
                record.pending_amount = 0.0
    
    @api.depends('order_line.product_id')
    def _compute_has_knife_order(self):        
        for record in self:
            if record.order_line:
                for line in record.order_line:
                    if line.product_id.categ_id.name in ('Cortex Knives V-3 Finished', 'Bridge Knives'):
                        record.has_knife_order = True
            else :
                record.has_knife_order = False


    def _compute_purchase_count(self):
        purchase_order = self.env['purchase.order'].search([('sale_order_ids', 'in', self.id)])
        self.purchase_count = len(purchase_order)
        self.purchase_order_ids = purchase_order
    
    def action_view_purchase_orders(self):
        purchase_obj = self.env['purchase.order'].search([('sale_order_ids', 'in', self.id)])
        purchase_ids = []
        for each in purchase_obj:
            purchase_ids.append(each.id)
        view_id = self.env.ref('purchase.purchase_order_form').id
        if purchase_ids:
            if len(purchase_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.order',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Purchase orders'),
                    'res_id': purchase_ids and purchase_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', purchase_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'purchase.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Purchase orders'),
                    'res_id': purchase_ids
                }
            return value

    def _compute_manufacturing_count(self):
        manufacturing_order = self.env['mrp.production'].search([('sale_order_ids', 'in', self.id)])
        self.manufacturing_count = len(manufacturing_order) 
    
    def action_view_manufacturing_orders(self):
        manufacturing_obj = self.env['mrp.production'].search([('sale_order_ids', 'in', self.id)])
        manufacturing_ids = []
        for each in manufacturing_obj:
            manufacturing_ids.append(each.id)
        view_id = self.env.ref('mrp.mrp_production_form_view').id
        if manufacturing_ids:
            if len(manufacturing_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mrp.production',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Manufacturing orders'),
                    'res_id': manufacturing_ids and manufacturing_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', manufacturing_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'mrp.production',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Manufacturing orders'),
                    'res_id': manufacturing_ids
                }
            return value

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    net_price = fields.Float('Discounted Price', digits=dp.get_precision('Discount'))

    @api.onchange('discount', 'price_unit')
    def _onchange_discount(self):
        if not self._context.get('is_discount'):
            self.net_price = self.price_unit - ((self.price_unit * self.discount) / 100)