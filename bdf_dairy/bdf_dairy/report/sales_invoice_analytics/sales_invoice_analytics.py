import frappe
from frappe.utils import getdate, add_to_date, add_days, formatdate
from dateutil.relativedelta import relativedelta

def get_period_date_ranges(filters):
	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	date_ranges = []
	increment = {"Monthly": 1, "Quarterly": 3, "Yearly": 12}.get(filters.range, 1)

	if filters.range == "Daily":
		date_ranges = [(from_date + relativedelta(days=i), from_date + relativedelta(days=i)) 
					for i in range((to_date - from_date).days + 1)]
	elif filters.range == "Weekly":
		current_start = from_date - relativedelta(days=from_date.weekday())
		while current_start <= to_date:
			week_end = current_start + relativedelta(days=6)
			date_ranges.append((current_start, min(week_end, to_date)))
			current_start += relativedelta(weeks=1)
	elif filters.range == "Monthly":
		current_start = from_date.replace(day=1)
		while current_start <= to_date:
			month_end = add_to_date(current_start, months=1, as_string=False) - relativedelta(days=1)
			date_ranges.append((current_start, min(month_end, to_date)))
			current_start = add_to_date(current_start, months=1, as_string=False)
	elif filters.range == "Quarterly":
		current_start = from_date.replace(month=((from_date.month - 1) // 3) * 3 + 1, day=1)
		while current_start <= to_date:
			quarter_end = add_to_date(current_start, months=3, as_string=False) - relativedelta(days=1)
			date_ranges.append((current_start, min(quarter_end, to_date)))
			current_start = add_to_date(current_start, months=3, as_string=False)
	elif filters.range == "Yearly":
		current_start = from_date.replace(month=1, day=1)
		while current_start <= to_date:
			year_end = add_to_date(current_start, years=1, as_string=False) - relativedelta(days=1)
			date_ranges.append((current_start, min(year_end, to_date)))
			current_start = add_to_date(current_start, years=1, as_string=False)

	return date_ranges

def execute(filters=None):
	columns = [
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 140,
		},
		{
			"label": "Customer Name",
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 140,
		},
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
	]
	
	date_ranges = get_period_date_ranges(filters)
	date_columns = []
	for start, end in date_ranges:
		if filters.range == "Daily":
			label = formatdate(start, "dd-MM-yyyy")
		elif filters.range == "Weekly":
			label = f"{formatdate(start, 'dd-MM-yyyy')} to {formatdate(end, 'dd-MM-yyyy')}"
		elif filters.range == "Monthly":
			label = start.strftime("%b")
		elif filters.range == "Quarterly":
			label = f"Quart {((start.month - 1) // 3) + 1}"
		elif filters.range == "Yearly":
			label = start.strftime("%Y")
		
		date_columns.append({
			"label": label,
			"fieldname": f"{start}_{end}",
			"fieldtype": "Float",
			"width": 100,
		})

	columns.extend(date_columns)

	filter_values = {
		'company': filters.company,
		'from_date': filters.from_date,
		'to_date': filters.to_date,
		"customers": tuple(filters.get("party", [])) if filters.get("party") else None,
		"item": tuple(filters.get("item", [])) if filters.get("item") else None,
	}
	if filters.type == "Quantity":
		query = """
			SELECT 
				sii.item_code,
				sii.item_name,
				SUM(sii.qty) AS qty,
				sii.uom,
				si.posting_date,
				si.customer,
				si.customer_name
			FROM 
				`tabSales Invoice Item` AS sii
			JOIN 
				`tabSales Invoice` AS si ON sii.parent = si.name
			WHERE 
				si.docstatus = 1
				AND si.company = %(company)s
				AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
		"""

		if filters.get("party"):
			query += " AND si.customer IN %(customers)s"
		if filters.get("item"):
			query += " AND sii.item_code IN %(item)s"

		query += " GROUP BY sii.item_code, sii.uom, si.customer"
		data = frappe.db.sql(query, filter_values, as_dict=True)

	elif filters.type == "Amount":
		query = """
			SELECT 
				sii.item_code,
				sii.item_name,
				SUM(sii.amount) AS qty,
				sii.uom,
				si.posting_date,
				si.customer,
				si.customer_name
			FROM 
				`tabSales Invoice Item` AS sii
			JOIN 
				`tabSales Invoice` AS si ON sii.parent = si.name
			WHERE 
				si.docstatus = 1
				AND si.company = %(company)s
				AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
		"""

		if filters.get("party"):
			query += " AND si.customer IN %(customers)s"
		if filters.get("item"):
			query += " AND sii.item_code IN %(item)s"

		query += " GROUP BY sii.item_code, sii.uom, si.customer"
		data = frappe.db.sql(query, filter_values, as_dict=True)

	result = []
	for row in data:
		row_data = {
			"customer": row["customer"],
			"customer_name": row["customer_name"],
			"item_code": row["item_code"],
			"item_name": row["item_name"]
		}
		for start, end in date_ranges:
			fieldname = f"{start}_{end}"
			row_data[fieldname] = 0.0

		for start, end in date_ranges:
			fieldname = f"{start}_{end}"
			if start <= row["posting_date"] <= end:
				row_data[fieldname] += row["qty"]
		
		result.append(row_data)

	return columns, result

