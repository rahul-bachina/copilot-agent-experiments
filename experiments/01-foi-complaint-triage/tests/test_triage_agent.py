"""Unit tests for the FOI Triage Agent."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import TriageOutput, Classification, Flags, ExtractedAsk
from mock_responses import (
    generate_mock_response,
    detect_classification,
    detect_urgency_flags,
    assess_cost_limit,
    extract_asks,
    detect_bulk_signals,
)
from triage_agent import triage, validate_output


class TestModels:
    """Test Pydantic models."""

    def test_extracted_ask_valid(self):
        ask = ExtractedAsk(
            ask_id=1,
            summary="Test ask",
            source_quote="This is a test quote from the request",
            specificity="specific"
        )
        assert ask.ask_id == 1
        assert ask.specificity == "specific"

    def test_classification_valid(self):
        classification = Classification(
            primary_type="foi_request",
            confidence="high",
            rationale="Test rationale for classification"
        )
        assert classification.primary_type == "foi_request"

    def test_flags_valid(self):
        flags = Flags(
            urgency_level="standard",
            safeguarding_concern=False,
            requires_immediate_human_review=False
        )
        assert flags.urgency_level == "standard"
        assert flags.safeguarding_concern is False


class TestMockClassification:
    """Test mock classification logic."""

    def test_foi_request_detection(self):
        text = "Under the Freedom of Information Act 2000, I request information about council spending."
        result = detect_classification(text)
        assert result["primary_type"] == "foi_request"
        assert result["confidence"] in ["high", "medium"]

    def test_eir_request_detection(self):
        text = "Please provide environmental information about pollution levels and air quality monitoring."
        result = detect_classification(text)
        assert result["primary_type"] == "eir_request"

    def test_sar_detection(self):
        text = "Under GDPR, I request a copy of all my personal data that you hold about me."
        result = detect_classification(text)
        assert result["primary_type"] == "subject_access_request"

    def test_complaint_detection(self):
        text = "I am writing to complain about the appalling service. This is unacceptable and I am disgusted."
        result = detect_classification(text)
        assert result["primary_type"] == "complaint"

    def test_mixed_detection(self):
        text = "I am unhappy with your service and want to complain. I also request information about how many complaints you received."
        result = detect_classification(text)
        assert result["primary_type"] in ["mixed", "complaint", "foi_request"]


class TestMockUrgencyFlags:
    """Test mock urgency detection."""

    def test_standard_urgency(self):
        text = "Please provide information about council meetings."
        result = detect_urgency_flags(text)
        assert result["urgency_level"] == "standard"
        assert result["safeguarding_concern"] is False

    def test_critical_safeguarding(self):
        text = "I am very worried about their safety. The children look thin and daddy gets angry."
        result = detect_urgency_flags(text)
        assert result["urgency_level"] == "critical"
        assert result["safeguarding_concern"] is True
        assert result["requires_immediate_human_review"] is True

    def test_elevated_legal(self):
        text = "My solicitor has advised me to request this information for court proceedings."
        result = detect_urgency_flags(text)
        assert result["urgency_level"] == "elevated"
        assert result["legal_action_mentioned"] is True

    def test_media_interest(self):
        text = "I am a journalist investigating this matter for a newspaper article."
        result = detect_urgency_flags(text)
        assert result["media_interest_indicated"] is True


class TestMockCostAssessment:
    """Test mock cost limit assessment."""

    def test_narrow_request(self):
        text = "Please provide the minutes from the council meeting on 15th March 2026."
        asks = extract_asks(text)
        result = assess_cost_limit(text, asks)
        assert result["likely_exceeds_limit"] is False

    def test_broad_request_exceeds(self):
        text = "Please provide all documents and all emails about everything since 2010. I want complete records of every decision."
        asks = extract_asks(text)
        result = assess_cost_limit(text, asks)
        assert result["likely_exceeds_limit"] is True
        assert result["clarification_needed"] is True
        assert result.get("draft_clarification_letter") is not None


class TestMockBulkSignals:
    """Test mock bulk submission detection."""

    def test_no_bulk_signals(self):
        text = "Hi, can you tell me how many potholes were reported last month? Thanks."
        result = detect_bulk_signals(text)
        assert result["detected"] is False

    def test_bulk_signals_detected(self):
        text = """In accordance with Section 1(1) of the Act, I would like to request information.
        Pursuant to Section 10 of the Act, I expect a response within 20 working days.
        Please cite the specific exemption if any information is withheld."""
        result = detect_bulk_signals(text)
        assert result["detected"] is True
        assert result["note"] is not None
        assert "informational only" in result["note"].lower()


class TestMockAskExtraction:
    """Test mock ask extraction."""

    def test_extract_single_ask(self):
        text = "Please provide the budget report for 2026."
        asks = extract_asks(text)
        assert len(asks) >= 1
        assert asks[0]["ask_id"] == 1

    def test_extract_multiple_asks(self):
        text = """Please provide:
        1. How many staff were employed in 2025?
        2. What was the total salary budget?
        3. How many contractors were used?"""
        asks = extract_asks(text)
        assert len(asks) >= 2


class TestFullMockTriage:
    """Test complete mock triage pipeline."""

    def test_full_triage_returns_valid_output(self):
        text = "Under FOI, please provide information about council spending on IT services in 2025."
        result = triage(text, mock=True)
        
        assert "triage_id" in result
        assert "timestamp" in result
        assert "extracted_asks" in result
        assert "classification" in result
        assert "routing" in result
        assert "flags" in result
        assert "cost_limit_assessment" in result
        assert "bulk_submission_signals" in result

    def test_full_triage_validates(self):
        text = "I want to complain about your housing service. It's been terrible."
        result = triage(text, mock=True)
        
        is_valid, errors = validate_output(result)
        assert is_valid, f"Validation errors: {errors}"

    def test_safeguarding_case(self):
        text = "I am concerned about a vulnerable adult who appears to be at risk from their carer."
        result = triage(text, mock=True)
        
        assert result["flags"]["urgency_level"] in ["critical", "urgent"]
        assert result["flags"]["safeguarding_concern"] is True
        assert result["flags"]["requires_immediate_human_review"] is True

    def test_metadata_present(self):
        text = "Simple test request for information."
        result = triage(text, mock=True)
        
        assert result.get("metadata") is not None
        assert result["metadata"]["processing_mode"] == "mock"
        assert result["metadata"]["input_character_count"] == len(text)


class TestSchemaValidation:
    """Test schema validation utilities."""

    def test_validate_good_output(self):
        text = "Test FOI request"
        result = triage(text, mock=True)
        is_valid, errors = validate_output(result)
        assert is_valid

    def test_triage_id_format(self):
        text = "Test request"
        result = triage(text, mock=True)
        import re
        pattern = r"^TRG-[0-9]{8}-[A-Z0-9]{6}$"
        assert re.match(pattern, result["triage_id"])


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_after_whitespace(self):
        text = "   \n\n   "
        result = triage(text, mock=True)
        assert len(result["extracted_asks"]) >= 1

    def test_very_short_input(self):
        text = "Hi"
        result = triage(text, mock=True)
        assert len(result["extracted_asks"]) >= 1

    def test_very_long_input(self):
        text = "Please provide information. " * 500
        result = triage(text, mock=True)
        assert result is not None
        assert len(result["extracted_asks"]) <= 10

    def test_special_characters(self):
        text = "Please provide info about £1,000 contracts & 50% discounts <test> \"quotes\""
        result = triage(text, mock=True)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
