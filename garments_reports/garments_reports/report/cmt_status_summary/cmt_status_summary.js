// Copyright (c) 2025, Tech Ventures and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["CMT Status Summary"] = {
    "filters": [
        {
            "fieldname": "subcontracting_for",
            "label": __("Subcontracting For"),
            "fieldtype": "Select",
            "options": "\nAll\nStitching Charges\nPacking Charges",  // Corrected options format
            "default": "All"
        },
        // {
        //     "fieldname": "start_date",
        //     "label": __("Start Date"),
        //     "fieldtype": "Date",
        //     "default": frappe.datetime.get_today(),  // Changed to get today’s date for better flexibility
        //     "reqd": 0
        // },
        // {
        //     "fieldname": "end_date",
        //     "label": __("End Date"),
        //     "fieldtype": "Date",
        //     "default": frappe.datetime.get_today(),  // Same as above for consistency
        //     "reqd": 0
        // }
    ]
};
