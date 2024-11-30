from collections import defaultdict

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_data(report_filters):
    fields = get_fields()
    filters = get_filter_condition(report_filters)

    wo_items = defaultdict(lambda: defaultdict(float))

    work_orders = frappe.get_all("Work Order", filters=filters, fields=fields)
    returned_materials = get_returned_materials(work_orders)

    for d in work_orders:
        d.extra_consumed_qty = 0.0
        if d.consumed_qty and d.consumed_qty > d.required_qty:
            d.extra_consumed_qty = d.consumed_qty - d.required_qty

        if d.extra_consumed_qty or not report_filters.show_extra_consumed_materials:
            key = (d.production_item, d.raw_material_item_code,d.raw_material_name)
            wo_items[key]['qty'] += d.qty
            wo_items[key]['produced_qty'] += d.produced_qty
            wo_items[key]['required_qty'] += d.required_qty
            wo_items[key]['transferred_qty'] += d.transferred_qty
            wo_items[key]['consumed_qty'] += d.consumed_qty
            wo_items[key]['extra_consumed_qty'] += d.extra_consumed_qty
            wo_items[key]['returned_qty'] += d.returned_qty

    data = []
    previous_production_item = None  # Variable to keep track of the previous production item
    for key, values in wo_items.items():
        production_item, raw_material_item, raw_material_name = key
        if production_item == previous_production_item:
            production_item_display = '' 	
            value_qty = 0
            prod_value_qty = 0
        else:
            production_item_display = production_item 
            value_qty = values['qty']
            prod_value_qty = values['produced_qty']
        row = {
			'name': '',  # You can choose to keep it blank or populate if necessary
			'status': '',  # Similarly, handle other fields
			'production_item': production_item_display,
			'production_item_name': frappe.db.get_value("Item", production_item_display, 'item_name'),
			'raw_material_item_code': raw_material_item,
			'raw_material_name': raw_material_name,  # Populate if needed
			'qty': value_qty,
			'produced_qty': values['produced_qty'],
			'required_qty': values['required_qty'],
			'transferred_qty': values['transferred_qty'],
			'consumed_qty': values['consumed_qty'],
			'extra_consumed_qty': values['extra_consumed_qty'],
			'returned_qty': values['returned_qty']
			}
        data.append(row)
        previous_production_item = production_item
    return data



def get_returned_materials(work_orders):
	raw_materials_qty = defaultdict(float)

	raw_materials = frappe.get_all(
		"Stock Entry",
		fields=["`tabStock Entry Detail`.`item_code`", "`tabStock Entry Detail`.`qty`"],
		filters=[
			["Stock Entry", "is_return", "=", 1],
			["Stock Entry Detail", "docstatus", "=", 1],
			["Stock Entry", "work_order", "in", [d.name for d in work_orders]],
		],
	)

	for d in raw_materials:
		raw_materials_qty[d.item_code] += d.qty

	for row in work_orders:
		row.returned_qty = 0.0
		if raw_materials_qty.get(row.raw_material_item_code):
			row.returned_qty = raw_materials_qty.get(row.raw_material_item_code)


def get_fields():
	return [
		"`tabWork Order Item`.`parent`",
		"`tabWork Order Item`.`item_code` as raw_material_item_code",
		"`tabWork Order Item`.`item_name` as raw_material_name",
		"`tabWork Order Item`.`required_qty`",
		"`tabWork Order Item`.`transferred_qty`",
		"`tabWork Order Item`.`consumed_qty`",
		"`tabWork Order`.`status`",
		"`tabWork Order`.`name`",	
		"`tabWork Order`.`production_item`",
		"`tabWork Order`.`qty`",
		"`tabWork Order`.`produced_qty`",
	]


def get_filter_condition(report_filters):
    filters = {
        "docstatus": 1,
        "status": ("in", ["In Process", "Completed", "Stopped"]),
        "creation": ("between", [report_filters.from_date, report_filters.to_date]),
    }

    for field in ["name", "company", "status"]:
        value = report_filters.get(field)
        if value:
            filters[field] = value

    production_items = report_filters.get("production_item")
    item_codes = report_filters.get("item_code")
    if production_items:
        filters["production_item"] = ("in", production_items)
       
    if item_codes:
        filters["item_code"] = ("in", item_codes)

    return filters




def get_columns():
	return [
		{
			"label": _("Production Item"),
			"fieldname": "production_item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 130,
		},
  		{
			"label": _("Production Item Name"),
			"fieldname": "production_item_name",
			"fieldtype": "Link",
			"options": "Item",
			"width": 130,
		},
		{"label": _("Qty to Produce"), "fieldname": "qty", "fieldtype": "Float", "width": 120},
		{"label": _("Produced Qty"), "fieldname": "produced_qty", "fieldtype": "Float", "width": 110},
		{
			"label": _("Raw Material Item"),
			"fieldname": "raw_material_item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{"label": _("Item Name"), "fieldname": "raw_material_name", "width": 130},
		{"label": _("Required Qty"), "fieldname": "required_qty", "fieldtype": "Float", "width": 100},
		{
			"label": _("Transferred Qty"),
			"fieldname": "transferred_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{"label": _("Consumed Qty"), "fieldname": "consumed_qty", "fieldtype": "Float", "width": 100},
		{
			"label": _("Extra Consumed Qty"),
			"fieldname": "extra_consumed_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Returned Qty"),
			"fieldname": "returned_qty",
			"fieldtype": "Float",
			"width": 100,
		},
	]