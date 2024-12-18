// Copyright (c) 2024, BDF and contributors
// For license information, please see license.txt

frappe.ui.form.on('BDF Gate Pass Reconcilation', {
	setup: function(frm) {
		frm.set_query('gate_pass', function () {
			return {
				filters: {
					'reconcilation_done': 0
				}
			}
		});
	},
	gate_pass(frm){
		if(frm.doc.gate_pass){
			method_call(frm, 'get_gate_pass_data', ['sales_invoice_details', 'stock_entry_details', 'extra_crate'])
		}
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