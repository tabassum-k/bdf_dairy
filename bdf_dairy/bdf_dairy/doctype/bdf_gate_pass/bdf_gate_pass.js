frappe.ui.form.on('BDF Gate Pass', {
	setup(frm){
		frm.set_query('transporter', function () {
			return {
				filters: {
					'is_transporter': 1
				}
			}
		});
	},
    refresh(frm){
		if (!frm.doc.__islocal) {
			frm.set_df_property("gate_pass_items", "hidden", 1);
			frm.set_df_property("gate_pass_items_summary", "hidden", 0);
		}
		if (frm.doc.__islocal) {
			frm.set_df_property("gate_pass_items_summary", "hidden", 1);
		}
	},
	get_sales_invoice(frm){
		erpnext.utils.map_current_doc({
			method: "bdf_dairy.bdf_dairy.doctype.bdf_gate_pass.bdf_gate_pass.make_sales_invoice",
			source_doctype: "Sales Invoice",
			target: frm,
			setters: [
				{fieldtype: "Link", label: "Route", options: "Route Master", fieldname: "route", default: frm.doc.route},
				{fieldtype: "Select", label: "Delivery Shift", options: "\nMorning\nEvening", fieldname: "delivery_shift", default: frm.doc.shift},
			],
			get_query_filters: {
				docstatus: 1, status: ["=", ["To Bill"]], gate_pass: 0, posting_date: frm.doc.date,
			},
		});
	},
	get_stock_entry(frm){
		erpnext.utils.map_current_doc({
			method: "bdf_dairy.bdf_dairy.doctype.bdf_gate_pass.bdf_gate_pass.make_stock_entry",
			source_doctype: "Stock Entry",
			target: frm,
			setters: [
				{
					fieldtype: "Select",
					label: "Delivery Shift",
					options: "\nMorning\nEvening",
					fieldname: "custom_delivery_shift",
					default: frm.doc.shift
				},
			],
			get_query_filters: {
				docstatus: 1,
				stock_entry_type: "Material Transfer For Gate Pass",
				custom_gate_pass: 0,
				posting_date: frm.doc.date
			},
			post_process: (source_docs, target_doc) => {
				if (source_docs && target_doc.items) {
					target_doc.items.forEach(item => {
						item.t_warehouse = frm.doc.warehouse || item.t_warehouse;
					});
				}
			},
		});
	},
	calculate_extra_crate(frm){
		frm.call({
			'method': 'calculate_extra_crate',
			doc: frm.doc,
			freeze: true, // Freezes the screen with a loading indicator
        	freeze_message: 'Calculating extra crate...',
			callback: function(resp){
				frm.refresh_field('calculate_extra_crate')
				frm.reload_doc();
			}
		})
	}
});

function method_call(frm, method, list_of_table_remove = null) {
    list_of_table_remove = list_of_table_remove || [];
    list_of_table_remove.forEach(function(table_name) {
        frm.clear_table(table_name);
        frm.refresh_field(table_name);
    });
    frm.call({
        method: method,
        doc: frm.doc,
    });
}