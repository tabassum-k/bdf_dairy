frappe.query_reports["Handling Loss"] = {
    "filters": [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
            reqd: 1,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
            reqd: 1,
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            reqd: 1,
        },
        {
            fieldname: "finished_item",
            label: __("Finished Item"),
            fieldtype: "MultiSelectList",
            options: "Item",
            get_data: (txt) => frappe.db.get_link_options("Item", txt),
        },
        {
            fieldname: "item_group",
            label: __("Finished Item Group"),
            fieldtype: "MultiSelectList",
            options: "Item Group",
            get_data: (txt) => frappe.db.get_link_options("Item Group", txt),
        },
        {
            fieldname: "item",
            label: __("Item"),
            fieldtype: "MultiSelectList",
            options: "Item",
            get_data: (txt) => frappe.db.get_link_options("Item", txt),
        },
        {
            fieldname: "summary",
            label: __("Get Summary"),
            fieldtype: "Check",
        },
    ]
};
