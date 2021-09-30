# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    READONLY_STATES = {
        'draft': [('readonly', True)],
        'sent': [('readonly', True)],
        'sale': [('readonly', True)],
    }

    project_id = fields.Many2one('project.project', string='Project', states=READONLY_STATES, tracking=True)
    purchase_count = fields.Integer(compute='_compute_purchase_count', string='Purchase Orders')
    manufacturing_count = fields.Integer(compute='_compute_manufacturing_count', string='Manufacturing Orders')

    def _compute_purchase_count(self):
        purchase_order = self.env['purchase.order'].search([('sale_order_ids', 'in', self.id)])
        self.purchase_count = len(purchase_order) 
    
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
