"""Sentences that may contain only figure values and the run's dates."""

from __future__ import annotations

from figures import sentence


def _period_sentence(figures: dict, start, end, as_of) -> dict:
    return sentence(
        "period",
        (
            f"The as-of date typed for this run is {as_of.isoformat()}. "
            f"Records inside {start.isoformat()} to {end.isoformat()}: "
            f"{figures['in_period_total']['value']}. "
            f"Records outside that period, excluded from the cluster counts: "
            f"{figures['outside_period']['value']}."
        ),
        ["in_period_total", "outside_period"],
    )


def _cluster_sentences(clusters: list[dict], figures: dict) -> list[dict]:
    rows = []
    for cluster in clusters:
        figure_id = cluster["figure_id"]
        rows.append(
            sentence(
                f"cluster-{cluster['theme']}",
                (
                    "This cluster has "
                    f"{figures[figure_id]['value']} records inside the reporting period."
                ),
                [figure_id],
                theme=cluster["theme"],
            )
        )
    return rows


def _redress_sentence(figures: dict) -> dict:
    return sentence(
        "redress",
        (
            "Known redress recorded on the source records is "
            f"{figures['redress_pence']['value']} pence, from "
            f"{figures['redress_records']['value']} records. "
            f"Records with no redress figure: {figures['redress_missing']['value']}. "
            "No figure was imputed. A pence total of "
            f"{figures['redress_pence']['value']} with "
            f"{figures['redress_records']['value']} contributing records is only "
            "the sum of figures that were already on the records."
        ),
        ["redress_pence", "redress_records", "redress_missing"],
    )


def _outcome_sentences(figures: dict, outcome_ids: list[str]) -> list[dict]:
    rows = []
    for figure_id in outcome_ids:
        label = figure_id.removeprefix("outcome_")
        rows.append(
            sentence(
                figure_id,
                (
                    f"Records with the recorded outcome {label.replace('_', ' ')}: "
                    f"{figures[figure_id]['value']}."
                ),
                [figure_id],
                outcome=label,
            )
        )
    return rows


def _prior_sentence(state: str, figures: dict) -> dict:
    if state == "not_supplied":
        return sentence(
            "prior",
            "No prior-period file was supplied. This draft does not state a trend.",
            [],
        )
    if state != "reconciled":
        return sentence(
            "prior",
            "The prior-period file did not reconcile to its record ids. "
            "This draft does not quote a prior count.",
            [],
        )
    return sentence(
        "prior",
        (
            "The reconciled prior file lists "
            f"{figures['prior_in_period_total']['value']} records. "
            f"Records inside the current period: {figures['in_period_total']['value']}."
        ),
        ["prior_in_period_total", "in_period_total"],
    )


def _stale_sentence(stale: bool) -> dict:
    if stale:
        text = "The pinned sources are marked stale for this as-of date."
    else:
        text = "The pinned sources are inside the freshness window for this as-of date."
    return sentence("sources", text, [])


def _duplicates_sentence(figures: dict) -> dict:
    return sentence(
        "duplicates",
        (
            "Records whose redacted text matches another in-period record exactly: "
            f"{figures['duplicate_text_records']['value']}. "
            "Matching records are still counted."
        ),
        ["duplicate_text_records"],
    )


def common_sentences(context: dict) -> list[dict]:
    figures = context["figures"]
    rows = [
        _period_sentence(figures, context["period_start"], context["period_end"], context["as_of"]),
        *_cluster_sentences(context["clusters"], figures),
        _redress_sentence(figures),
        *_outcome_sentences(figures, context["outcome_ids"]),
        _duplicates_sentence(figures),
        _prior_sentence(context["prior_state"], figures),
        _stale_sentence(context["sources_stale"]),
    ]
    if context["report_blocked"]:
        rows.append(
            sentence(
                "report-blocked",
                "The requested report does not match the sector, so no regulatory narrative was drafted.",
                [],
            )
        )
    return rows


def consumer_duty_sentences(context: dict) -> list[dict]:
    figures = context["figures"]
    rows = [
        sentence(
            "duty-boundary",
            "This draft does not state whether the firm is complying with the Consumer Duty. "
            "The governing body has not reviewed this draft.",
            [],
        ),
        sentence(
            "vulnerability",
            (
                "Records where the intake starter returned a characteristic for a person to review: "
                f"{figures['vulnerability_flags_for_review']['value']}. "
                "No customer is labelled vulnerable."
            ),
            ["vulnerability_flags_for_review"],
        ),
    ]
    for figure_id in context["duty_ids"]:
        label = figure_id.removeprefix("duty_")
        rows.append(
            sentence(
                figure_id,
                (
                    "Records where the intake starter mapped a duty outcome for a person to review, "
                    f"group {label.replace('_', ' ')}: {figures[figure_id]['value']}. "
                    "This is not a finding of breach."
                ),
                [figure_id],
                duty_outcome=label,
            )
        )
    return rows


def housing_sentences(context: dict) -> list[dict]:
    figures = context["figures"]
    rows = [
        sentence(
            "code-boundary",
            "This draft does not state whether the landlord complies with the Code. "
            "The comply field on every prompt is empty.",
            [],
        ),
        sentence(
            "refused",
            f"Complaints the record marks as refused: {figures['refused_total']['value']}.",
            ["refused_total"],
        ),
        sentence(
            "service-improvements",
            (
                "Service improvement strings recorded on the source records: "
                f"{figures['service_improvements']['value']}. "
                "This draft does not invent one."
            ),
            ["service_improvements"],
        ),
        sentence(
            "ombudsman-materials",
            (
                "Ombudsman materials supplied with the batch: "
                f"{figures['ombudsman_materials']['value']}. "
                "A count of zero is not a finding that the Ombudsman published nothing."
            ),
            ["ombudsman_materials"],
        ),
    ]
    for figure_id in context["refusal_ids"]:
        rows.append(
            sentence(
                figure_id,
                f"This refusal type has {figures[figure_id]['value']} records.",
                [figure_id],
                refusal_type=figure_id.removeprefix("refused_"),
            )
        )
    return rows


def energy_sentences(context: dict) -> list[dict]:
    figures = context["figures"]
    rows = [
        sentence(
            "ofgem-boundary",
            "This draft does not say an Ofgem return is complete, and it does not send one.",
            [],
        ),
        sentence(
            "unassigned",
            (
                f"Records left unassigned: {figures['cluster_unassigned']['value']}. "
                "Unassigned records are not placed in the residual category."
            ),
            ["cluster_unassigned"],
        ),
        sentence(
            "empty-categories",
            (
                "Guidance categories with no matching records: "
                f"{figures['empty_table_1_categories']['value']}."
            ),
            ["empty_table_1_categories"],
        ),
        sentence(
            "resolved-flag",
            (
                "Records with the supplier's own flag that the complaint was resolved by the "
                f"end of the first working day: {figures['resolved_d1_yes']['value']}. "
                f"Records with that flag recorded as no: {figures['resolved_d1_no']['value']}. "
                f"Records where the flag was not recorded: {figures['resolved_d1_not_recorded']['value']}. "
                "This draft did not calculate the flag from dates."
            ),
            ["resolved_d1_yes", "resolved_d1_no", "resolved_d1_not_recorded"],
        ),
        sentence(
            "repeat",
            (
                "Records with repeat complaint recorded as true: "
                f"{figures['repeat_true']['value']}. "
                "Records where that field was not recorded: "
                f"{figures['repeat_not_recorded']['value']}. "
                "A missing field is not counted as a repeat."
            ),
            ["repeat_true", "repeat_not_recorded"],
        ),
    ]
    for figure_id in context["channel_ids"]:
        label = figure_id.removeprefix("channel_")
        rows.append(
            sentence(
                figure_id,
                (
                    f"Records in channel group {label.replace('_', ' ')}: "
                    f"{figures[figure_id]['value']}."
                ),
                [figure_id],
                channel_group=label,
            )
        )
    if context["accounts_supplied"]:
        rows.append(
            sentence(
                "accounts",
                (
                    "Electricity accounts supplied with the batch: "
                    f"{figures['electricity_accounts']['value']}. "
                    "Gas accounts supplied with the batch: "
                    f"{figures['gas_accounts']['value']}. "
                    "The sum of those two supplied figures is "
                    f"{figures['account_total']['value']}. "
                    "Complaints inside the period: "
                    f"{figures['in_period_total']['value']}. "
                    "This draft does not state a rate per hundred thousand accounts, "
                    "and it does not state a rate per ten thousand accounts."
                ),
                [
                    "electricity_accounts",
                    "gas_accounts",
                    "account_total",
                    "in_period_total",
                ],
            )
        )
    else:
        rows.append(
            sentence(
                "accounts",
                "Customer account totals were not supplied with the batch. This draft does not state a rate.",
                [],
            )
        )
    return rows
