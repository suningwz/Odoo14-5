# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountPayments(models.Model):
    _inherit = "account.payment"


    purchase_order_id = fields.Many2one('purchase.order', 'purchase_id', ondelete='cascade', copy=False)
