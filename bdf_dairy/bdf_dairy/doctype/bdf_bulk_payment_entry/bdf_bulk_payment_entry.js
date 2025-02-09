// Copyright (c) 2024, Erpdata and contributors
// For license information, please see license.txt

frappe.ui.form.on('BDF Bulk Payment Entry', {
	setup: function (frm, cdt, cdn) {
		frm.fields_dict['bulk_payment_entry_details'].grid.get_field('party_type').get_query = function (doc, cdt, cdn) {
			return {
				filters: [
					['DocType', 'name', 'in', ['Customer', 'Supplier', 'Shareholder', 'Employee']]
				]
			};
		};
	}
});


frappe.ui.form.on('BDF Bulk Payment Entry', {
	setup: function (frm) {
		frm.set_query("party_type", function (doc) {
			return {
				filters: [
					['DocType', 'name', 'in', ['Customer', 'Supplier', 'Shareholder', 'Employee']]
				]
			};
		});
	}
});

frappe.ui.form.on('BDF Bulk Payment Entry Details', {
	check: function(frm) {
        frm.clear_table("payment_reference");
		frm.refresh_field('payment_reference');
		frm.call({
			method:'call_two_in_one',
			doc:frm.doc
		})
	}
});

frappe.ui.form.on('BDF Bulk Payment Entry Details', {
	check2: function(frm) {
        frm.clear_table("payment_reference");
		frm.refresh_field('payment_reference');
		frm.call({
			method:'call_two_in_one',
			doc:frm.doc
		})
	}
});




frappe.ui.form.on('BDF Bulk Payment Entry', {
	mode_of_payment: function(frm) {
		frm.call({
			method:'get_paid_to_account',
			doc:frm.doc
		})
	}
});

frappe.ui.form.on('BDF Bulk Payment Entry', {
	invoices: function(frm) {
        frm.clear_table("payment_reference");
		frm.refresh_field('payment_reference');
		frm.call({
			method:'invoices',
			doc:frm.doc
		})
	}
});

frappe.ui.form.on('BDF Bulk Payment Entry', {
	orders: function(frm) {
        frm.clear_table("payment_reference");
		frm.refresh_field('payment_reference');
		frm.call({
			method:'orders',
			doc:frm.doc
		})
	}
});



frappe.ui.form.on('BDF Bulk Payment Entry Details', {
	party: function (frm) {
		frm.call({
			method: 'get_accounts',
			doc: frm.doc
		})
	}
});

frappe.ui.form.on('BDF Bulk Payment Entry Details', {
	bulk_payment_entry_details_add: function (frm, cdt, cdn) {
		frm.refresh_field("bulk_payment_entry_details")
		frm.call({
			method: 'set_party_type',
			doc: frm.doc
		})
		frm.clear_table("bulk_payment_entry_details");
	}
});


frappe.ui.form.on('BDF Bulk Payment Entry Details', {
    bulk_payment_entry_details_remove: function(frm, cdt, cdn) {
        frm.clear_table("payment_reference");
        frm.refresh_field("payment_reference");
        frm.call({
            method: 'call_two_in_one',
            doc: frm.doc
        });
        frm.call({
            method: 'get_outstanding',
            doc: frm.doc
        });
    }
});

frappe.ui.form.on('BDF Bulk Payment Entry Details', {
	party: function (frm, cdt, cdn) {
		frm.call({
			method: 'set_pn',
			doc: frm.doc
		})
	}
});

frappe.ui.form.on('BDF Bulk Payment Reference', {
	allocated_amount: function (frm, cdt, cdn) {
		frm.call({
			method: 'get_allocatedsum',
			doc: frm.doc
		});
	}
});


frappe.ui.form.on('BDF Bulk Payment Entry', {
	gate_pass: function (frm) {	
		frm.clear_table("bulk_payment_entry_details");
		frm.clear_table("payment_reference");
		frm.call({
			method: 'gate_pass_cll',
			doc: frm.doc
		});
		frm.refresh_table("bulk_payment_entry_details");
		frm.refresh_table("payment_reference");	
	},

});

frappe.ui.form.on('BDF Bulk Payment Entry Payment Denomination', {
	denomination: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.denomination && d.count){
			frappe.model.set_value(cdt, cdn, 'total', d.denomination * d.count)
		}
	},
	count: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.denomination && d.count){
			frappe.model.set_value(cdt, cdn, 'total', d.denomination * d.count)
		}
	},
});


frappe.ui.form.on("BDF Bulk Payment Entry", {
	get_filter: async function (frm) {
		await frm.call({
			method: 'gate',
			doc: frm.doc,
			freeze:true,
			callback: function (r) {
				if (r.message) {
					var k = r.message;
					frm.fields_dict.gate_pass.get_query = function (doc, cdt, cdn) {
						return {
							filters: [
								['BDF Gate Pass', 'name', 'in', k],
							]
						};
					};
				}
			}
		});
	}
});


// enter
frappe.ui.form.on('BDF Bulk Payment Entry', {
   
    before_save: function(frm) {
        calculate_total(frm);
    }
});

function calculate_total(frm) {
    let due_balance = 0;
    let grand = 0;
    let balance = 0;
    let total = 0;

    frm.doc.bulk_payment_entry_details.forEach(row => {
        total += row.paid_amount || 0;
        due_balance += row.due_balance || 0;
        grand += row.grand_tot || 0;
        balance += row.balance || 0;
    });

    frm.set_value('total', total);
    frm.set_value('duebalance', due_balance);
    frm.set_value('grandtotal', grand);
    frm.set_value('balance_', balance);
}