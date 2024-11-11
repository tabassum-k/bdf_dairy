# Copyright (c) 2024, BDF and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = [
		{
			"label": "Item",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{
			"label": "Item Name",
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": "UOM",
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 140,
		},
		{
			"label": "Quantity",
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 140,
		},
	]

	filter_values = {
		"company": filters.company,
		"from_date": filters.from_date,
		"to_date": filters.to_date,
	}

	query = """
		SELECT 
			sei.item_code, 
			sei.item_name, 
			SUM(sei.qty) AS qty, 
			sei.uom
		FROM 
			`tabStock Entry Detail` as sei
		JOIN 
			`tabStock Entry` as se ON sei.parent = se.name
		WHERE 
			se.docstatus = 1 
			AND se.stock_entry_type = "Handling Loss"
			AND se.company = %(company)s
			AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s
	"""

	if filters.get('item'):
		query += " AND sei.item_code IN %(item)s"
		filter_values["item"] = tuple(filters.item) if isinstance(filters.item, list) else (filters.item,)

	query += " GROUP BY sei.item_code, sei.uom"
	data = frappe.db.sql(query, filter_values, as_dict=True)
	return columns, data



