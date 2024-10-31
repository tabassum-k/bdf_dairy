// Copyright (c) 2024, BDF and contributors
// For license information, please see license.txt
frappe.ui.form.on('Tanker Inward', {
    before_save(frm){
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        frm.set_value('tanker_inward_date', formattedDate)
    },
    before_submit(frm){
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];
        frm.set_value('tanker_inward_date', formattedDate)
    },
    from_date: function(frm) {
        if(frm.doc.from_date && frm.doc.to_date && frm.doc.from_shift && frm.doc.to_shift && frm.doc.milk_type && frm.doc.dcs){
            get_milk_entry_data(frm);
        }
    },
    to_date: function(frm) {
        if(frm.doc.from_date && frm.doc.to_date && frm.doc.from_shift && frm.doc.to_shift && frm.doc.milk_type && frm.doc.dcs){
            get_milk_entry_data(frm);
        }
    },
    from_shift: function(frm) {
        if(frm.doc.from_date && frm.doc.to_date && frm.doc.from_shift && frm.doc.to_shift && frm.doc.milk_type && frm.doc.dcs){
            get_milk_entry_data(frm);
        }
    },
    to_shift: function(frm) {
        if(frm.doc.from_date && frm.doc.to_date && frm.doc.from_shift && frm.doc.to_shift && frm.doc.milk_type && frm.doc.dcs){
            get_milk_entry_data(frm);
        }
    },
    milk_type: function(frm) {
        if(frm.doc.from_date && frm.doc.to_date && frm.doc.from_shift && frm.doc.to_shift && frm.doc.milk_type && frm.doc.dcs){
            get_milk_entry_data(frm);
        }
    },
    dcs: function(frm) {
        if(frm.doc.from_date && frm.doc.to_date && frm.doc.from_shift && frm.doc.to_shift && frm.doc.milk_type && frm.doc.dcs){
            get_milk_entry_data(frm);
        }
    },
});

function get_milk_entry_data(frm) {
    frm.call({
        method: 'get_milk_entry_data',
        doc: frm.doc
    });
}



frappe.ui.form.on('Milk Received From Tanker', {
    qty_in_liter: function(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        row.qty_in_kg = parseFloat(row.qty_in_liter) * 1.03;

        if (row.fat && row.qty_in_liter && frm.doc.milk_type) {
            updateKgValues(frm, row, cdt, cdn, 'fat', row.fat);
        }
        
        if (row.snf && row.qty_in_liter && frm.doc.milk_type) {
            updateKgValues(frm, row, cdt, cdn, 'snf', row.snf);
        }
        frm.refresh_field("milk_received_from_tanker");
    },
    
    qty_in_kg: function(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        row.qty_in_liter = parseFloat(row.qty_in_kg) * 0.970874;

        if (row.fat && row.qty_in_liter && frm.doc.milk_type) {
            updateKgValues(frm, row, cdt, cdn, 'fat', row.fat);
        }

        if (row.snf && row.qty_in_liter && frm.doc.milk_type) {
            updateKgValues(frm, row, cdt, cdn, 'snf', row.snf);
        }
        frm.refresh_field("milk_received_from_tanker");
    },

    fat: function(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        if (row.fat && row.qty_in_liter && frm.doc.milk_type) {
            updateKgValues(frm, row, cdt, cdn, 'fat', row.fat);
        }
    },

    snf: function(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        if (row.snf && row.qty_in_liter && frm.doc.milk_type) {
            updateKgValues(frm, row, cdt, cdn, 'snf', row.snf);
        }
    }
});

async function updateKgValues(frm, row, cdt, cdn, type, percentage) {
    try {
        const response = await frm.call({
            method: 'get_weight',
            doc: frm.doc
        });

        if (response && response.message) {
            const weight = response.message;
            const kg_value = (row.qty_in_liter * weight) * (percentage / 100);
            console.log(kg_value);

            if (type === 'fat') {
                await frappe.model.set_value(cdt, cdn, 'kg_fat', kg_value);
            } else if (type === 'snf') {
                await frappe.model.set_value(cdt, cdn, 'kg_snf', kg_value);
            }

            frm.refresh_field("milk_received_from_tanker");
        }
    } catch (error) {
        console.error("Error updating kg values:", error);
    }
}
