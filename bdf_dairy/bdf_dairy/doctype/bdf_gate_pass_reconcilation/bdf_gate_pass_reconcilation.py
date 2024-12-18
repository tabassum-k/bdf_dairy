# Copyright (c) 2024, BDF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BDFGatePassReconcilation(Document):
	def on_submit(self):
		gate_pass = frappe.get_doc("BDF Gate Pass",self.gate_pass)
		for si in self.sales_invoice_details:
			opening = frappe.db.sql("SELECT balance FROM `tabCrate Ledger` WHERE customer = %s", (si.customer), as_dict = True)
			if len(opening) > 0:
				opening_qty = opening[0]['balance']
			else:
				opening_qty = 0
			crate_ledger = frappe.new_doc("Crate Ledger")
			crate_ledger.customer = si.customer
			crate_ledger.route = gate_pass.route
			crate_ledger.crate_type = "Blue Crate"
			crate_ledger.opening = opening_qty
			crate_ledger.issue_qty = si.crate_issue_qty
			crate_ledger.return_qty = 0
			crate_ledger.balance = opening_qty +  si.crate_issue_qty
			crate_ledger.bdf_gate_pass = self.gate_pass
			crate_ledger.save()

		for st in self.stock_entry_details:
			opening_qty = 0	
			opening = frappe.db.sql("SELECT balance FROM `tabCrate Ledger` WHERE warehouse = %s", (st.warehouse), as_dict = True)
			if len(opening) > 0:
				opening_qty = opening[0]['balance']
			crate_ledger = frappe.new_doc("Crate Ledger")
			crate_ledger.warehouse = st.warehouse
			crate_ledger.route = gate_pass.route
			crate_ledger.crate_type = "Blue Crate"
			crate_ledger.opening = opening_qty
			crate_ledger.issue_qty = si.crate_extra_qty
			crate_ledger.return_qty = si.crate_return_qty
			crate_ledger.balance = opening_qty +  si.crate_extra_qty - si.crate_return_qty
			crate_ledger.bdf_gate_pass = self.gate_pass
			crate_ledger.save()
		frappe.db.set_value("BDF Gate Pass", self.gate_pass, 'reconcilation_done', 1)

	def before_save(self):
		for si in self.sales_invoice_details:
			si.crate_balance_qty = si.crate_issue_qty + si.crate_extra_qty - si.crate_return_qty
			
		for st in self.stock_entry_details:
			st.crate_balance_qty = st.crate_issue_qty + st.crate_extra_qty - st.crate_return_qty

	@frappe.whitelist()
	def get_gate_pass_data(self):
		opening_qty = 0
		gate_pass = frappe.get_doc("BDF Gate Pass",self.gate_pass)
		for st in gate_pass.stock_entry_details:
			self.append('stock_entry_details',{
				'stock_entry': st.stock_entry,
				'warehouse': st.warehouse,
				'crate_openning_qty': st.crate_openning_qty,
				'crate_issue_qty': st.crate_issue_qty,
				'crate_balance_qty': st.crate_balance_qty		
			})
		for si in gate_pass.sales_invoice_details:	
			self.append('sales_invoice_details', {
				'sales_invoice': si.sales_invoice,
				'customer': si.customer,
				'customer_name': si.customer_name,
				'crate_openning_qty': si.crate_openning_qty,
				'crate_issue_qty': si.crate_issue_qty,
				'crate_balance_qty': si.crate_balance_qty
			})
		for cr in gate_pass.extra_crate:
			self.append('extra_crate',{
				'crate_type': cr.crate_type,
				'extra': cr.quantity
			})
