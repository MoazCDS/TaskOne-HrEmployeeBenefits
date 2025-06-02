from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class HrEmployeeBenefits(models.Model):
    _name = "hr.employee.benefits"
    _description = "Hr Benefits"
    _rec_name = "employee_name" # As I don't have a field called name, I have to append it my self

    total_benefit = fields.Integer(string='Total Benefit', compute='_compute_total_benefit', store=True)
    amount = fields.Integer(string="Benefit Value")
    benefit_date = fields.Date(string="Benefit Date")

    employee_id = fields.Many2one("hr.employee", required=True, string="Employee Name", store=True)
    benefit_type_id = fields.Many2one("benefit.type", required=True, string="Benefit Type", store=True)

    #Related to employee_id
    employee_name = fields.Char(string="Employee Name" ,related="employee_id.name")
    department_id = fields.Many2one(string="Employee Department", related="employee_id.department_id")
    employee_manager = fields.Char(string="Employee Manager", compute="_compute_employee_manager")
    job_id = fields.Many2one(string="Employee Job", related="employee_id.job_id")

    #Related to benefit_id
    benefit_name = fields.Char(compute="_compute_benefit_name", store=True, string="Benefit Name")
    total = 0




    def unlink(self):
        employees = self.mapped('employee_id')
        res = super().unlink()
        for employee in employees:
            remaining_benefits = self.env['hr.employee.benefits'].search([
                ('employee_id', '=', employee.id)
            ])
            remaining_benefits._compute_total_benefit()

        return res

    @api.depends('employee_id', 'amount')
    def _compute_total_benefit(self):
        employee_ids = self.mapped('employee_id').ids
        all_benefits = self.env['hr.employee.benefits'].search([('employee_id', 'in', employee_ids)])
        totals_by_employee = {}
        for benefit in all_benefits:
            emp_id = benefit.employee_id.id
            totals_by_employee[emp_id] = totals_by_employee.get(emp_id, 0) + (benefit.amount or 0)
        for benefit in all_benefits:
            benefit.total_benefit = totals_by_employee.get(benefit.employee_id.id, 0)



    @api.depends('employee_id')
    def _compute_employee_manager(self):
        for rec in self:
            rec.employee_manager = rec.employee_id.parent_id.user_id.name


    @api.depends('benefit_type_id')
    def _compute_benefit_name(self):
        for rec in self:
            rec.benefit_name = rec.benefit_type_id.name


    def benefit_xlsx_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/benefit/excel/reports/{self.env.context.get("active_ids")}',
            'target': 'new'
        }

