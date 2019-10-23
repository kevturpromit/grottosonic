# -*- coding: utf-8 -*-
{
    'name': "Grotto Logistics",

    'summary': """
        Grotto Logistics
        """,

    'description': """
        Grotto Logistics
    """,

    'author': "DSA Software SG, C.A.",
    'website': "http://www.dsasoftware.com.ve",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','eq_invoice_from_picking','grotto_studio_fields'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/grotto_menu_views.xml',
        'views/grotto_cortes_views.xml',
        'views/stock_picking_views.xml',
        'wizard/stock_picking_reasignar_ruta_views.xml',
        'wizard/generar_corte_picking_views.xml',
        'reports/stock_picking_resumen_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
