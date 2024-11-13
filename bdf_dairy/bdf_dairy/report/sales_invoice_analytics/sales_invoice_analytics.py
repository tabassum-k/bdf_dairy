# import frappe
# from frappe.utils import getdate, add_to_date, add_days, formatdate
# from dateutil.relativedelta import relativedelta

# def get_period_date_ranges(filters):
# 	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
# 	date_ranges = []
# 	increment = {"Monthly": 1, "Quarterly": 3, "Yearly": 12}.get(filters.range, 1)

# 	if filters.range == "Daily":
# 		date_ranges = [(from_date + relativedelta(days=i), from_date + relativedelta(days=i)) 
# 					for i in range((to_date - from_date).days + 1)]
# 	elif filters.range == "Weekly":
# 		current_start = from_date - relativedelta(days=from_date.weekday())
# 		while current_start <= to_date:
# 			week_end = current_start + relativedelta(days=6)
# 			date_ranges.append((current_start, min(week_end, to_date)))
# 			current_start += relativedelta(weeks=1)
# 	elif filters.range == "Monthly":
# 		current_start = from_date.replace(day=1)
# 		while current_start <= to_date:
# 			month_end = add_to_date(current_start, months=1, as_string=False) - relativedelta(days=1)
# 			date_ranges.append((current_start, min(month_end, to_date)))
# 			current_start = add_to_date(current_start, months=1, as_string=False)
# 	elif filters.range == "Quarterly":
# 		current_start = from_date.replace(month=((from_date.month - 1) // 3) * 3 + 1, day=1)
# 		while current_start <= to_date:
# 			quarter_end = add_to_date(current_start, months=3, as_string=False) - relativedelta(days=1)
# 			date_ranges.append((current_start, min(quarter_end, to_date)))
# 			current_start = add_to_date(current_start, months=3, as_string=False)
# 	elif filters.range == "Yearly":
# 		current_start = from_date.replace(month=1, day=1)
# 		while current_start <= to_date:
# 			year_end = add_to_date(current_start, years=1, as_string=False) - relativedelta(days=1)
# 			date_ranges.append((current_start, min(year_end, to_date)))
# 			current_start = add_to_date(current_start, years=1, as_string=False)

# 	return date_ranges

# def execute(filters=None):
# 	columns = [
# 		{
# 			"label": "Customer",
# 			"fieldname": "customer",
# 			"fieldtype": "Link",
# 			"options": "Customer",
# 			"width": 140,
# 		},
# 		{
# 			"label": "Customer Name",
# 			"fieldname": "customer_name",
# 			"fieldtype": "Data",
# 			"width": 140,
# 		},
# 		{
# 			"label": "Item",
# 			"fieldname": "item_code",
# 			"fieldtype": "Link",
# 			"options": "Item",
# 			"width": 140,
# 		},
# 		{
# 			"label": "Item Name",
# 			"fieldname": "item_name",
# 			"fieldtype": "Data",
# 			"width": 140,
# 		},
# 		{
# 			"label": "Item Group",
# 			"fieldname": "item_group",
# 			"fieldtype": "Link",
# 			"options": "Item Group",
# 			"width": 140,
# 		},
# 		{
# 			"label": "Weight Per Unit",
# 			"fieldname": "weight_per_unit",
# 			"fieldtype": "Float",
# 			"width": 100,
# 		},
# 	]
	
# 	date_ranges = get_period_date_ranges(filters)
# 	date_columns = []
# 	for start, end in date_ranges:
# 		if filters.range == "Daily":
# 			label = formatdate(start, "dd-MM-yyyy")
# 		elif filters.range == "Weekly":
# 			label = f"{formatdate(start, 'dd-MM-yyyy')} to {formatdate(end, 'dd-MM-yyyy')}"
# 		elif filters.range == "Monthly":
# 			label = start.strftime("%b")
# 		elif filters.range == "Quarterly":
# 			label = f"Quart {((start.month - 1) // 3) + 1}"
# 		elif filters.range == "Yearly":
# 			label = start.strftime("%Y")
		
# 		date_columns.append({
# 			"label": label,
# 			"fieldname": f"{start}_{end}",
# 			"fieldtype": "Float",
# 			"width": 100,
# 		})

# 	columns.extend(date_columns)

# 	# Add columns for Total and Total Weight
# 	columns.append({
# 		"label": "Total",
# 		"fieldname": "total",
# 		"fieldtype": "Float",
# 		"width": 120,
# 	})
# 	columns.append({
# 		"label": "Total Weight",
# 		"fieldname": "total_weight",
# 		"fieldtype": "Float",
# 		"width": 120,
# 	})

# 	filter_values = {
# 		'company': filters.company,
# 		'from_date': filters.from_date,
# 		'to_date': filters.to_date,
# 		"customers": tuple(filters.get("party", [])) if filters.get("party") else None,
# 		"item": tuple(filters.get("item", [])) if filters.get("item") else None,
# 		"item_group": tuple(filters.get("item_group", [])) if filters.get("item_group") else None,
# 	}
# 	if filters.type == "Quantity":
# 		query = """
# 			SELECT 
# 				sii.item_code,
# 				sii.item_name,
# 				i.item_group,
# 				i.weight_per_unit,
# 				SUM(sii.stock_qty) AS qty,
# 				sii.uom,
# 				si.posting_date,
# 				si.customer,
# 				si.customer_name
# 			FROM 
# 				`tabSales Invoice Item` AS sii
# 			JOIN 
# 				`tabSales Invoice` AS si ON sii.parent = si.name
# 			JOIN 
# 				`tabItem` AS i ON sii.item_code = i.item_code
# 			WHERE 
# 				si.docstatus = 1
# 				AND si.company = %(company)s
# 				AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
# 		"""

# 		if filters.get("party"):
# 			query += " AND si.customer IN %(customers)s"
# 		if filters.get("item"):
# 			query += " AND sii.item_code IN %(item)s"
# 		if filters.get('item_group'):
# 			query += " AND i.item_group IN %(item_group)s"

# 		query += " GROUP BY sii.item_code, sii.uom, si.customer ORDER BY si.customer"
# 		data = frappe.db.sql(query, filter_values, as_dict=True)

# 	elif filters.type == "Amount":
# 		query = """
# 			SELECT 
# 				sii.item_code,
# 				sii.item_name,
# 				i.item_group,
# 				i.weight_per_unit,
# 				SUM(sii.amount) AS qty,
# 				sii.uom,
# 				si.posting_date,
# 				si.customer,
# 				si.customer_name
# 			FROM 
# 				`tabSales Invoice Item` AS sii
# 			JOIN 
# 				`tabSales Invoice` AS si ON sii.parent = si.name
# 			JOIN 
# 				`tabItem` AS i ON sii.item_code = i.item_code
# 			WHERE 
# 				si.docstatus = 1
# 				AND si.company = %(company)s
# 				AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
# 		"""

# 		if filters.get("party"):
# 			query += " AND si.customer IN %(customers)s"
# 		if filters.get("item"):
# 			query += " AND sii.item_code IN %(item)s"
# 		if filters.get('item_group'):
# 			query += " AND i.item_group IN %(item_group)s"

# 		query += " GROUP BY sii.item_code, sii.uom, si.customer ORDER BY si.customer"
# 		data = frappe.db.sql(query, filter_values, as_dict=True)

# 	result = []
# 	for row in data:
# 		row_data = {
# 			"customer": row["customer"],
# 			"customer_name": row["customer_name"],
# 			"item_code": row["item_code"],
# 			"item_name": row["item_name"],
# 			"item_group": row["item_group"],
# 			"weight_per_unit": row["weight_per_unit"]
# 		}
		
# 		total_qty = 0.0
# 		for start, end in date_ranges:
# 			fieldname = f"{start}_{end}"
# 			row_data[fieldname] = 0.0

# 		for start, end in date_ranges:
# 			fieldname = f"{start}_{end}"
# 			if start <= row["posting_date"] <= end:
# 				row_data[fieldname] += row["qty"]
# 				total_qty += row["qty"]
		
# 		row_data["total"] = total_qty
# 		row_data["total_weight"] = total_qty * row["weight_per_unit"]
		
# 		result.append(row_data)

# 	return columns, result
import frappe
from frappe.utils import getdate, add_to_date, add_days, formatdate
from dateutil.relativedelta import relativedelta

def execute(filters=None):
	columns = [
		{"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 140},
		{"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 140},
	]

	if filters.type == "Quantity":
		columns.append({"label": "Weight Per Unit", "fieldname": "weight_per_unit", "fieldtype": "Float", "width": 100})

	customers = frappe.get_list(
		"Sales Invoice",
		filters={'posting_date': ['BETWEEN', [filters.from_date, filters.to_date]]},
		pluck='customer'
	)
	customers = list(set(customers))

	filter_values = {
		'company': filters.company,
		'from_date': filters.from_date,
		'to_date': filters.to_date,
		"customers": tuple(filters.get("party", [])) if filters.get("party") else None,
		"item": tuple(filters.get("item", [])) if filters.get("item") else None,
		"item_group": tuple(filters.get("item_group", [])) if filters.get("item_group") else None,
	}

	metric_column = "sii.stock_qty" if filters.type == "Quantity" else "sii.amount"
	query = f"""
		SELECT 
			sii.item_code,
			sii.item_name,
			i.item_group,
			{'i.weight_per_unit,' if filters.type == 'Quantity' else ''} 
			SUM({metric_column}) AS qty,
			si.customer
		FROM 
			`tabSales Invoice Item` AS sii
		JOIN 
			`tabSales Invoice` AS si ON sii.parent = si.name
		JOIN 
			`tabItem` AS i ON sii.item_code = i.item_code
		WHERE 
			si.docstatus = 1
			AND si.company = %(company)s
			AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
	"""

	if filters.get("party"):
		query += " AND si.customer IN %(customers)s"
	if filters.get("item"):
		query += " AND sii.item_code IN %(item)s"
	if filters.get('item_group'):
		query += " AND i.item_group IN %(item_group)s"
	query += " GROUP BY sii.item_code, si.customer"

	data = frappe.db.sql(query, filter_values, as_dict=True)
	item_data = {}
	customer_totals = {cust: 0 for cust in customers}  # Track total quantity or amount per customer

	for row in data:
		item_key = row["item_code"]
		if item_key not in item_data:
			item_data[item_key] = {
				"item_code": row["item_code"],
				"item_name": row["item_name"],
				"item_group": row["item_group"],
				"weight_per_unit": row.get("weight_per_unit", 0) if filters.type == "Quantity" else None,
			}

		if row["qty"] > 0:
			customer_column_qty = f"{row['customer']}_qty"
			item_data[item_key][customer_column_qty] = row["qty"]
			customer_totals[row["customer"]] += row["qty"]

	customers = [cust for cust in customers if customer_totals[cust] > 0]

	for cust in customers:
		cust_name = frappe.get_value("Customer", cust, 'customer_name')
		columns.append({
			"label": f"{cust_name}",
			"fieldname": f"{cust}_qty",
			"fieldtype": "Float",
			"width": 120,
		})

	result = []

	for item in item_data.values():
		for cust in customers:
			item.setdefault(f"{cust}_qty", 0)
		result.append(item)
	columns.append({"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 140})
	if filters.type == "Quantity":
		columns.append({"label": "Total Wgt", "fieldname": "total_wgt", "fieldtype": "Float", "width": 140})
	for res in result:
		total_qty = 0
		for key, value in res.items():
			if key.endswith('_qty'):
				total_qty += value
		res['total_qty'] = total_qty
		if filters.type == "Quantity":		
			res['total_wgt'] = total_qty * res['weight_per_unit']
	return columns, result