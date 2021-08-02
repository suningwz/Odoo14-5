# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv import expression


class CortexCategory(models.Model):
    _name = "cortex.category"
    _description = "Category"
    _order = "sequence, name"


    CATEGORY_ORDER_COLORS = ['#F06050', '#6CC1ED', '#F7CD1F', '#814968', '#30C381', '#D6145F', '#475577', '#F4A460',
                          '#EB7E7F', '#2C8397']

    folder_id = fields.Many2one('cortex.folder', string="Folder", ondelete="cascade")
    name = fields.Char(required=True, translate=True)
    tag_ids = fields.One2many('cortex.tag', 'category_id')
    sequence = fields.Integer('Sequence', default=10)

    _sql_constraints = [
        ('name_unique', 'unique (folder_id, name)', "Category already exists in this folder"),
    ]


class CortexTags(models.Model):
    _name = "cortex.tag"
    _description = "Tag"
    _order = "sequence, name"

    folder_id = fields.Many2one('cortex.folder', string="Folder", related='category_id.folder_id', store=True, readonly=False)
    category_id = fields.Many2one('cortex.category', string="Category", ondelete='cascade', required=True)
    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)

    _sql_constraints = [
        ('category_name_unique', 'unique (category_id, name)', "Tag already exists for this category"),
    ]

    def name_get(self):
        names = []
        if self._context.get('simple_name'):
            return super(CortexTags, self).name_get()
        for record in self:
            names.append((record.id, "%s > %s" % (record.category_id.name, record.name)))
        return names

    @api.model
    def _get_tags(self, domain, folder_id):
        """
        fetches the tag and category ids for the document selector (custom left sidebar of the kanban view)
        """
        documents = self.env['cortex.document'].search(domain)
        # folders are searched with sudo() so we fetch the tags and categories from all the folder hierarchy (as tags
        # and categories are inherited from ancestor folders).
        folders = self.env['cortex.folder'].sudo().search([('parent_folder_id', 'parent_of', folder_id)])
        self.flush(['sequence', 'name', 'category_id'])
        self.env['cortex.category'].flush(['sequence', 'name'])
        query = """
            SELECT  category.sequence AS group_sequence,
                    category.id AS group_id,
                    cortex_tag.sequence AS sequence,
                    cortex_tag.id AS id,
                    COUNT(rel.cortex_document_id) AS __count
            FROM cortex_tag
                JOIN cortex_category category ON cortex_tag.category_id = category.id
                    AND category.folder_id = ANY(%s)
                LEFT JOIN cortex_tag_rel rel ON cortex_tag.id = rel.cortex_tag_id
                    AND rel.cortex_document_id = ANY(%s)
            GROUP BY category.sequence, category.name, category.id, cortex_tag.sequence, cortex_tag.name, cortex_tag.id
            ORDER BY category.sequence, category.name, category.id, cortex_tag.sequence, cortex_tag.name, cortex_tag.id
        """
        params = [
            list(folders.ids),
            list(documents.ids),  # using Postgresql's ANY() with a list to prevent empty list of documents
        ]
        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()

        # Translating result
        groups = self.env['cortex.category'].browse({r['group_id'] for r in result})
        group_names = {group['id']: group['name'] for group in groups}

        tags = self.env['cortex.tag'].browse({r['id'] for r in result})
        tags_names = {tag['id']: tag['name'] for tag in tags}

        for r in result:
            r['group_name'] = group_names.get(r['group_id'])
            r['display_name'] = tags_names.get(r['id'])

        return result