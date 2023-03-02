from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime
from dateutil import relativedelta
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)

class contract(models.Model):
    _name = 'real.estate.contract'
    _rec_name = 'contract_partner_name' # changes the name above edit and create button
    _description = 'Real estate contract'
    
    name=fields.Char('Contract No.',default='/')
    dealer_id = fields.Many2one('res.partner', string='Customer')
    dealer_name = fields.Char('Name', related='dealer_id.name', force_save=True)
    dealer_street = fields.Char('Street', related='dealer_id.street')
    dealer_phone = fields.Char('Phone', related='dealer_id.phone')
    dealer_mobile = fields.Char('Mobile', related='dealer_id.mobile')
    dealer_email = fields.Char('Email', related='dealer_id.email')



    contract_partner_id = fields.Many2one('res.partner', string='Customer')
    contract_partner_image_1920 = fields.Image(related='contract_partner_id.image_1920',store=True)
    contract_partner_name = fields.Char('Name', related='contract_partner_id.name', force_save=True)
    contract_partner_street = fields.Char('Street', related='contract_partner_id.street')
    contract_partner_phone = fields.Char('Phone', related='contract_partner_id.phone')
    contract_partner_mobile = fields.Char('Mobile', related='contract_partner_id.mobile')
    contract_partner_cnic = fields.Char('CNIC', related='contract_partner_id.cnic_no')
    contract_type = fields.Selection([('buy', 'Buy Back'), ('sell','Sell')])
    # contract_type = fields.Selection([('sell','Sell')])

    kin_name = fields.Char(string='Nominee')
    kine_relationship = fields.Char(string='Relation',)
    kin_cnic = fields.Char('Nominee CNIC')
    kin_address = fields.Char('Nominee Address', )
    kin_mobile = fields.Char(string='Nominee Mobile')
    payment_plan_type = fields.Selection([('lump_sum', 'Lump sum'),
                                          ('install_down', 'Installment + Down Payment'),
                                          ('install', 'Installment'),])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('active', 'Active'),
        ('inactive', 'Closed')
    ], string='State', readonly=True, default='draft')
    # installment_id = fields.One2many('real.estate.installment', 'contract_id', 'Installment plan', copy=True)
    frequency = fields.Selection([('monthly', 'Monthly'), ('quarterly', 'Quarterly')], string='Frequency')
    lump_sum_amount = fields.Float(string='Lump sum amount')
    down_payment = fields.Float('Down Payment', store=True)
    down_payment_amt = fields.Float(store=True)
    project_id = fields.Many2one(
        'real.estate.project', 'Project')
    block_id = fields.Many2one(
        'real.estate.block', 'Block',domain="[('state','=','available'),('project_id','=',project_id)]")
    plot_id = fields.Many2one(
        'real.estate.plot', 'Plot',domain="[('state','=','available'),('block_id','=',block_id)]")
    property_value = fields.Float('Property Value', compute='cal_property_value',store=True)
    property_name = fields.Char('Property Name', related='plot_id.name')
    installment_id = fields.One2many('real.estate.installment', 'contract_id')
    first_installment_date = fields.Date(string='First Installment due date')
    down_payment_date = fields.Date(string='Down payment due date')
    total_payment_date = fields.Date(string='Payment due date')
    total_installments = fields.Integer('Total installments')
    installment_product_id = fields.Many2one('product.product', string='Installment Product', readonly=False)
    token_money_product_id = fields.Many2one('product.product', string='Token money Product', readonly=False)
    down_payment_product_id = fields.Many2one('product.product', string='Down payment Product', readonly=False)
    buyback_product_id = fields.Many2one('product.product', string='Buyback Product', readonly=False)
    generate_installment_plan = fields.Boolean(default=False)
    generate_possession_amount = fields.Boolean(default=False)
    generate_demarcation_amount = fields.Boolean(default=False)
    buy_back_type = fields.Selection([('payback_full', 'Full Payment'),('payback_installments', 'Installments')])
    # buy_back_type = fields.Selection([('payback_full', 'Full Payment'), ('payback_installments', 'Installments'),
    #                                   ('payback_property_adjust','Adjust payment in other properties'), ('payback_payment_and_property','Partial payment and partial adjustment in property')])
    down_payment_type = fields.Selection([('lumpsum', 'Lumpsum'),('percentage', 'Percentage')])
    discount_hx = fields.Float('discount')
    amt_after_disc = fields.Float('Amount after discount',store=True, compute='_compute_amt_after_disc')
    buy_back_bill_due_date = fields.Date()
    contract_active = fields.Boolean(default=True)
    profit_on_buyback = fields.Float('Profit')
    buy_back_value = fields.Float()
    total_installments_buyback = fields.Integer()
    profit_on_buyback_product = fields.Many2one('product.product', string='Buyback Product', readonly=False)
    adjustment_plot_id = fields.Many2one(
        'real.estate.plot', 'Plot for adjustment ')
    check_buyback_selection = fields.Boolean()
    check_readonly = fields.Boolean()
    effective_date = fields.Date(string='Effective date')
    total_without_down_payment = fields.Float(string='Installments Balance')
    resale_value = fields.Float()
    contract_date = fields.Date(default=fields.Date.context_today)
    
    is_west_open=fields.Boolean('West Open', related='plot_id.is_west_open')
    west_open_charges=fields.Float('West Open Charges (%)',default=5)
    is_corner=fields.Boolean('Corner', related='plot_id.is_corner')
    corner_charges=fields.Float('Corner Charges (%)',default=10)
    amenity_facing=fields.Many2many('real.estate.amenity',string='Amenity Facing', related='plot_id.amenity_facing')
    amenity_facing_charges=fields.Float('Amenity Facing Charges (%)',default=5)
    road_facing=fields.Many2one('real.estate.road.type', related='plot_id.road_facing')
    road_facing_charges=fields.Float('Road Facing Charges (%)',default=5)
    total_value = fields.Float('Total Property Value', compute='cal_total_value',store=True)
    invoice_count = fields.Integer(compute='_compute_invoice_count', string="Invoices")
    possession_amount=fields.Float('Possession Amount')
    possession_amount_date=fields.Date('Possession Due Date')
    demarcation_amount=fields.Float('Demarcation Amount')
    demarcation_amount_date=fields.Date('Demarcation Due Date')
    half_yearly_amount=fields.Float('Half Yearly Amount')
    total_half_year=fields.Integer('Total Half Year')
    total_half_yearly_amount=fields.Float('Total Half Yearly Amount',compute='cal_half_yearly_amount',store=True)
    possission_product_id = fields.Many2one('product.product', string='Possession Product')
    demarcation_product_id = fields.Many2one('product.product', string='Demarcation Product')
    half_yearly_product_id = fields.Many2one('product.product', string='Half Yearly Product')
    total_paid=fields.Float('Total Paid Amount',compute='cal_paid_amount')
    balance_amount=fields.Float('Balance Amount',compute='cal_balance_amount')
    _sql_constraints = [
    ('value_discipline_name_unique', 'unique (name)',
        'Discipline name must be unique. !')
    ]
    
    @api.depends('installment_id')
    def cal_paid_amount(self):
        for each in self:
            paid_amount=0
            installment_obj=self.env['real.estate.installment'].search([('contract_id','=',each.id),('move_id.payment_state','=','paid')])
            for x in installment_obj:
                paid_amount+=x.amount
            each.total_paid=paid_amount
    
    @api.depends('total_paid')
    def cal_balance_amount(self):
        for each in self:
            each.balance_amount=each.property_value-each.total_paid
            
    @api.depends('plot_id')
    def cal_property_value(self):
        for each in self:
            if each.plot_id:
                each.property_value=each.plot_id.property_value
            else:
                each.property_value=0
    @api.depends('half_yearly_amount','total_half_year')
    def cal_half_yearly_amount(self):
        for each in self:
            if each.half_yearly_amount and each.total_half_year:
                each.total_half_yearly_amount=each.half_yearly_amount*each.total_half_year
            else:
                each.total_half_yearly_amount=0
            
    def _compute_invoice_count(self):
        for each in self:
            each.invoice_count=0
            query=self.env.cr.execute("""Select move_id from real_estate_installment where contract_id="""+str(each.id))
            result=self.env.cr.fetchall()
            invocie_list=[each[0] for each in result]
            move_obj=self.env['account.move'].search([('id','in',invocie_list)])
            each.invoice_count=len(move_obj.ids)
    def action_view_invoices(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        query=self.env.cr.execute("""Select move_id from real_estate_installment where contract_id="""+str(self.id))
        result=self.env.cr.fetchall()
        move_list=[each[0] for each in result]
        action['domain'] = [('id','in',move_list)]
        return action
    
    @api.depends('property_value','west_open_charges','corner_charges','amenity_facing_charges','road_facing_charges')
    def cal_total_value(self):
        for each in self:
            west_open_charges=0
            corner_charges=0
            amenity_facing_charges=0
            road_facing_charges=0
            if each.west_open_charges and each.property_value:
                west_open_charges=each.property_value*(each.west_open_charges/100)
            if each.corner_charges and each.property_value:
                corner_charges=each.property_value*(each.corner_charges/100)
            if each.amenity_facing_charges and each.property_value:
                amenity_facing_charges=each.property_value*(each.amenity_facing_charges/100)
            if each.road_facing_charges and each.property_value:
                road_facing_charges=each.property_value*(each.road_facing_charges/100)
            each.total_value=each.property_value+west_open_charges+corner_charges+amenity_facing_charges+road_facing_charges
    @api.constrains('total_installments')
    def _check_total_installments_value(self):
        if self.total_installments < 1 and self.contract_type=='sell':
            raise UserError(
                    'Total Installments should be greater than 0')
    def unlink(self):
        for c in self:
            if c.state in ('confirm', 'active'):
                raise UserError(
                    'You cannot delete a confirmed or active contract')
        return super(contract, self).unlink()

    def action_balance_installments(self):
        installments = self.env['real.estate.installment'].search(args=[('contract_id', '=', self.id)])
        temp = 0
        for i in installments:
            temp = temp + i.amount
        if temp != self.amt_after_disc:
            raise UserError('Sum of installments must be equal')

    def action_confirm(self):
        contract_sequence = self.env['ir.sequence'].next_by_code('real_estate_contract_sequence')
        self.write({'state':'confirm',
                    'name':str(self.project_id.code)+"-"+str(contract_sequence)})
        self.plot_id.write({'state':'sold'})
        self.block_id.cal_block_state(self.block_id)

    def action_active(self):
        if self.generate_installment_plan is False:
            raise UserError('Generate installment plan before confirming contract')
        else:
            self.state = 'active'

    def action_inactive(self):
        return {
            'name': _("Select Property Status"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'select.property.status',
            'view_id': self.env.ref('Property management.select_property_status_view_form').id,
            'target': 'new',
            'context': {
                'default_plot_id': self.plot_id.id,
                'default_contract_id': self.id,
            }}
    
    @api.depends('total_value','down_payment','resale_value','discount_hx','possession_amount','demarcation_amount','total_half_yearly_amount')
    def _compute_amt_after_disc(self):
        for line in self:
            line.amt_after_disc = line.total_value - line.discount_hx
            if line.discount_hx:
                line.amt_after_disc = line.total_value - line.discount_hx
            else:
                line.amt_after_disc = line.total_value
            if line.down_payment !=0:
                if line.resale_value > 0:
                    line.total_without_down_payment = line.amt_after_disc - line.down_payment + line.resale_value
                else:
                    line.total_without_down_payment = line.amt_after_disc - line.down_payment
            if line.possession_amount:
                line.total_without_down_payment = line.total_without_down_payment - line.possession_amount
            if line.demarcation_amount:
                line.total_without_down_payment = line.total_without_down_payment - line.demarcation_amount
            if line.total_half_yearly_amount:
                line.total_without_down_payment=line.total_without_down_payment-line.total_half_yearly_amount

    @api.onchange('contract_type')
    def onchange_contract_type(self):
        if self.contract_type == 'buy':
            self.check_buyback_selection = True
            results = self.env['real.estate.plot'].search([('status', '=', 'booked')])
            select_contract_type = True
            property_list = []
            for property in results:
                property_list.append(property.id)
            res = {}
            res['domain'] = {'plot_id': [('id', 'in', property_list)]}
            return res
        if self.contract_type == 'sell':
            self.check_buyback_selection = False

#     @api.onchange('property_value')
#     def onchange_property_value(self):
#         self.amt_after_disc = self.property_value - self.discount_hx

    @api.onchange('buy_back_type')
    def onchange_buy_back_type(self):
        if self.buy_back_type == 'payback_property_adjust':
            for rec in self:
                return {'domain': {'adjustment_plot_id': [('owned_by', '=', rec.contract_partner_id.id),
                                                              ('id', '!=', rec.plot_id.id)]}}
        if self.buy_back_type == 'payback_payment_and_property':
            for rec in self:
                return {'domain': {'adjustment_plot_id': [('owned_by', '=', rec.contract_partner_id.id),
                                                              ('id', '!=', rec.plot_id.id)]}}


        # if self.contract_type is not 'sell' or 'buy':
        #     raise ValidationError('Select contract type')


    # Will be used project dropdown is required

    # @api.onchange('project_id')
    # def onchange_project(self):
    #     for rec in self:
    #         return {'domain': {'building_id': [('real_estate_project', '=', rec.project_id.id)]}}

    @api.onchange('project_id')
    def onchange_project(self):
        for rec in self:
            return {'domain': {'block_id': [('project_id', '=', rec.project_id.id)]}}

    @api.onchange('block_id')
    def onchange_block(self):
        for rec in self:
            if self.contract_type == 'sell':
                return {'domain': {'plot_id': [('block_id', '=', rec.block_id.id),('state','=','available')]}}

    @api.onchange('plot_id')
    def onchange_plot(self):
        if self.contract_type == 'buy':
            self.check_buyback_selection = False
            self.check_readonly = True
            for line in self:
                line.plot_id = line.plot_id.id
                line.block_id = line.plot_id.block_id.id
                line.project_id = line.plot_id.block_id.project_id.id


    @api.onchange('kin_cnic')
    def add_validation(self):
        if self.kin_cnic:
            if len(self.kin_cnic) < 13:
                raise ValidationError('Invalid CNIC \n Enter 13 digit CNIC number')

    @api.onchange('down_payment_amt')
    def generate_down_payment(self):
        if self.down_payment_type == 'lumpsum':
            if self.down_payment_amt <= self.amt_after_disc:
                self.down_payment = self.down_payment_amt
            elif self.down_payment_amt < 0:
                raise ValidationError('Down payment is less than 0')
            else:
                raise ValidationError('Down payment is greater than Property Value')

        if self.down_payment_type == 'percentage':
            if self.down_payment_amt > 100:
                raise ValidationError('Down payment  percentage is greater than 100')
            elif self.down_payment_amt < 0:
                raise ValidationError('Down payment  percentage is less than 0')
            else:
                down_payment = (self.amt_after_disc * self.down_payment_amt) / 100
                self.down_payment = down_payment
        self.total_without_down_payment = self.amt_after_disc - self.down_payment
        if self.resale_value >0:
            self.total_without_down_payment = self.total_without_down_payment + self.resale_value

    @api.onchange('discount_hx')
    def generate_amt_after_discount(self):
        self._compute_amt_after_disc()
    
    def generate_possession_charges(self):
        if self.possession_amount_date and self.possession_amount:
            vals = {
                   'installment_no': 0,
                   'amount': self.possession_amount,
                   'due_date': self.possession_amount_date,
                   'frequency': 'One time',
                   'contract_id': self.id,
                   'product_id': self.possission_product_id.id,
                   'plot_id': self.plot_id.id,
            
               }
            try:
                self.installment_id.sudo().create(vals)
                self.write({'generate_possession_amount':True})
            except AccessError:
                _logger.warning("Access error")
        else:
            raise ValidationError('Possession amount and due date should not be empty.')
    def generate_demarcation_charges(self):
        if self.demarcation_amount_date and self.demarcation_amount:
            vals = {
                   'installment_no': 0,
                   'amount': self.demarcation_amount,
                   'due_date': self.demarcation_amount_date,
                   'frequency': 'One time',
                   'contract_id': self.id,
                   'product_id': self.demarcation_product_id.id,
                   'plot_id': self.plot_id.id,
            
               }
            try:
                self.installment_id.sudo().create(vals)
                self.write({'generate_demarcation_amount':True})
            except AccessError:
                _logger.warning("Access error")
        else:
            raise ValidationError('Demarcation amount and due date should not be empty.')
    def populate_installments(self):
        if not self.plot_id:
            raise UserError('Select property first.')
        if self.resale_value > 0:
            self.amt_after_disc = self.amt_after_disc + self.resale_value
        self.plot_id.owned_by = self.contract_partner_id.id
        if self.payment_plan_type == 'lump_sum':
            vals = {
                'installment_no': 1,
                'amount': self.amt_after_disc,
                'due_date': self.total_payment_date,
                'frequency': 'One time',
                'contract_id': self.id,
                'product_id': self.installment_product_id.id,
                'plot_id': self.plot_id.id,

            }
            try:
                self.installment_id.sudo().create(vals)
            except AccessError:
                _logger.warning("Access error")

        if self.payment_plan_type == 'install_down':
            amount_residual = self.total_without_down_payment
            single_installment = (amount_residual / self.total_installments)
            single_installment = round(single_installment,2)
            next_installment = self.first_installment_date
            var = self.total_installments-1
            last_installment = (amount_residual - (single_installment * var))
            # self.total_without_down_payment = amount_residual

            # Down payment installment generation
            down_vals = {
                'amount': self.down_payment,
                'due_date': self.down_payment_date,
                'frequency': 'one time',
                'contract_id': self.id,
                'product_id': self.down_payment_product_id.id,
                'plot_id': self.plot_id.id,
            }
            self.installment_id.sudo().create(down_vals)

            # Installments generation
            if self.frequency == 'monthly':
                for i in range(self.total_installments++self.total_half_year):
                    if (i+1) % 6==0:
                        vals = {
                        'installment_no': i+1,
                        'amount': self.half_yearly_amount,
                        'due_date': next_installment,
                        'frequency': 'half yearly',
                        'contract_id': self.id,
                        'product_id': self.half_yearly_product_id.id,
                        'plot_id': self.plot_id.id,
                        }
                    else:
                        vals = {
                            'installment_no': i+1,
                            'amount': single_installment,
                            'due_date': next_installment,
                            'frequency': self.frequency,
                            'contract_id': self.id,
                            'product_id': self.installment_product_id.id,
                            'plot_id': self.plot_id.id,
                        }
                    next_installment = next_installment + relativedelta.relativedelta(months=1)
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
                # next_installment = next_installment + relativedelta.relativedelta(months=1)
#                 last_installment_vals = {
#                     'installment_no': self.total_installments,
#                     'amount': last_installment,
#                     'due_date': next_installment,
#                     'frequency': self.frequency,
#                     'contract_id': self.id,
#                     'product_id': self.installment_product_id.id,
#                     'plot_id': self.plot_id.id,
#                 }
#                 try:
#                     self.installment_id.sudo().create(last_installment_vals)
#                 except AccessError:
#                     _logger.warning("Access error")

            if self.frequency == 'quarterly':
                for i in range(self.total_installments-1):
                    vals = {
                        'installment_no': i+1,
                        'amount': single_installment,
                        'due_date': next_installment,
                        'frequency': self.frequency,
                        'contract_id': self.id,
                        'product_id': self.installment_product_id.id,
                        'plot_id': self.plot_id.id,
                    }
                    next_installment = next_installment + relativedelta.relativedelta(months=3)
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
                # next_installment = next_installment + relativedelta.relativedelta(months=3)
#                 vals = {
#                     'installment_no': self.total_installments,
#                     'amount': last_installment,
#                     'due_date': next_installment,
#                     'frequency': self.frequency,
#                     'contract_id': self.id,
#                     'product_id': self.installment_product_id.id,
#                     'plot_id': self.plot_id.id,
#                 }
#                 try:
#                     self.installment_id.sudo().create(vals)
#                 except AccessError:
#                     _logger.warning("Access error")

        self.plot_id.update({
            'state': 'booked',
        })
        self.generate_installment_plan = True

        if self.payment_plan_type == 'install':
            single_installment = self.amt_after_disc / self.total_installments
            single_installment = round(single_installment,2)
            next_installment = self.first_installment_date
            var = self.total_installments - 1
            last_installment = (self.amt_after_disc - (single_installment * var))
            if self.frequency == 'monthly':
                for i in range(self.total_installments-1):
                    vals = {
                        'installment_no': i + 1,
                        'amount': single_installment,
                        'due_date': next_installment,
                        'frequency': self.frequency,
                        'contract_id': self.id,
                        'product_id': self.installment_product_id.id,
                        'plot_id': self.plot_id.id,
                    }
                    next_installment = next_installment + relativedelta.relativedelta(months=1)
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
                # next_installment = next_installment + relativedelta.relativedelta(months=1)
#                 vals = {
#                     'installment_no': self.total_installments,
#                     'amount': last_installment,
#                     'due_date': next_installment,
#                     'frequency': self.frequency,
#                     'contract_id': self.id,
#                     'product_id': self.installment_product_id.id,
#                     'plot_id': self.plot_id.id,
#                 }
#                 try:
#                     self.installment_id.sudo().create(vals)
#                 except AccessError:
#                     _logger.warning("Access error")
            if self.frequency == 'quarterly':
                for i in range(self.total_installments-1):
                    # next_installment = next_installment + relativedelta.relativedelta(months=3)
                    vals = {
                        'installment_no': i + 1,
                        'amount': single_installment,
                        'due_date': next_installment,
                        'frequency': self.frequency,
                        'contract_id': self.id,
                        'product_id': self.installment_product_id.id,
                        'plot_id': self.plot_id.id,
                    }
                    next_installment = next_installment + relativedelta.relativedelta(months=3)
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
                # next_installment = next_installment + relativedelta.relativedelta(months=3)
#                 vals = {
#                     'installment_no': self.total_installments,
#                     'amount': last_installment,
#                     'due_date': next_installment,
#                     'frequency': self.frequency,
#                     'contract_id': self.id,
#                     'product_id': self.installment_product_id.id,
#                     'plot_id': self.plot_id.id,
#                 }
#                 try:
#                     self.installment_id.sudo().create(vals)
#                 except AccessError:
#                     _logger.warning("Access error")

    def Populate_plan(self):
        temp = 0
        contracts = self.env['real.estate.contract'].search(
            [('plot_id', '=', self.plot_id.id), ('contract_type', '=', 'sell'),('contract_active', '=', True)])
        installments = self.env['real.estate.installment'].search([('contract_id', '=', contracts.id)])
        for i in installments:
            if i.move_id.payment_state == 'paid':
                temp = temp + i.move_id.amount_total
            if i.move_id.payment_state == 'partial':
                partial_payment = i.move_id.amount_total - i.move_id.amount_residual
                temp = temp + partial_payment
        self.buy_back_value = temp
        if self.buy_back_value > 0:
            if self.buy_back_type == 'payback_full':
                vals = {
                    'installment_no': 1,
                    'amount': self.buy_back_value,
                    'due_date': self.buy_back_bill_due_date,
                    'frequency': 'one-time',
                    'contract_id': self.id,
                    'receipt_type': 'bill',
                    'product_id': self.buyback_product_id.id,
                    'profit_on_buyback': self.profit_on_buyback,
                    'plot_id': self.plot_id.id,
                }
                try:
                    self.installment_id.sudo().create(vals)
                except AccessError:
                    _logger.warning("Access error")
            if self.buy_back_type == 'payback_installments':
                single_installment = self.buy_back_value / self.total_installments_buyback
                single_installment = round(single_installment, 2)
                single_profit_installment = self.profit_on_buyback / self.total_installments_buyback
                single_profit_installment = round(single_profit_installment, 2)
                # next_installment = self.first_installment_date
                # if self.frequency == 'monthly':
                for i in range(self.total_installments_buyback):
                    # next_installment = next_installment + relativedelta.relativedelta(months=1)
                    vals = {
                        'installment_no': i + 1,
                        'amount': single_installment,
                        # 'payment_status': 'Unpaid',
                        # 'due_date': next_installment,
                        # 'frequency': self.frequency,
                        'receipt_type': 'bill',
                        'contract_id': self.id,
                        'product_id': self.buyback_product_id.id,
                        'profit_on_buyback': single_profit_installment,
                        'plot_id': self.plot_id.id,
                    }
                    try:
                        self.installment_id.sudo().create(vals)
                    except AccessError:
                        _logger.warning("Access error")
            self.plot_id.update({
                'state': 'available',
            })
        else:
            raise UserError('Invoices not created')

    def view_invoice_hx(self):
        value = True
        if self.move_id:
            form_view = self.env.ref('account.view_move_form')
            tree_view = self.env.ref('account.view_invoice_tree')
            value = {
                'domain': str([('id', '=', self.move_id.id)]),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': self.move_id.id,
                'target': 'current',
                'nodestroy': True
            }
        else:
            _logger.warning("Access error")
        return value



class SelectPropertyStatus(models.TransientModel):
    _name = 'select.property.status'

    plot_id = fields.Many2one(
        'real.estate.plot', 'Plot', readonly=True, force_save=True)
    contract_id = fields.Many2one(
        'real.estate.contract', 'Contract', readonly=True, force_save=True)
    status = fields.Selection([('booked', 'Booked'), ('available', 'Available'),
                               ('rented', 'Rented'), ('sold', 'Sold'), ('legal_issue', 'Legal Issue')])

    def action_apply(self):
        self.plot_id.update({
                    'status': self.status,
                })
        self.contract_id.update({
            'state': 'inactive',
        })