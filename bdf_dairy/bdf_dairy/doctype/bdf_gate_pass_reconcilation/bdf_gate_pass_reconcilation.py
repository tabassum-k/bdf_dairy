# Copyright (c) 2024, BDF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BDFGatePassReconcilation(Document):
	def on_cancel(self):
		gate_pass = frappe.get_doc("BDF Gate Pass", self.gate_pass)
		for si in self.sales_invoice_details:
			opening_qty = frappe.get_value("Crate Ledger", {'customer': si.customer, 'crate_type': si.crate_type}, 'balance') or 0
			crate_ledger = frappe.new_doc("Crate Ledger")
			crate_ledger.customer = si.customer
			crate_ledger.route = gate_pass.route
			crate_ledger.crate_type = si.crate_type
			crate_ledger.opening = opening_qty
			crate_ledger.issue_qty = -si.crate_extra_qty  
			crate_ledger.return_qty = -si.crate_return_qty  
			crate_ledger.balance = opening_qty - si.crate_extra_qty + si.crate_return_qty
			crate_ledger.bdf_gate_pass = self.gate_pass
			crate_ledger.save()

		for st in self.stock_entry_details:
			opening_qty = frappe.get_value("Crate Ledger", {'warehouse': st.warehouse, 'crate_type': st.crate_type}, 'balance') or 0
			crate_ledger = frappe.new_doc("Crate Ledger")
			crate_ledger.warehouse = st.warehouse
			crate_ledger.route = gate_pass.route
			crate_ledger.crate_type = st.crate_type
			crate_ledger.opening = opening_qty
			crate_ledger.issue_qty = st.crate_extra_qty  
			crate_ledger.return_qty = st.crate_return_qty
			crate_ledger.balance = opening_qty - st.crate_extra_qty + st.crate_return_qty
			crate_ledger.bdf_gate_pass = self.gate_pass
			crate_ledger.save()

		frappe.db.set_value("BDF Gate Pass", self.gate_pass, 'reconcilation_done', 0)
		frappe.db.commit()
  
		for si in self.get('sales_invoice_details', {'sales_invoice': ['!=', None]}):
			frappe.db.set_value("BDF Gate Pass Sales Invoice Details", {'parent': self.gate_pass, 'sales_invoice': si.sales_invoice}, 'crate_return_qty', 0)
			frappe.db.set_value("BDF Gate Pass Sales Invoice Details", {'parent': self.gate_pass, 'sales_invoice': si.sales_invoice}, 'crate_extra_qty', 0)
			frappe.db.set_value("BDF Gate Pass Sales Invoice Details", {'parent': self.gate_pass, 'sales_invoice': si.sales_invoice}, 'crate_balance_qty', 0)


		for st in self.get('stock_entry_details', {'stock_entry': ['!=', None]}):
			frappe.db.set_value("BDF Gate Pass Stock Entry Details", {'parent': self.gate_pass, 'stock_entry': st.stock_entry}, 'crate_return_qty', 0)
			frappe.db.set_value("BDF Gate Pass Stock Entry Details", {'parent': self.gate_pass, 'stock_entry': st.stock_entry}, 'crate_extra_qty', 0)
			frappe.db.set_value("BDF Gate Pass Stock Entry Details", {'parent': self.gate_pass, 'stock_entry': st.stock_entry}, 'crate_balance_qty', 0)

	def on_submit(self):
		gate_pass = frappe.get_doc("BDF Gate Pass",self.gate_pass)	
		for si in self.sales_invoice_details:
			opening_qty = frappe.get_value("Crate Ledger", {'customer': si.customer, 'crate_type': si.crate_type}, 'balance') or 0
			crate_ledger = frappe.new_doc("Crate Ledger")
			crate_ledger.customer = si.customer
			crate_ledger.route = gate_pass.route
			crate_ledger.crate_type = si.crate_type
			crate_ledger.opening = opening_qty
			crate_ledger.issue_qty = si.crate_extra_qty
			crate_ledger.return_qty = si.crate_return_qty
			crate_ledger.balance = opening_qty + si.crate_extra_qty - si.crate_return_qty
			crate_ledger.bdf_gate_pass = self.gate_pass
			crate_ledger.save()

		for st in self.stock_entry_details:
			opening_qty = frappe.get_value("Crate Ledger", {'warehouse': st.warehouse, 'crate_type': st.crate_type}, 'balance') or 0
			crate_ledger = frappe.new_doc("Crate Ledger")
			crate_ledger.warehouse = st.warehouse
			crate_ledger.route = gate_pass.route
			crate_ledger.crate_type = st.crate_type
			crate_ledger.opening = opening_qty
			crate_ledger.issue_qty = st.crate_extra_qty
			crate_ledger.return_qty = st.crate_return_qty
			crate_ledger.balance = opening_qty +  st.crate_extra_qty - st.crate_return_qty
			crate_ledger.bdf_gate_pass = self.gate_pass
			crate_ledger.save()
		frappe.db.set_value("BDF Gate Pass", self.gate_pass, 'reconcilation_done', 1)
		
		for si in self.get('sales_invoice_details', {'sales_invoice': ['!=', None]}):
			frappe.db.set_value("BDF Gate Pass Sales Invoice Details", {'parent': self.gate_pass, 'sales_invoice': si.sales_invoice}, 'crate_return_qty', si.crate_return_qty)
			frappe.db.set_value("BDF Gate Pass Sales Invoice Details", {'parent': self.gate_pass, 'sales_invoice': si.sales_invoice}, 'crate_extra_qty', si.crate_extra_qty)
			frappe.db.set_value("BDF Gate Pass Sales Invoice Details", {'parent': self.gate_pass, 'sales_invoice': si.sales_invoice}, 'crate_balance_qty', si.crate_balance_qty)

		for st in self.get('stock_entry_details', {'stock_entry': ['!=', None]}):
			frappe.db.set_value("BDF Gate Pass Stock Entry Details", {'parent': self.gate_pass, 'stock_entry': st.stock_entry}, 'crate_return_qty', st.crate_return_qty)
			frappe.db.set_value("BDF Gate Pass Stock Entry Details", {'parent': self.gate_pass, 'stock_entry': st.stock_entry}, 'crate_extra_qty', st.crate_extra_qty)
			frappe.db.set_value("BDF Gate Pass Stock Entry Details", {'parent': self.gate_pass, 'stock_entry': st.stock_entry}, 'crate_balance_qty', st.crate_balance_qty)


	def before_save(self):
		self.crate_summary.clear()
		total_opening_qty, total_issue_qty, total_return_qty, total_extra_qty = {}, {}, {}, {}
		extra_qty = {}
		for extra in self.get('extra_crate', {'quantity': ['>', 0]}):
			if extra.crate_type in extra_qty:
				extra_qty[extra.crate_type] += extra.quantity
			else:
				extra_qty[extra.crate_type] = extra.quantity

		challan_extra = {}
		for si in self.get('sales_invoice_details'):
			if si.crate_type in total_opening_qty:
				total_opening_qty[si.crate_type] += si.crate_openning_qty
			else:
				total_opening_qty[si.crate_type] = si.crate_openning_qty
	
			if si.crate_type in total_issue_qty:
				total_issue_qty[si.crate_type] += si.crate_issue_qty
			else:
				total_issue_qty[si.crate_type] = si.crate_issue_qty
	
			if si.crate_type in total_return_qty:
				total_return_qty[si.crate_type] += si.crate_return_qty
			else:
				total_return_qty[si.crate_type] = si.crate_return_qty

			if si.crate_type in challan_extra:
				challan_extra[si.crate_type] += si.crate_extra_qty
				total_extra_qty[si.crate_type] += si.crate_extra_qty
			else:
				total_extra_qty[si.crate_type] = si.crate_extra_qty
				challan_extra[si.crate_type] = si.crate_extra_qty
	
		for st in self.get('stock_entry_details'):
			if st.crate_type in total_opening_qty:
				total_opening_qty[st.crate_type] += st.crate_openning_qty
			else:
				total_opening_qty[st.crate_type] = si.crate_openning_qty
	
			if st.crate_type in total_issue_qty:
				total_issue_qty[st.crate_type] += st.crate_issue_qty
			else:
				total_issue_qty[st.crate_type] = st.crate_issue_qty
	
			if st.crate_type in total_return_qty:
				total_return_qty[st.crate_type] += st.crate_return_qty
			else:
				total_return_qty[st.crate_type] = st.crate_return_qty

			if st.crate_type in total_extra_qty:
				total_extra_qty[st.crate_type] += st.crate_extra_qty
			else:
				total_extra_qty[st.crate_type] = st.crate_extra_qty
	
		for extra in self.get('extra_crate'):
			if extra.crate_type in challan_extra:
				challan_extra[extra.crate_type] += extra.return_quantity
			else:
				challan_extra[extra.crate_type] = extra.return_quantity
	
		for crate, qty in extra_qty.items():
			if crate in challan_extra:
				if challan_extra[crate] > qty:
					frappe.throw("The extra quantity is more than sum of customer extra qty and return extra qty.")
				elif challan_extra[crate] < qty:
					frappe.throw("The extra quantity is less than sum of customer extra qty and return extra qty.")
				

		for si in self.sales_invoice_details:
			si.crate_balance_qty = si.crate_openning_qty + si.crate_issue_qty + si.crate_extra_qty - si.crate_return_qty
			
		for st in self.stock_entry_details:
			st.crate_balance_qty = st.crate_openning_qty + st.crate_issue_qty + st.crate_extra_qty - st.crate_return_qty

		for crate, qty in total_issue_qty.items():
			self.append('crate_summary',{
				'crate_type': crate,
				'crate_openning_qty': total_opening_qty[crate],
				'crate_issue_qty': total_issue_qty[crate],
				'crate_return_qty': total_return_qty[crate],
				'crate_extra_qty': total_extra_qty[crate],
				'crate_balance_qty': total_opening_qty[crate] + total_issue_qty[crate] + total_extra_qty[crate] - total_return_qty[crate]
			})

	@frappe.whitelist()
	def get_gate_pass_data(self):
		opening_qty = 0
		gate_pass = frappe.get_doc("BDF Gate Pass",self.gate_pass)
		for st in gate_pass.stock_entry_details:
			opening_qty = frappe.get_value("Crate Ledger", {'warehouse': st.warehouse, 'crate_type': st.crate_type}, 'balance') or 0
			self.append('stock_entry_details',{
				'stock_entry': st.stock_entry,
				'warehouse': st.warehouse,
				'crate_type': st.crate_type,
				'crate_openning_qty': opening_qty - st.crate_issue_qty,
				'crate_issue_qty': st.crate_issue_qty,
				'crate_balance_qty': st.crate_balance_qty		
			})

		for si in gate_pass.sales_invoice_details:
			opening_qty = frappe.get_value("Crate Ledger", {'customer': si.customer, 'crate_type': si.crate_type}, 'balance') or 0
			self.append('sales_invoice_details', {
				'sales_invoice': si.sales_invoice,
				'customer': si.customer,
				'customer_name': si.customer_name,
				'crate_type': si.crate_type,
				'crate_openning_qty': opening_qty - si.crate_issue_qty,
				'crate_issue_qty': si.crate_issue_qty,
				'crate_balance_qty': si.crate_balance_qty
			})

		for cr in gate_pass.extra_crate:
			self.append('extra_crate',{
				'crate_type': cr.crate_type,
				'quantity': cr.quantity
			})

	# @frappe.whitelist()
	# def get_customer_opening(self, customer, crate_type):
	# 	opening = frappe.db.sql("""
	# 			SELECT balance 
	# 			FROM `tabCrate Ledger` 
	# 			WHERE customer = %s AND crate_type = %s 
	# 			ORDER BY creation DESC 
	# 			LIMIT 1
	# 		""", (customer, crate_type), as_dict=True)
	# 	if len(opening) > 0:
	# 		return opening[0]['balance']
	# 	else:
	# 		return 0

	# @frappe.whitelist()
	# def get_warehouse_opening(self, warehouse, crate_type):
	# 	opening = frappe.db.sql("""
	# 		SELECT balance 
	# 		FROM `tabCrate Ledger` 
	# 		WHERE warehouse = %s AND crate_type = %s 
	# 		ORDER BY creation DESC 
	# 		LIMIT 1
	# 	""", (warehouse, crate_type), as_dict=True)
	# 	if len(opening) > 0:
	# 		return opening[0]['balance']
	# 	else:
	# 		return 0