// Copyright (c) 2024, BDF and contributors
// For license information, please see license.txt

frappe.ui.form.on('BDF Gate Pass Reconcilation', {
	setup: function(frm) {
		frm.set_query('gate_pass', function () {
			return {
				filters: {
					'reconcilation_done': 0,
					'route': frm.doc.route,
					'docstatus': 1
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

frappe.ui.form.on('BDF Gate Pass Reconcilation Sales Invoice Details', {
	customer(frm, cdt, cdn){
		get_customer_opening(frm, cdt, cdn);
	},
	crate_type(frm, cdt,cdn){
		get_customer_opening(frm, cdt, cdn);
	}
})

function get_customer_opening(frm, cdt, cdn){
	let row = locals[cdt][cdn];
	if(row.customer && row.crate_type){
		frm.call({
			method: 'get_customer_opening',
			doc: frm.doc,
			args: {
				customer: row.customer,
				crate_type: row.crate_type
			},
			callback: function(resp){
				if(resp.message){
					frappe.model.set_value(cdt, cdn, 'crate_openning_qty', resp.message);
				}
			}
		})
	}
}

frappe.ui.form.on('BDF Gate Pass Reconcilation Stock Entry Details', {
	warehouse(frm, cdt, cdn){
		get_warehouse_opening(frm, cdt, cdn);
	},
	crate_type(frm, cdt,cdn){
		get_warehouse_opening(frm, cdt, cdn);
	}
})

function get_warehouse_opening(frm, cdt, cdn){
	let row = locals[cdt][cdn];
	if(row.customer && row.crate_type){
		frm.call({
			method: 'get_warehouse_opening',
			doc: frm.doc,
			args: {
				customer: row.customer,
				crate_type: row.crate_type
			},
			callback: function(resp){
				if(resp.message){
					frappe.model.set_value(cdt, cdn, 'crate_openning_qty', resp.message);
				}
			}
		})
	}
}

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