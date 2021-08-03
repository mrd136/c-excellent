# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    request_id = fields.Many2one('acs.laboratory.request', string='Lab Request', copy=False, ondelete='restrict')


class StockMove(models.Model):
    _inherit = "stock.move"

    lab_test_id = fields.Many2one('patient.laboratory.test', string="Lab Test", ondelete="restrict")


class ACSConsumableLine(models.Model):
    _inherit = "hms.consumable.line"

    patient_lab_test_id = fields.Many2one('patient.laboratory.test', string="Patient Lab Test", ondelete="restrict")
    lab_test_id = fields.Many2one('acs.lab.test', string="Lab Test", ondelete="restrict")


class ACSPatient(models.Model):
    _inherit = "hms.patient"

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        for rec in self:
            rec.request_count = len(rec.request_ids)
            rec.test_count = len(rec.test_ids)

    def _acs_get_attachemnts(self):
        attachments = super(ACSPatient, self)._acs_get_attachemnts()
        attachments += self.test_ids.mapped('attachment_ids')
        return attachments

    request_ids = fields.One2many('acs.laboratory.request', 'patient_id', string='Lab Requests')
    test_ids = fields.One2many('patient.laboratory.test', 'patient_id', string='Tests')
    request_count = fields.Integer(compute='_rec_count', string='# Lab Requests')
    test_count = fields.Integer(compute='_rec_count', string='# Lab Tests')

    def action_lab_requests(self):
        action = self.env.ref('acs_hms_laboratory.hms_action_lab_test_request').read()[0]
        action['domain'] = [('id','in',self.request_ids.ids)]
        action['context'] = {'default_patient_id': self.id}
        return action

    def action_view_test_results(self):
        action = self.env.ref('acs_hms_laboratory.action_lab_result').read()[0]
        action['domain'] = [('id','in',self.test_ids.ids)]
        action['context'] = {'default_patient_id': self.id}
        return action


class Hospitalization(models.Model):
    _inherit = "acs.hospitalization"

    def _rec_count(self):
        rec = super(Hospitalization, self)._rec_count()
        for rec in self:
            rec.request_count = len(rec.request_ids)
            rec.test_count = len(rec.test_ids)

    request_ids = fields.One2many('acs.laboratory.request', 'hospitalization_id', string='Lab Requests')
    test_ids = fields.One2many('patient.laboratory.test', 'hospitalization_id', string='Tests')
    request_count = fields.Integer(compute='_rec_count', string='# Lab Requests')
    test_count = fields.Integer(compute='_rec_count', string='# Lab Tests')

    def action_lab_request(self):
        action = self.env.ref('acs_hms_laboratory.hms_action_lab_test_request').read()[0]
        action['domain'] = [('id','in',self.request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_hospitalization_id': self.id}
        action['views'] = [(self.env.ref('acs_hms_laboratory.patient_laboratory_test_request_form').id, 'form')]
        return action

    def action_lab_requests(self):
        action = self.env.ref('acs_hms_laboratory.hms_action_lab_test_request').read()[0]
        action['domain'] = [('id','in',self.request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_hospitalization_id': self.id}
        return action

    def action_view_test_results(self):
        action = self.env.ref('acs_hms_laboratory.action_lab_result').read()[0]
        action['domain'] = [('id','in',self.test_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_hospitalization_id': self.id}
        return action


class ACSAppointment(models.Model):
    _inherit='hms.appointment'

    def _rec_count(self):
        for rec in self:
            rec.request_count = len(rec.lab_request_ids)
            rec.test_count = len(rec.test_ids)

    test_ids = fields.One2many('patient.laboratory.test', 'appointment_id', string='Lab Tests')
    lab_request_ids = fields.One2many('acs.laboratory.request', 'appointment_id', string='Lab Requests')
    request_count = fields.Integer(compute='_rec_count', string='# Lab Requests')
    test_count = fields.Integer(compute='_rec_count', string='# Lab Tests')

    def action_lab_request(self):
        action = self.env.ref('acs_hms_laboratory.hms_action_lab_test_request').read()[0]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        action['views'] = [(self.env.ref('acs_hms_laboratory.patient_laboratory_test_request_form').id, 'form')]
        return action

    def action_view_test_results(self):
        action = self.env.ref('acs_hms_laboratory.action_lab_result').read()[0]
        action['domain'] = [('id','in',self.test_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        return action

    def action_view_lab_request(self):
        action = self.env.ref('acs_hms_laboratory.hms_action_lab_test_request').read()[0]
        action['domain'] = [('id','in',self.lab_request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        return action


class Treatment(models.Model):
    _inherit = "hms.treatment"

    def _lab_rec_count(self):
        for rec in self:
            rec.request_count = len(rec.request_ids)
            rec.test_count = len(rec.test_ids)

    request_ids = fields.One2many('acs.laboratory.request', 'treatment_id', string='Lab Requests')
    test_ids = fields.One2many('patient.laboratory.test', 'treatment_id', string='Tests')
    request_count = fields.Integer(compute='_lab_rec_count', string='# Lab Requests')
    test_count = fields.Integer(compute='_lab_rec_count', string='# Lab Tests')

    def action_lab_request(self):
        action = self.env.ref('acs_hms_laboratory.hms_action_lab_test_request').read()[0]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        action['views'] = [(self.env.ref('acs_hms_laboratory.patient_laboratory_test_request_form').id, 'form')]
        return action

    def action_lab_requests(self):
        action = self.env.ref('acs_hms_laboratory.hms_action_lab_test_request').read()[0]
        action['domain'] = [('id','in',self.request_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        return action

    def action_view_test_results(self):
        action = self.env.ref('acs_hms_laboratory.action_lab_result').read()[0]
        action['domain'] = [('id','in',self.test_ids.ids)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_treatment_id': self.id}
        return action

class Physician(models.Model):
    _inherit = "hms.physician"

    def _lab_request_count(self):
        for record in self:
            Count=self.env['acs.laboratory.request'].search_count([('physician_id', '=', record.id)])
            record.lab_request_count=Count

    def _lab_result_count(self):
        for record in self:
            Count=self.env['acs.laboratory.request'].search_count([('physician_id', '=', record.id)])
            record.lab_result_count=Count

    lab_request_count = fields.Integer(compute='_lab_request_count', string='# Lab Request')
    lab_result_count = fields.Integer(compute='_lab_result_count', string='# Lab Result')

    def action_lab_request(self):
        action = self.env.ref('acs_hms_laboratory.hms_action_lab_test_request').read()[0]
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    def action_lab_result(self):
        action = self.env.ref('acs_hms_laboratory.action_lab_result').read()[0]
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: