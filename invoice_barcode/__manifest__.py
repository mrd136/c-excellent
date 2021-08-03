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
    'name': 'Add Products by Barcode in Invoice',
    'version': '1.0.2',
    'category': 'Accounting',
    'author': 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'summary': """Add Products by scanning barcode to avoid mistakes and make work faster in Invoice.""",
    'description': """Add Products by scanning barcode to avoid mistakes and make work faster in Invoice.
    Barcode
    Product barcode
    barcode in invoice
    Invoice Barcode
    Scan barcode and add product
    Scan product and add
    Scan to add product
    Scan barcode to add product
    product by barcode scan
    add product in invoice""",
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1', 
    "depends": ["account",'barcodes'],
    "data": [
        "views/account_invoice_view.xml",
    ],
    'images': [
        'static/description/barcode_cover.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 9,
    'currency': 'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: