# -*- coding: utf-8 -*-
{
    'name': "Theme Backend",

    'summary': """
        theme Backend, theme for every one""",

    'description': """
        theme base, backend theme for everyone
    """,

    'author': "Slnee ---- Nabil YAHIA",

    "category": "Themes/Backend",
    'version': '13.0.0.1',
    'license': 'OPL-1',
    'images': ['static/description/banner.png',
               'static/description/akl_screenshot.png'],

    'depends': ['base'],
    "application": True,
    "installable": True,
    "auto_install": False,

    'data': [
        'security/ir.model.access.csv',
        'views/ir_ui_menu_view.xml',
        'views/akl_assets.xml',
        'views/akl_login.xml',
        'views/akl_base.xml',
    ],

    'qweb': [
        'static/xml/*.*',
    ]
}
