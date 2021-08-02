# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _


class BaseRefusal(models.AbstractModel):
    _name = 'base.refusal'

    refusal_reason = fields.Text(string=u'سبب الرفض')

    
    def action_refuse(self):
        """override this method based on your business logic"""
        raise NotImplementedError()
