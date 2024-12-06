// Copyright (c) 2024, BDF and contributors
// For license information, please see license.txt

frappe.ui.form.on('Minimum Order Quantity', {
    customer_group: function (frm) {
        if (frm.doc.customer_group) {
            console.log("Applying filter for customer group:", frm.doc.customer_group);
            set_multiselect_filter(frm, 'customers', [
                ['Customer', 'customer_group', '=', frm.doc.customer_group]
            ]);
        }
    }
});

function set_multiselect_filter(frm, fieldname, filters) {
    frm.set_query(fieldname, function (doc) {
        return {
            filters: filters
        };
    });
}

