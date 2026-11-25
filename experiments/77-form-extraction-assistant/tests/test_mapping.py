"""A sentence supports a fee only when it states that fee."""

from datetime import date

from src.fields import extract_fields
from src.paraphrases import FEE_NEGATIVES, FEE_POSITIVES

ON = date(2026, 10, 15)
FEE = {
    "field_id": "fee_amount",
    "labels": ["fee", "fee amount"],
    "kind": "amount",
    "material": True,
    "material_class": "amount",
    "required": True,
    "minimum": "0",
    "maximum": "10000",
}


def _value(text: str):
    rows = extract_fields(text, [FEE], on=ON, threshold=5)["fields"]
    return rows[0]["value"]


def test_reworded_fee_lines_are_recalled_and_negatives_are_not():
    assert len(FEE_POSITIVES) >= 20
    assert len(FEE_NEGATIVES) >= 20
    true_positives = sum(1 for text in FEE_POSITIVES if _value(text) == "10.00")
    false_positives = sum(1 for text in FEE_NEGATIVES if _value(text) == "10.00")
    recall = true_positives / len(FEE_POSITIVES)
    precision = true_positives / (true_positives + false_positives)
    assert recall == 1.0
    assert precision == 1.0
    assert false_positives == 0
    denied = _value("fee_amount: it is not true that the figure is £10.00")
    assert denied is None
    illegible = extract_fields("fee_amount: [illegible]", [FEE], on=ON, threshold=5)["fields"][0]
    assert illegible["value"] is None
    assert illegible["coerced"] is False
    assert "0" != illegible["value"]
