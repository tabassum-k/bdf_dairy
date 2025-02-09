# Copyright (c) 2025, BDF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BDFBulkPaymentEntry(Document):
	def on_submit(self):
		self.payment_entry()

	
	@frappe.whitelist()
	def set_party_type(self):
		if self.party_type and self.payment_type:
			for i in self.get("bulk_payment_entry_details"):
				i.party_type = self.party_type
				i.payment_type = self.payment_type


	@frappe.whitelist()
	def set_pn(self):
		for account in self.get('bulk_payment_entry_details'):
			if account.party:
				account.reference_id = account.name
				if account.party_type == "Customer":
					field = 'customer_name'
				elif account.party_type == "Supplier":
					field = 'supplier_name'
				elif account.party_type == "Employee":
					field = 'employee_name'
				else:
					field = 'title'
				account.party_name = frappe.db.get_value(account.party_type, {"name": account.party}, field)


	@frappe.whitelist()
	def get_accounts(self):
		self.get_bank_account()
		self.get_paid_to_account()


	@frappe.whitelist()
	def get_bank_account(self):
		# frappe.msgprint("hiii")
		for i in self.get("bulk_payment_entry_details"):
			if i.party and i.party_type == "Supplier":  # Fixed party_type comparison
				ba = frappe.get_value('Party Account', {'parent': i.party}, "account")
				if ba:
					i.paid_to = ba
				else:
					gets = frappe.get_value('Supplier', {'name': i.party}, "supplier_group")
					if gets:
						grpba = frappe.get_value('Party Account', {'parent': gets}, "account")
						if grpba:
							i.paid_to = grpba
						else:
							cdpba = frappe.get_value('Company', {'name': self.company}, "default_payable_account")
							if cdpba:
								i.paid_to = cdpba

			else:
				if i.party and i.party_type == "Customer":  
					ba = frappe.get_value('Party Account', {'parent': i.party}, "account")
					if ba:
						i.paid_from = ba
					else:
						gets = frappe.get_value('Customer', {'name': i.party}, "customer_group")
						if gets:
							grpba = frappe.get_value('Party Account', {'parent': gets}, "account")
							if grpba:
								i.paid_from = grpba
							else:
								cdpba = frappe.get_value('Company', {'name': self.company}, "default_receivable_account")
								if cdpba:
		
									i.paid_from = cdpba

	@frappe.whitelist()
	def get_paid_to_account(self):
		mode_of_payment_account = frappe.get_value("Mode of Payment Account", {'parent': self.mode_of_payment, 'company': self.company}, "default_account")
		# frappe.throw(str(mode_of_payment_account))
		for i in self.get("bulk_payment_entry_details"):
			if i.party_type == "Supplier" and i.payment_type == "Pay":
				# frappe.throw(str(mode_of_payment_account))
				i.paid_from = mode_of_payment_account
			elif i.party_type == "Customer" and i.payment_type == "Receive":
				i.paid_to = mode_of_payment_account

		
	@frappe.whitelist()
	def call_two_in_one(self):
		self.check_invoice()
		self.check_orders()

	@frappe.whitelist()
	def check_orders(self):
		self.get_entries_so()
		self.get_entries_po()
		
	@frappe.whitelist()
	def check_invoice(self):
		self.get_entries()
		self.get_entries_pi()

	@frappe.whitelist()
	def get_entries(self):
		for i in self.get("bulk_payment_entry_details"):
			# i.reference_id = i.name
			if i.check ==1 and i.party_type == "Customer" and self.payment_type =="Receive":
			
				doc = frappe.get_list("Sales Invoice", 
							filters={"customer": i.party,"posting_date": ["between", [i.from_date, i.to_date]], "outstanding_amount": (">", 0), "status":["in",["Overdue","Partly Paid","Unpaid","Unpaid and Discounted","Overdue and Discounted","Partly Paid and Discounted"]]},
							fields=["name","grand_total","outstanding_amount","posting_date"],)

				# frappe.throw(str(doc))
				if(doc):
					for d in doc:
						self.append('payment_reference', {
															"party_type":i.party_type,
															"party_name":i.party_name,
															"reference_doctype":"Sales Invoice",
															"reference_name":d.name,
															"total_amount":d.grand_total,
															'reference_id':i.reference_id,
															"outstanding_amount":d.outstanding_amount,
															"posting_date":d.posting_date,

															})
			else:
				if i.check ==1 and i.party_type == "Customer" and self.payment_type =="Pay":
					frappe.throw("Cannot Pay to Customer without any negative outstanding invoice")




	@frappe.whitelist()
	def get_entries_so(self):
		for i in self.get("bulk_payment_entry_details"):
			# i.reference_id = i.name		
			if i.check2 ==1 and i.party_type == "Customer" and self.payment_type =="Receive":
				doc = frappe.get_list("Sales Order", 
						filters={"customer": i.party,"transaction_date": ["between", [i.from_date1, i.to_date1]],"billing_status":["in",["Not Billed","Partly Billed"]]},
						fields=["name","grand_total","rounded_total","advance_paid","transaction_date"],)

				# frappe.throw(str(doc))
				if(doc):
					for d in doc:
						self.append('payment_reference', {
															"party_type":i.party_type,
															"party_name":i.party_name,
															"reference_doctype":"Sales Order",
															"reference_name":d.name,
															"total_amount":d.grand_total,
															'reference_id':i.reference_id,
															"outstanding_amount":(d.rounded_total)-(d.advance_paid),
															"posting_date":d.transaction_date,
						
													})

			else:
				if i.check2 ==1 and i.party_type == "Customer" and self.payment_type =="Pay":
					frappe.throw("Cannot Pay to Customer without any negative outstanding invoice")




	@frappe.whitelist()
	def get_entries_pi(self):
		for i in self.get("bulk_payment_entry_details"):
			# i.reference_id = i.name
			if i.check ==1 and i.party_type == "Supplier" and self.payment_type =="Pay":
			
				doc = frappe.get_list("Purchase Invoice", 
							filters={"supplier": i.party,"posting_date": ["between", [i.from_date, i.to_date]],"outstanding_amount": (">", 0),"status":["in",["Overdue", "Partly Paid", "Unpaid"]]},
							fields=["name","grand_total","outstanding_amount","posting_date"],)

				# frappe.throw(str(doc))
				if(doc):
					for d in doc:
						self.append('payment_reference', {
															"party_type":i.party_type,
															"party_name":i.party_name,
															"reference_doctype":"Purchase Invoice",
															"reference_name":d.name,
															"total_amount":d.grand_total,
															'reference_id':i.name,
															"outstanding_amount":d.outstanding_amount,
															"posting_date":d.posting_date,

															})
			else:
				if i.check ==1 and i.party_type == "Supplier" and self.payment_type =="Receive":
					frappe.throw("Cannot Receive from Supplier without any negative outstanding invoice")


	@frappe.whitelist()
	def get_entries_po(self):
		for i in self.get("bulk_payment_entry_details"):
			# i.reference_id = i.name
			if i.check2 ==1 and i.party_type == "Supplier" and self.payment_type =="Pay":
				doc = frappe.get_list("Purchase Order", 
							filters={"supplier": i.party,"transaction_date": ["between", [i.from_date1, i.to_date1]],"status":["in",["To Bill", "To Receive and Bill", "To Receive" ]]},
							fields=["name","grand_total","rounded_total","advance_paid","transaction_date"],)

				# frappe.throw(str(doc))
				if(doc):
					for d in doc:
						self.append('payment_reference', {
															"party_type":i.party_type,
															"party_name":i.party_name,
															"reference_doctype":"Purchase Order",
															"reference_name":d.name,
															"total_amount":d.grand_total,
															'reference_id':i.name,
															"outstanding_amount":(d.rounded_total)-(d.advance_paid),
															"posting_date":d.transaction_date,

															})
			else:
				if i.check2 ==1 and i.party_type == "Supplier" and self.payment_type =="Receive":
					frappe.throw("Cannot Receive from Supplier without any negative outstanding invoice")



	@frappe.whitelist()
	def get_outstanding(self):
		self.invoices()
		self.orders()

	@frappe.whitelist()
	def invoices(self):
		self.get_all_sinvoices()
		self.get_all_pinvoices()
	
	@frappe.whitelist()
	def get_all_sinvoices(self):
		for i in self.get("bulk_payment_entry_details"):
			if i.party_type == "Customer" and self.payment_type =="Receive" and self.from_date and self.to_date:	
				doc = frappe.get_list("Sales Invoice", 
							filters={"customer": i.party,"posting_date": ["between", [self.from_date, self.to_date]], "outstanding_amount": (">", 0), "status":["in",["Overdue","Partly Paid","Unpaid","Unpaid and Discounted","Overdue and Discounted","Partly Paid and Discounted"]]},
							fields=["name","grand_total","outstanding_amount","posting_date"],)

				# frappe.throw(str(doc))
				if(doc):
					for d in doc:
						self.append('payment_reference', {
															"party_type":i.party_type,
															"party_name":i.party_name,
															"reference_doctype":"Sales Invoice",
															"reference_name":d.name,
															"total_amount":d.grand_total,
															'reference_id':i.name,
															"outstanding_amount":d.outstanding_amount,
															"posting_date":d.posting_date,

															})
			else:
				if i.party_type == "Customer" and self.payment_type =="Pay":
					frappe.throw("Cannot Pay to Customer without any negative outstanding invoice")

	@frappe.whitelist()
	def get_all_pinvoices(self):
		for i in self.get("bulk_payment_entry_details"):
			# i.reference_id = i.name
			if i.party_type == "Supplier" and self.payment_type =="Pay" and self.from_date and self.to_date:
			
				doc = frappe.get_list("Purchase Invoice", 
							filters={"supplier": i.party,"docstatus":1,"posting_date": ["between", [self.from_date, self.to_date]],"outstanding_amount": (">", 0),"status":["in",["Overdue", "Partly Paid", "Unpaid"]]},
							fields=["name","grand_total","outstanding_amount","posting_date"],)

				# frappe.throw(str(doc))
				if(doc):
					for d in doc:
						self.append('payment_reference', {
															"party_type":i.party_type,
															"party_name":i.party_name,
															"reference_doctype":"Purchase Invoice",
															"reference_name":d.name,
															"total_amount":d.grand_total,
															'reference_id':i.reference_id,
															"outstanding_amount":d.outstanding_amount,
															"posting_date":d.posting_date,

															})
			else:
				if i.party_type == "Supplier" and self.payment_type =="Receive":
					frappe.throw("Cannot Receive from Supplier without any negative outstanding invoice")
	
	

	@frappe.whitelist()
	def orders(self):
		self.get_all_sorders()
		self.get_all_porders()

	@frappe.whitelist()
	def get_all_sorders(self):
		for i in self.get("bulk_payment_entry_details"):
			# i.reference_id = i.name		
			if i.party_type == "Customer" and self.payment_type =="Receive" and self.from_date and self.to_date:
				doc = frappe.get_list("Sales Order", 
						filters={"customer": i.party,"transaction_date": ["between", [self.from_date, self.to_date]],"billing_status":["in",["Not Billed","Partly Billed"]]},
						fields=["name","grand_total","rounded_total","advance_paid","transaction_date"],)

				# frappe.throw(str(doc))
				if(doc):
					for d in doc:
						outstanding_amount = d.rounded_total - d.advance_paid
						if outstanding_amount > 0:
							self.append('payment_reference', {
																"party_type":i.party_type,
																"party_name":i.party_name,
																"reference_doctype":"Sales Order",
																"reference_name":d.name,
																"total_amount":d.grand_total,
																'reference_id':i.reference_id,
																"outstanding_amount":(d.rounded_total)-(d.advance_paid),
																"posting_date":d.transaction_date,
							
														})

			else:
				if i.party_type == "Customer" and self.payment_type =="Pay":
					frappe.throw("Cannot Pay to Customer without any negative outstanding invoice")


	@frappe.whitelist()
	def get_all_porders(self):
		for i in self.get("bulk_payment_entry_details"):
			# i.reference_id = i.name
			if i.party_type == "Supplier" and self.payment_type =="Pay" and self.from_date and self.to_date:
				doc = frappe.get_list("Purchase Order", 
							filters={"supplier": i.party,"transaction_date": ["between", [self.from_date, self.to_date]],"status":["in",["To Bill", "To Receive and Bill", "To Receive" ]]},
							fields=["name","grand_total","rounded_total","advance_paid","transaction_date"],)

				# frappe.throw(str(doc))
				if(doc):
					for d in doc:
						outstanding_amount = d.rounded_total - d.advance_paid
						if outstanding_amount > 0:
							self.append('payment_reference', {
																"party_type":i.party_type,
																"party_name":i.party_name,
																"reference_doctype":"Purchase Order",
																"reference_name":d.name,
																"total_amount":d.grand_total,
																'reference_id':i.reference_id,
																"outstanding_amount":(d.rounded_total)-(d.advance_paid),
																"posting_date":d.transaction_date,

																})
			else:
				if i.party_type == "Supplier" and self.payment_type =="Receive":
					frappe.throw("Cannot Receive from Supplier without any negative outstanding invoice")



	@frappe.whitelist()
	def get_allocatedsum(self):
		for i in self.get("bulk_payment_entry_details"):
			total_asum = 0  # Initialize outside the loop
			for j in self.get("payment_reference", {'reference_id': i.reference_id}):
				allocated_amount = 0
				if j.allocated_amount:
					total_asum += j.allocated_amount  # Corrected increment operation
			i.paid_amount = total_asum
			

	@frappe.whitelist()
	def gate_pass_cll(self):
		self.get_gate_pass()
		self.get_accounts()
		self.get_allocatedsum()


	@frappe.whitelist()
	def get_gate_pass(self):
		if self.party_type =="Customer":
			for i in self.get("gate_pass"):	
				child_data=frappe.get_all("Crate Summary",filters={"parent":i.gate_pass},fields=["voucher_type","voucher","name","parent"])
				for j in child_data:
					doc = frappe.get_list("Sales Invoice", filters={"name":j.voucher,"outstanding_amount": (">", 0), "status":["in",["Overdue","Partly Paid","Unpaid","Unpaid and Discounted","Overdue and Discounted","Partly Paid and Discounted"]]},fields=["grand_total","outstanding_amount","customer","party_balance"],)
					for k in doc:
						self.append("bulk_payment_entry_details", {
							'party':k.customer,
							'party_type':self.party_type,
							"party_name": frappe.db.get_value("Customer", {"name": k.customer}, 'customer_name'),
							"payment_type":self.payment_type,
							"due_balance":k.party_balance,
							"grand_tot":k.grand_total,
							"balance": k.party_balance + k.grand_total,
							"reference_id":j.name,
							"route":frappe.get_value("BDF Gate Pass",{"name":i.gate_pass},"route"),
						})
						self.append("payment_reference", {
							"party_type":self.party_type,
							"party_name":frappe.db.get_value("Customer", {"name": k.customer}, 'customer_name'),
							"reference_doctype":j.voucher_type,
							"reference_name":j.voucher,
							"total_amount":k.grand_total,
							"outstanding_amount":k.outstanding_amount,
							"gate_pass_date": j.parent,
							"reference_id":j.name,
						})
				no_create_invoices = frappe.get_all(
					"No Crate Invoice",
					filters={"parent": i.gate_pass},
					fields=["invoice_no", "name", "parent"]
				)
				for j in no_create_invoices:
					doc = frappe.get_list(
						"Sales Invoice",
						filters={
							"name": j.invoice_no,
							"outstanding_amount": (">", 0),
							"status": ["in", [
								"Overdue", "Partly Paid", "Unpaid",
								"Unpaid and Discounted", "Overdue and Discounted",
								"Partly Paid and Discounted"
							]]
						},
						fields=["grand_total", "outstanding_amount", "customer", "party_balance"]
					)
					for k in doc:
						self.append("bulk_payment_entry_details", {
							'party':k.customer,
							'party_type':self.party_type,
							"party_name": frappe.db.get_value("Customer", {"name": k.customer}, 'customer_name'),
							"payment_type":self.payment_type,
							"due_balance":k.party_balance,
							"grand_tot":k.grand_total,
							"balance": k.party_balance + k.grand_total,
							"reference_id":j.name,
							"route":frappe.get_value("BDF Gate Pass",{"name":i.gate_pass},"route"),
						})
		

	@frappe.whitelist()
	def gate(self):
		final_listed = []
		if self.party_type == "Customer" and self.payment_type == "Receive":
			sql_query = """
				SELECT DISTINCT cs.parent
				FROM `tabBDF Gate Pass Sales Invoice Details` cs
				INNER JOIN `tabSales Invoice` si ON cs.sales_invoice = si.name
				INNER JOIN `tabBDF Gate Pass` gp ON gp.name = cs.parent
				WHERE cs.docstatus = 1
				AND si.outstanding_amount > 0
				AND si.status IN ('Overdue', 'Partly Paid', 'Unpaid', 'Unpaid and Discounted', 'Overdue and Discounted', 'Partly Paid and Discounted')
				AND gp.route = %(route)s
				AND NOT EXISTS (
					SELECT 1
					FROM `tabBDF Gate Pass Sales Invoice Details` cs2
					WHERE cs2.docstatus = 1
					AND cs2.sales_invoice = si.name
					AND cs2.parent = cs.parent
				);
			"""
			
			result = frappe.db.sql(sql_query, {"route": self.route}, as_dict=True)
			final_listed = [row['parent'] for row in result]
			
		return final_listed

	@frappe.whitelist()
	def payment_entry(self):
		for i in self.get("bulk_payment_entry_details",{"paid_amount":(">",0)}):
			doc = frappe.new_doc("Payment Entry")
			doc.posting_date =self.posting_date
			doc.company = self.company	
			doc.mode_of_payment = self.mode_of_payment
			doc.payment_type = self.payment_type
			doc.party_type = self.party_type
			doc.party = i.party
			doc.paid_amount = i.paid_amount
			doc.paid_from = i.paid_from
			doc.paid_to = i.paid_to
			doc.base_paid_amount = i.base_paid_amount
			doc.received_amount = i.paid_amount
			doc.base_paid_amount = i.base_paid_amount
			doc.source_exchange_rate = i.source_exchange_rate
			doc.target_exchange_rate =i.target_exchange_rate
			doc.paid_from_account_currency = i.paid_from_account_currency
			doc.paid_to_account_currency = i.paid_to_account_currency
			
			for j in self.get("payment_reference",{"reference_id":i.reference_id,"allocated_amount": (">", 0)}):
				# frappe.throw("hiiii")
				doc.append("references",{
						"reference_doctype":j.reference_doctype,
						"reference_name":j.reference_name,
						"total_amount":j.total_amount,
						"outstanding_amount":j.outstanding_amount,
						"allocated_amount":j.allocated_amount,					
					})

			if i.reference_no and i.reference_date:
				doc.reference_date = i.reference_date
				doc.reference_no = i.reference_no

			doc.custom_bulk_payment_entry = self.name
			doc.insert()
			doc.save()
			doc.submit()

	def before_cancel(self):
		payment_entries = frappe.get_all("Payment Entry", filters={"custom_bulk_payment_entry": self.name})
		for pe in payment_entries:
			payment_entry = frappe.get_doc("Payment Entry", pe.name)
			payment_entry.cancel()

	def before_save(self):
		tot_pay = 0
		for i in self.get("bulk_payment_entry_details",{"paid_amount":(">",0)}):
			i.balance = i.due_balance + i.grand_tot - i.paid_amount
		for dom in self.payment_denomination:
			tot_pay += dom.total
		self.total_payment_denomination = tot_pay