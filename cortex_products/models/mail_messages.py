# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_post_process_attachments(self, attachments, attachment_ids, message_values):
        """ Preprocess attachments for mail_thread.message_post() or mail_mail.create().

        :param list attachments: list of attachment tuples in the form ``(name,content)``, #todo xdo update that
                                 where content is NOT base64 encoded
        :param list attachment_ids: a list of attachment ids, not in tomany command form
        :param dict message_data: model: the model of the attachments parent record,
          res_id: the id of the attachments parent record
        """
        return_values = super(MailThread, self)._message_post_process_attachments(attachments, attachment_ids, message_values)
        if self._context.get('active_model') == 'purchase.order':
            # Attach drawing files with PO mail 
            drawing_attachment_ids = []
            if attachment_ids:
                # taking advantage of cache looks better in this case, to check
                filtered_drawing_attachment_ids = self.env['ir.attachment'].sudo().browse(attachment_ids).filtered(lambda a: a.res_model in ['cortex.document', 'product.template'])
                drawing_attachment_ids += [(4, id) for id in filtered_drawing_attachment_ids.ids]

            return_values['attachment_ids'] = return_values.get('attachment_ids', []) + drawing_attachment_ids
        return return_values
