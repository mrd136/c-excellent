# -*- coding: utf-8 -*-
{
    'name': 'POS Session Report',
    'summary': 'Allow to Print Current Session Report',
    'description': """Module Developed for Session Report.""",

    'author': 'A&L.',
    'images': ['static/description/icon.png'],

    'category': 'Point of Sale',
    'version': '13.0.0.1.0',
    'depends': ['point_of_sale'],

    'data': [
        'views/templates.xml',
        'views/pos_config.xml',
        'report/report_pos_session.xml',
    ],
    'qweb': [
        'static/src/xml/session_report.xml',
    ],

    "auto_install": False,
    "installable": True,

}
