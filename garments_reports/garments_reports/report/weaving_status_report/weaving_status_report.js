frappe.query_reports["Weaving Status Report"] = {
    "filters": [
        {
            "fieldname": "item_code",
            "label": __("Service items"),
            "fieldtype": "Link",
            "options": "Item",
            "default": "Weaving Charges",
            // "reqd": 1

        },
        {
            "fieldname": "name",
            "label": __("Master Towel Costing"),
            "fieldtype": "Link",
            "options": "Master Towel Costing",
            "reqd": 1
        },
        {
            "fieldname": "supplier",
            "label": __("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier"
        }
    ]
};