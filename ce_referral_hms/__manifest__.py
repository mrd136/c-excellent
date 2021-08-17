# -*- coding: utf-8 -*-
{
    'name': 'Patient Referral',
    'summary': 'Patient Referral Management System for managing Referral',
    'description': """""",
    'version': '1.0.55',
    'category': 'Medical',
    'author': 'Connection Excellent',
    'support': 'Info@c-excellent.com',
    'website': 'http://c-excellent.com',
    'license': 'OPL-1',
    'depends': ['acs_hms', 'operating_unit'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/appointment.xml',
        'views/operating_unit_view.xml',
        'views/referral_view.xml',
        'views/multi_referral.xml',
        'views/config_view.xml',
    ],
    'demo': [],
    'images': [
        'static/description/hms_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
