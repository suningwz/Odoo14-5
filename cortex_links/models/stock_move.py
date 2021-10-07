# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES


class StockMove(models.Model):
    _inherit = "stock.move"


    rep_name = fields.Char('Reference', related='picking_id.name', copy=False, index=True, readonly=True, store=True)
    rep_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', related='picking_id.state', copy=False, index=True, readonly=True, store=True)
    rep_picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', related='picking_id.picking_type_id', readonly=True, store=True)
    rep_location_id = fields.Many2one('stock.location', "Source Location", related='picking_id.location_id',
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_rep_picking_type_id')).default_location_src_id,
        check_company=True, readonly=True, store=True)
    rep_location_dest_id = fields.Many2one('stock.location', "Destination Location", related='picking_id.location_dest_id',
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_rep_picking_type_id')).default_location_dest_id,
        check_company=True, readonly=True, store=True)
    rep_partner_id = fields.Many2one('res.partner', 'Contact', related='picking_id.partner_id', check_company=True, store=True)
    rep_group_id = fields.Many2one('procurement.group', 'Procurement Group', readonly=True, related='picking_id.group_id', store=True)
    rep_user_id = fields.Many2one('res.users', 'Responsible', related='picking_id.user_id',
        domain=lambda self: [('rep_groups_id', 'in', self.env.ref('stock.group_stock_user').id)], default=lambda self: self.env.user, store=True)
    rep_date = fields.Datetime('Creation Date', related='picking_id.date', default=fields.Datetime.now, index=True, store=True)
    rep_scheduled_date = fields.Datetime('Scheduled Date', related='picking_id.scheduled_date', index=True, default=fields.Datetime.now, 
        store=True)
    rep_origin = fields.Char('Source Document', related='picking_id.origin', index=True, store=True)
    rep_backorder_ids = fields.One2many('stock.picking', 'backorder_id', 'Back Orders', related='picking_id.backorder_ids', store=True)
    rep_priority = fields.Selection( PROCUREMENT_PRIORITIES, string='Priority', related='picking_id.priority', index=True, store=True)
    rep_company_id = fields.Many2one('res.company', string='Company', related='picking_id.company_id',readonly=True, index=True, store=True)
    rep_picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', related='picking_id.picking_type_id', readonly=True, store=True)
    rep_picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_type_id.code', readonly=True, store=True)
    
    def open_delivery(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfers',
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
            'view_mode': 'form',
            'context': {'force_detailed_view': 'true'},
        }
