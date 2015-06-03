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

from openerp import models,fields
 
AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('confirm', 'Confirm'),
    ('done', 'Done')
]

class report_hotel_restaurant_status(models.Model):
    _name = "report.hotel.restaurant.status"
    _description = "Reservation By State"
    _auto = False

    reservation_id = fields.Char('Reservation No', size=64, readonly=True)
    nbr = fields.Integer('Reservation', readonly=True)
    state = fields.Selection(AVAILABLE_STATES, 'State', size=16, readonly=True)

    def init(self,cr):
        print'restaurent init called----------------------------------'
        cr.execute("""
            create or replace view report_hotel_restaurant_status as (
                select
                    min(c.id) as id,
                    c.reservation_id,
                    c.state,
                    count(*) as nbr
                from
                    hotel_restaurant_reservation c
                group by c.state,c.reservation_id
            )""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
