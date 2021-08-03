# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class MedicamentGroupLine(models.Model):
    _name = "medicament.group.line"
    _description = "Medicament Group Line"

    group_id = fields.Many2one('medicament.group', ondelete='restrict', 
        string='Medicament Group')
    product_id = fields.Many2one('product.product', ondelete='restrict', 
        string='Medicine Name')
    allow_substitution = fields.Boolean(string='Allow substitution')
    prnt = fields.Boolean(string='Print', 
        help='Check this box to print this line of the prescription.')
    quantity = fields.Integer(string='Units',
        help="Number of units of the medicament. Example : 30 capsules of amoxicillin")
    dose = fields.Float(string='Dosage', digits=(16, 2), 
        help="Amount of medication (eg, 250 mg) per dose")
    common_dosage_id = fields.Many2one('medicament.dosage', ondelete='cascade', 
        string='Dosage Frequency', help='Amount of medication (eg, 250 mg) per dose')
    short_comment = fields.Char(string='Comment', help='Short comment on the specific drug')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.common_dosage_id = self.product_id.common_dosage_id.id
            self.quantity = 1


class ACSMedicamentGroup(models.Model):
    _name = "medicament.group"
    _description = "Medicament Group"
    _rec_name = 'name'

    name = fields.Char(string='Group Name', required=True)
    physician_id = fields.Many2one('hms.physician', ondelete='set null', string='Physician')
    diseases_id = fields.Many2one('hms.diseases', ondelete='set null', string='Diseases')
    medicine_list = fields.One2many('medicament.group.line', 'group_id', string='Medicament line')
    limit = fields.Integer('Limit')


class ACSMedicationDosage(models.Model):
    _name = 'medicament.dosage'
    _description = "Medicament Dosage"
    _rec_name = 'abbreviation'

    name = fields.Char(translate=True)
    abbreviation = fields.Char(string='Frequency',help='Dosage abbreviation, such as tid in the US or tds in the UK')
    code = fields.Char(size=8, string='Nos',help='Dosage Code,for example: SNOMED 229798009 = 3 times per day')

    _sql_constraints = [('name_uniq', 'UNIQUE(name)', 'Name must be unique!')]


class ACSPatientMedication(models.Model):
    _name = 'hms.patient.medication'
    _description = "Patient Medication"
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('hms.patient', string='Patient')
    doctor = fields.Many2one('hms.physician', string='Physician',
        help='Physician who prescribed the medicament')
    adverse_reaction = fields.Text(string='Adverse Reactions',
        help='Side effects or adverse reactions that the patient experienced')
    notes = fields.Text(string='Extra Info')
    is_active = fields.Boolean(string='Active', 
        help='Check if the patient is currently taking the medication')
    course_completed = fields.Boolean(string='Course Completed')
    template = fields.Many2one('product.template', string='Medication Template')
    discontinued_reason = fields.Char(string='Reason for discontinuation',
        help='Short description for discontinuing the treatment')
    discontinued = fields.Boolean(string='Discontinued')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: