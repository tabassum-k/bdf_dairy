# Copyright (c) 2024, BDF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PriceListSettings(Document):
	@frappe.whitelist()
	def get_all_price_list(self):
		standard_price_list = frappe.get_value('Item Price', {'item_code': self.item_code, 'price_list': self.standard_price_list}, 'price_list_rate')
		self.standard_price_rate = standard_price_list
		price_list = frappe.get_all("Price List", filters={'selling': 1})
		self.price_list_settings_changes.clear()
		for pl in price_list:
			if pl.name != self.standard_price_list:
				self.append('price_list_settings_changes',{
					'price_list': pl.name,
					'rate': frappe.get_value('Item Price', {'item_code': self.item_code, 'price_list': pl.name}, 'price_list_rate')
				})