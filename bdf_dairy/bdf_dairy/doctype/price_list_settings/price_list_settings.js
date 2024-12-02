// Copyright (c) 2024, BDF and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price List Settings', {
	standard_price_list: function(frm) {
		if(frm.doc.standard_price_list && frm.doc.item_code){
			frm.call({
				method: 'get_all_price_list',
				doc: frm.doc
			})
		}
	},
	item_code: function(frm) {
		if(frm.doc.standard_price_list && frm.doc.item_code){
			frm.call({
				method: 'get_all_price_list',
				doc: frm.doc
			})
		}
	},
	update_rate: function(frm) {
		frappe.confirm(
			'Are you sure you want to update the rate?', 
			() => {
				frm.call({
					method: 'update_rate',
					doc: frm.doc
				});
			},
			() => {
				console.log('Rate update canceled');
			}
		);
	},	
	setup(frm){
		set_filters(frm, 'standard_price_list', 'None',[['Price List', 'custom_is_standard', '=', 1]])
	}
});

function set_filters(frm, DocTypeFieldName, DocTypeField, filters){
    if(DocTypeField !== 'None'){
        frm.set_query(DocTypeFieldName, DocTypeField, function(doc, cdt, cdn) {
            return {
                filters: filters
            };
        });
    } else{
        frm.set_query(DocTypeFieldName, function(doc) {
            return {
                filters: filters,
            };
        });
    }
}