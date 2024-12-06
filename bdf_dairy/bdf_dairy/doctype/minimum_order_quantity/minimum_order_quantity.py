# Copyright (c) 2024, BDF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MinimumOrderQuantity(Document):
	def before_save(self):
		unique_combinations = set()
		for moq in self.moq_details:
			combination = (moq.item, moq.uom)
			if combination in unique_combinations:
				frappe.throw(f"Duplicate entry found for Item: {moq.item} and UOM: {moq.uom}. Each combination must be unique.")
			
			unique_combinations.add(combination)

