# -*- coding: utf-8 -*-

import base64
import io

from odoo import models, api
from PyPDF2 import PdfFileWriter, PdfFileReader


class CortexIrAttachment(models.Model):
    _inherit = ['ir.attachment']


    def _create_document(self, vals):

        if vals.get('res_model') == 'cortex.document' and vals.get('res_id'):
            document = self.env['cortex.document'].browse(vals['res_id'])
            if document.exists() and not document.attachment_id:
                document.attachment_id = self[0].id
            return False

        res_model = vals.get('res_model')
        res_id = vals.get('res_id')
        model = self.env.get(res_model)
        if model is not None and res_id and issubclass(type(model), self.pool['cortex.documents.mixin']):
            vals_list = [
                model.browse(res_id)._get_document_vals(attachment)
                for attachment in self
                if not attachment.res_field
            ]
            vals_list = [vals for vals in vals_list if vals]  # Remove empty values
            self.env['cortex.document'].create(vals_list)
            return True
        return False

    @api.model
    def create(self, vals):
        attachment = super(CortexIrAttachment, self).create(vals)
        if not self._context.get('no_document') and not attachment.res_field:
            attachment.sudo()._create_document(dict(vals, res_model=attachment.res_model, res_id=attachment.res_id))
        return attachment

    def write(self, vals):
        if not self._context.get('no_document'):
            self.filtered(lambda a: not (vals.get('res_field') or a.res_field)).sudo()._create_document(vals)
        return super(CortexIrAttachment, self).write(vals)
