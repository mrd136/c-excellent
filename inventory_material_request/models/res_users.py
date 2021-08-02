# -*- coding:utf-8 -*-
from odoo import models, fields, api

class ResUsers(models.Model):

	_inherit = "res.users"

	department_id = fields.Many2one('hr.department', string="Depatment")
	department_ids = fields.Many2many('hr.department', string="Depatments")

		