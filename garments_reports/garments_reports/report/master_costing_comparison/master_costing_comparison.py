# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        filters = {}
    data = []
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Item Code"),
            "fieldname": "rm_item_code",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": _("LBS"),
            "fieldname": "consumed_qty",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Bags"),
            "fieldname": "bags",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Data",
            "width": 150
        }
    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []

    if filters.get("name"):
        conditions.append(f"{doctype}.master_towel_costing = %(name)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []
    srsi_query = """
            SELECT 
                srsi.rm_item_code,
                SUM(srsi.consumed_qty) AS consumed_qty,
                SUM(srsi.consumed_qty/100) AS bags,
                SUM(srsi.amount) AS amount
            FROM 
                `tabSubcontracting Receipt Supplied Item` AS srsi, `tabSubcontracting Receipt` AS sr, `tabItem` AS item
            WHERE
                srsi.rm_item_code = item.item_code AND item.item_group = 'Yarn' AND sr.docstatus = 1 AND sr.name = srsi.parent
                AND {conditions}
            GROUP BY
                srsi.rm_item_code
            """.format(conditions=get_conditions(filters, "sr"))

    srsi_result = frappe.db.sql(srsi_query, filters, as_dict=1)
    # for row in si_result:
    #     row.update({
    #         'cargo_in_tons': row.import_teus + row.import_teus,
    #     })
    # total_import_teus = 0
    # total_export_teus = 0
    # total_grand_total = 0
    # total_credit = 0
    # total_outstanding_amount = 0
    # total_customer_name = len(si_result)
    # for row in si_result:
    #     total_grand_total += row["grand_total"]
    #     total_credit += row["credit"]
    #     total_outstanding_amount += row["outstanding_amount"]
    #     total_import_teus += row["import_teus"]
    #     total_export_teus += row["export_teus"]
    # si_result.append({
    #     "customer": _("Total"),
    #     "customer_name": f"Total parties :  {total_customer_name}",
    #     "import_teus": total_import_teus,
    #     "export_teus": total_export_teus,
    #     "cargo_in_tons": total_import_teus + total_export_teus,
    #     "grand_total": total_grand_total,
    #     "credit": total_credit,
    #     "outstanding_amount": total_outstanding_amount
    # })
    data.extend(srsi_result)
    return data
