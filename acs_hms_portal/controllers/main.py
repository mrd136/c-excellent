# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.exceptions import AccessError, MissingError


class HMSPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(HMSPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id.commercial_partner_id
        appointment_count = request.env['hms.appointment'].search_count([('patient_id.partner_id', '=', partner.id)])
        prescription_count = request.env['prescription.order'].search_count([('patient_id.partner_id', '=', partner.id)])
        values.update({
            'appointment_count': appointment_count,
            'prescription_count': prescription_count,
        })
        return values

    @http.route(['/my/appointments', '/my/appointments/page/<int:page>'], type='http', auth="user", website=True)
    def my_appointments(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
 
        pager = portal_pager(
            url="/my/appointments",
            url_args={},
            total=values['appointment_count'],
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        partner = request.env.user.partner_id.commercial_partner_id
        appointments = request.env['hms.appointment'].search([
            ('patient_id.partner_id', '=', partner.id),],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'appointments': appointments,
            'page_name': 'appointment',
            'default_url': '/my/appointments',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_hms_portal.my_appointments", values)

    @http.route(['/my/appointments/<int:appointment_id>'], type='http', auth="user", website=True)
    def my_appointments_appointment(self, appointment_id=None, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('hms.appointment', appointment_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("acs_hms_portal.my_appointments_appointment", {'appointment': order_sudo})

    #Prescriptions
    @http.route(['/my/prescriptions', '/my/prescriptions/page/<int:page>'], type='http', auth="user", website=True)
    def my_prescriptions(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        if not sortby:
            sortby = 'date'

        sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        order = sortings.get(sortby, sortings['date'])['order']
 
        pager = portal_pager(
            url="/my/prescriptions",
            url_args={},
            total=values['prescription_count'],
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        partner = request.env.user.partner_id.commercial_partner_id
        prescriptions = request.env['prescription.order'].search([
            ('patient_id.partner_id', '=', partner.id)],
            order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'sortings': sortings,
            'sortby': sortby,
            'prescriptions': prescriptions,
            'page_name': 'prescription',
            'default_url': '/my/prescriptions',
            'searchbar_sortings': sortings,
            'pager': pager
        })
        return request.render("acs_hms_portal.my_prescriptions", values)

    @http.route(['/my/prescriptions/<int:prescription_id>'], type='http', auth="user", website=True)
    def my_appointments_prescription(self, prescription_id=None, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('prescription.order', prescription_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render("acs_hms_portal.my_prescriptions_prescription", {'prescription': order_sudo})

    def details_form_validate(self, data):
        error, error_message = super(HMSPortal, self).details_form_validate(data)
        # prevent VAT/name change if invoices | Prescription exist
        partner = request.env['res.users'].browse(request.uid).partner_id
        has_prescription = request.env['prescription.order'].search([
            ('patient_id.partner_id', 'child_of', partner.id),
        ], limit=1)
        
        if has_prescription:
            if 'name' in data and (data['name'] or False) != (partner.name or False):
                error['name'] = 'error'
                error_message.append(_('Changing your name is not allowed once Prescriptions have been issued for your account. Please contact us directly for this operation.'))
        return error, error_message

    @http.route(['/acs/cancel/<int:appointment_id>/appointment'], type='http', auth="user", website=True)
    def cancel_appointment(self, appointment_id,**kw):
        try:
            order_sudo = self._document_check_access('hms.appointment', appointment_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        order_sudo.write({
            'cancel_reason': kw.get('cancel_reason')
        })
        order_sudo.appointment_cancel()

        return request.redirect('/my/appointments')
