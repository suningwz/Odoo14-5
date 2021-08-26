# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    length = fields.Float(string="Length", related='product_tmpl_id.length', store=True)
