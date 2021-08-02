# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class RefusalWizard(models.TransientModel):
    _name = "refusal.wizard"
    _description = "Refuse Wizard"

    message = fields.Text(string=u'سبب الرفض')
  
    def button_refuse(self):
        # Variables
        cx = self.env.context or {}
        # Write refuse message
        for wiz in self:
            if wiz.message and cx.get('active_id', False) and cx.get('active_model', False):
                model_obj = self.env[cx.get('active_model')]
                rec_id = model_obj.browse(cx.get('active_id'))
                rec_id.write({'refusal_reason': wiz.message})
                return rec_id.action_refuse()
