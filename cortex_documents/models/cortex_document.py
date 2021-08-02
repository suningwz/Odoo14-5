# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import image_process
from ast import literal_eval
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import re


class CortexDocument(models.Model):
    _name = 'cortex.document'
    _description = 'Document'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _order = 'id desc'

    attachment_id = fields.Many2one('ir.attachment', ondelete='cascade', auto_join=True, copy=False)
    attachment_name = fields.Char('Attachment Name', related='attachment_id.name', readonly=False)
    attachment_type = fields.Selection(string='Attachment Type', related='attachment_id.type', readonly=False)
    datas = fields.Binary(related='attachment_id.datas', related_sudo=True, readonly=False)
    file_size = fields.Integer(related='attachment_id.file_size', store=True)
    checksum = fields.Char(related='attachment_id.checksum')
    mimetype = fields.Char(related='attachment_id.mimetype', default='application/octet-stream')
    res_model = fields.Char('Resource Model', compute="_compute_res_record", inverse="_inverse_res_model", store=True)
    res_id = fields.Integer('Resource ID', compute="_compute_res_record", inverse="_inverse_res_id", store=True)
    res_name = fields.Char('Resource Name', related='attachment_id.res_name')
    index_content = fields.Text(related='attachment_id.index_content')
    description = fields.Text('Attachment Description', related='attachment_id.description', readonly=False)

    name = fields.Char('Name', copy=True, store=True, compute='_compute_name', inverse='_inverse_name')
    active = fields.Boolean(default=True, string="Active")
    thumbnail = fields.Binary(readonly=1, store=True, attachment=True, compute='_compute_thumbnail')
    res_model_name = fields.Char(compute='_compute_res_model_name', index=True)
    tag_ids = fields.Many2many('cortex.tag', 'cortex_tag_rel', string="Tags")
    partner_id = fields.Many2one('res.partner', string="Contact", tracking=True)
    owner_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Owner", tracking=True)
    folder_id = fields.Many2one('cortex.folder', string="Folder", ondelete="restrict", tracking=True, required=True, index=True)
    company_id = fields.Many2one('res.company', string='Company', related='folder_id.company_id', readonly=True)
    group_ids = fields.Many2many('res.groups', string="Access Groups", readonly=True, related='folder_id.group_ids')

    _sql_constraints = [
        ('attachment_unique', 'unique (attachment_id)', "This attachment is already a document"),
    ]

    @api.depends('attachment_id.name')
    def _compute_name(self):
        for record in self:
            if record.attachment_name:
                record.name = record.attachment_name

    def _inverse_name(self):
        for record in self:
            if record.attachment_id:
                record.attachment_name = record.name

    @api.depends('attachment_id', 'attachment_id.res_model', 'attachment_id.res_id')
    def _compute_res_record(self):
        for record in self:
            attachment = record.attachment_id
            if attachment:
                record.res_model = attachment.res_model
                record.res_id = attachment.res_id

    def _inverse_res_id(self):
        for record in self:
            attachment = record.attachment_id.with_context(no_document=True)
            if attachment:
                attachment.res_id = record.res_id

    def _inverse_res_model(self):
        for record in self:
            attachment = record.attachment_id.with_context(no_document=True)
            if attachment:
                attachment.res_model = record.res_model

    @api.depends('checksum')
    def _compute_thumbnail(self):
        for record in self:
            try:
                record.thumbnail = image_process(record.datas, size=(80, 80), crop='center')
            except UserError:
                record.thumbnail = False
    
    #this needs work
    def _get_models(self, domain):

        not_a_file = []
        not_attached = []
        models = []
        groups = self.read_group(domain, ['res_model'], ['res_model'], lazy=True)
        for group in groups:
            res_model = group['res_model']
            if not res_model:
                not_a_file.append({
                    'id': res_model,
                    'display_name': _('Not a file'),
                    '__count': group['res_model_count'],
                })
            elif res_model == 'cortex.document':
                not_attached.append({
                    'id': res_model,
                    'display_name': _('Not attached'),
                    '__count': group['res_model_count'],
                })
            else:
                models.append({
                    'id': res_model,
                    'display_name': self.env['ir.model']._get(res_model).display_name,
                    '__count': group['res_model_count'],
                })
        return sorted(models, key=lambda m: m['display_name']) + not_attached + not_a_file

    @api.depends('res_model')
    def _compute_res_model_name(self):
        for record in self:
            if record.res_model:
                model = self.env['ir.model'].name_search(record.res_model, limit=1)
                if model:
                    record.res_model_name = model[0][1]
                else:
                    record.res_model_name = False
            else:
                record.res_model_name = False

    def access_content(self):
        self.ensure_one()
        action = {
            'type': "ir.actions.act_url",
            'target': "new",
        }
        action['url'] = '/cortex_documents/content/%s' % self.id
        return action

    @api.model
    def create(self, vals):
        keys = [key for key in vals if
                self._fields[key].related and self._fields[key].related[0] == 'attachment_id']
        attachment_dict = {key: vals.pop(key) for key in keys if key in vals}
        attachment = self.env['ir.attachment'].browse(vals.get('attachment_id'))

        if attachment and attachment_dict:
            attachment.write(attachment_dict)
        elif attachment_dict:
            attachment_dict.setdefault('name', vals.get('name', 'unnamed'))
            attachment = self.env['ir.attachment'].create(attachment_dict)
            vals['attachment_id'] = attachment.id
        new_record = super(CortexDocument, self).create(vals)

        if (attachment and not attachment.res_id and (not attachment.res_model or attachment.res_model == 'cortex.document')):
            attachment.with_context(no_document=True).write({'res_model': 'cortex.document', 'res_id': new_record.id})
        return new_record

    def write(self, vals):
        attachment_id = vals.get('attachment_id')
        if attachment_id:
            self.ensure_one()
        for record in self:

            if vals.get('datas') and not vals.get('attachment_id'):
                res_model = vals.get('res_model', record.res_model or 'cortex.document')
                res_id = vals.get('res_id') if vals.get('res_model') else record.res_id if record.res_model else record.id
                if res_model and res_model != 'cortex.document' and not self.env[res_model].browse(res_id).exists():
                    record.res_model = res_model = 'cortex.document'
                    record.res_id = res_id = record.id
                attachment = self.env['ir.attachment'].with_context(no_document=True).create({
                    'name': vals.get('name', record.name),
                    'res_model': res_model,
                    'res_id': res_id
                })
                record.attachment_id = attachment.id

        attachment_dict = {key: vals.pop(key) for key in ['datas', 'mimetype'] if key in vals}

        write_result = super(CortexDocument, self).write(vals)
        if attachment_dict:
            self.mapped('attachment_id').write(attachment_dict)

        return write_result

    def _get_processed_tags(self, domain, folder_id):

        tags = self.env['cortex.tag']._get_tags(domain, folder_id)
        facets = list(OrderedDict.fromkeys([tag['group_id'] for tag in tags]))
        facet_colors = self.env['cortex.category'].CATEGORY_ORDER_COLORS
        for tag in tags:
            color_index = facets.index(tag['group_id']) % len(facet_colors)
            tag['group_hex_color'] = facet_colors[color_index]

        return tags
    
    def call_upload_wizard(self):
        return  {
            'type': 'ir.actions.act_window',
            'name': 'Upload attachments',
            'res_model': 'cortex.document.upload',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
        }
    