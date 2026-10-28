"""Pinned sources for invoice exception triage. Checked 28 October 2026.

The strings below are short extracts used as labels. They are not a
restatement of the notice or the Act, and they are not a decision that
an invoice is valid.
"""

from __future__ import annotations

from datetime import date

SOURCES_PINNED_ON = date(2026, 10, 28)
LAST_VERIFIED = "2026-10-28"
DEFAULT_STALE_AFTER_DAYS = 90
PCR_REVOKED_ON = date(2025, 2, 24)
ACT_IN_FORCE_ON = date(2025, 2, 24)

# VAT Notice 700/21 sections 4.4 and 4.5, retrieved 28 October 2026.
# "£250 or less (including VAT)" and "does not exceed £250".
SIMPLIFIED_GROSS_CEILING_PENCE = 25_000

CATALOGUE_ID = "F004"
EXPERIMENT_ID = "exp-17-invoice-exception-triage"
INTAKE_EXPERIMENT_ID = "exp-12-document-intake"
INTAKE_PURPOSE = "general_records"
AP_REVIEWER_ROLE = "AP reviewer"
BANK_VERIFIER_ROLE = "Bank-detail verifier"

QUOTES = {
    "vat_700_21_2_4": (
        "Generally, you must keep all your business records for VAT purposes for at least 6 years."
    ),
    "vat_700_21_3_1_issue": (
        "Normally you must issue a VAT invoice within 30 days of the date you make the supply."
    ),
    "vat_700_21_3_2": (
        "The VAT invoices you receive are the primary evidence for you to recover VAT "
        "you have incurred as input tax."
    ),
    "vat_700_21_4_1": "You must show the following details on any VAT invoices you issue.",
    "vat_700_21_4_5": (
        "If you're not a retailer and the total value of your supply does not exceed £250 "
        "you may issue your customer with a simplified invoice."
    ),
    "pa2023_s68_2": (
        "Any sum due to be paid under the public contract by the contracting authority must be "
        "paid before the end of the period of 30 days beginning with the day the invoice is "
        "received, or if later the day the payment falls due in accordance with the invoice."
    ),
    "pa2023_s68_3": (
        "Subsection (2) does not apply if the contracting authority considers the invoice "
        "invalid, or disputes the invoice."
    ),
    "pa2023_s68_4": (
        "On receiving an invoice, the contracting authority must notify the payee without "
        "undue delay if it considers the invoice invalid or disputes it."
    ),
    "pa2023_s68_9": (
        "The minimum required information is the name of the invoicing party, a description "
        "of the goods, services or works supplied, the sum requested, and a unique identification number."
    ),
    "pa2023_s88_2": (
        "Section 88 uses the same 30-day shape for a regulated below-threshold contract. "
        "The later day is the day the sum first became due in accordance with the invoice."
    ),
    "pcr2015_reg113_revoked": (
        "The Public Contracts Regulations 2015 are recorded on legislation.gov.uk as revoked "
        "on 24 February 2025 by the Procurement Act 2023, Schedule 11, paragraph 5."
    ),
}

SOURCES = (
    {
        "id": "vat-notice-700-21",
        "title": "Record keeping (VAT Notice 700/21)",
        "url": "https://www.gov.uk/guidance/record-keeping-for-vat-notice-70021",
        "retrieved": LAST_VERIFIED,
        "page_updated": "2024-03-18",
        "used_for": "Sections 2.4, 3.1, 3.2, 4.1, 4.4, and 4.5. A field checklist, not a VAT assessment.",
    },
    {
        "id": "pa2023-s68",
        "title": "Procurement Act 2023, section 68",
        "url": "https://www.legislation.gov.uk/ukpga/2023/54/section/68",
        "retrieved": LAST_VERIFIED,
        "in_force": ACT_IN_FORCE_ON.isoformat(),
        "used_for": "Implied 30-day payment term in a public contract, and when that term does not apply.",
    },
    {
        "id": "pa2023-s88",
        "title": "Procurement Act 2023, section 88",
        "url": "https://www.legislation.gov.uk/ukpga/2023/54/section/88",
        "retrieved": LAST_VERIFIED,
        "in_force": ACT_IN_FORCE_ON.isoformat(),
        "used_for": "Implied 30-day payment term in a regulated below-threshold contract.",
    },
    {
        "id": "pcr2015-reg113",
        "title": "Public Contracts Regulations 2015, regulation 113 (revoked)",
        "url": "https://www.legislation.gov.uk/uksi/2015/102/regulation/113",
        "retrieved": LAST_VERIFIED,
        "used_for": "Shows the regulation no longer has effect. The 30-day rule in the text as made is not applied.",
    },
    {
        "id": "pa2023-sch11",
        "title": "Procurement Act 2023, Schedule 11, paragraph 5",
        "url": "https://www.legislation.gov.uk/ukpga/2023/54/schedule/11",
        "retrieved": LAST_VERIFIED,
        "used_for": "Paragraph 5 names the Public Contracts Regulations 2015. In force 24 February 2025.",
    },
)

LABELS = {
    "invoice number": "invoice_number",
    "invoice date": "invoice_date",
    "time of supply": "time_of_supply",
    "tax point": "time_of_supply",
    "date of issue": "date_of_issue",
    "supplier name": "supplier_name",
    "supplier address": "supplier_address",
    "supplier vat": "supplier_vat",
    "customer name": "customer_name",
    "customer address": "customer_address",
    "po number": "po_number",
    "purchase order": "po_number",
    "description": "description",
    "quantity": "quantity",
    "unit price": "unit_price",
    "net": "net",
    "amount excluding vat": "net",
    "vat rate": "vat_rate",
    "vat amount": "vat_amount",
    "gross": "gross",
    "total including vat": "gross",
    "currency": "currency",
    "cash discount": "cash_discount",
    "bank fingerprint": "bank_fingerprint",
}

# Full VAT invoice details in section 4.1, mapped to labels this starter reads.
# Cash discount is recorded as stated or not stated. Absence is not a gap:
# the notice requires the rate of any cash discount offered.
FULL_INVOICE_FIELDS = (
    "invoice_number",
    "supply_or_issue_date",
    "supplier_name",
    "supplier_address",
    "supplier_vat",
    "customer_name",
    "customer_address",
    "description",
    "quantity",
    "unit_price",
    "net",
    "vat_rate",
    "vat_amount",
)

# Sections 4.4 and 4.5. This starter does not decide that the supplier is a retailer.
SIMPLIFIED_FIELDS = (
    "supplier_name",
    "supplier_address",
    "supplier_vat",
    "supply_or_issue_date",
    "description",
    "gross",
    "vat_rate",
)

SECTION_68_MINIMUM = (
    "supplier_name",
    "description",
    "sum_requested",
    "invoice_number",
)

CLASS_ORDER = (
    "bank_detail_change",
    "duplicate_suspicion",
    "missing_po",
    "vat_supplier_mismatch",
    "price_variance",
    "quantity_variance",
)

ROUTE_BANK = "route_to_separate_bank_verification"
REFER_DUPLICATE = "refer_duplicate_suspicion_to_reviewer"
ASK_PO = "ask_buyer_to_confirm_purchase_order"
ASK_CORRECTED = "ask_supplier_for_corrected_invoice"
REFER_VARIANCE = "refer_variance_to_buyer"
INSUFFICIENT = "insufficient_evidence"
RETURN_MATCHING = "return_to_automated_matching"
WITHIN_TOLERANCE = "within_tolerance_reviewer_decides"

RECOMMENDATION_FOR = {
    "bank_detail_change": ROUTE_BANK,
    "duplicate_suspicion": REFER_DUPLICATE,
    "missing_po": ASK_PO,
    "vat_supplier_mismatch": ASK_CORRECTED,
    "price_variance": REFER_VARIANCE,
    "quantity_variance": REFER_VARIANCE,
}

BUYER_KINDS = frozenset(
    {
        "contracting_authority",
        "regulated_below_threshold",
        "not_a_public_contract",
        "unspecified",
    }
)
CONTRACT_EXCEPTIONS = frozenset({"concession_contract", "private_utility", "school"})
MATCH_TYPES = frozenset({"two_way", "three_way"})
DECISIONS = frozenset({"approve_resolution", "return_for_edit", "reject_resolution"})

SUPPLIER_NAME = "North Quay Supplies Ltd"
SUPPLIER_VAT = "GB999999999"
CUSTOMER_NAME = "Harbour Test Council"
BANK_FINGERPRINT = "master-account-1"

DEFAULT_LINES = (
    ("Invoice number", "SYN-INV-1001"),
    ("Invoice date", "2026-10-01"),
    ("Time of supply", "2026-10-01"),
    ("Supplier name", SUPPLIER_NAME),
    ("Supplier address", "1 Fixture Lane, Testtown"),
    ("Supplier VAT", SUPPLIER_VAT),
    ("Customer name", CUSTOMER_NAME),
    ("Customer address", "2 Fixture Square, Testtown"),
    ("PO number", "SYN-PO-44"),
    ("Description", "Synthetic stationery"),
    ("Quantity", "10"),
    ("Unit price", "5.00"),
    ("Net", "50.00"),
    ("VAT rate", "20%"),
    ("VAT amount", "10.00"),
    ("Gross", "60.00"),
    ("Currency", "GBP"),
    ("Cash discount", "none"),
    ("Bank fingerprint", BANK_FINGERPRINT),
)


def render_invoice(overrides: dict | None = None, extra: str = "") -> str:
    """Render one synthetic invoice. Overrides replace a label. None drops it."""

    chosen = dict(DEFAULT_LINES)
    if overrides:
        for label, value in overrides.items():
            if value is None:
                chosen.pop(label, None)
            else:
                chosen[label] = value
    lines = [f"{label}: {value}" for label, value in chosen.items()]
    text = "\n".join(lines)
    if extra:
        text = text + "\n" + extra
    if not text.endswith("\n"):
        text += "\n"
    return text
