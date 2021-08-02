# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class CortexDocumentUpload(models.TransientModel):
    _name = "cortex.document.upload"
    _description = "Document Upload"


    owner_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Owner", tracking=True, required=True,)
    folder_id = fields.Many2one('cortex.folder', string="Folder", required=True)
    files = fields.Many2many(comodel_name='ir.attachment', relation='class_ir_attachments_rel_cortex', column1='class_id', column2='attachment_id', string='Attachments')
    res_model = fields.Char('Resource Model')
    res_id = fields.Integer('Resource ID')

    def upload_document(self):
        for file in self.files:
            document = self.env['cortex.document'].create({
                'name': file.name,
                'attachment_id': file.id,
                'folder_id': self.folder_id.id,
                'owner_id': self.owner_id.id if self.owner_id else False,
                'res_model': self.res_model,
                'res_id': self.res_id,
            })
            file.write({
                'res_model': 'cortex.document',
                'res_id': document.id,
            })
        
        #if document and document.attachment_id.mimetype != 'application/pdf':
        #    document.unlink()
        #    raise ValidationError('Only Format Pdf allowed')             
        
        if self.env.context.get('from_form_view', False):
            return {'type': 'ir.actions.act_window_close'}
        else:
            return { 'type': 'ir.actions.client', 'tag': 'reload'}


