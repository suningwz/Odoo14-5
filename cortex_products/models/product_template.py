# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"


    drawing_no = fields.Char('Drawing #', track_visibility='onchange')
    drawing_version = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F'), ('g', 'G'), ('h', 'H')], string='Drawing Version')
    drawing_number = fields.Char(string='Drawing #', compute='_compute_drawing_number', store=True)
    drawing_pdf = fields.Binary(string='Drawing pdf')
    file_name = fields.Char(string='FileName')
    documents = fields.One2many('cortex.document', 'document_owner', string="Documents")
    category_name = fields.Char('Category name', related='categ_id.name')

    @api.onchange('drawing_no', 'drawing_version')
    def onchange_drawing_no(self):
        if not self.drawing_no and self.drawing_version:
            self.drawing_version = ''

    @api.depends('drawing_no', 'drawing_version')
    def _compute_drawing_number(self):
        for record in self:
            drawing_number = record.drawing_no
            if record.drawing_version and drawing_number:
                drawing_number = drawing_number + ' - ' + (record.drawing_version).upper()
            record.drawing_number = drawing_number

    @api.onchange('documents')
    def onchange_pdf_file(self):
        for record in self:
            for doc in record.documents:
                if doc.mimetype == 'application/pdf':
                    record.drawing_pdf = doc.datas


class DocumentProduct(models.Model):
    _inherit = 'cortex.document'

    document_owner = fields.Many2one('product.template', string="Documents Owner")
