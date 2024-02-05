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
            "label": _("Required"),
            "fieldname": "required_qty",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        },
        {
            "label": _("Send to Supplied "),
            "fieldname": "supplied_qty",
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
            "label": _("Received Balance"),
            "fieldname": "received_balance",
            "fieldtype": "Data",
            "width": 120,
            "default": ''
        }

    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []
    #
    # if filters.get("item_code") and doctype != "sco":
    #     conditions.append(f"`{doctype}`.item_code = %(item_code)s")
    if filters.get("name"):
        conditions.append(f"`{doctype}`.master_towel_costing = %(name)s")
    if filters.get("supplier"):
        conditions.append(f"`{doctype}`.supplier = %(supplier)s")

    return " AND ".join(conditions)


# SUM(socsi.required_qty) AS required_qty,
# SUM(socsi.supplied_qty) AS supplied_qty,
# SUM(socsi.required_qty - socsi.supplied_qty) AS balance

def get_data(filters):
    data = []

    sco_entry = """
        SELECT
            subquery.name,
            subquery.transaction_date,
            subquery.supplier,
            subquery.item_code,
            subquery.qty_pcs,
            subquery.qty,
            subquery.rm_item_code,
            subquery.required_qty,
            subquery.supplied_qty,
            subquery.balance_to_supplied,
            subquery.received_qty,
            subquery.description,
            subquery.received_balance
        FROM (
            SELECT
                so.name,
                so.transaction_date,
                so.supplier,
                soi.item_code,
                soi.qty_pcs,
                soi.qty,
                SUM(soi.received_qty) AS received_qty,
                NULL AS rm_item_code,
                NULL AS required_qty,
                NULL AS supplied_qty,
                NULL AS balance_to_supplied,
                NULL AS description,
                NULL AS received_balance
            FROM
                `tabSubcontracting Order` AS so
            LEFT JOIN
                `tabSubcontracting Order Item` AS soi ON so.name = soi.parent
            WHERE
                {conditions} AND so.docstatus = 1

            UNION

            SELECT
                so.name,
                so.transaction_date,
                so.supplier,
                soi.item_code,
                NULL AS qty_pcs,
                NULL AS qty,
                soi.received_qty,
                socsi.rm_item_code,
                socsi.required_qty,
                socsi.supplied_qty,
                socsi.required_qty - socsi.supplied_qty AS balance_to_supplied,
                NULL AS description,
                socsi.supplied_qty - soi.received_qty AS received_balance
                
            FROM
                `tabSubcontracting Order` AS so
            LEFT JOIN
                `tabSubcontracting Order Item` AS soi ON so.name = soi.parent
            LEFT JOIN
                `tabSubcontracting Order Supplied Item` AS socsi ON so.name = socsi.parent
            WHERE
                {conditions} AND so.docstatus = 1
                
            UNION

            SELECT
                so.name,
                NULL AS transaction_date,
                NULL AS supplier,
                NULL AS item_code,
                NULL AS qty_pcs,
                NULL AS qty,
                NULL AS received_qty,
                NULL AS rm_item_code,
                NULL AS required_qty,
                NULL AS supplied_qty,
                NULL AS balance_to_supplied,
                tsri.description,
                NULL AS received_balance
            FROM
                `tabSubcontracting Order` AS so
            LEFT JOIN
                `tabSubcontracting Receipt Item` AS tsri ON so.name = tsri.parent
            WHERE
                {conditions} AND so.docstatus = 1
            
        ) AS subquery
        GROUP BY subquery.rm_item_code,subquery.item_code,subquery.name, subquery.supplier
        ORDER BY subquery.name
    """.format(conditions=get_conditions(filters, "so"))

    sco_result = list(frappe.db.sql(sco_entry, filters, as_dict=1))
    # TO REMOVE DUPLICATES
    keys_to_check = ['name','received_qty']
    seen_values = {key: set() for key in keys_to_check}

    for entry in sco_result:
        key_values = tuple(entry[key] for key in keys_to_check)

        if any(value in seen_values[key] for key, value in zip(keys_to_check, key_values)):
            for key in keys_to_check:
                entry[key] = None
        else:
            for key, value in zip(keys_to_check, key_values):
                seen_values[key].add(value)

    # END
    data.extend(sco_result)
    return data
# or key_master_towel_costing in seen_value_master_towel_costing
#                 or key_item_code in seen_value_item_code or key_supplier in seen_value_supplier