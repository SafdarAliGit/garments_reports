// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Master Costing Comparison"] = {
    "filters": [
        {

            "label": __("Master Towel Costing"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Master Towel Costing",
            "reqd": 1
        }
    ],
};

