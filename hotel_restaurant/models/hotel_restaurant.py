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
from openerp import netsvc
from openerp.exceptions import except_orm, Warning, RedirectWarning

class product_category(models.Model):
    _inherit = "product.category"
    
    ismenutype = fields.Boolean('Is Menu Type')

class product_product(models.Model):
    _inherit = "product.product"
 
    ismenucard = fields.Boolean('Is Menucard')

class hotel_menucard_type(models.Model):
    _name = 'hotel.menucard.type'
    _description = 'Amenities Type'
    _inherits = {'product.category':'menu_id'}
    
    menu_id = fields.Many2one(comodel_name='product.category',string='Category',required=True, ondelete='cascade')
    
    _defaults = {
        'ismenutype': 1,
    }

class hotel_menucard(models.Model):
    _name = 'hotel.menucard'
    _inherits = {'product.product':'product_id'}
    _description = 'Hotel Menucard'

    product_id = fields.Many2one(comodel_name='product.product',string='Product',required=True, ondelete='cascade')
    image = fields.Binary("Image", help="This field holds the image used as image for the product, limited to 1024x1024px.")
    
    _defaults = {
        'ismenucard': 1,
    }

class hotel_restaurant_tables(models.Model):
    _name = "hotel.restaurant.tables"
    _description = "Includes Hotel Restaurant Table"

    name = fields.Char('Table Number', size=64, required=True)
    capacity = fields.Integer('Capacity')

class hotel_restaurant_reservation(models.Model):

#when table is booked and create order button is clicked then this method is called and order is created.
#you can see this created order in "Orders"
 
    @api.multi
    def create_order(self):
        proxy = self.env['hotel.reservation.order']
        for record in self:
            table_ids = [tableno.id for tableno in record.tableno]
            values = {
                'reservationno':record.reservation_id,
                'date1':record.start_date,
                'table_no':[(6, 0, table_ids)],
            }
            proxy.create(values)
        return True

#completed in v8
#    def create_order(self, cr, uid, ids, context=None):
#        proxy = self.pool.get('hotel.reservation.order')
#        for record in self.browse(cr, uid, ids):
#            table_ids = [tableno.id for tableno in record.tableno]
#            values = {
#                'reservationno':record.reservation_id,
#                'date1':record.start_date,
#                'table_no':[(6, 0, table_ids)],
#            }
#            proxy.create(cr, uid, values, context=context)
#        return True

#When Customer name is changed respective adress will display in Adress field
    @api.onchange('cname')
    def onchange_partner_id(self):
        if not self.cname:
            self.partner_address_id = False
        else:
            addr = self.cname.address_get(['default'])
            self.partner_address_id = addr['default']

    @api.multi
    def action_set_to_draft(self):
        self.write({'state': 'draft'})
        wf_service = netsvc.LocalService('workflow')
        for id in self.ids:
            wf_service.trg_create(self._uid, self._name, self.id, self._cr)
        return True        

#when CONFIRM BUTTON is clicked this method is called (table booking)...!!
    @api.multi
    def table_reserved(self):
        for reservation in self:
            self._cr.execute("select count(*) from hotel_restaurant_reservation as hrr " \
                       "inner join reservation_table as rt on rt.reservation_table_id = hrr.id " \
                       "where (start_date,end_date)overlaps( timestamp %s , timestamp %s ) " \
                       "and hrr.id<> %s " \
                       "and rt.name in (select rt.name from hotel_restaurant_reservation as hrr " \
                       "inner join reservation_table as rt on rt.reservation_table_id = hrr.id " \
                       "where hrr.id= %s) " \
                        , (self.start_date, self.end_date, reservation.id, reservation.id))
            res = self._cr.fetchone()
            roomcount = res and res[0] or 0.0
            if roomcount:
                raise except_orm(_('Warning'), _('You tried to confirm reservation with table those already reserved in this reservation period'))
            else:
                self.write({'state':'confirm'})
            return True

#completed in v8
#    def table_reserved(self, cr, uid, ids, *args):
#        for reservation in self.browse(cr, uid, ids):
#            cr.execute("select count(*) from hotel_restaurant_reservation as hrr " \
#                       "inner join reservation_table as rt on rt.reservation_table_id = hrr.id " \
#                       "where (start_date,end_date)overlaps( timestamp %s , timestamp %s ) " \
#                       "and hrr.id<> %s " \
#                       "and rt.name in (select rt.name from hotel_restaurant_reservation as hrr " \
#                       "inner join reservation_table as rt on rt.reservation_table_id = hrr.id " \
#                       "where hrr.id= %s) " \
#                        , (reservation.start_date, reservation.end_date, reservation.id, reservation.id))
#            res = cr.fetchone()
#            roomcount = res and res[0] or 0.0
#            if roomcount:
#                raise except_orm(_('Warning'), _('You tried to confirm reservation with table those already reserved in this reservation period'))
#            else:
#                self.write(cr, uid, ids, {'state':'confirm'})
#            return True

    @api.multi
    def table_cancel(self):
        self.write({'state':'cancel'})
        return True

    @api.multi
    def table_done(self):
        self.write({'state':'done'})
        return True

    _name = "hotel.restaurant.reservation"
    _description = "Includes Hotel Restaurant Reservation"
                                                                                
    reservation_id = fields.Char('Reservation No', size=64, required=True)#,default=lambda obj: obj.env['ir.sequence'].get('hotel.restaurant.reservation'))
    room_no = fields.Many2one(comodel_name='hotel.room',string='Room No',size=64)
    start_date = fields.Datetime('Start Time', required=True)
    end_date = fields.Datetime('End Time', required=True)
    cname = fields.Many2one(comodel_name='res.partner',string='Customer Name',size=64, required=True)
    partner_address_id = fields.Many2one(comodel_name='res.partner',string='Address')
    tableno = fields.Many2many(comodel_name='hotel.restaurant.tables',relation='reservation_table',column1='reservation_table_id',column2='name',string='Table Number',help="Table reservation detail. ")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], 'state', select=True, required=True, readonly=True,default=lambda * a: 'draft')

#    _defaults = {
#        'reservation_id':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hotel.restaurant.reservation'),
#    }

    @api.constrains('start_date')
    def check_dates(self):    
          if self.start_date >= self.end_date:
                raise except_orm(_('error!'),_('Start Date Should be less than the End Date'))

# completed in v8
#    _sql_constraints = [
#        ('check_dates', 'CHECK (start_date<=end_date)', 'Start Date Should be less than the End Date!'),
#    ]

class hotel_restaurant_kitchen_order_tickets(models.Model):
    _name = "hotel.restaurant.kitchen.order.tickets"
    _description = "Includes Hotel Restaurant Order"

    orderno = fields.Char('Order Number', size=64, readonly=True)
    resno = fields.Char('Reservation Number', size=64)
    kot_date = fields.Datetime('Date')
    room_no = fields.Char('Room No', size=64, readonly=True)
    w_name = fields.Char('Waiter Name', size=64, readonly=True)
    tableno = fields.Many2many(comodel_name='hotel.restaurant.tables',relation='temp_table3',column1='table_no',column2='name',string='Table Number' ,size=64, help="Table reservation detail.")
    kot_list = fields.One2many(comodel_name='hotel.restaurant.order.list',inverse_name='kot_order_list',string='Order List' ,help="Kitchen order list")


class hotel_restaurant_order(models.Model):

#    @api.multi
#    def _sub_total(self):
#        res = {}
#        for sale in self:
#            res[sale.id] = sum(line.price_subtotal for line in sale.order_list)
#            print "res= sub==========",res
#        return res

#completed but how can i test...isse--->order listt...
#    def _sub_total(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        for sale in self.browse(cr, uid, ids, context=context):
#            res[sale.id] = sum(line.price_subtotal for line in sale.order_list)
#        return res

#    @api.multi  
#    def _total(self):
#        res = {}
#        for line in self:
#            res[line.id] = line.amount_subtotal + (line.amount_subtotal * line.tax) / 100
#            print "res=total==========",res
#        return res  
    
#completed but how can i test...isse--->order listt...
#    def _total(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = line.amount_subtotal + (line.amount_subtotal * line.tax) / 100
#        return res

#    def generate_kot(self, cr, uid, ids, part):
#        order_tickets_obj = self.pool.get('hotel.restaurant.kitchen.order.tickets')
#        restaurant_order_list_obj = self.pool.get('hotel.restaurant.order.list')
#        for order in self.browse(cr, uid, ids):
#            table_ids = [x.id for x in order.table_no]
#            kot_data = order_tickets_obj.create(cr, uid, {
#                'orderno':order.order_no,
#                'kot_date':order.o_date,
#                'room_no':order.room_no.name,
#                'w_name':order.waiter_name.name,
#                'tableno':[(6, 0, table_ids)],
#            })
#            for order_line in order.order_list:
#                o_line = {
#                         'kot_order_list':kot_data,
#                         'name':order_line.name.id,
#                         'item_qty':order_line.item_qty,
#                }
#                restaurant_order_list_obj.create(cr, uid, o_line)
#        return True

    _name = "hotel.restaurant.order"
    _description = "Includes Hotel Restaurant Order"

    order_no = fields.Char('Order Number', size=64, required=True)
    o_date = fields.Datetime('Date', required=True)
    room_no = fields.Many2one(comodel_name='hotel.room',string='Room No')
    waiter_name = fields.Many2one(comodel_name='res.partner',string='Waiter Name')
    table_no = fields.Many2many(comodel_name='hotel.restaurant.tables',relation='temp_table2',column1='table_no',column2='name',string='Table Number')
#    order_list = fields.One2many(comodel_name='hotel.restaurant.order.list',reverse_name = 'o_list',string='Order List')
    tax = fields.Float('Tax (%) ')
#    amount_subtotal = fields.Float(compute=_sub_total, method=True, string='Subtotal')
#    amount_total = fields.Float(compute=_total, method=True, string='Total')

    _defaults = {
     'order_no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hotel.restaurant.order'),
     }

class hotel_reservation_order(models.Model):

#    def _sub_total(self, cr, uid, ids, field_name, arg, context):
#        res = {}
#        for sale in self.browse(cr, uid, ids):
#            res[sale.id] = 0.00
#            for line in sale.order_list:
#                res[sale.id] += line.price_subtotal
#        return res

#    @api.multi
#    @api.depends('order_list')
#    def _sub_total(self):
#       res = {}
#       for sale in self:
#            res[sale.id] = 0.00
#            for line in sale.order_list:
#                res[sale.id] += line.price_subtotal
#       return res



#    @api.multi
#    @api.depends('order_list')
#    def _sub_total(self):
#       print "hiiiiiiiiiiiiiii----------------------------" 
#       self.sale.id = 0.00
#       self.amount_subtotal=self.sale.id + self.order_list.price_subtotal
#       print "-------",self.amount_subtotal

#    @api.multi
#    @api.depends('amount_subtotal')
#    def _total(self):
#        print "hiiii1"
#        res = {}
#        for line in self:
#            res[line.id] = line.amount_subtotal + (line.amount_subtotal * line.tax) / 100.0
#        return res    


#    def _total(self, cr, uid, ids, field_name, arg, context):
#        res = {}
#        for line in self.browse(cr, uid, ids):
#            res[line.id] = line.amount_subtotal + (line.amount_subtotal * line.tax) / 100.0
#        return res

#    @api.multi
#    def reservation_generate_kot(self):
#        order_tickets_obj = self.env['hotel.restaurant.kitchen.order.tickets']
#        rest_order_list_obj = self.env['hotel.restaurant.order.list']
#        for order in self:
#            table_ids = [x.id for x in order.table_no]
#            kot_data = order_tickets_obj.create({
#                'orderno':order.order_number,
#                'resno':order.reservationno,
#                'kot_date':order.date1,
#                'w_name':order.waitername.name,
#                'tableno':[(6, 0, table_ids)],
#            })
#            print "------------",kot_data
#            for order_line in order.order_list:
#                o_line = {
#                    'kot_order_list':kot_data,
#                    'name':order_line.name.id,
#                    'item_qty':order_line.item_qty,
#                }
#                print "o line---------",o_line
#                rest_order_list_obj.create(o_line)
#            return True

#    def reservation_generate_kot(self, cr, uid, ids, part):
#        order_tickets_obj = self.pool.get('hotel.restaurant.kitchen.order.tickets')
#        rest_order_list_obj = self.pool.get('hotel.restaurant.order.list')
#        for order in self.browse(cr, uid, ids):
#            table_ids = [x.id for x in order.table_no]
#            kot_data = order_tickets_obj.create(cr, uid, {
#                'orderno':order.order_number,
#                'resno':order.reservationno,
#                'kot_date':order.date1,
#                'w_name':order.waitername.name,
#                'tableno':[(6, 0, table_ids)],
#            })
#            for order_line in order.order_list:
#                o_line = {
#                    'kot_order_list':kot_data,
#                    'name':order_line.name.id,
#                    'item_qty':order_line.item_qty,
#                }
#                rest_order_list_obj.create(cr, uid, o_line)
#            return True

    _name = "hotel.reservation.order"
    _description = "Reservation Order"

    order_number = fields.Char('Order No', size=64,default=lambda obj: obj.env['ir.sequence'].get('hotel.reservation.order'))
    reservationno = fields.Char('Reservation No', size=64)
    date1 = fields.Datetime('Date', required=True)
    waitername = fields.Many2one(comodel_name='res.partner',string='Waiter Name',size=64)
    table_no = fields.Many2many(comodel_name='hotel.restaurant.tables',relation='temp_table4',column1='table_no',column2='name',string='Table Number',size=64)
    order_list = fields.One2many('hotel.restaurant.order.list','o_l','Order List')
    tax = fields.Float('Tax (%) ', size=64)
#    amount_subtotal = fields.Float(compute='_sub_total', method=True, string='Subtotal')
#    amount_total = fields.Float(compute='_total', method=True, string='Total')

#    _defaults = {
#        'order_number':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hotel.reservation.order'),
#    }

class hotel_restaurant_order_list(models.Model):

    @api.one
    def _sub_total(self):
        self.price_subtotal=self.item_rate * int(self.item_qty)


    #item rate will display on change of item name     
    @api.onchange('name')
    def on_change_item_name(self):   
        
        temp = self.env['hotel.menucard'].browse(self.name.id)
        if temp.name:
            self.item_rate=temp.list_price     

#completed in v8
#    def on_change_item_name(self, cr, uid, ids, name, context=None):
#        if not name:
#            return {'value':{}}
#        temp = self.pool.get('hotel.menucard').browse(cr, uid, name, context)
#        return {'value':{'item_rate':temp.list_price}}

    _name = "hotel.restaurant.order.list"
    _description = "Includes Hotel Restaurant Order"

    o_list = fields.Many2one('hotel.restaurant.order','Restaurant Order')
    o_l = fields.Many2one('hotel.reservation.order','Reservation Order')
    kot_order_list = fields.Many2one('hotel.restaurant.kitchen.order.tickets','Kitchen Order Tickets')
    name = fields.Many2one(comodel_name='hotel.menucard',string='Item Name',required=True)
    item_qty = fields.Char('Qty', size=64, required=True)
    item_rate = fields.Float('Rate', size=64)
    price_subtotal = fields.Integer(compute='_sub_total', method=True, string='Subtotal')

## vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
