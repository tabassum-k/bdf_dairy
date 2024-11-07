import frappe
from frappe import _, scrub
from frappe.utils import add_days, add_to_date, flt, getdate
from erpnext.accounts.utils import get_fiscal_year


def execute(filters=None):
	return SalesInvoiceAnalytics(filters).run()

class SalesInvoiceAnalytics:
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.date_field = "posting_date"
		self.months = [
			"Jan", "Feb", "Mar", "Apr", "May", "Jun",
			"Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
		]
		self.get_period_date_ranges()

	def run(self):
		self.get_columns()
		self.get_data()
		self.get_chart_data()

		# Skipping total row for tree-view reports
		skip_total_row = 0

		return self.columns, self.data, None, self.chart, None, skip_total_row

	def get_columns(self):
		self.columns = [
			{
				"label": _("Customer"),
				"fieldname": "customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 140,
			},
			{
				"label": _("Customer Name"),
				"fieldname": "customer_name",
				"fieldtype": "Data",
				"width": 140,
			},
			{
				"label": _("Item"),
				"fieldname": "item",
				"fieldtype": "Link",
				"options": "Item",
				"width": 140,
			},
			{
				"label": _("Item Name"),
				"fieldname": "item_name",
				"fieldtype": "Data",
				"width": 140,
			},
   			{
				"label": _("Shift"),
				"fieldname": "shift",
				"fieldtype": "Data",
				"width": 140,
			},
		]

		for end_date in self.periodic_daterange:
			period = self.get_period(end_date)
			self.columns.append(
				{"label": _(period), "fieldname": scrub(period), "fieldtype": "Float", "width": 120}
			)

		self.columns.append({"label": _("Total"), "fieldname": "total", "fieldtype": "Float", "width": 120})

	def get_data(self):
		self.get_sales_invoice_data()
		self.get_rows()

	def get_sales_invoice_data(self):
		value_field = "base_net_total" if self.filters["value_quantity"] == "Value" else "total_qty"
		filters = {
			"company": self.filters.company,
			"from_date": self.filters.from_date,
			"to_date": self.filters.to_date,
			"customers": tuple(self.filters.get("party", [])) if self.filters.get("party") else None,
			"items": tuple(self.filters.get("item", [])) if self.filters.get("item") else None,
			"shift": self.filters.get("shift", None)
		}

		query = """
		SELECT 
			si.name AS sales_invoice,
			sii.item_code,
			sii.item_name,
			sii.qty,
			sii.amount,
			si.{date_field},
			si.customer,
			si.delivery_shift,
			si.customer_name,
			si.{value_field} 
		FROM 
			`tabSales Invoice Item` AS sii
		JOIN 
			`tabSales Invoice` AS si ON sii.parent = si.name
		WHERE 
			si.docstatus = 1
			AND si.company = %(company)s
			AND si.{date_field} BETWEEN %(from_date)s AND %(to_date)s
		""".format(date_field=self.date_field, value_field=value_field)

		if filters["customers"]:
			query += " AND si.customer IN %(customers)s"
		if filters["items"]:
			query += " AND sii.item_code IN %(items)s"
		if filters["shift"]:
			query += " AND si.delivery_shift = %(shift)s"

		query += " ORDER BY si.name, si.customer, si.delivery_shift, sii.item_code"
		self.entries = frappe.db.sql(query, filters, as_dict=True)
		self.customer_names = {d.customer: d.customer_name for d in self.entries}

	def get_rows(self):
		self.data = []
		self.get_periodic_data()

		for (customer, item_code, delivery_shift), period_data in self.entity_periodic_data.items():
			row = {
				"customer": customer,
				"customer_name": self.customer_names.get(customer),
				"item": item_code,
				"item_name": next((d.item_name for d in self.entries if d.item_code == item_code), ""),
				"shift": delivery_shift
			}
			total = 0
			for end_date in self.periodic_daterange:
				period = self.get_period(end_date)
				amount = flt(period_data.get(period, 0.0))
				row[scrub(period)] = amount
				total += amount

			row["total"] = total
			self.data.append(row)


	def get_period(self, posting_date):
		if self.filters.range == "Weekly":
			period = _("Week {0} {1}").format(str(posting_date.isocalendar()[1]), str(posting_date.year))
		elif self.filters.range == "Monthly":
			period = _(str(self.months[posting_date.month - 1])) + " " + str(posting_date.year)
		elif self.filters.range == "Quarterly":
			period = _("Quarter {0} {1}").format(
				str(((posting_date.month - 1) // 3) + 1), str(posting_date.year)
			)
		elif self.filters.range == "Daily":
			period = posting_date.strftime("%Y-%m-%d")
		else:
			period = str(get_fiscal_year(posting_date, company=self.filters.company)[0])

		return period


	def get_periodic_data(self):
		self.entity_periodic_data = frappe._dict()

		for d in self.entries:
			period = self.get_period(d.get(self.date_field))
			key = (d.customer, d.item_code, d.delivery_shift)  # Added delivery_shift to the key
			if key not in self.entity_periodic_data:
				self.entity_periodic_data[key] = frappe._dict()
			self.entity_periodic_data[key][period] = self.entity_periodic_data[key].get(period, 0.0) + \
				flt(d.base_net_total if self.filters["value_quantity"] == "Value" else d.total_qty)



	def get_period_date_ranges(self):
		from dateutil.relativedelta import MO, relativedelta
		from_date, to_date = getdate(self.filters.from_date), getdate(self.filters.to_date)
		increment = {"Monthly": 1, "Quarterly": 3, "Yearly": 12}.get(self.filters.range, 1)

		if self.filters.range == "Daily":
			self.periodic_daterange = [from_date + relativedelta(days=i) for i in range((to_date - from_date).days + 1)]

		elif self.filters.range == "Monthly":
			from_date = from_date.replace(day=1)
			self.periodic_daterange = []
			while from_date <= to_date:
				self.periodic_daterange.append(from_date)
				from_date = add_to_date(from_date, months=1)

		elif self.filters.range == "Quarterly":
			from_date = from_date.replace(month=((from_date.month - 1) // 3) * 3 + 1, day=1)
			self.periodic_daterange = []
			while from_date <= to_date:
				self.periodic_daterange.append(from_date)
				from_date = add_to_date(from_date, months=3)

		elif self.filters.range == "Yearly":
			from_date = from_date.replace(month=1, day=1)
			self.periodic_daterange = []
			while from_date <= to_date:
				self.periodic_daterange.append(from_date)
				from_date = add_to_date(from_date, years=1)

		elif self.filters.range == "Weekly":
			from_date = from_date - relativedelta(days=from_date.weekday())
			self.periodic_daterange = []
			while from_date <= to_date:
				self.periodic_daterange.append(from_date)
				from_date = add_days(from_date, 7) 


	def get_chart_data(self):
		length = len(self.columns)
		labels = [d.get("label") for d in self.columns[2 : length - 1]]
		self.chart = {"data": {"labels": labels, "datasets": []}, "type": "line"}
		self.chart["fieldtype"] = "Currency" if self.filters["value_quantity"] == "Value" else "Float"
