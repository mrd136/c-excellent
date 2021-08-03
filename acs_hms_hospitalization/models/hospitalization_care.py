# coding=utf-8

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
import dateutil.relativedelta
from odoo.exceptions import ValidationError, AccessError, UserError, RedirectWarning, Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AdmissionCheckListTemplate(models.Model):
    _name="inpatient.checklist.template"
    _description = "Inpatient Checklist Template"

    name = fields.Char(string="Name", required=True)
    remark = fields.Char(string="Remarks")


class AdmissionCheckList(models.Model):
    _name="inpatient.checklist"
    _description = "Inpatient Checklist"

    name = fields.Char(string="Name", required=True)
    is_done = fields.Boolean(string="Y/N", default=False)
    remark = fields.Char(string="Remarks")
    hospitalization_id = fields.Many2one("acs.hospitalization", ondelete="cascade", string="Hospitalization")


class PreWardCheckListTemplate(models.Model):
    _name="pre.ward.check.list.template"
    _description = "Pre Ward Checklist Template"

    name = fields.Char(string="Name", required=True)
    remark = fields.Char(string="Remarks")


class PreWardCheckList(models.Model):
    _name="pre.ward.check.list"
    _description = "Pre Ward Checklist"

    name = fields.Char(string="Name", required=True)
    is_done = fields.Boolean(string="Done", default=False)
    remark = fields.Char(string="Remarks")
    hospitalization_id = fields.Many2one("acs.hospitalization", ondelete="cascade", string="Hospitalization")


#ACS NOTE: hms14: improve model name from accomodation to accommodation
class PatientAccommodationHistory(models.Model):
    _name = "patient.accomodation.history"
    _rec_name = "patient_id"
    _description = "Patient Accommodation History"

    def _rest_time(self):
        for registration in self:
            if registration.end_date and registration.start_date:
                diff = (registration.end_date - registration.start_date)
                if registration.bed_id.invoice_policy=='full':
                    registration.rest_time = diff.days if diff.days > 0 else 1
                else:
                    total_seconds = int(diff.total_seconds())
                    registration.rest_time = (total_seconds/3600) if total_seconds else 0
            else:
                registration.rest_time = 0

    hospitalization_id = fields.Many2one('acs.hospitalization', ondelete="cascade", string='Inpatient', required=True)
    patient_id = fields.Many2one('hms.patient', ondelete="restrict", string='Patient', required=True)
    ward_id = fields.Many2one('hospital.ward', ondelete="restrict", string='Ward/Room')
    bed_id = fields.Many2one('hospital.bed', ondelete="restrict", string='Bed No.')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    rest_time = fields.Float(compute=_rest_time, string='Rest Time')
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Hospital', related='hospitalization_id.company_id') 
    invoice_policy = fields.Selection([
        ('full', 'Days (Full)'),
        ('hourly', 'Hours')], related="bed_id.invoice_policy", string='Invoice Policy', readonly=True)


class WardRounds(models.Model):
    _name = "ward.rounds"
    _description = "Ward Rounds"

    instruction = fields.Char(string='Instruction')
    remarks = fields.Char(string='Remarks')          
    hospitalization_id = fields.Many2one('acs.hospitalization', ondelete="restrict",string='Inpatient')
    #ACS 14: Remove date and use DateTime, change executed_by to user_id
    date = fields.Date(string='Date')
    execution_time = fields.Datetime(string='Execution Date', default=fields.Datetime.now)
    executed_by = fields.Many2one('res.users', ondelete="restrict", string='Executed By', default=lambda self: self.env.user.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: