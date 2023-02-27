from odoo import models, fields, api
from stdnum.exceptions import ValidationError

class Category(models.Model):
    _name='real.estate.category'
    _description='Category'
    name=fields.Char('Name',required=True)

class Amenity(models.Model):
    _name='real.estate.amenity'
    _description='Amenity'
    name=fields.Char('Name',required=True)

class RoadType(models.Model):
    _name='real.estate.road.type'
    _description='Road Type'
    name=fields.Char('Name',required=True)
# class Document(models.Model):
#     _inherit='documents.document'
#     project_id=fields.Many2one('real.estate.project','Project')
class Project(models.Model):
    _name = 'real.estate.project'
    _inherit = ['mail.thread','mail.activity.mixin', 'portal.mixin']
    _description = 'Real estate project'

    name = fields.Char(string='Project name', required=True)
    description = fields.Text()
    location = fields.Char('Location')
    city = fields.Char('City')
    type = fields.Selection([('Residential','Residential'),('Commercial','Commercial')],'Type',default='Residential',required=True)
    block_ids = fields.One2many('real.estate.block', 'project_id', 'Block')
    image = fields.Binary(string='Image')
    contract_id = fields.One2many('real.estate.contract', 'project_id','Contract',copy=True)
    total_area=fields.Char('Total Area')
    phase=fields.Char('Phase')
    code=fields.Char('Code')
#     document_ids=fields.One2many('documents.document','project_id','Documents')
#     
#     def view_document(self):
#         document_ids=self.env['documents.document'].search([('project_id','=',self.id)])
#         action = self.env.ref('documents.document_action').sudo().read()[0]
#         action['domain'] = [('id','in',document_ids.ids)]
#         action['context'] = {
#             'default_project_id':self.id,}
#         return action


class Block(models.Model):
    _name = 'real.estate.block'
    _description = 'Block'
    name = fields.Char(string='Block Name', required=True)
    total_area = fields.Char('Total Area')
    total_plots=fields.Integer('Total Plots',compute='cal_total_plots')
    project_id=fields.Many2one('real.estate.project','Project')
    plot_ids=fields.One2many('real.estate.plot','block_id','Plots')
    image = fields.Binary(string='Image')
    state=fields.Selection([('booked', 'Booked'),('available', 'Available'),('sold', 'Sold')], default='available')
    
    @api.depends('plot_ids')
    def cal_total_plots(self):
        for each in self:
            each.total_plots=len(each.plot_ids)
    
    def cal_block_state(self,block):
        plot_obj=self.env['real.estate.plot'].search([('state','=','available'),('block_id','=',block.id)])
        if plot_obj:
            block.state='available'
        else:
            block.state='sold'
            
class Plot(models.Model):
    _name = 'real.estate.plot'
    _description = 'Plot'
    _order='sequence asc'
    name = fields.Char(string='Plot No.',default='/',compute='cal_name',store=True)
    sequence = fields.Integer(string='Sequence', required=True)
    postfix=fields.Char('Postfix')
    type=fields.Selection([('Residential','Residential'),('Commercial','Commercial')],'Type',default='Residential',required=True)
    category_id=fields.Many2one('real.estate.category','Category',required=True)
    size=fields.Char('Plot Size')
    block_id=fields.Many2one('real.estate.block')
    is_west_open=fields.Boolean('West Open')
    is_corner=fields.Boolean('Corner')
    amenity_facing=fields.Many2many('real.estate.amenity',string='Amenity Facing')
    road_facing=fields.Many2one('real.estate.road.type')
    image = fields.Binary(string='Image')
    property_value = fields.Float(string='Property Value', digits='Product Price')
    currency_id = fields.Many2one('res.currency', help='The currency used to enter statement', string="Currency")
    state = fields.Selection([('booked', 'Booked'),('available', 'Available'),('sold', 'Sold')], default='available')
    contract_id = fields.One2many('real.estate.contract', 'plot_id', 'Contract', copy=True)
    owned_by = fields.Many2one('res.partner', string='Customer', readonly=True)
    _sql_constraints = [
    ('value_plot_number_uniq', 'unique (sequence,block_id,postfix)', 
        'Plot number should be unique in a block!')
    ]
    @api.depends('sequence','category_id','postfix')
    def cal_name(self):
        for each in self:
            if each.category_id and each.sequence and each.postfix:
                each.name=str(each.category_id.name)+str(each.sequence)+str(each.postfix or '')
            elif each.category_id and each.sequence:
                each.name=str(each.category_id.name)+str(each.sequence)
            else:
                each.name='/'
    
    
class GeneratePlot(models.TransientModel):
    _name='generate.plot.wizard'
    
    block_id=fields.Many2one('real.estate.block','Block')
    from_plot=fields.Integer('From')
    to_plot=fields.Integer('To')
    type=fields.Selection([('Residential','Residential'),('Commercial','Commercial')],'Type',default='Residential',required=True)
    category_id=fields.Many2one('real.estate.category','Category',required=True)
    size=fields.Char('Plot Size')
    is_west_open=fields.Boolean('West Open')
    is_corner=fields.Boolean('Corner')
    amenity_facing=fields.Many2many('real.estate.amenity',string='Amenity Facing')
    road_facing=fields.Many2one('real.estate.road.type')
    image = fields.Binary(string='Image')
    property_value = fields.Float(string='Property Value', digits='Product Price')
    currency_id = fields.Many2one('res.currency', help='The currency used to enter statement', string="Currency")
    
    def generate_plots(self):
        from_plot = self.from_plot
        for each in range(self.from_plot,self.to_plot+1):            
            vals = {'block_id':self.block_id.id,
                    'sequence':from_plot,
                    'type':self.type,
                    'category_id':self.category_id.id,
                    'size':self.size,
                    'is_west_open':self.is_west_open,
                    'is_corner':self.is_corner,
                    'amenity_facing':self.amenity_facing.ids,
                    'road_facing':self.road_facing.id,
                    'property_value':self.property_value,
                    'currency_id':self.env.user.company_id.currency_id.id,
                }
            self.env['real.estate.plot'].create(vals)
            from_plot+=1

class GenerateDuplicatePlot(models.TransientModel):
    _name='generate.duplicate.plot.wizard'
    
    block_id=fields.Many2one('real.estate.block','Block')
    postfix=fields.Char('Postfix',required=True)
    
    def generate_plots(self):
        plot_obj=self.env['real.estate.plot'].search([('block_id','=',self.block_id.id)])
        for each in plot_obj:            
            vals = {'block_id':self.block_id.id,
                    'sequence':each.sequence,
                    'type':each.type,
                    'postfix':self.postfix,
                    'category_id':each.category_id.id,
                    'size':each.size,
                    'is_west_open':each.is_west_open,
                    'is_corner':each.is_corner,
                    'amenity_facing':each.amenity_facing.ids,
                    'road_facing':each.road_facing.id,
                    'property_value':each.property_value,
                    'currency_id':each.currency_id.id,
                }
            self.env['real.estate.plot'].create(vals)

class GenerateDevelopmentCharges(models.Model):
    _name='generate.development.charges'
    name=fields.Char('Name',compute='cal_name')
    project_id=fields.Many2one('real.estate.project','Project',required=True)
    block_id=fields.Many2one('real.estate.block',string='Blocks',required=True)
    contract_ids=fields.Many2many('real.estate.contract',string='Contracts',domain="[('block_id','=',block_id)]",required=True)
    product_id=fields.Many2one('product.product','Charges Head',required=True)
    amount=fields.Float('Amount',required=True)
    due_date=fields.Date('Due Date',required=True)
    state=fields.Selection([('Draft','Draft'),('Confirmed','Confirmed')],default='Draft',required=True)
    @api.depends('block_id','product_id')
    def cal_name(self):
        for each in self:
            if each.block_id and each.product_id and each.project_id:
                each.name=str(each.product_id.name)+" of "+str(each.block_id.name)+"-"+str(each.project_id.name)
            else:
                each.name='/'
    def set_confirm(self):
        if self.contract_ids:
            for each in self.contract_ids:
                
                vals = {
                    'installment_no': len(each.installment_id),
                    'amount': self.amount,
                    'due_date': self.due_date,
                    'frequency': 'One time',
                    'contract_id': each.id,
                    'product_id': self.product_id.id,
                    'plot_id': each.plot_id.id,
                }
                intallment_obj=self.env['real.estate.installment'].create(vals)
                invoice_obj=intallment_obj.create_invoice_hx()
                invoice_obj.action_post()
            self.write({'state':'Confirmed'})
        else:
            raise ValidationError('Please select contracts before confirm the record.')
    