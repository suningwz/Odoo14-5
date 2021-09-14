# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    

    machine_parts_count = fields.Integer(string='Machine Parts', compute='_compute_installed_parts_ids')
    installed_parts_count = fields.Integer(string='Installed Parts', compute='_compute_installed_parts_ids')

    def _compute_installed_parts_ids(self):
        for partner in self:
            machine_parts = self.env['installed.part'].search([('partner_id', 'in', partner.ids)])
            installed_parts = self.env['installed.part.detail'].search([('install_part_id.partner_id', 'in', partner.ids)])
            partner.machine_parts_count = len(machine_parts)
            partner.installed_parts_count = len(installed_parts)

    def action_view_machine_parts(self):
        return {
            'name': _('Machine Center'),
            'res_model': 'installed.part',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id':self.id}
        }        

    def action_view_installed_parts(self):
        return {
            'name': _('Installed Part'),
            'res_model': 'installed.part.detail',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'domain': [('install_part_id.partner_id', '=', self.id)],
            'context': {'search_default_filter_frequency': 1}
        }
