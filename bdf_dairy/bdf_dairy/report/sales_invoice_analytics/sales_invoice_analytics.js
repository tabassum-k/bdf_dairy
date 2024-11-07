// Copyright (c) 2024, BDF and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Invoice Analytics"] = {
	filters: [
		{
			fieldname: "doc_type",
			label: __("based_on"),
			fieldtype: "Select",
			options: ["Sales Invoice"],
			default: "Sales Invoice",
			reqd: 1,
		},
		{
			fieldname: "value_quantity",
			label: __("Value Or Qty"),
			fieldtype: "Select",
			options: [
				{ value: "Value", label: __("Value") },
				{ value: "Quantity", label: __("Quantity") },
			],
			default: "Value",
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
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
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
		{
			fieldname: "party",
			label: __("Customer"),
			fieldtype: "MultiSelectList",
			options: "Customer",
			get_data: function(txt) {
				return frappe.db.get_link_options("Customer", txt);
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
            fieldname: "shift",
            label: __("Shift"),
            fieldtype: "Select",
            options: ["","Morning", "Evening"],
            reqd: 0,
        },
	],
};
