# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("ID"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Subcontracting Order",
            "width": 150
        },
        {
            "label": _("Date"),
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
         "label": _("PO#"),
         "fieldname": "master_towel_costing",
         "fieldtype": "Link",
         "options": "Master Towel Costing",
         "width": 120
        },

        {
            "label": _("Supplier"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 120
        },
        {
            "label": _("Item Description"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200
        },
        {
            "label": _("Qty In Pcs"),
            "fieldname": "qty_pcs",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Qty In LBS"),
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Raw Material"),
            "fieldname": "rm_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 140
        },
        {
            "label": _("Color"),
            "fieldname": "color",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Required"),
            "fieldname": "required_qty",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Supplied Qty"),
            "fieldname": "supplied_qty",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Returned Qty"),
            "fieldname": "returned_qty",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Net Qty"),
            "fieldname": "net_qty",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Balance to supplied"),
            "fieldname": "balance_to_supplied",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Received in LBS"),
            "fieldname": "received_qty",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Received in Pcs"),
            "fieldname": "pcs",
            "fieldtype": "Data",
            "width": 120,
            "default": ''

        },
        {
            "label": _("Received Balance(LBS)"),
            "fieldname": "received_balance",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        }

    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []
    if filters.get("subcontracting_for"):
        conditions.append(f"`{doctype}`.subcontracting_for = %(subcontracting_for)s")
    if filters.get("name"):
        conditions.append(f"`{doctype}`.master_towel_costing = %(name)s")
    if filters.get("item_group"):
        conditions.append(f"socsi.rm_item_code IN (SELECT name FROM `tabItem` WHERE item_group =  %(item_group)s)")
    if filters.get("supplier"):
        conditions.append(f"`{doctype}`.supplier = %(supplier)s")

    return " AND ".join(conditions)


def get_data(filters):
    data = []
    # Get the item_group from filter
    # Adding the condition for item_group


    sco_entry = """
        SELECT
            so.name,
            so.transaction_date,
            so.supplier,
            so.master_towel_costing,
            soi.item_code,
            dp.color,
            soi.qty_pcs,
            soi.qty,
            soi.received_qty,
            socsi.rm_item_code,
            ROUND(socsi.required_qty,3) AS required_qty,
            socsi.supplied_qty,
            socsi.returned_qty,
            ROUND(socsi.supplied_qty - socsi.returned_qty,3) AS net_qty,
            soi.qty_pcs_receipt AS pcs,
            ROUND((socsi.required_qty ) - (socsi.supplied_qty + socsi.returned_qty),3) AS balance_to_supplied,
            ROUND(soi.qty - soi.received_qty,3) AS received_balance
        FROM 
            `tabSubcontracting Order` AS so
        
         JOIN 
            `tabSubcontracting Order Item` AS soi ON so.name = soi.parent
        LEFT JOIN 
            `tabSubcontracting Order Supplied Item` AS socsi ON so.name = socsi.parent
        LEFT JOIN 
            `tabSubcontracting Receipt Item` AS tsri ON so.name = tsri.subcontracting_order   
        LEFT JOIN 
            `tabDyeing Program` AS dp ON so.name = dp.parent
        WHERE 
            {conditions}
            AND so.docstatus = 1
        GROUP BY 
            so.name,socsi.rm_item_code,so.transaction_date, so.supplier, so.master_towel_costing, dp.color
        ORDER BY 
            so.name,soi.item_code,socsi.rm_item_code,so.transaction_date, so.supplier, so.master_towel_costing, dp.color
    """.format(conditions=get_conditions(filters, "so"))


    sco_result = frappe.db.sql(sco_entry, filters, as_dict=1)
    # TO REMOVE DUPLICATES
    keys_to_check = ['name', 'transaction_date', 'supplier', 'item_code','qty_pcs', 'qty', 'received_qty','master_towel_costing','pcs','received_balance']
    seen_values = []

    for entry in sco_result:
        key_values = tuple(entry[key] for key in keys_to_check)

        if key_values in seen_values:
            for key in keys_to_check:
                entry[key] = None
        else:
            seen_values.append(key_values)

    # END
    data.extend(sco_result)

    return data

