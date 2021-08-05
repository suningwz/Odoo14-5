# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CortexFolder(models.Model):
    _name = 'cortex.folder'
    _description = 'Documents Folder'
    _parent_name = 'parent_folder_id'
    _order = 'sequence'

    @api.constrains('parent_folder_id')
    def _check_parent_folder_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive folders.'))

    @api.model
    def default_get(self, fields):
        res = super(CortexFolder, self).default_get(fields)
        if 'parent_folder_id' in fields and self._context.get('folder_id') and not res.get('parent_folder_id'):
            res['parent_folder_id'] = self._context.get('folder_id')

        return res

    def name_get(self):
        name_array = []
        hierarchical_naming = self.env.context.get('hierarchical_naming', True)
        for record in self:
            if hierarchical_naming and record.parent_folder_id:
                name_array.append((record.id, "%s / %s" % (record.parent_folder_id.name, record.name)))
            else:
                name_array.append((record.id, record.name))
        return name_array

    company_id = fields.Many2one('res.company', 'Company')
    parent_folder_id = fields.Many2one('cortex.folder', string="Parent Folder", ondelete="cascade")
    name = fields.Char(required=True, translate=True)
    description = fields.Html(string="Description", translate=True)
    children_folder_ids = fields.One2many('cortex.folder', 'parent_folder_id', string="Sub Folders")
    document_ids = fields.One2many('cortex.document', 'folder_id', string="Documents")
    sequence = fields.Integer('Sequence', default=10)
    category_ids = fields.One2many('cortex.category', 'folder_id', string="Tag Categories")
    group_ids = fields.Many2many('res.groups', string="Write Groups", )
    read_group_ids = fields.Many2many('res.groups', 'cortex_folder_read_groups', string="Read Groups")
    document_count = fields.Integer('Document Count', compute='_compute_document_count')

    def _compute_document_count(self):
        read_group_var = self.env['cortex.document'].read_group(
            [('folder_id', 'in', self.ids)],
            fields=['folder_id'],
            groupby=['folder_id'])

        document_count_dict = dict((d['folder_id'][0], d['folder_id_count']) for d in read_group_var)
        for record in self:
            record.document_count = document_count_dict.get(record.id, 0)

    def action_see_documents(self):
        domain = [('folder_id', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'cortex.document',
            'type': 'ir.actions.act_window',
            'views': [(False, 'list'), (False, 'form')],
            'view_mode': 'tree,form',
            'context': "{'default_folder_id': %s}" % self.id
        }

    def action_upload_wizard(self):
        from_form_view = self.env.context.get('from_form_view', False)
        ctx = dict(self.env.context or {})        
        ctx.update({ 'default_folder_id': self.id }) 
        ctx.update({ 'from_form_view': from_form_view }) 
        return  {
            'type': 'ir.actions.act_window',
            'name': 'Upload attachments',
            'res_model': 'cortex.document.upload',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'context': ctx,
            'target': 'new',
        }