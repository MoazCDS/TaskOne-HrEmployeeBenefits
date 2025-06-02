{
    'name' : "Hr Benefits",
    'description': "HR Benefits App",
    'author' : "Moaz Elbahr",
    'category': '',
    'version': '17.0.0.1.0',
    'depends': ['base', 'hr'],
    'data': [
             "security/security.xml",
             "security/ir.model.access.csv",
             "views/base_menu.xml",
             "views/hr_employee_benefits_view.xml",
             "views/benefit_types_view.xml",
    ],
    'application': True,
}