# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class hms_next_patient_screen(http.Controller):

    @http.route(['/waiting_screen/<model("acs.hms.waiting.screen"):screen>'], type='http', auth="public", website=True)
    def waiting_screen(self, screen=False, **kw):
        Appointment = request.env['hms.appointment']
        domain = [('company_id','=',screen.company_id.id), ('state', '=', 'waiting')]
        if screen and screen.physician_ids:
            domain += [('physician_id','in',screen.physician_ids.ids)]
        waiting_appointments = Appointment.sudo().search(domain, order="id asc")
        return request.render("acs_hms_next_patient_screen.next_patient_view",{'waiting_screen': screen, 'waiting_appointments': waiting_appointments, 'Appointment': Appointment})
