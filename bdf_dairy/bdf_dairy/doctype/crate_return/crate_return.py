# Copyright (c) 2025, BDF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CrateReturn(Document):
	@frappe.whitelist()
	def get_all_customer(self):
		customer = []
		bdf_gate = frappe.get_doc("BDF Gate Pass", self.bdf_gate_pass)
		for cust in bdf_gate.sales_invoice_details:
			if cust.customer not in customer:
				customer.append(cust.customer)
		return customer

	@frappe.whitelist()
	def get_opening_qty(self):
		opening = frappe.db.sql("""
				SELECT balance 
				FROM `tabCrate Ledger` 
				WHERE customer = %s AND crate_type = %s 
				ORDER BY creation DESC 
				LIMIT 1
			""", (self.customer, self.crate_type), as_dict=True)
		return opening[0]['balance'] if opening else 0

	def before_submit(self):
		if self.return_quantity > 0:
			opening_qty = 0
			opening = frappe.db.sql("""
				SELECT balance 
				FROM `tabCrate Ledger` 
				WHERE customer = %s AND crate_type = %s 
				ORDER BY creation DESC 
				LIMIT 1
			""", (self.customer, self.crate_type), as_dict=True)

			if len(opening) > 0:
				opening_qty = opening[0]['balance']
			crate_ledger = frappe.new_doc("Crate Ledger")
			crate_ledger.customer = self.customer
			crate_ledger.route = self.route
			crate_ledger.crate_type = self.crate_type
			crate_ledger.opening = opening_qty
			crate_ledger.issue_qty = 0
			crate_ledger.return_qty = self.return_quantity
			crate_ledger.balance = opening_qty - self.return_quantity
			crate_ledger.crate_return = self.name
			crate_ledger.save()