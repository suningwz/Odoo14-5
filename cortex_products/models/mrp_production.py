# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    READONLY_STATES = {
        'draft': [('readonly', True)],
        'sent': [('readonly', True)],
        'sale': [('readonly', True)],
    }

    project_id = fields.Many2one('project.project', string='Project', states=READONLY_STATES, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, states={'draft': [('readonly', False)]}, 
        default=lambda self: self.env.company.currency_id)
    sale_order_ids = fields.Many2many('sale.order', string='Sale Orders')
    sale_count = fields.Integer(compute='_compute_sale_count', string='Sale Orders')
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Order')
    purchase_count = fields.Integer(compute='_compute_purchase_count', string='Purchase Orders')

    def _compute_sale_count(self):
        sale_order = self.env['sale.order'].search([('id', '=', self.sale_order_ids.ids)])
        self.sale_count = len(sale_order)

    def action_view_sale_orders(self):
        sale_obj = self.env['sale.order'].search([('id', '=',self.sale_order_ids.ids)])
        sale_ids = []
        view_id = self.env.ref('sale.view_order_form').id
        for each in sale_obj:
            sale_ids.append(each.id)
        if len(sale_ids) <= 1:
            return {
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'name': _('Sale Orders'),
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'domain': [('id', '=', self.sale_order_ids.ids)],
                'res_id': sale_ids and sale_ids[0]
            }
        else:
            return {
                'name': _('Sale Orders'),
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'view_mode': 'list,form',
                'domain': [('id', '=', self.sale_order_ids.ids)],
            }
    
    def _compute_purchase_count(self):
        purchase_order = self.env['purchase.order'].search([('id', '=', self.purchase_order_ids.ids)])
        self.purchase_count = len(purchase_order)

    def action_view_purchase_orders(self):
        purchase_obj = self.env['purchase.order'].search([('id', '=', self.purchase_order_ids.ids)])
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
