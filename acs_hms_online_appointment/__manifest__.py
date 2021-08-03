# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║ SOFTWARE DEVELOPED AND SUPPORTED BY ALMIGHTY CONSULTING SERVICES ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   http://www.almightycs.com                      ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name' : 'HMS Online Appointment',
    'summary' : 'Allow patients to Book an Appointment on-line from portal',
    'description' : """HMS Website Portal to Book an Appointment online. acs hms medical Allow patients to Book an Appointment online from portal""",
    'version': '1.0.14',
    'category': 'Medical',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'depends' : ['acs_hms_portal','website_payment','account_payment'],
    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/weekly_slot_cron_view.xml',
        'views/hms_base_view.xml',
        'views/schedule_views.xml',
        'views/template.xml',
        'views/res_config_settings_views.xml',
        'wizard/appointment_scheduler_wizard.xml',
        'views/menu_item.xml',
    ],
    'images': [
        'static/description/acs_hms_online_booking_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 70,
    'currency': 'EUR',
}
