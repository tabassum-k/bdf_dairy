import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import math

class BDFGatePass(Document):
    def on_cancel(self):
        for si in self.sales_invoice_details:
            frappe.db.set_value("Sales Invoice", si, 'gate_pass', 0)
        for st in self.stock_entry_details:
            frappe.db.set_value("Stock Entry", st, 'custom_gate_pass', 0)

    def on_submit(self):
        opening_qty = 0
        for si in self.sales_invoice_details:
            opening = frappe.db.sql("SELECT balance FROM `tabCrate Ledger` WHERE customer = %s", (si.customer), as_dict = True)
            if len(opening) > 0:
                opening_qty = opening[0]['balance']
            crate_ledger = frappe.new_doc("Crate Ledger")
            crate_ledger.customer = si.customer
            crate_ledger.route = self.route
            crate_ledger.crate_type = "Blue Crate"
            crate_ledger.opening = opening_qty
            crate_ledger.issue_qty = si.crate_issue_qty
            crate_ledger.return_qty = 0
            crate_ledger.balance = opening_qty +  si.crate_issue_qty
            crate_ledger.bdf_gate_pass = self.name
            crate_ledger.save()
            frappe.db.set_value("Sales Invoice", si.sales_invoice, 'gate_pass', 1)

        for st in self.stock_entry_details:
            opening = frappe.db.sql("SELECT balance FROM `tabCrate Ledger` WHERE warehouse = %s", (st.warehouse), as_dict = True)
            if len(opening) > 0:
                opening_qty = opening[0]['balance']
            else:
                opening_qty = 0
            crate_ledger = frappe.new_doc("Crate Ledger")
            crate_ledger.warehouse = st.warehouse
            crate_ledger.route = self.route
            crate_ledger.crate_type = "Blue Crate"
            crate_ledger.opening = opening_qty
            crate_ledger.issue_qty = si.crate_issue_qty
            crate_ledger.return_qty = 0
            crate_ledger.balance = opening_qty +  si.crate_issue_qty
            crate_ledger.bdf_gate_pass = self.name
            crate_ledger.save()
            frappe.db.set_value("Stock Entry", st.stock_entry, 'custom_gate_pass', 1)

            
    def validate(self):
        self.sales_invoice_details.clear()
        self.stock_entry_details.clear()
        self.gate_pass_items_summary.clear()

        sales_invoices = set()
        stock_entries = set()
        item_qty_sum = {}
        total_crate_qty, total_extra_crate = 0, 0

        for i in self.gate_pass_items:
            if i.item_code:
                item_qty_sum[i.item_code] = item_qty_sum.get(i.item_code, 0) + (i.item_qty or 0)
            if i.sales_invoice:
                sales_invoices.add(i.sales_invoice)
            if i.stock_entry:
                stock_entries.add(i.stock_entry)

        for it in self.gate_pass_items:
            count = 0
            if not it.item_code or not it.item_qty:
                continue
            item_doc = frappe.get_doc("Item", it.item_code)
            if hasattr(item_doc, 'crate') and item_doc.crate:
                for itm in item_doc.crate:
                    if itm.crate_quantity and itm.crate_type and count == 0:
                        crate_qty = math.floor(it.item_qty / itm.crate_quantity)
                        it.crate_type = itm.crate_type
                        it.crate_qty = crate_qty
                        total_crate_qty += crate_qty
                        count = 1

        for item_code, total_qty in item_qty_sum.items():
            weight_per_unit = 0
            matching_item = next((itm for itm in self.gate_pass_items if itm.item_code == item_code), None)
            if matching_item:
                weight_per_unit = matching_item.weight_per_unit or 0
            self.append('gate_pass_items_summary', {
                'item_code': item_code,
                'item_name': frappe.get_value("Item", item_code, 'item_name'),
                'item_group': frappe.get_value("Item", item_code, 'item_group'),
                'weight_per_unit': weight_per_unit,
                'total_weight': total_qty * weight_per_unit,
                'item_qty': total_qty,
            })

        for extra in self.extra_crate:
            if extra.quantity > 0:
                total_extra_crate += extra.quantity
        
        for si in sales_invoices:
            opening_qty, issue_qty = 0, 0
            for items in self.get('gate_pass_items', {'crate_qty':['>', 0], 'sales_invoice': si}):
                issue_qty += items.crate_qty
            customer =  frappe.get_value("Sales Invoice", si, 'customer')
            opening = frappe.db.sql("SELECT balance FROM `tabCrate Ledger` WHERE customer = %s", (customer), as_dict = True)
            if len(opening) > 0:
                opening_qty = opening[0]['balance']
            self.append('sales_invoice_details', {
                'sales_invoice': si,
                'customer': customer,
                'customer_name': frappe.get_value("Sales Invoice", si, 'customer_name'),
                'crate_openning_qty': opening_qty,
                'crate_issue_qty': issue_qty,
                'crate_balance_qty': opening_qty + issue_qty
            })

        for st in stock_entries:
            opening_qty, issue_qty = 0, 0
            for items in self.get('gate_pass_items', {'crate_qty':['>', 0], 'stock_entry': st}):
                issue_qty += items.crate_qty
            warehouse = frappe.get_value("Stock Entry Detail", {'parent': st}, 't_warehouse')
            opening = frappe.db.sql("SELECT balance FROM `tabCrate Ledger` WHERE warehouse = %s", (warehouse), as_dict = True)
            if len(opening) > 0:
                opening_qty = opening[0]['balance']
            self.append('stock_entry_details', {
                'stock_entry': st,
                'warehouse': warehouse,
                'crate_openning_qty': opening_qty,
                'crate_issue_qty': issue_qty,
                'crate_balance_qty': opening_qty + issue_qty
            })

        self.total_crate_qty = total_crate_qty
        self.total_extra_crate = total_extra_crate



@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, skip_item_mapping=False):
    doclist = get_mapped_doc("Sales Invoice", source_name, {
        "Sales Invoice": {
            "doctype": "BDF Gate Pass",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Sales Invoice Item": {
            "doctype": "BDF Gate Pass Items",
            "field_map": [
                ["stock_qty", 'item_qty'],
                ["item_code", "item_code"],
                ["item_name", "item_name"],
                ["stock_uom", "uom"],
                ["sales_invoice_item","name"],
                ["weight_per_unit","weight_per_unit"],
                ["total_weight","total_weight"],
                ["parent","sales_invoice"],
            ]
        }
    }, target_doc)

    return doclist


@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None, skip_item_mapping=False):
    doclist = get_mapped_doc("Stock Entry", source_name, {
        "Stock Entry": {
            "doctype": "BDF Gate Pass",
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Stock Entry Detail": {
            "doctype": "BDF Gate Pass Items",
            "field_map": [
                ["qty", "item_qty"],
                ["item_code", "item_code"],
                ["item_name", "item_name"],
                ["stock_uom", "uom"],
                ["parent", "stock_entry"],
            ]
        }
    }, target_doc)

    return doclist
