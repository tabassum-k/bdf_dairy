frappe.query_reports["Sales Invoice Analytics"] = {
	filters: [
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
	],
};
