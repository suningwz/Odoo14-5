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
    purchase_count = fields.Integer(compute='_compute_purchase_count', string='Purchase Order')

    def _compute_purchase_count(self):
        purchase_order = self.env['purchase.order'].search([('select_sale_order_ids', 'in', self.id)])
        self.purchase_count = len(purchase_order) 
    
    def action_view_purchase_order(self):
        purchase_obj = self.env['purchase.order'].search([('select_sale_order_ids', 'in', self.id)])
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
