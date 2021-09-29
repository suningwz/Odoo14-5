# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"


    product_and_demand = fields.Text('Attachment Description', compute='_compute_product_and_demand', store=True, default="")

    @api.depends('move_ids_without_package', 'product_id')
    def _compute_product_and_demand(self):
        for record in self:
            if record.move_ids_without_package:
                record.product_and_demand = ""
                for move in record.move_ids_without_package:
                    if isinstance(move.id, int):
                        product = self.env['product.product'].search([('id', '=', move.product_id.id)])
                        line = product.name + "   - Demand: " + str(move.product_uom_qty) + "\n"
                        record.product_and_demand += line
            else :
                record.product_and_demand = ""
                

