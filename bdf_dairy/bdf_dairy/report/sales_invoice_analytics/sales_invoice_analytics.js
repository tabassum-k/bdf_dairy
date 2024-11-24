// frappe.query_reports["Sales Invoice Analytics"] = {
// 	filters: [
// 		{
// 			fieldname: "view_by",
// 			label: __("View By"),
// 			fieldtype: "Select",
// 			options: [
// 				{ value: "Customer", label: __("Customer") },
// 				{ value: "Calendar", label: __("Calendar") }
// 			],
// 			default: "Customer",
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "company",
// 			label: __("Company"),
// 			fieldtype: "Link",
// 			options: "Company",
// 			default: frappe.defaults.get_user_default("Company"),
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "from_date",
// 			label: __("From Date"),
// 			fieldtype: "Date",
// 			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "to_date",
// 			label: __("To Date"),
// 			fieldtype: "Date",
// 			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "type",
// 			label: __("Type"),
// 			fieldtype: "Select",
// 			options: [
// 				{ value: "Quantity", label: __("Quantity") },
// 				{ value: "Amount", label: __("Amount") }
// 			],
// 			default: "Quantity",
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "party",
// 			label: __("Customer"),
// 			fieldtype: "MultiSelectList",
// 			options: "Customer",
// 			get_data: function(txt) {
// 				return frappe.db.get_link_options("Customer", txt);
// 			},
// 			reqd: 0,
// 		},
// 		{
// 			fieldname: "customer_group",
// 			label: __("Customer Group"),
// 			fieldtype: "MultiSelectList",
// 			options: "Customer Group",
// 			get_data: function(txt) {
// 				return frappe.db.get_link_options("Customer Group", txt);
// 			},
// 			reqd: 0,
// 		},
// 		{
// 			fieldname: "item",
// 			label: __("Item"),
// 			fieldtype: "MultiSelectList",
// 			options: "Item",
// 			get_data: function(txt) {
// 				return frappe.db.get_link_options("Item", txt);
// 			},
// 			reqd: 0,
// 		},
// 		{
// 			fieldname: "item_group",
// 			label: __("Item Group"),
// 			fieldtype: "MultiSelectList",
// 			options: "Item Group",
// 			get_data: function(txt) {
// 				return frappe.db.get_link_options("Item Group", txt);
// 			},
// 			reqd: 0,
// 		},
// 		{
// 			fieldname: "range",
// 			label: __("Range"),
// 			fieldtype: "Select",
// 			options: [
// 				{ value: "Daily", label: __("Daily") },
// 				{ value: "Weekly", label: __("Weekly") },
// 				{ value: "Monthly", label: __("Monthly") },
// 				{ value: "Quarterly", label: __("Quarterly") },
// 				{ value: "Yearly", label: __("Yearly") },
// 			],
// 			default: "Monthly",
// 			reqd: 1,
// 		},
// 	],
// };


frappe.query_reports["Sales Invoice Analytics"] = {
	filters: [
		{
			fieldname: "view_by",
			label: __("View By"),
			fieldtype: "Select",
			options: [
				{ value: "Customer", label: __("Customer") },
				{ value: "Calendar", label: __("Calendar") }
			],
			default: "Customer",
			reqd: 1,
			on_change: function () {
				let view_by = frappe.query_report.get_filter_value("view_by");
				frappe.query_report.toggle_filter_display("range", view_by === "Customer");
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
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "MultiSelectList",
			options: "Customer Group",
			get_data: function(txt) {
				return frappe.db.get_link_options("Customer Group", txt);
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
		// Ensure the "Range" filter visibility is updated on report load
		let view_by = frappe.query_report.get_filter_value("view_by");
		frappe.query_report.toggle_filter_display("range", view_by === "Customer");
	},
};
