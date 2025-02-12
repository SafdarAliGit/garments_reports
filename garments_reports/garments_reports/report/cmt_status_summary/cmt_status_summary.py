from frappe import _
import frappe  

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    columns = [
        {"label": _("Date"), "fieldname": "transaction_date", "fieldtype": "Date", "width": 120},
        {"label": _("PO#"), "fieldname": "master_towel_costing", "fieldtype": "Link", "options": "Master Towel Costing", "width": 120},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 120},
        {"label": _("Service Item"), "fieldname": "subcontracting_for", "fieldtype": "Data", "width": 150},
        {"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 120},
        {"label": _("RM Required Qty"), "fieldname": "total_required_qty", "fieldtype": "Float", "width": 120},
        {"label": _("RM Supplied Qty"), "fieldname": "total_supplied_qty", "fieldtype": "Float", "width": 120},
        {"label": _("RM Balance Qty"), "fieldname": "balance_qty", "fieldtype": "Float", "width": 120}
    ]
    return columns

def get_conditions(filters, doctype):
    conditions = []
    
    if filters.get("subcontracting_for"):
        if filters["subcontracting_for"] == "All":
            conditions.append(f"`{doctype}`.subcontracting_for IN ('Stitching Charges', 'Packing Charges')")
        else:
            conditions.append(f"`{doctype}`.subcontracting_for = %(subcontracting_for)s")
    
    if filters.get("start_date"):
        conditions.append(f"`{doctype}`.transaction_date >= %(start_date)s")

    if filters.get("end_date"):
        conditions.append(f"`{doctype}`.transaction_date <= %(end_date)s")
    
    return " AND ".join(conditions) if conditions else "1=1"

def get_data(filters):
    sco_entry = """
        SELECT 
            so.transaction_date,
            so.supplier,
            so.master_towel_costing,
            so.subcontracting_for,
            ROUND(so.total_qty, 2) AS total_qty,
            ROUND(so.total_required_qty, 2) AS total_required_qty,
            ROUND(so.total_supplied_qty, 2) AS total_supplied_qty,
            ROUND(so.total_required_qty - so.total_supplied_qty, 2) AS balance_qty
        FROM 
            `tabSubcontracting Order` so
        WHERE 
            {conditions}
            AND so.docstatus = 1
    """.format(conditions=get_conditions(filters, "so"))
    
    sco_result = frappe.db.sql(sco_entry, filters or {}, as_dict=1)
    
    return sco_result
