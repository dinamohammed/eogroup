# -*- coding: utf-8 -*-

from odoo import models, fields


class HrLevel(models.Model):
    _inherit = 'hr.level'
    code = fields.Char(string="Level Code")

class StatusEmployee(models.Model):
    _name = 'status.employee'
    name = fields.Char(string="Status Name")