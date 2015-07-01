from openerp import models,fields,api,_
from decimal import Decimal
import datetime
import urllib2
import time

class CurrencyExchangeRate(models.Model):

    _name = "currency.exchange"
    _description = "currency"

    name = fields.Char('Reg Number', size=24,default=lambda obj: obj.env['ir.sequence'].get('currency.exchange'),readonly=True)
    today_date = fields.Datetime('Date Ordered', required=True,default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    input_curr = fields.Many2one('res.currency', string='Input Currency',track_visibility='always')
    in_amount = fields.Float('Amount Taken', size=64 ,default = 1.0)
    out_curr = fields.Many2one('res.currency', string='Output Currency',track_visibility='always')
    out_amount = fields.Float('Subtotal', size=64)
    folionumber = fields.Many2one('hotel.folio','Folio Number')
    guest_name = fields.Many2one('res.partner',string='Guest Name')
    room_number = fields.Char(string='Room Number')
    state = fields.Selection([('draft','Draft'),('done','Done'),('cancel','Cancel')], 'State', default='draft')
    rate =  fields.Float('Rate(per unit)', size=64)
    hotel_id = fields.Many2one('stock.warehouse','Hotel Name')
    type = fields.Selection([('cash', 'Cash')], 'Type',default='cash')
    tax = fields.Selection([('2','2%'),('5','5%'),('10','10%')], 'Service Tax', default='2')
    total = fields.Float('Amount Given')

    @api.onchange('folionumber')
    def get_folionumber(self):
        if self.folionumber:
            for rec in self:
                self.guest_name = self.folionumber.partner_id.id
                self.hotel_id = self.folionumber.warehouse_id.id
                self.room_number = self.folionumber.room_lines.product_id.name

    @api.multi
    def act_cur_done(self):
        self.write({'state' : 'done'})
        return True

    @api.multi
    def act_cur_cancel(self):
        self.write({'state' : 'cancel'})
        return True

    @api.multi
    def act_cur_cancel123(self):
        self.write({'state' : 'draft'})
        return True


    @api.model
    def get_rate(self, a, b):
        try:
            url = 'http://finance.yahoo.com/d/quotes.csv?s=%s%s=X&f=l1' % (a, b)
            rate = urllib2.urlopen(url).read().rstrip()
            return Decimal(rate)
        except:
            return Decimal('-1.00')

    @api.onchange('input_curr','out_curr','in_amount')
    def mycurrency(self):
        self.out_amount = 0.0
        if self.input_curr:
            for rec in self:
                result = rec.get_rate(self.input_curr.name, self.out_curr.name)
                if self.out_curr:
                        self.rate = result or 0.0
                        self.out_amount = (float(result) * float(self.in_amount))

    @api.onchange('out_amount','tax')
    def tax_change(self):
        if self.out_amount:
            for rec in self:
                ser_tax = ((self.out_amount)*(float(self.tax)))/100 
                self.total = self.out_amount - ser_tax