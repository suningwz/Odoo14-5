# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, SUPERUSER_ID, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    rfq = fields.Char(string='RFQ', compute='_compute_rfq_po', store=True)

    @api.depends('state')
    def _compute_rfq_po(self):
        for record in self:
            if record.state not in ('draft', 'sent'):
                record.rfq = record.name.replace("RFQ", "P")
                record.name = record.rfq 
            if record.state in ('draft', 'sent'):
                record.rfq = record.name.replace("P", "RFQ")
                record.name = record.rfq 

