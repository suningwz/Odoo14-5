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
    ], string='Status', related='picking_id.state', copy=False, index=True, readonly=True, store=True, tracking=True)
    rep_picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', related='picking_id.picking_type_id', 
        readonly=True, states={'draft': [('readonly', False)]}, store=True)

    rep_location_id = fields.Many2one('stock.location', "Source Location", related='picking_id.location_id',
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_rep_picking_type_id')).default_rep_location_src_id,
        check_company=True, readonly=True, states={'draft': [('readonly', False)]}, store=True)

    rep_location_dest_id = fields.Many2one('stock.location', "Destination Location", related='picking_id.location_dest_id',
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_rep_picking_type_id')).default_rep_location_dest_id,

        check_company=True, readonly=True, required=True,states={'draft': [('readonly', False)]})
    rep_partner_id = fields.Many2one('res.partner', 'Contact', related='picking_id.partner_id',
        check_company=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    rep_user_id = fields.Many2one('res.users', 'Responsible', tracking=True, related='picking_id.user_id',
        domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').id)],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, default=lambda self: self.env.user)
    rep_date = fields.Datetime('Creation Date', related='picking_id.date',
        default=fields.Datetime.now, index=True, tracking=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    rep_scheduled_date = fields.Datetime('Scheduled Date', related='picking_id.scheduled_date', store=True,
        index=True, default=fields.Datetime.now, tracking=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    rep_origin = fields.Char('Source Document', related='picking_id.origin', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    rep_group_id = fields.Many2one('procurement.group', 'Procurement Group', readonly=True, related='picking_id.group_id', store=True)
    rep_backorder_ids = fields.One2many('stock.picking', 'backorder_id', 'Back Orders', related='picking_id.backorder_ids')
    rep_priority = fields.Selection( PROCUREMENT_PRIORITIES, string='Priority', related='picking_id.priority', store=True,
        index=True, tracking=True,states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    rep_company_id = fields.Many2one('res.company', string='Company', related='picking_id.company_id',readonly=True, store=True, index=True)

    rep_picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', related='picking_id.picking_type_id',
        required=True, readonly=True, states={'draft': [('readonly', False)]})
    rep_picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_type_id.code', readonly=True)
