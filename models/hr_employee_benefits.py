from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

total = 0

class HrEmployeeBenefits(models.Model):
    _name = "hr.employee.benefits"
    _description = "Hr Benefits"
    _rec_name = "employee_name" # As I don't have a field called name, I have to append it my self

    total_benefit = fields.Integer(string='Total Benefit', compute='_compute_total_benefit', store=True)
    value = fields.Integer(string="Benefit Value")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('refused', 'Refused')
    ], default="draft")
    benefit_date = fields.Date(string="Benefit Date", required=True)
    month_benefit_total = fields.Integer(string="Total Month Benefit", compute="_compute_month_benefit_total",
                                         store=True)

    employee_id = fields.Many2one("hr.employee", required=True, string="Employee Name", store=True)
    benefit_type_id = fields.Many2one("benefit.type", required=True, string="Benefit Type", store=True)

    #Related to employee_id
    employee_name = fields.Char(compute="_compute_employee_name", store=True)
    employee_department = fields.Char(compute="_compute_employee_department", store=True)
    employee_manager = fields.Char(compute="_compute_employee_manager", store=True)
    employee_job = fields.Char(compute="_compute_employee_job", store=True)

    #Related to benefit_id
    benefit_name = fields.Char(compute="_compute_benefit_name", store=True, string="Benefit Name")



    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec._compute_total_benefit()

    def action_confirmed(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_refused(self):
        for rec in self:
            rec.state = 'refused'
            rec._compute_total_benefit()

    def unlink(self):
        employees = self.mapped('employee_id')
        res = super().unlink()
        for employee in employees:
            remaining_benefits = self.env['hr.employee.benefits'].search([
                ('employee_id', '=', employee.id)
            ])
            remaining_benefits._compute_total_benefit()
            remaining_benefits._compute_month_benefit_total()

        return res

    @api.depends('employee_id', 'state', 'value')
    def _compute_total_benefit(self):
        global total
        employees = self.mapped('employee_id')
        for employee in employees:
            employee_benefits = self.env['hr.employee.benefits'].search([('employee_id', '=', employee.id),
                                                                         ('state', '=', 'confirmed')])
            total = sum(employee_benefits.mapped('value'))
        for employee in employees:
            employee_benefits = self.env['hr.employee.benefits'].search([('employee_id', '=', employee.id)])
            for benefit in employee_benefits:
                benefit.total_benefit = total

    @api.depends('employee_id', 'state', 'value', 'benefit_date')
    def _compute_month_benefit_total(self):
        global total
        employees = self.mapped('employee_id')
        for employee in employees:

            confirmed_benefits = self.env['hr.employee.benefits'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'confirmed'),
            ])

            monthly_groups = {}
            for b in confirmed_benefits:
                key = (b.benefit_date.year, b.benefit_date.month)
                monthly_groups.setdefault(key, []).append(b)

            for (year, month), benefits_in_month in monthly_groups.items():
                total = sum(b.value for b in benefits_in_month)

                all_benefits_this_month = self.env['hr.employee.benefits'].search([
                    ('employee_id', '=', employee.id),
                    ('benefit_date', '>=', date(year, month, 1)),
                    ('benefit_date', '<', date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)),
                ])
                for benefit in all_benefits_this_month:
                    benefit.month_benefit_total = total


    @api.depends('employee_id')
    def _compute_employee_name(self):
        for rec in self:
            rec.employee_name = rec.employee_id.name


    @api.depends('employee_id')
    def _compute_employee_department(self):
        for rec in self:
            rec.employee_department = rec.employee_id.department_id.name


    @api.depends('employee_id')
    def _compute_employee_manager(self):
        for rec in self:
            rec.employee_manager = rec.employee_id.parent_id.name


    @api.depends('employee_id')
    def _compute_employee_job(self):
        for rec in self:
            rec.employee_job = rec.employee_id.job_id.name


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

