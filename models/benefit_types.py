from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrEmployeeBenefits(models.Model):
    _name = "benefit.type"
    _description = "Benefit Types"

    name = fields.Char(required=True, string="Benefits")
    code = fields.Char(string="Code")