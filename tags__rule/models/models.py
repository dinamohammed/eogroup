# -*- coding: utf-8 -*-

import base64

from datetime import datetime

from odoo import models, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.safe_eval import safe_eval


class TagsRule(models.Model):
    
    _inherit = 'hr.payslip'
    
    tax_base_temp = fields.Float(string='Tax Base Temp', default=0)

    def Tags_function(self, category_ids):
        value = 0
        tag = []
        for category in category_ids:
            tag.append(category.name)
        return tag
    
    # ############### ############### ##################
    # To Execute the previous function on a salary rule :
    # Write the following code :
    #       result = payslip.env['hr.payslip'].Tags_function(employee.category_ids)
    
    def Date_Error(self, Specific_Date):
        Current_Date = datetime.now()
        Day_Current_Date = Current_Date.strftime("%d")
        Specific_Date_str = datetime.strptime(Specific_Date,DEFAULT_SERVER_DATE_FORMAT)
        Day_Specific_Date = Specific_Date_str.strftime("%d")
        
        if Day_Specific_Date < Day_Current_Date:
            raise ValidationError(_('Sorry, Today Date Must be greater Than Start Date...'))
    
    # ############### ############### ##################
    #To Execute the previous function on a salary rule :
    # Write the following code :
    #       result = payslip.env['hr.payslip'].Date_Error('2019-1-12')
    
    
    def Tax_Base_Value(self,Tax_Base,Field_to_Give):
        emp_rec = self.env['hr.employee'].search([('id', '=', Field_to_Give)])
        payslip_rec = self.env['hr.payslip'].search([('employee_id', '=', emp_rec['id']),('state', '=', 'draft')])
        payslip_rec['tax_base_temp'] = Tax_Base
        
        return 0
    
    # ############### ############### ##################
    #To Execute the previous function on a salary rule :
    # Write the following code :
    #       result = payslip.env['hr.payslip'].Tax_Base_Value(categories.RuleofTaxBase , employee.id)
    
    
    def action_payslip_done(self):
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state' : 'done'})
        self.mapped('payslip_run_id').action_close()
        for payslip in self:
            ##### Add the part of Tax Base Container
            payslip.employee_id.tax_base = payslip.tax_base_temp + payslip.employee_id.tax_base
            # ############### ##########################
        if self.env.context.get('payslip_generate_pdf'):
            for payslip in self:
                if not payslip.struct_id or not payslip.struct_id.report_id:
                    report = self.env.ref('hr_payroll.action_report_payslip', False)
                else:
                    report = payslip.struct_id.report_id
                pdf_content, content_type = report.render_qweb_pdf(payslip.id)
                if payslip.struct_id.report_id.print_report_name:
                    pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
                else:
                    pdf_name = _("Payslip")
                self.env['ir.attachment'].create({
                    'name': pdf_name,
                    'type': 'binary',
                    'datas': base64.encodestring(pdf_content),
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })
                
                
class HrLevel(models.Model):
    _name = 'hr.level'
    
    name = fields.Char("Level")



class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    location_type = fields.Selection([('static', 'Static'),
                                      ('dynamic', 'Dynamic'),
                                      ('management', 'Management')], string="Location Type",
                                     required=True, default='static')
    
    tax_base = fields.Float(string='Tax Base', default=0)
    work_location_id = fields.Many2one('hr.location', 'Work Location Ertrac')
    
    def Daily_Check_Value(self):
        
        Current_Date = datetime.now()
        if Current_Date.day == '30' or Current_Date.day == '31':
            emp_rec = self.env['hr.employee'].search([])
            for emp in emp_rec :
                emp['tax_base'] = 0
    
    # ############### ############### ############### ############### ################
    # Create A Scheduled Action :
    # Name : Update Tax Base Value
    # Model : Employee
    # Execute Every : 1 Week
    # Number of calls : -1
    # Action to Do : Execute Python Code
    # Code to write : Update Tax Base Value
    
    # ############### ############### ############### ############### #################
    # Add Fields to Employee Screen
    levels = fields.Selection([('level1', 'Level 1'),
                               ('level2', 'Level 2'),
                               ('level3', 'Level 3'),
                               ('level4', 'Level 4'),
                               ('level5', 'Level 5'),
                               ('level6', 'Level 6'),
                               ('level_dep_manager', 'Department Manager Level'),
                               ('level_sec_manager', 'Section Manager Level'),
                               ('level_sho2on_manager', 'Shoaon Manager Level')], string='Level')
    level_id = fields.Many2one('hr.level', "Level")
    
    certificate_level = fields.Selection([('diploma', 'Diploma'),
                                          ('bachelor', 'Bachelor'),
                                          ('license', 'License'),
                                          ('master', 'Master'),
                                          ('other', 'Other')], string='Certificate')
    
    grade_level = fields.Selection([('excellent', 'Excellent'),
                                    ('very_good', 'Very Good'),
                                    ('good', 'Good'),
                                    ('med', 'Med'),
                                    ('other', 'Other')], string='Grade Level')
    grade_year = fields.Char(string ='Graduation Year')
    
    social_insurance_no = fields.Char(string='Social Insurance No.')
    insurance_date = fields.Date(string='Social Insurance Date')
    start_date = fields.Date(string='Social Insurance Start Date')
    end_date = fields.Date(string='Social Insurance End Date')
    medical_insurance_no = fields.Char(string='Medical Insurance No.')
    medical_location = fields.Char(string='Medical Location')



class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    # ################## Contract Type # ##########################
    
    contract_type_id = fields.Many2one('hr.contract.type', 'Contract Type' ,store=True)
    
    
    # ####################### Allowance Fields # ############### ###############
    internal_transportation_value = fields.Float(string='Internal Transportation')
    veracity_value = fields.Float(string='Veracity')
    external_transportation_value = fields.Float(string='External Transportation')
    meal_value = fields.Float(string='Meal Voucher')
    rest_allowance = fields.Float(string='Rest Allowance')
    supervision_allowance = fields.Float(string='Supervision Allowance')
    allowance_1 = fields.Float(string='Allowance 1')
    allowance_2 = fields.Float(string='Allowance 2')
    allowance_3 = fields.Float(string='Allowance 3')
    allowance_4 = fields.Float(string='Allowance 4')
    allowance_5 = fields.Float(string='Allowance 5')
    allowance_6 = fields.Float(string='Allowance 6')
    allowance_7 = fields.Float(string='Allowance 7')
    allowance_8 = fields.Float(string='Allowance 8')
    
    # ####################### Deduction Fields # ############### ###############
    absence_value = fields.Float(string='Absence')
    deduction_1 = fields.Float(string='Deduction 1')
    house_deduction = fields.Float(string='House Deduction')
    deduction_2 = fields.Float(string='Deduction 2')
    deduction_3 = fields.Float(string='Deduction 3')
    
    
    # ############### ################ 7afeez --> Incentive # ############### ####################
    effort_allowance = fields.Float(string='Effort Allowance')
    manufacturing_allowance = fields.Float(string='Manufacturing Allowance')
    additional_allowance = fields.Float(string='Additional Allowance')
    ceo_allowance = fields.Float(string='CEO Allowance')
    traveling_days = fields.Integer(string='Traveling Days')
    transportation_expenses = fields.Float(string='Transportation Expenses')
    
    
    ########################### Extra Fields Added #########################################
    security_days = fields.Integer(string = 'Security Days Allowance')
    company_pay = fields.Float(string = 'Company Pay')
    allowance_apecial = fields.Float(string = 'Special Allowance')
    total_institution_Value= fields.Float(string = 'Total Institutions Value')


    def Daily_Check_Contract_Value(self):

        Current_Date = datetime.now()
        if Current_Date.day == '20':
            cont_rec = self.env['hr.contract'].search([])
            for cont in cont_rec :
                cont['security_days'] = 0
                cont['allowance_1'] = 0
                cont['deduction_3'] = 0
                cont['effort_allowance'] = 0
                cont['manufacturing_allowance'] = 0
                cont['additional_allowance'] = 0

    # ############### ############### ############### ############### ################
    # Create A Scheduled Action :
    # Name : Update Specific Values in
    # Model : Contract
    # Execute Every : 1 Week
    # Number of calls : -1
    # Action to Do : Execute Python Code
    # Code to write : Update Multi Contract Value
