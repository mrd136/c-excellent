{
    'name': 'Product Return In POS',
    'version': '13.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'POS Order Return',
    'author': 'A&L.',
    'images': ['static/description/icon.png'],
    'depends': ['point_of_sale'],
    'data': [
             'views/return.xml',
             'views/pos_template.xml',
             'security/return_security.xml',
             'security/ir.model.access.csv',
            ],
    'qweb': ['static/src/xml/pos_return.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,

}
