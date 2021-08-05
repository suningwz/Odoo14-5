# -*- coding: utf-8 -*-

from odoo import models


class CortexDocumentMixin(models.AbstractModel):
    _name = 'cortex.documents.mixin'
    _description = "Documents creation mixin"

    def _get_document_vals(self, attachment):
        self.ensure_one()
        document_vals = {}
        if self._check_create_documents():
            document_vals = {
                'attachment_id': attachment.id,
                'name': attachment.name or self.display_name,
                'folder_id': self._get_document_folder().id,
                'owner_id': self._get_document_owner().id,
                'tag_ids': [(6, 0, self._get_document_tags().ids)],
            }
        return document_vals

    def _get_document_owner(self):
        return self.env.user

    def _get_document_tags(self):
        return self.env['cortex.tag']

    def _get_document_folder(self):
        return self.env['cortex.folder']

    def _check_create_documents(self):
        return bool(self and self._get_document_folder())