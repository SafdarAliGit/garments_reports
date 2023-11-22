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
            "width": 180
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Data",
            "width": 180
        }
    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []
    if doctype == 'sr':
        if filters.get("name"):
            conditions.append(f"`{doctype}`.master_towel_costing = %(name)s")
    elif doctype == 'mtc':
        if filters.get("name"):
            conditions.append(f"`{doctype}`.name = %(name)s")
    elif doctype == 'glentry':
        if filters.get("name"):
            conditions.append(f"`{doctype}`.master_towel_costing = %(name)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []


    mtc_query = """
            SELECT 
                mtcrm.raw_material AS rm_item_code,
                ROUND(SUM(mtcrm.yarn_required_in_lbs),2) AS consumed_qty,
                ROUND(SUM(mtcrm.bags_reqd)) AS bags,
                SUM(mtcrm.cost) AS amount
            FROM 
                `tabMaster Towel Costing` AS mtc, `tabMaster Towel Costing Raw Material` AS mtcrm, `tabItem` AS item
            WHERE
                mtcrm.raw_material = item.item_code AND item.item_group = 'Yarn' AND mtc.docstatus < 1 AND mtc.name = mtcrm.parent AND
                {conditions}
            GROUP BY
                mtcrm.raw_material
            """.format(conditions=get_conditions(filters, "mtc"))

    mtc_result = frappe.db.sql(mtc_query, filters, as_dict=1)

    srsi_query = """
                SELECT 
                    srsi.rm_item_code,
                    ROUND(SUM(srsi.consumed_qty),2) AS consumed_qty,
                    ROUND(SUM(srsi.consumed_qty/100)) AS bags,
                    SUM(srsi.amount) AS amount
                FROM 
                    `tabSubcontracting Receipt Supplied Item` AS srsi, `tabSubcontracting Receipt` AS sr, `tabItem` AS item
                WHERE
                    srsi.rm_item_code = item.item_code AND item.item_group = 'Yarn' AND sr.docstatus = 1 AND sr.name = srsi.parent AND
                    {conditions}
                GROUP BY
                    srsi.rm_item_code
                """.format(conditions=get_conditions(filters, "sr"))

    srsi_result = frappe.db.sql(srsi_query, filters, as_dict=1)

    glentry_query = """
                SELECT 
                    glentry.account AS rm_item_code,
                    glentry.posting_date AS consumed_qty,
                    "------------" AS bags,
                    SUM(glentry.debit_in_account_currency) AS amount
                FROM 
                    `tabGL Entry` AS glentry
                WHERE
                    glentry.debit_in_account_currency >0 AND  glentry.is_cancelled = 0 AND glentry.docstatus = 1 AND voucher_type = 'Subcontracting Receipt' AND
                    {conditions}
                GROUP BY
                    glentry.posting_date, glentry.account 
                """.format(conditions=get_conditions(filters, "glentry"))

    glentry_result = frappe.db.sql(glentry_query, filters, as_dict=1)
    # sum for first query
    total_yarn_required_in_lbs = 0
    total_bags_reqd = 0
    total_cost = 0
    heading1=[{
        "rm_item_code": _("<b style='font-size: 12px;'><u>Master Costing Yarn Projection</u></b>"),
        "consumed_qty": _("------------"),
        "bags": _("------------"),
        "amount": None,
    }]

    for row in mtc_result:
        total_yarn_required_in_lbs += row["consumed_qty"]
        total_bags_reqd += row["bags"]
        total_cost += row["amount"]
    mtc_result.append({
        "rm_item_code": _("<b>Total</b>"),
        "consumed_qty": f"<b>{int(total_yarn_required_in_lbs)}</b>",
        "bags": f"<b>{total_bags_reqd}</b>",
        "amount": total_cost,
    })
    mtc_result = heading1 + mtc_result

    # sum for second query
    total_consumed_qty = 0
    total_bags = 0
    total_amount = 0
    heading2=[{
        "rm_item_code": _("<b style='font-size: 12px;'><u>Actual Yarn Consumption</u></b>"),
        "consumed_qty": _("------------"),
        "bags": _("------------"),
        "amount": None,
    }]
    for row in srsi_result:
        total_consumed_qty += row["consumed_qty"]
        total_bags += row["bags"]
        total_amount += row["amount"]
    srsi_result.append({
        "rm_item_code": _("<b>Total</b>"),
        "consumed_qty": f"<b>{int(total_consumed_qty)}</b>",
        "bags": f"<b>{total_bags }</b>",
        "amount": total_amount,
    })
    srsi_result = heading2 + srsi_result

    # sum for third query
    total_gle_amount = 0
    heading3 = [{
        "rm_item_code": _("<b style='font-size: 12px;'><u>Payment Entries</u></b>"),
        "consumed_qty": _("------------"),
        "bags": _("------------"),
        "amount":None,
        },
        {
            "rm_item_code": _("<b style='font-size: 12px;'>Debit Account</b>"),
            "consumed_qty": _("<b style='font-size: 12px;'>Posting Date</b>"),
            "bags": _("------------"),
            "amount":_("<b style='font-size: 12px;'>Debit Amount</b>"),
        }
    ]
    for row in glentry_result:
        total_gle_amount += row["amount"]
    glentry_result.append({
        "rm_item_code": _("<b>Total</b>"),
        "consumed_qty": _("------------"),
        "bags": _("------------"),
        "amount": total_gle_amount,
    })
    glentry_result = heading3 + glentry_result
# diff of sums
    srsi_result.append(
        {
            "rm_item_code": _("<b>Difference</b>"),
            "consumed_qty": f"<b>{int(total_yarn_required_in_lbs - total_consumed_qty)}</b>",
            "bags": f"<b>{total_bags_reqd - total_bags}</b>",
            "amount": total_cost - total_amount,
        }
    )
    # sum for third query
    data.extend(mtc_result)
    data.extend(srsi_result)
    data.extend(glentry_result)

    return data
