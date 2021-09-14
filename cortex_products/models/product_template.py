# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"


    drawing_no = fields.Char('Drawing #', track_visibility='onchange')
    drawing_version = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F'), ('g', 'G'), ('h', 'H')], string='Drawing Version')
    drawing_number = fields.Char(string='Drawing #', compute='_compute_drawing_number', store=True)
    drawing_pdf = fields.Binary(string='Drawing pdf')
    file_name = fields.Char(string='FileName')
    documents = fields.One2many('cortex.document', 'document_owner', string="Documents")
    category_name = fields.Char('Category name', related='categ_id.name')
    length = fields.Float('Length', compute='_compute_length', digits='Stock Length', inverse='_set_length', store=True)
    machine_parts_count = fields.Integer(string='Machine Part', compute='_compute_installed_parts_ids')
    installed_parts_count = fields.Integer(string='Installed Part', compute='_compute_installed_parts_ids')
    installed_quantity = fields.Float(string="Installed Quantity",compute="_compute_installed_parts_ids",digits='New Cortex Precision')

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
    
    @api.depends('product_variant_ids', 'product_variant_ids.length')
    def _compute_length(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.length = template.product_variant_ids.length
        for template in (self - unique_variants):
            template.length = 0.0

    def _set_length(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.length = template.length
    
    @api.depends('product_variant_id')
    def _compute_installed_parts_ids(self):
        for product in self:
            machine_parts = self.env['installed.part'].search([('installed_part_detail_id.product_id', 'in', product.product_variant_id.ids)])
            installed_parts = self.env['installed.part.detail'].search(
                [('product_id', 'in',  product.product_variant_id.ids)])

            total=0
            for record in installed_parts:
                total += record.installed_knife

            product.installed_quantity = total
            product.machine_parts_count = len(machine_parts)
            product.installed_parts_count = len(installed_parts)

    def action_view_machine_parts(self):
        return {
            'name': _('Machine Center'),
            'res_model': 'installed.part',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'domain': [('installed_part_detail_id.product_id', 'in', self.product_variant_id.ids)],
            'context': {'default_partner_id':self.id}
        }

    def action_view_installed_parts(self):
        return {
            'name': _('Installed Part'),
            'res_model': 'installed.part.detail',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'domain': [('product_id', 'in', self.product_variant_id.ids)],
            'context': {'search_default_filter_frequency': 1}
        }


class DocumentProduct(models.Model):
    _inherit = 'cortex.document'

    document_owner = fields.Many2one('product.template', string="Documents Owner")
