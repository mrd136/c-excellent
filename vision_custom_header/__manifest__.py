# -*- coding: utf-8 -*-

{
    'name': 'Custom Report Header',
    'version': '1.0',
    'sequence': 125,
    'description': """
        Extend HR""",
    'depends': ['hr', 'hr_contract'],
    'summary': 'Report Extend',
    'website': '',
    'data': [
        'views/extend_report_templates.xml',
    ],
    'installable': True,
    'application': False,
}
