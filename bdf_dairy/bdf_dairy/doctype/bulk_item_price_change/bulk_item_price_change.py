# Copyright (c) 2024, BDF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BulkItemPriceChange(Document):
	def on_submit(self):
		for itm in self.item_prices_list:
			if itm.expected_rate > 0:
				frappe.db.set_value("Item Price", itm.item_price, 'price_list_rate', itm.expected_rate)
	
	def on_cancel(self):
		for itm in self.item_prices_list:
			if itm.expected_rate > 0:
				frappe.db.set_value("Item Price", itm.item_price, 'price_list_rate', itm.current_rate)

	@frappe.whitelist()
	def get_all_item_price(self):
		if self.type == "Buying":
			item_price = frappe.get_all("Item Price", filters={'item_code': self.item_code, 'buying': 1})
		elif self.type == "Selling":
			item_price = frappe.get_all("Item Price", filters={'item_code': self.item_code, 'selling': 1})
		elif self.type == "Both":
			item_price = frappe.get_all("Item Price", filters={'item_code': self.item_code})
		else:
			return
		for itm in item_price:
			itm_p = frappe.get_doc("Item Price", itm['name'])
			self.append('item_prices_list',{
				'item_price': itm_p.name,
				'price_list': itm_p.price_list,
				'item_code': itm_p.item_code,
				'item_name': itm_p.item_name,
				'type': 'Buying' if itm_p.buying else 'Selling',
				'current_rate': itm_p.price_list_rate
			})
