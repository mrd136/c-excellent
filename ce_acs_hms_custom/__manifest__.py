# -*- coding: utf-8 -*-
{
    'name': 'Hms Custom',
    'summary': '',
    'description': """""",
    'version': '1.0.3',
    'category': 'Medical',
    'author': 'Connection Excellent',
    'support': 'Info@c-excellent.com',
    'website': 'http://c-excellent.com',
    'license': 'OPL-1',
    'depends': ['web_timer_widget', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hms_base_views.xml',
        'views/patient_view.xml',
        'views/doctor_view.xml',
        'views/diseases_view.xml',
        # 'views/menu_item.xml',
    ],
    'application': False,
    'sequence': 2,
}
