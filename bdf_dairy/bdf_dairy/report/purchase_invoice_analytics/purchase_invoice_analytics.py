import frappe
from frappe.utils import getdate, add_to_date, formatdate
from dateutil.relativedelta import relativedelta

def get_period_date_ranges(filters):
    """
    Generate date ranges based on the selected range type (Daily, Weekly, Monthly, Quarterly, Yearly).
    """
    from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
    date_ranges = []

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
    """
    Generate columns and data based on selected view (Vendor or Calendar).
    """
    columns = []
    result = []

    # Filter values for query
    filter_values = {
        'company': filters.company,
        'from_date': filters.from_date,
        'to_date': filters.to_date,
        "vendors": tuple(filters.get("party", [])) if filters.get("party") else None,
        "item": tuple(filters.get("item", [])) if filters.get("item") else None,
        "item_group": tuple(filters.get("item_group", [])) if filters.get("item_group") else None,
        "supplier_group": tuple(filters.get("supplier_group", [])) if filters.get("supplier_group") else None,
    }

    metric_column = "SUM(pii.qty)" if filters.type == "Quantity" else "SUM(pii.net_amount)"

    # Vendor-wise view
    if filters.view_by == "Supplier":
        columns = [
            {"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
            {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 140},
            {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 140},
        ]
        columns.append({"label": "Total", "fieldname": "total_qty", "fieldtype": "Float", "width": 140})
        if filters.type == "Quantity":
            columns.append({"label": "Weight Per Unit", "fieldname": "weight_per_unit", "fieldtype": "Float", "width": 100})
            columns.append({"label": "Total Wgt", "fieldname": "total_wgt", "fieldtype": "Float", "width": 140})

        # Fetch unique vendors within the date range
        vendors = frappe.get_list(
            "Purchase Invoice",
            filters={'posting_date': ['BETWEEN', [filters.from_date, filters.to_date]]},
            pluck='supplier'
        )
        vendors = list(set(vendors))
        vendor_totals = {vendor: 0 for vendor in vendors}

        # Dynamic query based on selected filters
        query = f"""
            SELECT 
                pii.item_code,
                pii.item_name,
                i.item_group,
                {'i.weight_per_unit,' if filters.type == 'Quantity' else ''} 
                {metric_column} AS qty,
                pi.supplier
            FROM 
                `tabPurchase Invoice Item` AS pii
            JOIN 
                `tabPurchase Invoice` AS pi ON pii.parent = pi.name
            JOIN 
                `tabItem` AS i ON pii.item_code = i.item_code
            JOIN 
                `tabSupplier` AS s ON pi.supplier = s.name
            WHERE 
                pi.docstatus = 1
                AND pi.company = %(company)s
                AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        """

        if filters.get("party"):
            query += " AND pi.supplier IN %(vendors)s"
        if filters.get("item"):
            query += " AND pii.item_code IN %(item)s"
        if filters.get('item_group'):
            query += " AND i.item_group IN %(item_group)s"
        if filters.get('supplier_group'):
            query += " AND s.supplier_group IN %(supplier_group)s"

        query += " GROUP BY pii.item_code, pi.supplier"
        data = frappe.db.sql(query, filter_values, as_dict=True)

        # Process data for result
        item_data = {}
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
                vendor_column_qty = f"{row['supplier']}_qty"
                item_data[item_key][vendor_column_qty] = row["qty"]
                vendor_totals[row["supplier"]] += row["qty"]

        vendors = [vendor for vendor in vendors if vendor_totals[vendor] > 0]

        for vendor in vendors:
            vendor_name = frappe.get_value("Supplier", vendor, 'supplier_name')
            columns.append({
                "label": f"{vendor_name}",
                "fieldname": f"{vendor}_qty",
                "fieldtype": "Float",
                "width": 120,
            })
            
        for item in item_data.values():
            total_qty = sum(value for key, value in item.items() if key.endswith('_qty'))
            item["total_qty"] = total_qty
            if filters.type == "Quantity":
                item["total_wgt"] = total_qty * item["weight_per_unit"]
            result.append(item)

    elif filters.view_by == "Calendar":
        columns = [
            {"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 140},
            {"label": "Supplier Name", "fieldname": "supplier_name", "fieldtype": "Data", "width": 140},
            {"label": "Item", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
            {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 140},
            {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 140},
        ]
        columns.append({"label": "Total", "fieldname": "total", "fieldtype": "Float", "width": 120})
        if filters.type == "Quantity":
            columns.append({"label": "Weight Per Unit","fieldname": "weight_per_unit","fieldtype": "Float","width": 100})
            columns.append({"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 120})
        date_ranges = get_period_date_ranges(filters)
        date_columns = []
        for start, end in date_ranges:
            label = {
                "Daily": formatdate(start, "dd-MM-yyyy"),
                "Weekly": f"{formatdate(start, 'dd-MM-yyyy')} to {formatdate(end, 'dd-MM-yyyy')}",
                "Monthly": start.strftime("%b %Y"),
                "Quarterly": f"Q{((start.month - 1) // 3) + 1} {start.year}",
                "Yearly": start.strftime("%Y"),
            }[filters.range]
            date_columns.append({
                "label": label,
                "fieldname": f"{start}_{end}",
                "fieldtype": "Float",
                "width": 100,
            })

        columns.extend(date_columns)

        query = f"""
            SELECT 
                pi.supplier,
                pi.supplier_name,
                pii.item_code,
                pii.item_name,
                i.item_group,
                i.weight_per_unit,
                {metric_column} AS qty,
                pi.posting_date
            FROM 
                `tabPurchase Invoice Item` AS pii
            JOIN 
                `tabPurchase Invoice` AS pi ON pii.parent = pi.name
            JOIN 
                `tabItem` AS i ON pii.item_code = i.item_code
            JOIN 
                `tabSupplier` AS s ON pi.supplier = s.name
            WHERE 
                pi.docstatus = 1
                AND pi.company = %(company)s
                AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
        """

        # Apply additional filters
        if filters.get("party"):
            query += " AND pi.supplier IN %(vendors)s"
        if filters.get("item"):
            query += " AND pii.item_code IN %(item)s"
        if filters.get("item_group"):
            query += " AND i.item_group IN %(item_group)s"
        if filters.get("supplier_group"):
            query += " AND s.supplier_group IN %(supplier_group)s"

        query += " GROUP BY pii.item_code, pi.supplier, pi.posting_date"


        data = frappe.db.sql(query, filter_values, as_dict=True)

        for row in data:
            row_data = {
                "supplier": row["supplier"],
                "supplier_name": row["supplier_name"],
                "item_code": row["item_code"],
                "item_name": row["item_name"],
                "item_group": row["item_group"],
                "weight_per_unit": row["weight_per_unit"] or 0,
                "total": 0.0,
                "total_weight": 0.0,
            }
            for start, end in date_ranges:
                fieldname = f"{start}_{end}"
                if start <= row["posting_date"] <= end:
                    row_data[fieldname] = row.get("qty", 0)
                    row_data["total"] += row_data[fieldname]
                    row_data["total_weight"] += row_data[fieldname] * row_data["weight_per_unit"]
            result.append(row_data)

    return columns, result
