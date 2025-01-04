# Copyright (c) 2025, BDF and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters):
    if not filters:
        filters = {}

    conditions = []
    params = {"from_date": filters.get("from_date"), "to_date": filters.get("to_date")}

    if filters.get("shift"):
        conditions.append("shift = %(shift)s")
        params["shift"] = filters.get("shift")
    
    if filters.get("dcs"):
        conditions.append("dcs_id in %(dcs)s")
        params["dcs"] = filters.get("dcs")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = f" AND {where_clause}"

    query = f"""
        SELECT 
            dcs_id as dcs, 
            date, 
            member, 
            shift, 
            SUM(volume) as qty, 
            SUM(volume) * 1.003 as qty_kg, 
            AVG(fat) as fat, 
            AVG(snf) as snf, 
            SUM(fat_kg) as kg_fat, 
            SUM(snf_kg) as kg_snf
        FROM 
            `tabMilk Entry`
        WHERE 
            docstatus = 1 
            AND date BETWEEN %(from_date)s AND %(to_date)s
            {where_clause}
        GROUP BY 
            dcs_id, date, member, shift
    """

    data = frappe.db.sql(query, params, as_dict=True)
    return data

def get_columns():
    return [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": "DCS", "fieldname": "dcs", "fieldtype": "Link", "options": "Warehouse", "width": 120},
        {"label": "Member", "fieldname": "member", "fieldtype": "Data", "width": 120},
        {"label": "Shift", "fieldname": "shift", "fieldtype": "Data", "width": 120},
        {"label": "Qty (LITER)", "fieldname": "qty", "fieldtype": "Float", "width": 120},
        {"label": "Qty (KG)", "fieldname": "qty_kg", "fieldtype": "Float", "width": 120},
        {"label": "FAT", "fieldname": "fat", "fieldtype": "Float", "width": 120},
        {"label": "SNF", "fieldname": "snf", "fieldtype": "Float", "width": 120},
        {"label": "KG FAT", "fieldname": "kg_fat", "fieldtype": "Float", "width": 120},
        {"label": "KG SNF", "fieldname": "kg_snf", "fieldtype": "Float", "width": 120},
    ]
