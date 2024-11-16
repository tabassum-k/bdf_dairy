// Copyright (c) 2024, BDF and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Item Price Change', {
	item_code: function(frm) {
		if(frm.doc.item_code && frm.doc.type){
			frm.call({
				'method': 'get_all_item_price',
				doc: frm.doc
			})
		}
	},
	type: function(frm) {
		if(frm.doc.item_code && frm.doc.type){
			frm.call({
				'method': 'get_all_item_price',
				doc: frm.doc
			})
		}
	},
});
