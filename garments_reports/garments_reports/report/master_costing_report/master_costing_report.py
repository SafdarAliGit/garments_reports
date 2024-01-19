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
    elif doctype == 'pii':
        if filters.get("name"):
            conditions.append(f"`{doctype}`.master_towel_costing = %(name)s")
    elif doctype == 'mtc_other':
        if filters.get("name"):
            conditions.append(f"`{doctype}`.name = %(name)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []

    # AND item.item_group = 'Yarn'
    mtc_query = """
            SELECT 
                mtcrm.raw_material AS rm_item_code,
                ROUND(SUM(mtcrm.yarn_required_in_lbs),2) AS consumed_qty,
                ROUND(SUM(mtcrm.bags_reqd)) AS bags,
                ROUND(SUM(mtcrm.cost),2) AS amount
            FROM 
                `tabMaster Towel Costing` AS mtc, `tabMaster Towel Costing Raw Material` AS mtcrm, `tabItem` AS item, `tabItem Group` AS ig
            WHERE
                mtcrm.raw_material = item.item_code AND item.item_group = ig.name AND ig.parent_item_group = 'Yarn' AND mtc.docstatus < 1 AND mtc.name = mtcrm.parent AND
                {conditions}
            GROUP BY
                mtcrm.raw_material
            """.format(conditions=get_conditions(filters, "mtc"))

    mtc_result = frappe.db.sql(mtc_query, filters, as_dict=1)

    srsi_query = """
                SELECT 
                    srsi.rm_item_code,
                    ROUND(SUM(srsi.required_qty),2) AS consumed_qty,
                    ROUND(SUM(srsi.required_qty/100)) AS bags,
                    ROUND(SUM(srsi.amount),2) AS amount
                FROM 
                    `tabSubcontracting Receipt Supplied Item` AS srsi, `tabSubcontracting Receipt` AS sr, `tabItem` AS item, `tabItem Group` AS ig
                WHERE
                    srsi.rm_item_code = item.item_code AND item.item_group = ig.name AND ig.parent_item_group = 'Yarn' AND sr.docstatus = 1 AND sr.name = srsi.parent AND
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
                    ROUND(SUM(glentry.debit_in_account_currency),2) AS amount
                FROM 
                    `tabGL Entry` AS glentry
                WHERE
                    glentry.debit_in_account_currency >0 AND  glentry.is_cancelled = 0 AND glentry.docstatus = 1 AND voucher_type = 'Journal Entry' AND
                    {conditions}
                GROUP BY
                    glentry.posting_date, glentry.account 
                """.format(conditions=get_conditions(filters, "glentry"))

    glentry_result = frappe.db.sql(glentry_query, filters, as_dict=1)
    purchase_items = """
                    SELECT 
                        pii.item_code AS rm_item_code,
                        pi.name AS consumed_qty,
                        pi.supplier AS bags,
                        ROUND(SUM(pii.amount),2) AS amount
                    FROM 
                        `tabPurchase Invoice` AS pi, `tabPurchase Invoice Item` AS pii
                    WHERE
                        pii.parent = pi.name AND pi.docstatus = 1 AND pii.amount >0 AND
                        {conditions}
                    GROUP BY
                        pii.item_code, pi.name
                    """.format(conditions=get_conditions(filters, "pii"))

    purchase_items_result = frappe.db.sql(purchase_items, filters, as_dict=1)
    mtc_other_query = """
            SELECT 
                ROUND(mtc_other.weaving,2) AS weaving,
                ROUND(mtc_other.dying,2) AS dying,
                ROUND(mtc_other.stitching,2) AS stitching,
                ROUND(mtc_other.accessories,2) AS accessories,
                ROUND(mtc_other.clearing,2) AS clearing 
            FROM 
                `tabMaster Towel Costing` AS mtc_other
            WHERE
                 mtc_other.docstatus < 1  AND
                {conditions}
            """.format(conditions=get_conditions(filters, "mtc_other"))

    mtc_other_result = frappe.db.sql(mtc_other_query, filters, as_dict=1)
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
        "amount": f"<b>{total_cost:.2f}</b>",
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
        "amount": f"<b>{total_amount:.2f}</b>"
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
        "amount": f"<b>{total_gle_amount:.2f}</b>"
    })
    glentry_result = heading3 + glentry_result
# diff of sums
    srsi_result.append(
        {
            "rm_item_code": _("<b>Difference</b>"),
            "consumed_qty": f"<b>{int(total_yarn_required_in_lbs - total_consumed_qty):.2f}</b>",
            "bags": f"<b>{total_bags_reqd - total_bags}</b>",
            "amount": f"<b>{total_cost - total_amount:.2f}</b>"
        }
    )
    # sum for third query
    # sum for fourth query
    total_amount = 0
    heading4=[{
        "rm_item_code": _("<b style='font-size: 12px;'><u>Purchase Items</u></b>"),
        "consumed_qty": _("------------"),
        "bags": _("------------"),
        "amount": None,
    },
    {
        "rm_item_code": _("<b style='font-size: 12px;'>Item Code</b>"),
        "consumed_qty": _("<b style='font-size: 12px;'>Voucher No</b>"),
        "bags": _("<b style='font-size: 12px;'>Supplier</b>"),
        "amount": _("<b style='font-size: 12px;'>Amount</b>"),
    }
    ]
    for row in purchase_items_result:
        total_amount += row["amount"]
    purchase_items_result.append({
        "rm_item_code": _("<b>Total</b>"),
        "consumed_qty": _("------------"),
        "bags": _("------------"),
        "amount": f"<b>{total_amount:.2f}</b>"
    })
    purchase_items_result = heading4 + purchase_items_result
    # fifth query
    total_other_amount = mtc_other_result[0]['weaving'] + mtc_other_result[0]['dying'] + mtc_other_result[0]['stitching'] + \
                   mtc_other_result[0]['accessories'] + mtc_other_result[0]['clearing']
    heading5 = [{
        "rm_item_code": _("<b style='font-size: 12px;'><u>Master Costing Other Projection</u></b>"),
        "consumed_qty": _("------------"),
        "bags": _("------------"),
        "amount": None,
    },
        {
            "rm_item_code": _("<b style='font-size: 12px;'>Weaving</b>"),
            "consumed_qty": _("------------"),
            "bags": _("------------"),
            "amount": _(f"<b style='font-size: 12px;'>{mtc_other_result[0]['weaving']:.2f}</b>"),
        },
        {
            "rm_item_code": _("<b style='font-size: 12px;'>Dying</b>"),
            "consumed_qty": _("------------"),
            "bags": _("------------"),
            "amount": _(f"<b style='font-size: 12px;'>{mtc_other_result[0]['dying']:.2f}</b>"),
        },
        {
            "rm_item_code": _("<b style='font-size: 12px;'>Stitching</b>"),
            "consumed_qty": _("------------"),
            "bags": _("------------"),
            "amount": _(f"<b style='font-size: 12px;'>{mtc_other_result[0]['stitching']:.2f}</b>"),
        },
        {
            "rm_item_code": _("<b style='font-size: 12px;'>Accessories</b>"),
            "consumed_qty": _("------------"),
            "bags": _("------------"),
            "amount": _(f"<b style='font-size: 12px;'>{mtc_other_result[0]['accessories']:.2f}</b>"),
        },
        {
            "rm_item_code": _("<b style='font-size: 12px;'>Freight + Clearing</b>"),
            "consumed_qty": _("------------"),
            "bags": _("------------"),
            "amount": _(f"<b style='font-size: 12px;'>{mtc_other_result[0]['clearing']:.2f}</b>"),
        },
        {
            "rm_item_code": _("<b>Total</b>"),
            "consumed_qty": _("------------"),
            "bags": _("------------"),
            "amount": _(f"<b style='font-size: 12px;'>{total_other_amount:.2f}</b>"),
        }
    ]
    mtc_other_result = heading5

    data.extend(mtc_result)
    data.extend(srsi_result)
    data.extend(purchase_items_result)
    data.extend(glentry_result)
    data.extend(mtc_other_result)

    return data
