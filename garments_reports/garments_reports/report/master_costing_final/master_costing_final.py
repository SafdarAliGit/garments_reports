# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def decimal_format(value, decimals):
    formatted_value = "{:.{}f}".format(value, decimals)
    return formatted_value


def get_columns():
    columns = [
        {
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "fieldtype": "Link",
            "options": "DocType",
            "width": 150
        },
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Voucher No"),
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 180
        },
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "GL Entry",
            "width": 180
        },
        {
            "label": _("Supplier"),
            "fieldname": "supplier",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type.party",
            "width": 180
        },


        {
            "label": _("Grand Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Against"),
            "fieldname": "against",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Item"),
            "fieldname": "items",
            "fieldtype": "Data",
            "width": 250
        }

    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []

    if doctype in ["Purchase Invoice", "Stock Entry", "GL Entry"]:
        conditions.append(f"`tab{doctype}`.master_towel_costing = %(name)s")

    return " AND ".join(conditions)


def get_account_type_from_name(account_name):
    try:
        account_doc = frappe.get_doc("Account", account_name)
        account_type = account_doc.account_type
        return account_type
    except frappe.DoesNotExistError:
        return None


def get_data(filters):
    data = []

    purchase = """
                SELECT
                    `tabPurchase Invoice`.posting_date,
                    `tabPurchase Invoice`.name AS voucher_no,
                    `tabPurchase Invoice`.supplier,
                    `tabPurchase Invoice`.grand_total,
               
                    GROUP_CONCAT(
                        CONCAT(
                            `tabPurchase Invoice Item`.item_code,
                            " : ",
                            ROUND(`tabPurchase Invoice Item`.qty,0),
                            " X ",
                            ROUND(`tabPurchase Invoice Item`.rate,2),
                            " = ",
                            ROUND(`tabPurchase Invoice Item`.amount,2)
                        ) SEPARATOR '<br>'
                    ) AS items
                FROM
                    `tabPurchase Invoice`
                LEFT JOIN
                    `tabPurchase Invoice Item` ON `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                WHERE
                    {conditions} AND `tabPurchase Invoice`.docstatus = 1
                GROUP BY
                    `tabPurchase Invoice`.name, `tabPurchase Invoice`.supplier, `tabPurchase Invoice`.grand_total
                ORDER BY
                    `tabPurchase Invoice`.posting_date ASC, `tabPurchase Invoice`.name ASC
            """.format(conditions=get_conditions(filters, "Purchase Invoice"))

    stock_entry = """
                    SELECT
                        `tabStock Entry`.posting_date,
                        `tabStock Entry`.name AS voucher_no,
                        `tabStock Entry`.stock_entry_type,
                        `tabStock Entry`.total_amount AS grand_total,
                        GROUP_CONCAT(
                            CONCAT(
                                `tabStock Entry Detail`.item_code,
                                " : ",
                                ROUND(`tabStock Entry Detail`.qty,0),
                                " X ",
                                ROUND(`tabStock Entry Detail`.basic_rate,2),
                                " = ",
                                ROUND(`tabStock Entry Detail`.amount,2)
                            ) SEPARATOR '<br>'
                        ) AS items
                    FROM
                        `tabStock Entry`
                    LEFT JOIN
                        `tabStock Entry Detail` ON `tabStock Entry`.name = `tabStock Entry Detail`.parent
                    WHERE
                        {conditions} AND `tabStock Entry`.docstatus = 1
                    GROUP BY
                        `tabStock Entry`.name, `tabStock Entry`.supplier, `tabStock Entry`.total_amount
                    ORDER BY
                        `tabStock Entry`.posting_date ASC, `tabStock Entry`.name ASC
                """.format(conditions=get_conditions(filters, "Stock Entry"))

    gl_entry = """
                    SELECT
                        `tabGL Entry`.posting_date,
                        `tabGL Entry`.name AS voucher_no,
                        `tabGL Entry`.account,
                        `tabGL Entry`.against,
                        `tabGL Entry`.debit AS grand_total,
                        `tabGL Entry`.remarks
                    FROM
                        `tabGL Entry`
                    WHERE
                        {conditions} AND `tabGL Entry`.docstatus = 1
                    ORDER BY
                        `tabGL Entry`.posting_date ASC, `tabGL Entry`.name ASC
                """.format(conditions=get_conditions(filters, "GL Entry"))

    purchase_result = frappe.db.sql(purchase, filters, as_dict=1)
    stock_entry_result = frappe.db.sql(stock_entry, filters, as_dict=1)
    gl_entry_result = frappe.db.sql(gl_entry, filters, as_dict=1)

    # ====================CALCULATING TOTAL IN PURCHASE====================
    purchase_header_dict = [{'voucher_type': '<b><u>Purchase Invoice</b></u>', 'posting_date': '', 'voucher_no': '','account': '',
                             'supplier': '', 'grand_total': '',
                             'items': ''}]
    purchase_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------','account': '-------',
                           'supplier': '-------', 'grand_total': None,
                           'items': '--------------'}
    purchase_grand_total = 0
    for purchase in purchase_result:
        purchase_grand_total += purchase.grand_total

    purchase_total_dict['grand_total'] = purchase_grand_total
    purchase_result = purchase_header_dict + purchase_result
    purchase_result.append(purchase_total_dict)
    # ====================CALCULATING TOTAL IN PURCHASE END====================

    # ====================CALCULATING TOTAL IN STOCK ENTRY====================
    stock_entry_header_dict = [{'voucher_type': '<b><u>Stock Entry</b></u>', 'posting_date': '', 'voucher_no': '','account': '',
                                'supplier': '', 'grand_total': '',
                                'items': ''}]
    stock_entry_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------','account': '-------',
                              'supplier': '-------', 'grand_total': 0,
                              'items': '--------------'}
    stock_entry_grand_total = 0
    for stock_entry in stock_entry_result:
        stock_entry_grand_total += stock_entry.grand_total

    stock_entry_total_dict['grand_total'] = stock_entry_grand_total
    stock_entry_result = stock_entry_header_dict + stock_entry_result
    stock_entry_result.append(stock_entry_total_dict)
    # ====================CALCULATING TOTAL IN STOCK ENTRY END====================

    # ====================CALCULATING TOTAL IN GL ENTRY====================
    gl_entry_header_dict = [{'voucher_type': '<b><u>GL Entry</b></u>', 'posting_date': '', 'voucher_no': '','account': '',
                             'supplier': '',  'grand_total': '',
                             'items': ''}]
    gl_entry_total_dict = {'voucher_type': '<b>Sum</b>', 'posting_date': '-------', 'voucher_no': '-------','account': '-------',
                           'supplier': '-------', 'grand_total': 0,
                           'items': '--------------'}
    gl_entry_grand_total = 0
    for gl_entry in gl_entry_result:
        gl_entry_grand_total += gl_entry.grand_total

    gl_entry_total_dict['grand_total'] = gl_entry_grand_total
    gl_entry_result = gl_entry_header_dict + gl_entry_result
    gl_entry_result.append(gl_entry_total_dict)
    # ====================CALCULATING TOTAL IN GL ENTRY====================
    #
    # ====================TRANSACTION TYPE FILTER====================
    if filters.get('transaction_types') == "All":
        data.extend(purchase_result)
        data.extend(stock_entry_result)
        data.extend(gl_entry_result)
    if 'Purchases' in filters.get('transaction_types'):
        data.extend(purchase_result)
    if 'Stock Entry' in filters.get('transaction_types'):
        data.extend(stock_entry_result)
    if 'GL Entry' in filters.get('transaction_types'):
        data.extend(gl_entry_result)
        # ====================FILTERS END====================

    return data
