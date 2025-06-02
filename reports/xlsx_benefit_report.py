from odoo import http
from odoo.http import request
import io
import xlsxwriter
from ast import literal_eval
class XlsxBenefitReport(http.Controller):
    @http.route('/benefit/excel/reports/<string:benefit_ids>', type="http", auth="user")
    def download_benefit_excel_report(self, benefit_ids):

        benefit_ids = request.env['hr.employee.benefits'].browse(literal_eval(benefit_ids))

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Benefits')

        headers = ['Employee Name', 'Department ID', 'Job ID', 'Total Benefit', 'Benefit Name']
        col_width = [len(header) for header in headers ]
        header_format = workbook.add_format({"bold": True, 'bg_color': '#D3D3D3', 'border': 1, 'align': 'center'})
        left_align_format = workbook.add_format({'align': 'left'})

        # Write headers to the first row
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        # Write benefit data row by row
        for row_num, benefit in enumerate(benefit_ids, start=1):
            for col_num, header in enumerate(headers):
                field_name = header.lower().replace(' ', '_')
                # Example Of Its Job : "Employee Department" -> "employee_department"
                value = getattr(benefit, field_name, '')
                if isinstance(value, bool):
                    value = 'Yes' if value else 'No'
                elif hasattr(value, 'display_name'):  # handles many2one fields
                    value = value.display_name
                worksheet.write(row_num, col_num, value, left_align_format)

# Function to auto-size the column:
        # Step1: Make the values string to iterate on them and use the len function
                str_value = str(value or "")
        # Step2: Set a variable to compare the col_width with the width of the current value
                width = len(str_value)
        # Step3: Compare between the 2 variables and set the column width to the width if it's a bigger value
                if width > col_width[col_num]:
                    col_width[col_num] = width

# Applying the auto-sizing function made above
        for col_index, width in enumerate(col_width):
            worksheet.set_column(col_index, col_index, width + 2)

        workbook.close()
        output.seek(0)

        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename="Benefit Report.xlsx"')
            ]
        )