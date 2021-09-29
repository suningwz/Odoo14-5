# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    sales_count = fields.Integer(compute='_compute_sale_count', string='Sale Order')
    purchase_count = fields.Integer(compute='_compute_purchase_count', string='Purchase Order')
    manufacturing_count = fields.Integer(compute='_compute_manufacturing_count', string='Manufacturing Order')
    

    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders').read()[0]
        sale_order = self.env['sale.order'].search([('project_id', '=', self.id)])
        action['domain'] = [('id', 'in', sale_order.ids)]
        action['views'] = [(False, 'tree'), (False, 'form')]
        if sale_order and len(sale_order) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = sale_order.id
        action['context'] = {'default_partner_id': self.partner_id.id, 'default_project_id': self.id}
        return action

    def _compute_sale_count(self):
        for record in self:
            sale_order = self.env['sale.order'].search([('project_id', '=', record.id)])
            record.sales_count = len(sale_order)

    def action_view_purchase_order(self):
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        purchase_order = self.env['purchase.order'].search([('project_id', '=', self.id)])
        action['domain'] = [('id', 'in', purchase_order.ids)]
        action['views'] = [(False, 'tree'), (False, 'form')]
        if purchase_order and len(purchase_order) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = purchase_order.id
        action['context'] = {'default_project_id': self.id}
        return action

    def _compute_purchase_count(self):
        for record in self:
            purchase_order = self.env['purchase.order'].search([('project_id', '=', record.id)])
            record.purchase_count = len(purchase_order)

    def action_view_manufacturing_order(self):
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        manufacturing_order = self.env['mrp.production'].search([('project_id', '=', self.id)])
        action['domain'] = [('id', 'in', manufacturing_order.ids)]
        action['views'] = [(False, 'tree'), (False, 'form')]
        if manufacturing_order and len(manufacturing_order) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = manufacturing_order.id
        action['context'] = {'default_project_id': self.id}
        return action

    def _compute_manufacturing_count(self):
        for record in self:
            manufacturing_order = self.env['mrp.production'].search([('project_id', '=', record.id)])
            record.manufacturing_count = len(manufacturing_order)

    def action_open_project_view(self):
        self.ensure_one()
        return {
            'view_mode': 'form',
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'view_id': self.env.ref('project.edit_project').id,
            'context': dict(self._context)
        }
