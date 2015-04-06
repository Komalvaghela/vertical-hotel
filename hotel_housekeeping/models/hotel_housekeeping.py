# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import models,fields,api,_
import time
from openerp import netsvc

class product_category(models.Model):
    _inherit = "product.category"
    
    isactivitytype = fields.Boolean('Is Activity Type')

    _defaults = {
        'isactivitytype': lambda *a: True,
    }

class hotel_housekeeping_activity_type(models.Model):
    _name = 'hotel.housekeeping.activity.type'
    _description = 'Activity Type'
    _inherits = {'product.category':'activity_id'}
    
    activity_id = fields.Many2one(comodel_name='product.category',string='Category',required=True, ondelete='cascade')

class hotel_activity(models.Model):
    _name = 'hotel.activity'
    _inherits = {'product.product': 'h_id'}
    _description = 'Housekeeping Activity'

    h_id = fields.Many2one(comodel_name='product.product',string='Product',required=True, ondelete='cascade')

class hotel_housekeeping(models.Model):

    _name = "hotel.housekeeping"
    _description = "Reservation"
                
    current_date = fields.Date("Today's Date", required=True,default=lambda *a: time.strftime('%Y-%m-%d'))
    clean_type = fields.Selection([('daily', 'Daily'), ('checkin', 'Check-In'), ('checkout', 'Check-Out')], 'Clean Type', required=True)
    room_no = fields.Many2one(comodel_name='hotel.room',string='Room No',required=True)
    activity_lines =fields.One2many(comodel_name='hotel.housekeeping.activities',inverse_name='a_list',string='Activities',help='Details of housekeeping activities.')
    inspector = fields.Many2one(comodel_name='res.users',string='Inspector' ,required=True)
    inspect_date_time =fields.Datetime('Inspect Date Time', required=True)
    quality = fields.Selection([('bad', 'Bad'), ('good', 'Good'), ('ok', 'Ok')], 'Quality', required=True, help='Inspector inspect the room and mark as Bad, Good or Ok. ')
    state = fields.Selection([('dirty', 'Dirty'), ('clean', 'Clean'), ('inspect', 'Inspect'), ('done', 'Done'), ('cancel', 'Cancelled')], 'State', select=True, required=True, readonly=True,default=lambda *a: 'dirty')

#    @api.multi
#    def action_set_to_dirty(self):
#        self.write({'state': 'dirty'})
#        wf_service = netsvc.LocalService('workflow')
#        for id in ids:
#            wf_service.trg_create(uid, self._name, id, cr)
#        return True

    @api.multi
    def action_set_to_dirty(self):
        self.write({'state': 'dirty'})
#        wf_service = netsvc.LocalService('workflow')
#        for id in self.ids:
#            wf_service.trg_create(self._name)
        return True

    @api.multi
    def room_cancel(self):
        self.write({'state':'cancel'})
        return True


    @api.multi
    def room_done(self):
        self.write({'state':'done'})
        return True

    @api.multi    
    def room_inspect(self):
        self.write({'state':'inspect'})
        return True

    @api.multi    
    def room_clean(self):
        self.write({'state':'clean'})
        return True


class hotel_housekeeping_activities(models.Model):
    _name = "hotel.housekeeping.activities"
    _description = "Housekeeping Activities "

    a_list = fields.Many2one(comodel_name='hotel.housekeeping',string='Reservation')
    room_id = fields.Many2one(comodel_name='hotel.room',string='Room No')
    today_date = fields.Date('Today Date')
    activity_name = fields.Many2one(comodel_name='hotel.activity',string='Housekeeping Activity')
    housekeeper = fields.Many2one(comodel_name='res.users',string='Housekeeper' ,required=True)
    clean_start_time = fields.Datetime('Clean Start Time', required=True)
    clean_end_time = fields.Datetime('Clean End Time', required=True)
    dirty = fields.Boolean('Dirty', help='Checked if the housekeeping activity results as Dirty.')
    clean = fields.Boolean('Clean', help='Checked if the housekeeping activity results as Clean.')

#    def default_get(self, cr, uid, fields, context=None):
#        """ To get default values for the object.
#        @param self: The object pointer.
#        @param cr: A database cursor
#        @param uid: ID of the user currently logged in
#        @param fields: List of fields for which we want default values 
#        @param context: A standard dictionary 
#        @return: A dictionary which of fields with values. 
#        """ 
#        if context is None:
#            context = {}
#        res = super(hotel_housekeeping_activities, self).default_get(cr, uid, fields, context=context)
#        if context.get('room_id', False):
#            res.update({'room_id':context['room_id']})
#        if context.get('today_date', False):
#            res.update({'today_date':context['today_date']})
#        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
