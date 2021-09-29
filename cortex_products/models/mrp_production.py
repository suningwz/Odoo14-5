# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    READONLY_STATES = {
        'draft': [('readonly', True)],
        'sent': [('readonly', True)],
        'sale': [('readonly', True)],
    }

    partner_id = fields.Many2one('res.partner', string='Vendor', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, states={'draft': [('readonly', False)]}, 
        default=lambda self: self.env.company.currency_id)
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', copy=False)
    sale_order_ids = fields.Many2many('sale.order', string='Sale Orders')
    sale_order_count = fields.Integer(compute='_compute_sale_order_count', string='Sale Order')
    project_id = fields.Many2one('project.project', string='Project', states=READONLY_STATES, tracking=True)

    def action_open_sale_orders(self):
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


    def _compute_sale_order_count(self):
        sale_order = self.env['sale.order'].search([('id', '=', self.sale_order_ids.ids)])
        self.sale_order_count = len(sale_order)
