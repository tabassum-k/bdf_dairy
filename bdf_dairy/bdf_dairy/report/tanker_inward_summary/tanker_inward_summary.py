import frappe

def execute(filters=None):
    columns, data = get_columns(), []
    ack_data = get_ack_data(filters)
    # frappe.throw(str(ack_data))
    for ack in ack_data:
        data.append({
            "id": ack.get('id'),
            "dcs": ack.get('dcs'),
            "ack_liter": ack.get('ack_liter', 0),
            "ack_kg": ack.get('ack_kg', 0),
            "ack_fat": ack.get('ack_fat', 0),
            "ack_snf": ack.get('ack_snf', 0),
            "ack_kg_fat": ack.get('ack_kg_fat', 0),
            "ack_kg_snf": ack.get('ack_kg_snf', 0),
            "diff_liter": format_diff(ack.get('diff_liter', 0)),
            "diff_kg": format_diff(ack.get('diff_kg', 0)),
            "diff_fat": format_diff(ack.get('diff_fat', 0)),
            "diff_snf": format_diff(ack.get('diff_snf', 0)),
            "diff_kg_fat": format_diff(ack.get('diff_kg_fat', 0)),
            "diff_kg_snf": format_diff(ack.get('diff_kg_snf', 0)),
        })

    return columns, data

def get_columns():
    return [
        {"label": "ID", "fieldname": "id", "fieldtype": "Link", "options": "Tanker Inward", "width": 120},
        {"label": "DCS", "fieldname": "dcs", "fieldtype": "Link", "options": "Warehouse"},
        {"label": "ACK LITER", "fieldname": "ack_liter", "fieldtype": "Float", "width": 120},
        {"label": "ACK KG", "fieldname": "ack_kg", "fieldtype": "Float", "width": 120},
        {"label": "ACK FAT", "fieldname": "ack_fat", "fieldtype": "Float", "width": 120},
        {"label": "ACK SNF", "fieldname": "ack_snf", "fieldtype": "Float", "width": 120},
        {"label": "ACK KG FAT", "fieldname": "ack_kg_fat", "fieldtype": "Float", "width": 120},
        {"label": "ACK KG SNF", "fieldname": "ack_kg_snf", "fieldtype": "Float", "width": 120},
        {"label": "DIFF LITER", "fieldname": "diff_liter", "fieldtype": "Data", "width": 120},
        {"label": "DIFF KG", "fieldname": "diff_kg", "fieldtype": "Data", "width": 120},
        {"label": "DIFF FAT", "fieldname": "diff_fat", "fieldtype": "Data", "width": 120},
        {"label": "DIFF SNF", "fieldname": "diff_snf", "fieldtype": "Data", "width": 120},
        {"label": "DIFF KG FAT", "fieldname": "diff_kg_fat", "fieldtype": "Data", "width": 120},
        {"label": "DIFF KG SNF", "fieldname": "diff_kg_snf", "fieldtype": "Data", "width": 120},
    ]

def get_ack_data(filters):
    # Start building the query and parameters
    query = """
        SELECT
            ti.name AS id,
            ti.dcs,
            SUM(mrt.qty_in_liter) AS ack_liter,
            SUM(mrt.qty_in_kg) AS ack_kg,
            AVG(mrt.fat) AS ack_fat,
            AVG(mrt.snf) AS ack_snf,
            SUM(mrt.kg_fat) AS ack_kg_fat,
            SUM(mrt.kg_snf) AS ack_kg_snf,
            SUM(d.qty_in_liter) AS diff_liter,
            SUM(d.qty_in_kg) AS diff_kg,
            AVG(d.fat) AS diff_fat,
            AVG(d.snf) AS diff_snf,
            SUM(d.kg_fat) AS diff_kg_fat,
            SUM(d.kg_snf) AS diff_kg_snf
        FROM 
            `tabTanker Inward` AS ti
        LEFT JOIN 
            `tabMilk Received From Tanker` AS mrt ON mrt.parent = ti.name
        LEFT JOIN 
            `tabDifference of DCS and Tanker Milk Received` AS d ON d.parent = ti.name
        WHERE 
            ti.tanker_inward_date BETWEEN %s AND %s
            AND ti.docstatus = 1
    """
    parameters = [filters.get('from_date'), filters.get('to_date')]
    if filters.get('dcs'):
        query += " AND ti.dcs IN %s"
        parameters.append(tuple(filters.get('dcs')))
    query += " GROUP BY ti.dcs, ti.name"

    return frappe.db.sql(query, tuple(parameters), as_dict=True)


def format_diff(value):
    color = "green" if value >= 0 else "red"
    return f'<span style="color:{color}">{value}</span>'

