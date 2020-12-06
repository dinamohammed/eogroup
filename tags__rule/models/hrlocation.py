# -*- coding: utf-8 -*-

from odoo import models, fields


class HrLocation(models.Model):
    _name = 'hr.location'
    _inherit = ['mail.thread']
    
    name = fields.Char(string="Program", required=True)
    code = fields.Char(string="Program Code", required=True)

