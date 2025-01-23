import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import math


class BDFGatePass(Document):
    def on_update_after_submit(self):
        total_extra_crate = 0
        for ext in self.extra_crate:
            total_extra_crate += ext.quantity
        self.total_extra_crate = total_extra_crate
    
    def on_cancel(self):
        for si in self.sales_invoice_details:
            opening_qty = frappe.get_value("Crate Ledger", {'customer': si.customer, 'crate_type': si.crate_type}, 'balance') or 0
            crate_ledger = frappe.new_doc("Crate Ledger")
            crate_ledger.customer = si.customer
            crate_ledger.route = self.route
            crate_ledger.crate_type = si.crate_type
            crate_ledger.opening = opening_qty
            crate_ledger.issue_qty = 0
            crate_ledger.return_qty = si.crate_issue_qty
            crate_ledger.balance = opening_qty - si.crate_issue_qty
            crate_ledger.bdf_gate_pass = self.name
            crate_ledger.save()
            frappe.db.set_value("Sales Invoice", si.sales_invoice, 'gate_pass', 0)
        for st in self.stock_entry_details:
            opening_qty = frappe.get_value("Crate Ledger", {'warehouse': st.warehouse, 'crate_type': st.crate_type}, 'balance') or 0
            crate_ledger = frappe.new_doc("Crate Ledger")
            crate_ledger.warehouse = st.warehouse
            crate_ledger.route = self.route
            crate_ledger.crate_type = st.crate_type
            crate_ledger.opening = opening_qty
            crate_ledger.issue_qty = 0
            crate_ledger.return_qty = st.crate_issue_qty
            crate_ledger.balance = opening_qty - st.crate_issue_qty
            crate_ledger.bdf_gate_pass = self.name
            crate_ledger.save()
            frappe.db.set_value("Stock Entry", st.stock_entry, 'custom_gate_pass', 0)


    def on_submit(self):
        for si in self.sales_invoice_details:
            opening_qty = frappe.get_value("Crate Ledger", {'customer': si.customer, 'crate_type': si.crate_type}, 'balance') or 0
            crate_ledger = frappe.new_doc("Crate Ledger")
            crate_ledger.customer = si.customer
            crate_ledger.route = self.route
            crate_ledger.crate_type = si.crate_type
            crate_ledger.opening = opening_qty
            crate_ledger.issue_qty = si.crate_issue_qty
            crate_ledger.return_qty = 0
            crate_ledger.balance = opening_qty +  si.crate_issue_qty
            crate_ledger.bdf_gate_pass = self.name
            crate_ledger.save()
            frappe.db.set_value("Sales Invoice", si.sales_invoice, 'gate_pass', 1)

        for st in self.stock_entry_details:
            opening_qty = frappe.get_value("Crate Ledger", {'warehouse': st.warehouse, 'crate_type': st.crate_type}, 'balance') or 0
            crate_ledger = frappe.new_doc("Crate Ledger")
            crate_ledger.warehouse = st.warehouse
            crate_ledger.route = self.route
            crate_ledger.crate_type = st.crate_type
            crate_ledger.opening = opening_qty
            crate_ledger.issue_qty = st.crate_issue_qty
            crate_ledger.return_qty = 0
            crate_ledger.balance = opening_qty +  st.crate_issue_qty
            crate_ledger.bdf_gate_pass = self.name
            crate_ledger.save()
            frappe.db.set_value("Stock Entry", st.stock_entry, 'custom_gate_pass', 1)

    def before_save(self):
        self.sales_invoice_details.clear()
        self.stock_entry_details.clear()
        self.gate_pass_items_summary.clear()
        self.total_crate_summary.clear()
        self.challan_crate_summary.clear()

        sales_invoices = {}
        stock_entries = {}
        item_qty_sum = {}
        total_crate_qty, total_extra_crate, challan_wise_crate, total_supply_qty, grand_total = 0, 0, 0, 0, 0
        total_opening_qty, total_issue_qty = {}, {}

        for i in self.gate_pass_items:
            count = 0
            if i.item_code:
                item_qty_sum[i.item_code] = item_qty_sum.get(i.item_code, 0) + (i.item_qty or 0)
            
            if i.sales_invoice:
                if i.sales_invoice in sales_invoices:
                    sales_invoices[i.sales_invoice] += i.item_qty
                else:
                    sales_invoices[i.sales_invoice] = i.item_qty
                
            if i.stock_entry:
                if i.stock_entry in stock_entries:
                    stock_entries[i.stock_entry] += i.item_qty
                else:
                    stock_entries[i.stock_entry] = i.item_qty

        for it in self.gate_pass_items:
            count = 0
            if not it.item_code or not it.item_qty:
                continue
            item_doc = frappe.get_doc("Item", it.item_code)
            if hasattr(item_doc, 'crate') and item_doc.crate:
                for itm in item_doc.crate:
                    if itm.crate_quantity and itm.crate_type and count == 0:
                        limit = frappe.db.get_value('Crate Type', itm.crate_type, 'limit')
                        if limit:
                            crate_qty = math.ceil(it.item_qty / itm.crate_quantity)
                        else:
                            crate_qty = math.floor(it.item_qty / itm.crate_quantity)
                        it.crate_type = itm.crate_type
                        it.crate_qty = crate_qty
                        challan_wise_crate += crate_qty
                        count = 1

        for item_code, total_qty in item_qty_sum.items():
            weight_per_unit, count = 0, 0
            matching_item = next((itm for itm in self.gate_pass_items if itm.item_code == item_code), None)
            if matching_item:
                weight_per_unit = matching_item.weight_per_unit or 0
            item_doc = frappe.get_doc("Item", item_code)
            if hasattr(item_doc, 'crate') and item_doc.crate:
                for itm in item_doc.crate:
                    if itm.crate_quantity and itm.crate_type and count == 0:
                        limit = frappe.db.get_value('Crate Type', itm.crate_type, 'limit')
                        if limit:
                            crate_qty = math.ceil(total_qty / itm.crate_quantity)
                        else:
                            crate_qty = math.floor(total_qty / itm.crate_quantity)
                        loose_qty = total_qty - (crate_qty * itm.crate_quantity)
                        self.append('gate_pass_items_summary', {
                            'item_code': item_code,
                            'item_name': frappe.get_value("Item", item_code, 'item_name'),
                            'item_group': frappe.get_value("Item", item_code, 'item_group'),
                            'weight_per_unit': weight_per_unit,
                            'total_weight': total_qty * weight_per_unit,
                            'item_qty': total_qty,
                            'crate_type': itm.crate_type,
                            'crate_qty': crate_qty,
                            'loose_qty': loose_qty if loose_qty > 0 else 0
                        })
                        total_crate_qty += crate_qty
                        count = 1
            else:
                self.append('gate_pass_items_summary', {
                    'item_code': item_code,
                    'item_name': frappe.get_value("Item", item_code, 'item_name'),
                    'item_group': frappe.get_value("Item", item_code, 'item_group'),
                    'weight_per_unit': weight_per_unit,
                    'total_weight': total_qty * weight_per_unit,
                    'item_qty': total_qty,
                })
        
        crate_types = {}
        for items in self.get('gate_pass_items_summary'):
            if items.crate_qty is not None and items.crate_qty > 0 and items.crate_type:
                crate_types[items.crate_type] = crate_types.get(items.crate_type, 0) + items.crate_qty


        for crate, qty in crate_types.items():
            self.append('total_crate_summary', {
                'crate_type': crate,
                'quantity': qty
            })
            

        for si, supply_qty in sales_invoices.items():
            issue_qty = 0
            crate_types = {}
            for items in self.get('gate_pass_items', {'crate_qty': ['>', 0], 'sales_invoice': si}):
                issue_qty += items.crate_qty
                crate_types[items.crate_type] = crate_types.get(items.crate_type, 0) + items.crate_qty
            for crate, qty in crate_types.items():
                customer = frappe.get_value("Sales Invoice", si, 'customer')
                opening_qty = frappe.get_value("Crate Ledger", {'customer': customer, 'crate_type': crate}, 'balance') or 0
                if crate in total_opening_qty:
                    total_opening_qty[crate] += opening_qty
                else:
                    total_opening_qty[crate] = opening_qty
                    
                if crate in total_issue_qty:
                    total_issue_qty[crate] += qty
                else:
                    total_issue_qty[crate] = qty
                total_supply_qty += supply_qty
                grand_tot = frappe.get_value("Sales Invoice", si, 'rounded_total')
                grand_total += grand_tot
                self.append('sales_invoice_details', {
                    'sales_invoice': si,
                    'customer': customer,
                    'supply_qty': supply_qty,
                    'customer_name': frappe.get_value("Sales Invoice", si, 'customer_name'),
                    'crate_openning_qty': opening_qty,
                    'crate_issue_qty': qty,
                    'crate_balance_qty': opening_qty + qty,
                    'crate_type': crate,
                    'grand_total': grand_tot
                })

        for st, supply_qty in stock_entries.items():
            opening_qty, issue_qty = 0, 0
            crate_types = {}
            for items in self.get('gate_pass_items', {'crate_qty': ['>', 0], 'stock_entry': st}):
                issue_qty += items.crate_qty
                crate_types[items.crate_type] = crate_types.get(items.crate_type, 0) + items.crate_qty
            for crate, qty in crate_types.items():
                warehouse = frappe.get_value("Stock Entry Detail", {'parent': st}, 't_warehouse')
                opening = frappe.get_value("Crate Ledger", {'warehouse': warehouse, 'crate_type': crate}, 'balance') or 0
                if crate in total_opening_qty:
                    total_opening_qty[crate] += opening_qty
                else:
                    total_opening_qty[crate] = opening_qty
                    
                if crate in total_issue_qty :
                    total_issue_qty[crate] += qty
                else:
                    total_issue_qty[crate] = qty
                total_supply_qty += supply_qty
                grand_tot = frappe.get_value("Stock Entry", st, 'total_incoming_value')    
                grand_total += grand_tot
                
                self.append('stock_entry_details', {
                    'stock_entry': st,
                    'warehouse': warehouse,
                    'supply_qty': supply_qty,
                    'crate_openning_qty': opening_qty,
                    'crate_issue_qty': qty,
                    'crate_balance_qty': opening_qty + qty,
                    'crate_type': crate,
                    'grand_total': grand_tot
                })

        for extra in self.extra_crate:
            if extra.quantity > 0:
                total_extra_crate += extra.quantity
        
        for crate, qty in total_opening_qty.items():
            self.append("challan_crate_summary", {
                'crate_type': crate,
                'crate_openning_qty': total_opening_qty[crate],
                'crate_issue_qty': total_issue_qty[crate],
                'crate_balance_qty': total_opening_qty[crate] + total_issue_qty[crate]
            })
            
        self.total_supply_qty = total_supply_qty
        self.grand_total = grand_total
        self.total_crate_qty = total_crate_qty
        self.total_extra_crate = total_extra_crate

    @frappe.whitelist()
    def calculate_extra_crate(self):
        self.extra_crate.clear()
        total_qty = {}
        challan_qty = {}
        total_extra_crate = 0
        
        for tq in self.get('total_crate_summary'):
            total_qty[tq.crate_type] = tq.quantity

        for si in self.get('sales_invoice_details'):
            if si.crate_type in challan_qty:
                challan_qty[si.crate_type] += si.crate_issue_qty
            else:
                challan_qty[si.crate_type] = si.crate_issue_qty

        for st in self.get('stock_entry_details'):
            if st.crate_type in challan_qty:
                challan_qty[st.crate_type] += st.crate_issue_qty
            else:
                challan_qty[st.crate_type] = st.crate_issue_qty

        extra = {}
        for crate_type, qty in total_qty.items():
            extra[crate_type] = qty - challan_qty.get(crate_type, 0)

        for crate_type, quantity in extra.items():
            if quantity > 0:
                total_extra_crate += quantity
                self.append('extra_crate', {
                    'crate_type': crate_type,
                    'quantity': quantity
                })
        self.total_extra_crate = total_extra_crate
        self.save()

    # @frappe.whitelist()
    # def get_customer_opening(self, customer, crate_type):
    #     opening = frappe.db.sql("""
    #             SELECT balance 
    #             FROM `tabCrate Ledger` 
    #             WHERE customer = %s AND crate_type = %s 
    #             ORDER BY creation DESC 
    #             LIMIT 1
    #         """, (customer, crate_type), as_dict=True)
    #     if len(opening) > 0:
    #         return opening[0]['balance']
    #     else:
    #         return 0

    # @frappe.whitelist()
    # def get_warehouse_opening(self, warehouse, crate_type):
    #     opening = frappe.db.sql("""
    #         SELECT balance 
    #         FROM `tabCrate Ledger` 
    #         WHERE warehouse = %s AND crate_type = %s 
    #         ORDER BY creation DESC 
    #         LIMIT 1
    #     """, (warehouse, crate_type), as_dict=True)
    #     if len(opening) > 0:
    #         return opening[0]['balance']
    #     else:
    #         return 0
    


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
