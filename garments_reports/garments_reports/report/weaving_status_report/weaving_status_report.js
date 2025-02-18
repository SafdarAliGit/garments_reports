frappe.query_reports["Weaving Status Report"] = {
    "filters": [
        {
            "fieldname": "subcontracting_for",
            "label": __("Subcontracting For"),
            "fieldtype": "Select",
            "options": ["Weaving Charges","Dyeing Charges","Stitching Charges","Packing Charges"],
            "default": "Weaving Charges"
            // "reqd": 1

        },
        {
            "fieldname": "name",
            "label": __("Master Towel Costing"),
            "fieldtype": "Link",
            "options": "Master Towel Costing"
            // "reqd": 1
        },
        {
            "fieldname": "supplier",
            "label": __("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier"
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group"
        },
        {
            "fieldname": "subcontracting_order",
            "label": __("Subcontracting Order"),
            "fieldtype": "Link",
            "options": "Subcontracting Order"
        }
    ]
};
