"""Phrase checks mapped to pinned FCA pages.

A signal is a word or phrase in the text the reviewer supplied. Finding it
is not a control that works. Missing it is not a breach. Rule stage is pinned
here and cannot be changed by the policy.
"""

from __future__ import annotations

# Stages:
# in_force_expectation — the FCA page describes this as something it looks for
#   now (MLR registration expectations, Travel Rule, financial promotions).
# final_not_yet_in_force — named in the June 2026 policy statements as final
#   rules or finalised guidance for the FSMA regime. The pinned pages put
#   commencement on 25 October 2027. Not scored as a current MLR expectation.
# consultation — the page calls it a consultation or a guidance consultation.
# planned_consultation — the page says the FCA will consult. Not verified as published.

REQUIREMENTS: list[dict] = [
    {
        "id": "R-BWRA-01",
        "control_area": "bwra",
        "title": "Business-wide risk assessment covering money laundering, terrorist financing and proliferation financing",
        "doc_types": ["bwra"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says the AML framework should include a "
            "business-wide risk assessment and its methodology, and that a BWRA "
            "focused on money laundering, terrorist financing and proliferation "
            "financing tends to perform better. The page cites Regulations 18 and "
            "18A of the MLRs. This checker does not interpret those regulations."
        ),
        "signal_groups": [
            ["business-wide risk assessment", "bwra"],
            ["money laundering"],
            ["terrorist financing"],
            ["proliferation"],
        ],
    },
    {
        "id": "R-BWRA-02",
        "control_area": "bwra",
        "title": "BWRA covers the five risk-factor headings named on the registration page",
        "doc_types": ["bwra"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says the BWRA should cover the risk factors in "
            "Regulation 18(2)(b): customers, products and services, geography, "
            "transactions and delivery channel."
        ),
        "signal_groups": [
            ["customer"],
            ["product"],
            ["geograph"],
            ["transaction"],
            ["delivery channel"],
        ],
    },
    {
        "id": "R-BWRA-03",
        "control_area": "bwra",
        "title": "BWRA methodology records inherent risk, control effectiveness and residual risk",
        "doc_types": ["bwra"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says the methodology should identify inherent "
            "risks, assess their severity, identify controls, assess control "
            "effectiveness, and calculate residual risk."
        ),
        "signal_groups": [
            ["inherent"],
            ["residual"],
            ["control effectiveness", "effectiveness of the control", "effectiveness of controls"],
        ],
    },
    {
        "id": "R-CRA-01",
        "control_area": "cra",
        "title": "Customer risk assessment produces a rating that drives due diligence",
        "doc_types": ["cra"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page expects a customer risk assessment with a "
            "risk-rating outcome that drives the level of due diligence."
        ),
        "signal_groups": [
            ["customer risk"],
            ["risk rating", "risk-rating"],
            ["due diligence"],
        ],
    },
    {
        "id": "R-CRA-02",
        "control_area": "cra",
        "title": "Customer risk assessment refers to the business-wide risk assessment",
        "doc_types": ["cra"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says the CRA risk factors must align with the "
            "BWRA, and gives the example of a product treated as higher risk in both."
        ),
        "signal_groups": [["business-wide risk assessment", "bwra"]],
    },
    {
        "id": "R-CRA-03",
        "control_area": "cra",
        "title": "Customer risk assessment says when it is run and when it is refreshed",
        "doc_types": ["cra"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page lists, among characteristics of a good application, "
            "detailing when the CRA is run against new customers and the frequency "
            "with which it is re-run."
        ),
        "signal_groups": [
            ["onboarding", "new customer"],
            ["periodic", "re-run", "rerun", "refresh", "annually"],
        ],
    },
    {
        "id": "R-CDD-01",
        "control_area": "cdd_onboarding",
        "title": "Onboarding procedure covers customer due diligence and enhanced due diligence",
        "doc_types": ["cdd_onboarding"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says operational procedures should cover customer "
            "due diligence and enhanced due diligence, and should show the steps "
            "rather than only recite the MLRs."
        ),
        "signal_groups": [
            ["customer due diligence", "cdd"],
            ["enhanced due diligence", "edd"],
        ],
    },
    {
        "id": "R-CDD-02",
        "control_area": "cdd_onboarding",
        "title": "Onboarding procedure covers PEPs and sanctions screening",
        "doc_types": ["cdd_onboarding"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page lists politically exposed persons and sanctions "
            "screening among the operational procedures, and expects sanctions "
            "controls that are kept current."
        ),
        "signal_groups": [
            ["politically exposed", "peps", "pep"],
            ["sanction"],
        ],
    },
    {
        "id": "R-CDD-03",
        "control_area": "cdd_onboarding",
        "title": "Onboarding procedure names the identity evidence the firm will accept",
        "doc_types": ["cdd_onboarding"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says that where identification uses documentary "
            "evidence, the procedures should document the evidence that will be "
            "accepted and any criteria it must satisfy."
        ),
        "signal_groups": [
            ["passport", "driving licence", "photographic", "acceptable identity", "identity document"],
        ],
    },
    {
        "id": "R-TM-01",
        "control_area": "transaction_monitoring",
        "title": "Transaction monitoring covers fiat or off-chain activity",
        "doc_types": ["transaction_monitoring"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page expects the firm to have selected and configured "
            "a fiat (off-chain) transaction monitoring tool, and to submit the rules "
            "and thresholds."
        ),
        "signal_groups": [
            ["transaction monitoring", "monitor transactions"],
            ["fiat", "off-chain", "off chain"],
        ],
    },
    {
        "id": "R-TM-02",
        "control_area": "transaction_monitoring",
        "title": "Transaction monitoring covers on-chain activity",
        "doc_types": ["transaction_monitoring"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page expects a cryptoasset (on-chain) transaction "
            "monitoring tool as well as the fiat tool. The FCA page says the FCA "
            "does not recommend or endorse any tool."
        ),
        "signal_groups": [["on-chain", "on chain", "blockchain analytics"]],
    },
    {
        "id": "R-TM-03",
        "control_area": "transaction_monitoring",
        "title": "Transaction monitoring states rules and thresholds",
        "doc_types": ["transaction_monitoring"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says the firm must submit the rules and thresholds "
            "set in the monitoring tools, and that they need to show how high-risk "
            "activity will be detected."
        ),
        "signal_groups": [["threshold"], ["rules", "alert"]],
    },
    {
        "id": "R-TR-01",
        "control_area": "travel_rule",
        "title": "Travel Rule procedure covers originator and beneficiary information",
        "doc_types": ["travel_rule"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-travel-rule", "fca-mlr-application"],
        "handbook_names": ["MLRs Part 7A, as named on the FCA pages"],
        "page_says": (
            "The Travel Rule statement says that from 1 September 2023 UK cryptoasset "
            "businesses will be required to collect, verify and share information "
            "about transfers. The registration page says procedures must show how "
            "beneficiary and originator details are received and transmitted, and "
            "cites Part 7A of the MLRs."
        ),
        "signal_groups": [
            ["travel rule"],
            ["originator"],
            ["beneficiary"],
            ["verif"],
        ],
    },
    {
        "id": "R-TR-02",
        "control_area": "travel_rule",
        "title": "Travel Rule material includes a flow of funds",
        "doc_types": ["travel_rule"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says Travel Rule procedures should be supported "
            "by a detailed flow of funds diagram which includes the flow of Travel "
            "Rule data, and any technology used."
        ),
        "signal_groups": [["flow of funds", "flow-of-funds"]],
    },
    {
        "id": "R-TR-03",
        "control_area": "travel_rule",
        "title": "Travel Rule procedure addresses a jurisdiction where the rule is not in force",
        "doc_types": ["travel_rule"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-travel-rule"],
        "handbook_names": [],
        "page_says": (
            "The Travel Rule statement says that when sending to a jurisdiction "
            "without the Travel Rule the firm still collects and verifies the "
            "information, and that when receiving a transfer with missing or "
            "incomplete information the firm makes a risk-based assessment, taking "
            "account of the status of the Travel Rule in the countries concerned."
        ),
        "signal_groups": [
            ["travel rule"],
            ["jurisdiction", "sunrise"],
            ["missing", "incomplete", "not yet in force", "not in force", "cannot receive"],
        ],
    },
    {
        "id": "R-TR-04",
        "control_area": "travel_rule",
        "title": "Travel Rule procedure says a supplier does not remove the firm's responsibility",
        "doc_types": ["travel_rule"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-travel-rule"],
        "handbook_names": [],
        "page_says": (
            "The Travel Rule statement says firms remain responsible for achieving "
            "compliance even when using third-party suppliers."
        ),
        "signal_groups": [
            ["remain responsible", "remains responsible", "our responsibility", "we remain responsible"],
        ],
        "applicability": {
            "any_of": ["third-party", "third party", "supplier", "vendor"],
            "search": "doc_types",
        },
    },
    {
        "id": "R-GOV-01",
        "control_area": "governance_smcr",
        "title": "Governance material names an MLRO or nominated officer",
        "doc_types": ["governance_smcr"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says the firm must appoint an MLRO, citing "
            "Regulation 21(3) of the MLRs, to receive disclosures under the "
            "Terrorism Act 2000 and the Proceeds of Crime Act 2002."
        ),
        "signal_groups": [["mlro", "nominated officer"]],
    },
    {
        "id": "R-GOV-02",
        "control_area": "governance_smcr",
        "title": "Governance material names a senior manager or board responsibility for the MLRs",
        "doc_types": ["governance_smcr"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page says Regulation 21(1)(a) requires a board member "
            "or senior manager responsible for compliance with the MLRs. The page "
            "says this is often the same person as the MLRO, and need not be."
        ),
        "signal_groups": [
            ["senior manager", "board"],
            ["money laundering", "mlrs"],
        ],
    },
    {
        "id": "R-GOV-03",
        "control_area": "governance_smcr",
        "title": "Governance material discusses SM&CR for the FSMA cryptoasset regime",
        "doc_types": ["governance_smcr"],
        "rule_stage": "final_not_yet_in_force",
        "source_ids": ["fca-regime-overview", "fca-mlr-application"],
        "handbook_names": ["SM&CR, as named on the 30 June 2026 overview", "PS26/13"],
        "page_says": (
            "The 30 June 2026 overview says PS26/13 applies key Handbook obligations "
            "including SM&CR. The Handbook text was not opened. The MLR registration "
            "page says registering under the MLRs does not of itself subject the firm "
            "to SM&CR. This row is a preparation item for the FSMA regime. It is not "
            "scored as a current MLR expectation. The pinned pages put regime "
            "commencement on 25 October 2027, and the landing page says expected."
        ),
        "signal_groups": [
            ["sm&cr", "smcr", "senior managers and certification", "statement of responsibilities"],
        ],
    },
    {
        "id": "R-GOV-04",
        "control_area": "governance_smcr",
        "title": "Suspicious activity reporting, including tipping off, is described",
        "doc_types": ["governance_smcr", "cdd_onboarding", "transaction_monitoring"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page expects a suspicious activity reporting policy "
            "for the whole business, staff obligations, tipping off, and when a "
            "defence against money laundering or terrorist financing report may "
            "need to be considered, with escalation to the MLRO or nominated officer "
            "and externally to the National Crime Agency."
        ),
        "signal_groups": [
            ["suspicious activity"],
            ["tipping off", "tipping-off", "daml", "national crime agency", "nca"],
        ],
    },
    {
        "id": "R-CD-01",
        "control_area": "consumer_duty",
        "title": "Consumer Duty text for the cryptoasset regime is present",
        "doc_types": ["consumer_duty"],
        "rule_stage": "final_not_yet_in_force",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": ["FG26/5", "PS26/13"],
        "page_says": (
            "The 30 June 2026 overview says the Consumer Duty is applied across "
            "regulated cryptoasset activities and names FG26/5 as non-handbook "
            "guidance. FG26/5 was not opened. This is a preparation item. A missing "
            "phrase is not a finding that the Duty has been breached."
        ),
        "signal_groups": [
            ["consumer duty"],
            ["fair value", "products and services", "consumer understanding", "consumer support", "price and value"],
        ],
    },
    {
        "id": "R-OR-01",
        "control_area": "operational_resilience",
        "title": "Operational resilience text names an important business service or an impact tolerance",
        "doc_types": ["operational_resilience"],
        "rule_stage": "final_not_yet_in_force",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": ["FG26/6"],
        "page_says": (
            "The 30 June 2026 overview names FG26/6 Cryptoasset Operational Resilience "
            "alongside PS26/13. FG26/6 was not opened. This is a preparation item, "
            "not a current MLR expectation and not a finding under SYSC."
        ),
        "signal_groups": [
            ["operational resilience"],
            ["important business service", "impact tolerance"],
        ],
    },
    {
        "id": "R-OR-02",
        "control_area": "operational_resilience",
        "title": "Business continuity is described",
        "doc_types": ["operational_resilience"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-mlr-application"],
        "handbook_names": [],
        "page_says": (
            "The registration page lists a description of the business continuity "
            "plan among the contents it expects in the business plan for an MLR "
            "registration application."
        ),
        "signal_groups": [["business continuity"]],
    },
    {
        "id": "R-FP-01",
        "control_area": "financial_promotions",
        "title": "Financial promotions policy says promotions are fair, clear and not misleading",
        "doc_types": ["financial_promotions"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-marketing", "fca-mlr-application"],
        "handbook_names": ["PS23/6, named and not opened", "FG23/3, named and not opened"],
        "page_says": (
            "The registration page says the firm must provide its financial promotions "
            "policy so that promotions are fair, clear and not misleading. The "
            "marketing page, last updated 6 February 2026, says the regime applies "
            "from 8 October 2023 and points to PS23/6. PS23/6 and FG23/3 were not opened."
        ),
        "signal_groups": [
            ["financial promotion"],
            ["fair, clear and not misleading", "fair clear and not misleading"],
        ],
    },
    {
        "id": "R-FP-02",
        "control_area": "financial_promotions",
        "title": "Financial promotions policy names a communication route from the marketing page",
        "doc_types": ["financial_promotions"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-marketing"],
        "handbook_names": [],
        "page_says": (
            "The marketing page lists four routes: communication by an FCA authorised "
            "person; approval by an authorised person; communication by an "
            "MLR-registered cryptoasset business; or an exemption in the Financial "
            "Promotion Order. As last updated on 6 February 2026 the page still says "
            "legislation on a regulatory gateway for approvers was before Parliament. "
            "This checker does not update that sentence. The s.21 approvers page "
            "named on the gateway was not opened."
        ),
        "signal_groups": [
            ["section 21", "s.21", "s21", "approver", "article 73za", "financial promotion order", "mlr-registered", "mlr registered"],
        ],
    },
    {
        "id": "R-FP-03",
        "control_area": "financial_promotions",
        "title": "Financial promotions policy mentions a risk warning or a cooling-off period",
        "doc_types": ["financial_promotions"],
        "rule_stage": "in_force_expectation",
        "source_ids": ["fca-marketing"],
        "handbook_names": [],
        "page_says": (
            "The marketing page says firms must use specific risk warnings and "
            "positive frictions such as a 24-hour cooling-off period, as well as "
            "the fair, clear and not misleading requirement."
        ),
        "signal_groups": [["risk warning", "cooling-off", "cooling off"]],
    },
    {
        "id": "R-SG-01",
        "control_area": "safeguarding_custody",
        "title": "Safeguarding text covers client cryptoasset records, reconciliation or private keys",
        "doc_types": ["safeguarding_custody"],
        "rule_stage": "final_not_yet_in_force",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": ["CASS 17", "PS26/11"],
        "page_says": (
            "The 30 June 2026 overview says PS26/11 proceeds with CASS 17 for client "
            "cryptoassets, including ownership rights, record-keeping, reconciliation "
            "and private key management. It also says CASS 17 is not being applied to "
            "relevant specified investment cryptoasset (RSIC) custody at this stage, "
            "and names CASS 6 for RSICs for the time being. The policy statement PDF "
            "was not opened. Preparation item only."
        ),
        "signal_groups": [["private key", "reconciliation", "client cryptoasset"]],
    },
    {
        "id": "R-SG-02",
        "control_area": "safeguarding_custody",
        "title": "Stablecoin issuance text covers backing assets",
        "doc_types": ["safeguarding_custody"],
        "rule_stage": "final_not_yet_in_force",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": ["CASS 16", "CRYPTO 2", "PS26/10"],
        "page_says": (
            "The overview says PS26/10 and CASS 16 cover safeguarding of stablecoin "
            "backing assets, including statutory trust arrangements. The PDF was not "
            "opened. This row is only considered when the pack says the firm issues "
            "qualifying stablecoins. A custodian that does not say that is not given "
            "a missing-phrase row for backing assets."
        ),
        "signal_groups": [["backing asset", "cass 16", "statutory trust"]],
        "applicability": {
            "any_of": [
                "we issue qualifying stablecoins",
                "stablecoin issuer",
                "issuing qualifying stablecoins",
            ],
            "search": "pack",
        },
    },
    {
        "id": "R-MARC-01",
        "control_area": "transaction_monitoring",
        "title": "Trading-platform pack mentions market-abuse controls",
        "doc_types": [],
        "search_scope": "pack",
        "rule_stage": "final_not_yet_in_force",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": ["CRYPTO 4", "PS26/9"],
        "page_says": (
            "The overview says MARC sits in CRYPTO 4 under PS26/9, and that the "
            "on-chain monitoring requirement for large UK qualifying cryptoasset "
            "trading platforms was narrowed. This row does not decide whether a "
            "firm is large. It is only considered when the pack says the firm "
            "operates a qualifying cryptoasset trading platform. The PDF was not opened."
        ),
        "signal_groups": [["market abuse", "marc"]],
        "applicability": {
            "any_of": [
                "qualifying cryptoasset trading platform",
                "we operate a trading platform",
                "qcatp",
            ],
            "search": "pack",
        },
    },
    {
        "id": "R-CON-01",
        "control_area": "prudential",
        "title": "GC26/4 COREPRU guidance consultation",
        "doc_types": [],
        "rule_stage": "consultation",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": ["GC26/4", "COREPRU"],
        "page_says": (
            "The 30 June 2026 overview says the FCA is consulting on non-handbook "
            "guidance for the overall risk assessment under COREPRU and names GC26/4. "
            "That is a guidance consultation. It is not scored as a rule."
        ),
        "mention_aliases": ["gc26/4", "corepru guidance consultation"],
    },
    {
        "id": "R-CON-02",
        "control_area": "prudential",
        "title": "GC26/5 CRYPTOPRU guidance consultation",
        "doc_types": [],
        "rule_stage": "consultation",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": ["GC26/5", "CRYPTOPRU"],
        "page_says": (
            "The overview names GC26/5 as a consultation on CRYPTOPRU guidance. "
            "It is not scored as a rule. PS26/12 is the prudential policy statement "
            "named on the same page. This row is only the guidance consultation."
        ),
        "mention_aliases": ["gc26/5", "cryptopru guidance consultation"],
    },
    {
        "id": "R-CON-03",
        "control_area": "financial_crime_guide",
        "title": "Financial Crime Guide update for cryptoasset firms",
        "doc_types": [],
        "rule_stage": "planned_consultation",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": ["Financial Crime Guide, update not verified as published"],
        "page_says": (
            "The 30 June 2026 overview says the FCA plans to consult on Financial "
            "Crime Guide updates, including AML and KYC for cryptoasset firms, later "
            "that year. This starter did not verify that a consultation paper has "
            "since been published. The row stays a planned consultation."
        ),
        "mention_aliases": ["financial crime guide"],
    },
    {
        "id": "R-CON-04",
        "control_area": "defi",
        "title": "Tailored DeFi guidance",
        "doc_types": [],
        "rule_stage": "planned_consultation",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": [],
        "page_says": (
            "The overview says the FCA will consult on tailored DeFi guidance, "
            "including indicators of decentralisation. A mention of DeFi in a policy "
            "does not make that guidance final. Not scored."
        ),
        "mention_aliases": ["decentralised finance", "defi"],
    },
    {
        "id": "R-CON-05",
        "control_area": "resolution",
        "title": "Resolution and distribution rules for a failed stablecoin issuer or custodian",
        "doc_types": [],
        "rule_stage": "planned_consultation",
        "source_ids": ["fca-regime-overview"],
        "handbook_names": [],
        "page_says": (
            "The overview says the FCA will consult later in the year of that page "
            "on managing cryptoasset firm failure, including distribution rules where "
            "a stablecoin issuer or a cryptoasset custodian has failed. Not scored. "
            "This starter did not verify that the consultation has opened."
        ),
        "mention_aliases": ["firm failure", "distribution rules", "resolution rules"],
    },
    {
        "id": "R-CON-06",
        "control_area": "perimeter",
        "title": "Further perimeter guidance after PS26/18",
        "doc_types": [],
        "rule_stage": "planned_consultation",
        "source_ids": ["fca-ps26-18"],
        "handbook_names": [],
        "page_says": (
            "PS26/18, 16 September 2026, says the FCA plans to consult on further "
            "changes to perimeter guidance in late 2026, following a Government "
            "statutory instrument, and aims to publish that guidance in early 2027. "
            "PS26/18 itself is final guidance. This row is only the further consultation. "
            "Not scored."
        ),
        "mention_aliases": ["further perimeter", "perimeter guidance in late 2026"],
    },
]


def requirement_by_id() -> dict[str, dict]:
    """Return requirements keyed by id."""
    return {item["id"]: item for item in REQUIREMENTS}
