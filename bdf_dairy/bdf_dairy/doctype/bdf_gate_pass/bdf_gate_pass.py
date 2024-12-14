import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import math

class BDFGatePass(Document):
	def before_save(self):
		self.sales_invoice_details.clear()
		self.stock_entry_details.clear()
		self.gate_pass_item.clear()
		sales_invoice, stock_entry = [], []
		item_qty_sum = {}
		total_crate_qty, total_extra_crate = 0, 0
		for i in self.gate_pass_items:
			if i.item_code:
				if i.item_code not in item_qty_sum:
					item_qty_sum[i.item_code] = 0
				item_qty_sum[i.item_code] += i.item_qty or 0

		for i in self.get('gate_pass_items', filters={'sales_invoice': ['!=', None], 'item_qty': ['not in', [None, 0]]}):
			if i.sales_invoice not in sales_invoice:
				sales_invoice.append(i.sales_invoice)

		for i in self.get('gate_pass_items', filters={'stock_entry': ['!=', None], 'item_qty': ['not in', [None, 0]]}):
			if i.stock_entry not in stock_entry:
				stock_entry.append(i.stock_entry)

		for si in sales_invoice:
			self.append('sales_invoice_details', {
				'sales_invoice': si,
				'customer': frappe.get_value("Sales Invoice", si, 'customer')
			})

		for st in stock_entry:
			self.append('stock_entry_details', {
				'stock_entry': st,
				'warehouse': frappe.get_value("Stock Entry Detail", {'parent': st}, 't_warehouse')
			})

		for item_code, total_qty in item_qty_sum.items():
			weight_per_unit =0
			if self.get('gate_pass_items', {'item_code': item_code}):
				weight_per_unit = self.get('gate_pass_items', {'item_code': item_code})[0].weight_per_unit
			count = 0
			item_doc = frappe.get_doc("Item",item_code)
			if item_doc.crate:
				for itm in item_doc.crate:
					if itm.crate_quantity and itm.crate_type and count == 0:
						crate_qty = math.ceil(total_qty/ itm.crate_quantity)
						total_crate_qty += crate_qty
						self.append('gate_pass_item', {
							'item_code': item_code,
							'item_name': frappe.get_value("Item", item_code, 'item_name'),
							'item_group': frappe.get_value("Item", item_code, 'item_group'),
							'weight_per_unit': weight_per_unit,
							'total_weight': total_qty * weight_per_unit,
							'item_qty': total_qty,
							'crate_type': itm.crate_type,
							'crate_qty': crate_qty,
						})
						count = 1
			else:
				self.append('gate_pass_item', {
					'item_code': item_code,
					'item_name': frappe.get_value("Item", item_code, 'item_name'),
					'item_group': frappe.get_value("Item", item_code, 'item_group'),
					'weight_per_unit': weight_per_unit,
					'total_weight': total_qty * weight_per_unit,
					'item_qty': total_qty,
				})
    
		for extra in self.get('extra_crate', {'quantity': ['>', 0]}):
			total_extra_crate += extra.quantity
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
