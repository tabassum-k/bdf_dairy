import frappe

def execute(filters=None):
    columns = [
        {
            "label": "Finished Item",
            "fieldname": "finished_item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 140,
        },
        {
            "label": "Finished Item Name",
            "fieldname": "finished_item_name",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": "Finished Item Group",
            "fieldname": "finished_item_grp",
            "fieldtype": "Link",
            "options": "Item Group",
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
        {
            "label": "Item Group",
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 140,
        },
        {
            "label": "UOM",
            "fieldname": "uom",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 100,
        },
        {
            "label": "Quantity",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100,
        },
    ]

    if not filters.summary:
        columns.insert(0, {
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 140,
        })

    filter_values = {
        "company": filters.company,
        "from_date": filters.from_date,
        "to_date": filters.to_date,
    }

    query = build_query(filters, filter_values)
    data = frappe.db.sql(query, filter_values, as_dict=True)
    return columns, data


def build_query(filters, filter_values):
    """
    Construct the SQL query based on filters.
    """
    select_clause = """
        se.posting_date as date,
        sei.custom_finished_item as finished_item,
        fi.item_name as finished_item_name,
        fi.item_group as finished_item_grp,
        sei.item_code, 
        sei.item_name,
        i.item_group,
        SUM(sei.qty) AS qty, 
        sei.uom
    """ if not filters.summary else """
        sei.custom_finished_item as finished_item,
        fi.item_name as finished_item_name,
        fi.item_group as finished_item_grp,
        sei.item_code, 
        sei.item_name,
        i.item_group,
        SUM(sei.qty) AS qty, 
        sei.uom
    """

    query = f"""
        SELECT 
            {select_clause}
        FROM 
            `tabStock Entry Detail` as sei
        JOIN 
            `tabStock Entry` as se ON sei.parent = se.name
        JOIN 
            `tabItem` AS fi ON sei.custom_finished_item = fi.item_code
        JOIN 
            `tabItem` AS i ON sei.item_code = i.item_code
        WHERE 
            se.docstatus = 1 
            AND se.stock_entry_type = "Handling Loss"
            AND se.company = %(company)s
            AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s
    """

    if filters.get('item'):
        query += " AND sei.item_code IN %(item)s"
        filter_values["item"] = tuple(filters.item) if isinstance(filters.item, list) else (filters.item,)

    if filters.get('finished_item'):
        query += " AND sei.custom_finished_item IN %(finished_item)s"
        filter_values["finished_item"] = tuple(filters.finished_item) if isinstance(filters.finished_item, list) else (filters.finished_item,)

    if filters.get('item_group'):
        query += """
            AND sei.item_code IN (
                SELECT name FROM `tabItem` WHERE item_group IN %(item_group)s
            )
        """
        filter_values["item_group"] = tuple(filters.item_group) if isinstance(filters.item_group, list) else (filters.item_group,)

    if filters.summary:
        query += " GROUP BY sei.item_code, sei.uom ORDER BY sei.item_code"
    else:
        query += " GROUP BY se.posting_date, sei.item_code, sei.uom ORDER BY se.posting_date"

    return query
