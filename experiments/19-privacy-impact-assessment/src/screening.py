"""Screen recorded answers against Article 35(1) and (3) and the ICO list.

A yes is the project team's answer. It is not a finding that a DPIA is
legally required. ``dpia_required`` is never set. The privacy officer decides.
"""

from __future__ import annotations

from sources import (
    ARTICLE_35_1,
    ARTICLE_35_3,
    ICO_DUAA_BANNER,
    ICO_LIST,
    ICO_LIST_URL,
    ICO_TWO_FACTORS,
    ICO_WHEN_URL,
    UK_GDPR_ARTICLE_35_URL,
    WP248_CRITERIA,
)

TRI = ("yes", "no", "unknown")

READINGS = {
    "article_35_3_recorded": (
        "At least one recorded answer matches a type Article 35(3) says shall "
        "in particular be required. That is the project's answer. It is not a "
        "decision that Article 35 applies, and a 'no' on the Article 35(1) "
        "view does not clear it."
    ),
    "ico_list_recorded": (
        "At least one recorded answer matches an item on the ICO list in the "
        "way that list describes: either the when-page does not require another "
        "European criterion, or it does and another recorded criterion is yes. "
        "The ICO pages say the list is under review because of the Data (Use "
        "and Access) Act. This is not a decision that a DPIA is required."
    ),
    "ico_list_combination_not_shown": (
        "An ICO list item that the when-page ties to another European criterion "
        "is recorded as yes, and that other criterion is not recorded as yes. "
        "The row is not treated as a completed list trigger. The ICO also says "
        "that if you are in any doubt, they recommend a DPIA. This tool does "
        "not make that recommendation into a determination."
    ),
    "exception_not_decided": (
        "Genetic data is recorded, and the brief also says an individual GP or "
        "health professional processes it for direct care. The ICO list states "
        "that case as outside the item. This tool does not decide that the "
        "exception applies, and it does not decide that a DPIA is unnecessary."
    ),
    "wp248_two_factors_recorded": ICO_TWO_FACTORS
    + " Two of those criteria are recorded as yes. The privacy officer decides. "
    "This is not a strict rule, and this tool does not apply it as one.",
    "single_factor_recorded": (
        "One European-guidelines criterion, as listed on the ICO when-page, is "
        "recorded as yes. The same page says that in some cases one factor may "
        "be enough, and that it is good practice to do a DPIA. It also says "
        "you may be able to justify not doing one. This tool does not choose."
    ),
    "article_35_1_view_recorded": (
        "The brief records that the controller considers the processing likely "
        "to result in a high risk. Article 35(1) is the overarching test. This "
        "tool does not decide that the view is correct. A recorded 'no' on that "
        "view would not be a decision that Article 35(1) does not apply."
    ),
    "insufficient_facts": (
        "At least one screening answer is missing or not yes, no, or unknown. "
        "No completed screen result is given beyond that gap. Absence of an "
        "answer is not a 'no'."
    ),
    "recorded_answers_do_not_indicate": (
        "Every Article 35(3) item, every ICO list item, and every European "
        "criterion on the ICO when-page is recorded as no. That is not a "
        "decision that Article 35(1) does not apply. The ICO says that if the "
        "processing is not on those lists, it is for the controller to decide, "
        "and that if in doubt they recommend a DPIA. Article 35(4) now says the "
        "Commission shall publish the list. This tool does not decide whether "
        "the ICO page is that list."
    ),
}


def _tri(block: dict, key: str) -> tuple[str, str | None]:
    if key not in block or block[key] in (None, ""):
        return "unknown", None
    value = block[key]
    if value in TRI:
        return value, None
    return "unknown", "answer_not_yes_no_or_unknown"


def screen(answers: dict | None, *, article_35_1_view: str = "unknown") -> dict:
    """Return the screening. ``dpia_required`` stays null."""

    block = answers if isinstance(answers, dict) else {}
    flags: list[str] = []
    rejected: list[str] = []

    view, view_problem = _tri({"view": article_35_1_view}, "view")
    if view_problem:
        rejected.append("article_35_1_controller_view")
        view = "unknown"

    article_rows = []
    for key, quote in ARTICLE_35_3.items():
        value, problem = _tri(block, key)
        if problem:
            rejected.append(key)
        article_rows.append(
            {
                "id": key,
                "provision": "UK GDPR Article 35(3)",
                "recorded_answer": value,
                "statutory_text": quote,
                "triggers_list": value == "yes",
            }
        )

    wp_rows = []
    wp_values: dict[str, str] = {}
    for key, label in WP248_CRITERIA:
        value, problem = _tri(block, key)
        if problem:
            rejected.append(key)
        wp_values[key] = value
        wp_rows.append({"id": key, "criterion": label, "recorded_answer": value})

    ico_rows = []
    for item in ICO_LIST:
        value, problem = _tri(block, item["id"])
        if problem:
            rejected.append(item["id"])
        exception_value = None
        if item["exception_key"]:
            exception_value, exception_problem = _tri(block, item["exception_key"])
            if exception_problem:
                rejected.append(item["exception_key"])
        status = _ico_status(item, value, exception_value, wp_values)
        ico_rows.append(
            {
                "id": item["id"],
                "title": item["title"],
                "recorded_answer": value,
                "combination_required": item["combination_required"],
                "exception_recorded": exception_value,
                "status": status,
                "question": item["question"],
            }
        )

    if any(row["recorded_answer"] == "yes" for row in article_rows) and view == "no":
        flags.append("controller_view_does_not_clear_article_35_3")

    result = _result(article_rows, ico_rows, wp_rows, view)
    if rejected:
        flags.append("answer_rejected")
    indicated = result in {
        "article_35_3_recorded",
        "ico_list_recorded",
        "article_35_1_view_recorded",
    }
    return {
        "screen_result": result,
        "reading": READINGS[result],
        "indicated_on_recorded_answers": indicated,
        "dpia_required": None,
        "dpia_required_decided_by_this_tool": False,
        "article_35_1": {
            "recorded_view": view,
            "quote": ARTICLE_35_1,
            "url": UK_GDPR_ARTICLE_35_URL,
        },
        "article_35_3": article_rows,
        "ico_list": ico_rows,
        "wp248_as_listed_on_the_ico_when_page": wp_rows,
        "wp248_yes_count": sum(1 for row in wp_rows if row["recorded_answer"] == "yes"),
        "two_factors_usually_indicate": result == "wp248_two_factors_recorded",
        "flags": flags,
        "rejected_keys": rejected,
        "ico_pages_under_review": True,
        "ico_banner": ICO_DUAA_BANNER,
        "sources": [
            {"name": "UK GDPR Article 35", "url": UK_GDPR_ARTICLE_35_URL},
            {"name": "ICO, When do we need to do a DPIA?", "url": ICO_WHEN_URL},
            {"name": "ICO, Examples of processing likely to result in high risk", "url": ICO_LIST_URL},
        ],
        "wp248_opened": False,
    }


def _ico_status(item: dict, value: str, exception_value: str | None, wp_values: dict[str, str]) -> str:
    if value != "yes":
        return "recorded_no" if value == "no" else "unknown"
    if item["exception_key"] and exception_value == "yes":
        return "exception_not_decided"
    if not item["combination_required"]:
        return "recorded_yes"
    twin = item["twin_wp248"]
    others = [
        (key, answer)
        for key, answer in wp_values.items()
        if key != twin
    ]
    if any(answer == "yes" for _, answer in others):
        return "combination_recorded"
    return "combination_not_shown"


def _result(article_rows: list[dict], ico_rows: list[dict], wp_rows: list[dict], view: str) -> str:
    if any(row["triggers_list"] for row in article_rows):
        return "article_35_3_recorded"
    if any(row["status"] in {"recorded_yes", "combination_recorded"} for row in ico_rows):
        return "ico_list_recorded"
    if any(row["status"] == "combination_not_shown" for row in ico_rows):
        return "ico_list_combination_not_shown"
    if any(row["status"] == "exception_not_decided" for row in ico_rows):
        return "exception_not_decided"
    yes_count = sum(1 for row in wp_rows if row["recorded_answer"] == "yes")
    if yes_count >= 2:
        return "wp248_two_factors_recorded"
    if yes_count == 1:
        return "single_factor_recorded"
    if view == "yes":
        return "article_35_1_view_recorded"
    unanswered = any(row["recorded_answer"] == "unknown" for row in article_rows + ico_rows + wp_rows)
    if any(row["status"] == "exception_not_decided" for row in ico_rows) and not unanswered:
        return "exception_not_decided"
    if unanswered:
        return "insufficient_facts"
    return "recorded_answers_do_not_indicate"
