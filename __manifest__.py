# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Blog',
    'version': '1.1',
    'summary': 'Blog',
    'sequence': 15,
    'description': 'Blog',
    'category': 'New',
    'website': 'https://www.odoo.com/page/billing',
    'images': [],
    'depends': ['base', 'web', 'mail'],
    'data': [
        'data/blog_data.xml',
        'security/blog_security.xml',
        'security/ir.model.access.csv',
        'views/menu_view.xml',
        'views/article_view.xml',
        'views/blog_type_view.xml',
        'views/category_view.xml',
        'views/sub_category_view.xml',
        'views/gallery_view.xml',
        'views/settings_view.xml',
        'wizard/export_service_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
