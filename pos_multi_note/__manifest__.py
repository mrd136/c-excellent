{
    'name': 'Multiple Order Notes In POS',
    'summary': """The module enables to add multiple order line from the pos interface and other than
    selection of the order note text is also enabled""",
    'version': '12.0.1.0.0',
    'description': """The module enables to add multiple order line from the pos interface and other than
    selection of the order note text is also enabled""",
    'author': 'A&L.',
    'images': ['static/description/icon.png'],
    'category': 'Point of Sale',
    'depends': ['base', 'point_of_sale', 'pos_restaurant'],
    'data': [
        'views/order_note_templates.xml',
        'views/order_note_backend.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': ['static/src/xml/pos_internal_note.xml'],
    'installable': True,
    'auto_install': False,

}