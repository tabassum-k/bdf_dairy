// Copyright (c) 2024, BDF and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Invoice Analytics"] = {
	"filters": [
		{
            fieldname: "view_by",
            label: __("View By"),
            fieldtype: "Select",
            options: [
                { value: "Supplier", label: __("Supplier") },
                { value: "Calendar", label: __("Calendar") }
            ],
            default: "Supplier",
            reqd: 1,
            on_change: function () {
                let view_by = frappe.query_report.get_filter_value("view_by");
                // Toggle the "range" filter based on the selected view
                frappe.query_report.toggle_filter_display("range", view_by === "Vendor");
            },
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
            fieldname: "type",
            label: __("Type"),
            fieldtype: "Select",
            options: [
                { value: "Quantity", label: __("Quantity") },
                { value: "Amount", label: __("Amount") }
            ],
            default: "Quantity",
            reqd: 1,
        },
        {
            fieldname: "party",  // Change "party" to "Supplier"
            label: __("Supplier"),
            fieldtype: "MultiSelectList",
            options: "Supplier",
            get_data: function(txt) {
                return frappe.db.get_link_options("Supplier", txt);
            },
            reqd: 0,
        },
        {
            fieldname: "supplier_group",  // Supplier Group filter
            label: __("Supplier Group"),
            fieldtype: "MultiSelectList",
            options: "Supplier Group",
            get_data: function(txt) {
                return frappe.db.get_link_options("Supplier Group", txt);
            },
            reqd: 0,
        },
        {
            fieldname: "item",
            label: __("Item"),
            fieldtype: "MultiSelectList",
            options: "Item",
            get_data: function(txt) {
                return frappe.db.get_link_options("Item", txt);
            },
            reqd: 0,
        },
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "MultiSelectList",
            options: "Item Group",
            get_data: function(txt) {
                return frappe.db.get_link_options("Item Group", txt);
            },
            reqd: 0,
        },
        {
            fieldname: "range",
            label: __("Range"),
            fieldtype: "Select",
            options: [
                { value: "Daily", label: __("Daily") },
                { value: "Weekly", label: __("Weekly") },
                { value: "Monthly", label: __("Monthly") },
                { value: "Quarterly", label: __("Quarterly") },
                { value: "Yearly", label: __("Yearly") },
            ],
            default: "Monthly",
            reqd: 1,
        },
    ],

    onload: function () {
        let view_by = frappe.query_report.get_filter_value("view_by");
        frappe.query_report.toggle_filter_display("range", view_by === "Supplier");
    },
};
