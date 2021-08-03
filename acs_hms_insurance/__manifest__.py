# -*- coding: utf-8 -*-

{
    'name': 'Patient Insurance Management System',
    'summary': 'Patient Insurance Management for Hospitalization and related Claims',
    'description': """
        Patient Insurance Management for Hospitalization and related Claims. Hospital Management with Insurance Claim. ACS HMS
    """,
    'category': 'Medical',
    'version': '1.0.20',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends': ['acs_hms_hospitalization', 'acs_hms_document'], #acs_invoice_split
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hms_base_view.xml',
        'views/tpa_view.xml',
        'views/insurance_view.xml',
        'views/claim_view.xml',
        'views/package_view.xml',
        'views/menu_items.xml',
        'report/package_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/hms_insuranceacs_almightycs_odoo_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
    'price': 51,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: