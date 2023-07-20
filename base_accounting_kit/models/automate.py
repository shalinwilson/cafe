import base64

import xlrd
from odoo import models, fields, api
import openpyxl
import io

from odoo.exceptions import UserError


class AutomateWizard(models.TransientModel):
    _name = 'automate.wizard'

    file = fields.Binary(string='Excel File',required=1)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    partner_id = fields.Many2one('res.partner')
    import openpyxl
    import io

    def create_sale_orders(self):
        for rec in self:
            if not rec.file:
                continue


            # Read the Excel file using openpyxl
            file_bytes = base64.b64decode(rec.file)
            file_stream = io.BytesIO(file_bytes)
            workbook = openpyxl.load_workbook(file_stream, read_only=True)
            sheet = workbook.active  # Assuming you want to work with the active sheet
            start_row = 7  # Start reading from the 6th row (excluding header)
            partner_id = self.partner_id.id
            sale_order = self.env['sale.order'].create({
                'partner_id': partner_id,
                'warehouse_id':self.warehouse_id.id,
                'pricelist_id': self.env.user.partner_id.property_product_pricelist.id,
            })
            # Loop through rows and extract data from columns A and D
            for row_idx, row in enumerate(sheet.iter_rows(min_row=start_row, values_only=True), start=start_row):
                product_row = row[0]  # Column A is at index 0
                qty = row[3]  # Column D is at index 3
                rate = row[4]  # Column D is at index 3
                print(f"Row {row_idx}, Column product: {product_row}, Column qty: {qty},rate{rate}")
                if product_row != 'TOTAL*':
                    product = self.env['product.template'].search([('name', '=', product_row)], limit=1)
                    product_pro_id = self.env['product.product'].search([('product_tmpl_id','=',product.id)])
                    if not product:
                        print("product not found 90000000000000000000000000000000", product_row)
                        raise UserError(f"Product with default code {product_row} not found in Odoo.")


                    vals = {
                        'order_id': sale_order.id,
                        'product_id':product_pro_id.id,
                        'product_uom_qty': qty,
                        'name':product.name,
                        'product_uom':product.uom_id.id,
                        'price_unit': rate,
                        'customer_lead':0,
                        'display_type':False,
                    }
                    print(vals)

                    order_line = self.env['sale.order.line'].create(vals)
                else:
                    break;



