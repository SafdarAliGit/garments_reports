// Copyright (c) 2023, Tech Ventures and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Custom Subcontract Order Summary"] = {
	"filters": [
		{
			label: __("Company"),
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			label: __("From Date"),
			fieldname: "from_date",
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},
		{
			label: __("To Date"),
			fieldname: "to_date",
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			label: __("Order Type"),
			fieldname: "order_type",
			fieldtype: "Select",
			options: ["Purchase Order", "Subcontracting Order"],
			default: "Subcontracting Order"
		},
		{
			label: __("Subcontract Order"),
			fieldname: "name",
			fieldtype: "Data"
		},
		{
			label: __("Master T.C"),
			fieldname: "master_towel_costing",
			fieldtype: "Link",
			options: "Master Towel Costing",
		}
	]
};

