# -*- coding: utf-8 -*-
{
    'name': "Cortex Products",

    'summary': "Products Customization",

    'description': """
        App to add additional feature to Products.
    """,

    'author': "Mounir Lahsini",
    'version': '1.0',
    'installable': True,
    'website': 'https://github.com/mounirlahsini',

    'depends': ['base', 'product', 'cortex_documents'],

    'data': [
        'views/product_template_views.xml',
    ],

    'demo': [
    ],
    
    'application': False,
}
