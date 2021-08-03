# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import time

import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from babel.dates import format_datetime, format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools.misc import formatLang
from odoo.release import version

COLORS = [
    ('green','Green'),
    ('red','Red'),
    ('yellow','Yellow'),
    ('primary','Primary'),
    ('info','Info'),
    ('warning','Warning')]

class Users(models.Model):
    _inherit = "res.users"

    def get_filter(self, field_name):
        for rec in self:
            domain = []
            if rec.dashboard_data_filter=='today':
                domain = [(field_name, '>=', time.strftime('%Y-%m-%d 00:00:00')),(field_name, '<=', time.strftime('%Y-%m-%d 23:59:59'))]
            if rec.dashboard_data_filter=='week':
                domain = [(field_name, '>=', (fields.Datetime.today() + relativedelta(weeks=-1,days=1,weekday=0)).strftime('%Y-%m-%d')), (field_name, '<=', (fields.Datetime.today() + relativedelta(weekday=6)).strftime('%Y-%m-%d'))]
            if rec.dashboard_data_filter=='month':
                domain = [(field_name,'<',(fields.Datetime.today()+relativedelta(months=1)).strftime('%Y-%m-01')), (field_name,'>=',time.strftime('%Y-%m-01'))]
        return domain
        
    @api.depends('dashboard_data_filter')
    def _compute_dashboard_data(self):
        #Patients
        Patient = self.env['hms.patient']
        patient_domain = self.get_filter('create_date')
        self.total_patients = Patient.search_count(patient_domain)
        patient_domain += [('primary_doctor.user_id','=',self.env.uid)]
        self.my_total_patients = Patient.search_count(patient_domain)

        #Physicians
        Physician = self.env['hms.physician']
        Partner = self.env['res.partner']
        physicians_domain = self.get_filter('create_date')
        self.total_physicians = Physician.search_count(physicians_domain)
        ref_physicians_domain = self.get_filter('create_date')
        ref_physicians_domain += [('is_referring_doctor','=',True)]
        self.total_referring_physicians = Partner.search_count(ref_physicians_domain)

        #Schedules
        Shedules = self.env['resource.calendar']
        self.total_shedules = Shedules.search_count([])

        #Appointments
        Appointment = self.env['hms.appointment']
        appointment_domain = self.get_filter('date')
        self.total_appointments = Appointment.search_count(appointment_domain)
        self.my_total_appointments =  Appointment.search_count(appointment_domain+[('physician_id.user_id','=',self.env.uid)])

        #My Avg Time
        my_appointments_domain = self.get_filter('date')
        my_appointments_domain += [('physician_id.user_id','=',self.env.uid)]
        my_total_appointments = Appointment.search(my_appointments_domain)
        my_avg_cons_time = my_avg_wait_time = 0
        my_total_appointments_cnt = len(my_total_appointments)
        for app in my_total_appointments:
            my_avg_cons_time += app.appointment_duration
            my_avg_wait_time += app.waiting_duration
        self.my_avg_cons_time = my_avg_cons_time/my_total_appointments_cnt if my_total_appointments_cnt else 0
        self.my_avg_wait_time = my_avg_wait_time/my_total_appointments_cnt if my_total_appointments_cnt else 0

        #Avg Time
        total_appointments_domain = self.get_filter('date')
        total_appointments = Appointment.search(total_appointments_domain)
        avg_cons_time = avg_wait_time = 0
        total_appointments_cnt = len(total_appointments)
        self.total_appointments = total_appointments_cnt
        for app in total_appointments:
            avg_cons_time += app.appointment_duration
            avg_wait_time += app.waiting_duration
        self.avg_cons_time = avg_cons_time/total_appointments_cnt if total_appointments_cnt else 0
        self.avg_wait_time = avg_wait_time/total_appointments_cnt if total_appointments_cnt else 0

        #Total Treatment
        treatment_domain = self.get_filter('date')
        Treatment = self.env['hms.treatment']
        self.total_treatments = Treatment.search_count(treatment_domain)
        running_treatment_domain = treatment_domain + [('state','=','running')]
        self.total_running_treatments = Treatment.search_count(running_treatment_domain)
        my_treatment_domain = treatment_domain + [('physician_id.user_id','=',self.env.uid)]
        self.my_total_treatments = Treatment.search_count(my_treatment_domain)
        my_running_treatment_domain = treatment_domain + [('state','=','running'), ('physician_id.user_id','=',self.env.uid)]
        self.my_total_running_treatments = Treatment.search_count(my_running_treatment_domain)

        #Open Invoices
        Invoice = self.env['account.move'].sudo()
        open_invoice_domain = self.get_filter('invoice_date')
        open_invoice_domain += [('type','=','out_invoice'),('state','=','posted')]
        open_invoice = Invoice.search(open_invoice_domain)
        self.total_open_invoice = len(open_invoice)
        total = 0
        for inv in open_invoice:
            total += inv.amount_residual
        self.total_open_invoice_amount =total

        #Birthday
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        self.birthday_patients = Patient.search_count([('birthday', 'like', today_month_day)])
        self.birthday_employee = self.env['hr.employee'].search_count([('birthday', 'like', today_month_day)])

        self.appointment_bar_graph = json.dumps(self.get_bar_graph_datas())
        self.patient_line_graph = json.dumps(self.get_line_graph_datas())

    #Not used remove it in v14
    dashboard_type = fields.Selection([
            ('receptionist','Receptionist'),
            ('nurse','Nurse'),
            ('doctor','Doctor'),
            ('admin','Admin')
        ], "Dashboard", default="receptionist")

    dashboard_data_filter = fields.Selection([
            ('today','Today'),
            ('week','This Week'),
            ('month','This Month'),
            ('year','This Year'),
            ('all','All'),
        ], "Dashboard Filter Type", default="today")

    birthday_patients = fields.Integer(compute="_compute_dashboard_data")
    birthday_employee = fields.Integer(compute="_compute_dashboard_data")
    birthday_color = fields.Selection(COLORS,string='Birthday Color', default="green")

    #Receptionist Dashboard fields
    total_patients = fields.Integer(compute="_compute_dashboard_data")
    total_patients_color = fields.Selection(COLORS,string='Total Patient Color', default="info")
    total_running_treatments = fields.Integer(compute="_compute_dashboard_data")
    total_treatments = fields.Integer(compute="_compute_dashboard_data")
    total_treatments_color = fields.Selection(COLORS,string='Total Treatments Color', default="green")

    total_appointments = fields.Integer(compute="_compute_dashboard_data")
    total_appointments_color = fields.Selection(COLORS,string='Total Appointments Color', default="yellow")
    
    total_open_invoice = fields.Integer(compute="_compute_dashboard_data")
    total_open_invoice_amount = fields.Integer(compute="_compute_dashboard_data")
    total_open_invoice_color = fields.Selection(COLORS,string='Open Invoices', default="red")

    total_shedules = fields.Integer(compute="_compute_dashboard_data")
    total_shedules_color = fields.Selection(COLORS,string='Total Shedules Color', default="primary")

    appointment_bar_graph = fields.Text(compute='_compute_dashboard_data')
    appointment_bar_graph_color = fields.Selection(COLORS,string='Patient Barchart Color', default="info")
    patient_line_graph = fields.Text(compute='_compute_dashboard_data')
    patient_line_graph_color = fields.Selection(COLORS,string='Patient Linechart Color', default="primary")

    #Nurse Dashboard fields

    #Doctor Fields
    my_total_patients = fields.Integer(compute="_compute_dashboard_data")
    my_total_patients_color = fields.Selection(COLORS,string='My Total Patient Color', default="info")
    my_total_appointments = fields.Integer(compute="_compute_dashboard_data")
    my_total_appointments_color = fields.Selection(COLORS,string='My Total Appointments Color', default="yellow")
    my_avg_wait_time = fields.Float(compute="_compute_dashboard_data")
    my_avg_cons_time = fields.Float(compute="_compute_dashboard_data")
    my_avg_time_color = fields.Selection(COLORS,string='My Avg Time Color', default="primary")
    
    my_total_treatments = fields.Integer(compute="_compute_dashboard_data")
    my_total_running_treatments = fields.Integer(compute="_compute_dashboard_data")
    my_total_treatments_color = fields.Selection(COLORS,string='My Total Treatments Color', default="green")

    #Admin Fields
    total_appointments = fields.Integer(compute="_compute_dashboard_data")
    avg_wait_time = fields.Float(compute="_compute_dashboard_data")
    avg_cons_time = fields.Float(compute="_compute_dashboard_data")
    avg_time_color = fields.Selection(COLORS, string='Avg Time Color', default="primary")
    total_physicians = fields.Integer(compute="_compute_dashboard_data")
    total_referring_physicians = fields.Integer(compute="_compute_dashboard_data")
    physicians_color = fields.Selection(COLORS,string='Total Physicians Color', default="info")

    def _get_user_role(self):
        for rec in self:
            rec.is_physician = True if (rec.physician_count > 0) else False
            rec.is_manager = rec.has_group('acs_hms.group_hms_manager')

    is_physician = fields.Boolean(compute='_get_user_role', string="Is Physician", readonly=True)
    is_manager = fields.Boolean(compute='_get_user_role', string="Is Manager", readonly=True)

    def get_bar_graph_datas(self):
        data = []
        today = fields.Datetime.now()
        data.append({'label': _('Past'), 'value':0.0, 'type': 'past'})
        day_of_week = int(format_datetime(today, 'e', locale=self._context.get('lang') or 'en_US'))
        first_day_of_week = today + timedelta(days=-day_of_week+1)
        for i in range(-1,4):
            if i==0:
                label = _('This Week')
            elif i==3:
                label = _('Future')
            else:
                start_week = first_day_of_week + timedelta(days=i*7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = str(start_week.day) + '-' +str(end_week.day)+ ' ' + format_date(end_week, 'MMM', locale=self._context.get('lang') or 'en_US')
                else:
                    label = format_date(start_week, 'd MMM', locale=self._context.get('lang') or 'en_US')+'-'+format_date(end_week, 'd MMM', locale=self._context.get('lang') or 'en_US')
            data.append({'label':label,'value':0.0, 'type': 'past' if i<0 else 'future'})

        # Build SQL query to find amount aggregated by week
        (select_sql_clause, query_args) = ("""SELECT count(id) as total, min(date) as aggr_date
               FROM hms_appointment WHERE state != 'cancel'""",{})
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))
        for i in range(0,6):
            if i == 0:
                query += "("+select_sql_clause+" and date < '"+start_date.strftime(DF)+"')"
            elif i == 5:
                query += " UNION ALL ("+select_sql_clause+" and date >= '"+start_date.strftime(DF)+"')"
            else:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL ("+select_sql_clause+" and date >= '"+start_date.strftime(DF)+"' and date < '"+next_date.strftime(DF)+"')"
                start_date = next_date

        self.env.cr.execute(query, query_args)
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            if query_results[index].get('aggr_date') != None:
                data[index]['value'] = query_results[index].get('total')

        [graph_title, graph_key] = ['', _('Appointments')]
        return [{'values': data, 'title': graph_title, 'key': graph_key}]

    def get_line_graph_datas(self):
        data = []
        today = fields.Date.today()
        last_month = today + timedelta(days=-30)
        data_stmt = []
        # Query to optimize loading of data for bank graphs
        # last 30 days
        query = """SELECT count(id) as total, create_date::timestamp::date as date
               FROM hms_patient WHERE create_date > %s
                                    AND create_date <= %s
                                    GROUP BY create_date::timestamp::date
                                    ORDER BY create_date::timestamp::date"""
 
        self.env.cr.execute(query, (last_month, today))
        data_stmt = self.env.cr.dictfetchall()

        locale = self._context.get('lang') or 'en_US'
        show_date = last_month
        #get date in locale format
        name = format_date(show_date, 'd LLLL Y', locale=locale)
        short_name = format_date(show_date, 'd MMM', locale=locale)
        data.append({'x':short_name,'y':0, 'name':name})

        for stmt in data_stmt:
            #fill the gap between last data and the new one
            number_day_to_add = (stmt.get('date') - show_date).days
            last_balance = data[len(data) - 1]['y']
            for day in range(0,number_day_to_add + 1):
                show_date = show_date + timedelta(days=1)
                #get date in locale format
                name = format_date(show_date, 'd LLLL Y', locale=locale)
                short_name = format_date(show_date, 'd MMM', locale=locale)
                data.append({'x': short_name, 'y':last_balance, 'name': name})
            #add new stmt value
            data[len(data) - 1]['y'] = stmt.get('total')

        #continue the graph if the last rec isn't today
        if show_date != today:
            number_day_to_add = (today - show_date).days
            last_balance = data[len(data) - 1]['y']
            for day in range(0,number_day_to_add):
                show_date = show_date + timedelta(days=1)
                #get date in locale format
                name = format_date(show_date, 'd LLLL Y', locale=locale)
                short_name = format_date(show_date, 'd MMM', locale=locale)
                data.append({'x': short_name, 'y':last_balance, 'name': name})

        [graph_title, graph_key] = ['', _('New Patients')]
        color = '#875A7B' if '+e' in version else '#7c7bad'
        return [{'values': data, 'title': graph_title, 'key': graph_key, 'area': True, 'color': color}]

    def today_data(self):
        self.sudo().dashboard_data_filter = 'today'

    def week_data(self):
        self.sudo().dashboard_data_filter = 'week'

    def month_data(self):
        self.sudo().dashboard_data_filter = 'month'

    def year_data(self):
        self.sudo().dashboard_data_filter = 'year'

    def all_data(self):
        self.sudo().dashboard_data_filter = 'all'

    def open_patients(self):
        action = self.env.ref('acs_hms.action_patient').read()[0]
        action['domain'] = self.get_filter('create_date')
        return action

    def open_my_patients(self):
        action = self.env.ref('acs_hms.action_patient').read()[0]
        action['domain'] = self.get_filter('create_date') + [('primary_doctor.user_id','=',self.env.uid)]
        return action

    def open_referring_physicians(self):
        action = self.env.ref('acs_hms.action_referring_doctors').read()[0]
        action['domain'] = self.get_filter('create_date') + [('is_referring_doctor','=',True)]
        return action

    def open_physicians(self):
        action = self.env.ref('acs_hms.action_physician').read()[0]
        action['domain'] = self.get_filter('create_date')
        return action

    def open_appointments(self):
        action = self.env.ref('acs_hms.action_appointment').read()[0]
        action['domain'] = self.get_filter('date')
        action['context'] = {}
        return action

    def open_treatments(self):
        action = self.env.ref('acs_hms.acs_action_form_hospital_treatment').read()[0]
        action['domain'] = self.get_filter('date')
        action['context'] = {}
        return action

    def open_my_appointments(self):
        action = self.env.ref('acs_hms.action_appointment').read()[0]
        action['domain'] = self.get_filter('date') + [('physician_id.user_id','=',self.env.uid)]
        action['context'] = {}
        return action

    def open_running_treatments(self):
        action = self.env.ref('acs_hms.acs_action_form_hospital_treatment').read()[0]
        action['domain'] = self.get_filter('date') + [('state','=','running')]
        return action

    def open_my_running_treatments(self):
        action = self.env.ref('acs_hms.acs_action_form_hospital_treatment').read()[0]
        action['domain'] = self.get_filter('date') + [('state','=','running'),('physician_id.user_id','=',self.env.uid)]
        return action

    def open_my_treatments(self):
        action = self.env.ref('acs_hms.acs_action_form_hospital_treatment').read()[0]
        action['domain'] = self.get_filter('date') + [('physician_id.user_id','=',self.env.uid)]
        action['context'] = {}
        return action
    
    def open_invoices(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = self.get_filter('invoice_date') + [('type','=','out_invoice'),('state', 'in', ['posted'])]
        return action

    def open_shedules(self):
        action = self.env.ref('resource.action_resource_calendar_form').read()[0]
        return action

    def open_birthday_patients(self):
        Patient = self.env['hms.patient']
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        patient_ids = Patient.search([('birthday', 'like', today_month_day)])
        action = self.env.ref('acs_hms.action_patient').read()[0]
        action['domain'] = [('id','in',patient_ids.ids)]
        return action

    def open_birthday_employee(self):
        Employee = self.env['hr.employee']
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        employee_ids = Employee.search([('birthday', 'like', today_month_day)])
        action = self.env.ref('hr.hr_employee_public_action').read()[0]
        action['domain'] = [('id','in',employee_ids.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: