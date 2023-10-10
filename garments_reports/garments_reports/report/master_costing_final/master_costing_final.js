
frappe.query_reports["Master Costing Final"] = {
	"filters": [
		  {
            "fieldname": "transaction_types",
            "label": __("Transaction Types"),
            "fieldtype": "Select",
            "options": ["All", "Purchases","Stock Entry","GL Entry"],
            "default": ["All"]  // Preselecting "Sales"
        },
        {
            "fieldname": "name",
            "label": __("Master Towel Costing"),
            "fieldtype": "Link",
            "options": "Master Towel Costing",
            "reqd": 1
        }
	]
};
