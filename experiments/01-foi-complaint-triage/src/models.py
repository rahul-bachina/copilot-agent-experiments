"""Pydantic models for FOI Triage output schema."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Specificity(str, Enum):
    SPECIFIC = "specific"
    BROAD = "broad"
    UNCLEAR = "unclear"


class EstimatedScope(str, Enum):
    NARROW = "narrow"
    MODERATE = "moderate"
    WIDE = "wide"
    VERY_WIDE = "very_wide"


class ClassificationType(str, Enum):
    FOI_REQUEST = "foi_request"
    EIR_REQUEST = "eir_request"
    SUBJECT_ACCESS_REQUEST = "subject_access_request"
    COMPLAINT = "complaint"
    MIXED = "mixed"
    OTHER = "other"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class UrgencyLevel(str, Enum):
    STANDARD = "standard"
    ELEVATED = "elevated"
    URGENT = "urgent"
    CRITICAL = "critical"


class ProcessingMode(str, Enum):
    LIVE = "live"
    MOCK = "mock"


class ExtractedAsk(BaseModel):
    """A distinct question or request extracted from the submission."""
    ask_id: int = Field(..., ge=1, description="Sequential identifier for this ask")
    summary: str = Field(..., max_length=200, description="Brief summary of what is being asked")
    source_quote: str = Field(..., description="Direct quote from the original text")
    specificity: Specificity = Field(..., description="How specific and answerable the ask is")
    date_range_specified: Optional[bool] = Field(None, description="Whether a date range is specified")
    estimated_scope: Optional[EstimatedScope] = Field(None, description="Estimated scope of records")


class Classification(BaseModel):
    """Classification of the submission type."""
    primary_type: ClassificationType = Field(..., description="Primary classification")
    secondary_types: Optional[list[ClassificationType]] = Field(None, description="Additional classifications")
    confidence: Confidence = Field(..., description="Confidence level")
    rationale: str = Field(..., max_length=500, description="Explanation of classification")
    indicators: Optional[list[str]] = Field(None, description="Key phrases that led to classification")


class AlternativeRoute(BaseModel):
    """An alternative routing option."""
    department: str
    team: str
    reason: str


class Routing(BaseModel):
    """Suggested routing for the submission."""
    suggested_department: str = Field(..., description="Suggested department category")
    suggested_team: str = Field(..., description="Suggested team or function")
    alternative_routes: Optional[list[AlternativeRoute]] = Field(None, description="Alternative options")
    external_referral_needed: Optional[bool] = Field(None, description="Whether external referral needed")
    external_referral_suggestion: Optional[str] = Field(None, description="Suggested external body")


class Flags(BaseModel):
    """Priority and safeguarding flags."""
    urgency_level: UrgencyLevel = Field(..., description="Urgency level for processing")
    urgency_reasons: Optional[list[str]] = Field(None, description="Reasons for elevated urgency")
    safeguarding_concern: bool = Field(..., description="Whether safeguarding concerns exist")
    safeguarding_details: Optional[str] = Field(None, description="Details of safeguarding concern")
    requires_immediate_human_review: bool = Field(..., description="Whether immediate escalation needed")
    escalation_reason: Optional[str] = Field(None, description="Reason for immediate escalation")
    vulnerability_indicators: Optional[list[str]] = Field(None, description="Indicators of vulnerability")
    legal_action_mentioned: Optional[bool] = Field(None, description="Whether legal action mentioned")
    media_interest_indicated: Optional[bool] = Field(None, description="Whether media interest indicated")


class CostLimitAssessment(BaseModel):
    """Assessment of whether the request may exceed FOI cost limits."""
    likely_exceeds_limit: bool = Field(..., description="Whether likely to exceed cost limit")
    assessment_rationale: str = Field(..., description="Explanation of cost assessment")
    scope_concerns: Optional[list[str]] = Field(None, description="Concerns about request breadth")
    refinement_suggestions: Optional[list[str]] = Field(None, description="Suggestions to narrow request")
    clarification_needed: Optional[bool] = Field(None, description="Whether clarification should be requested")
    draft_clarification_letter: Optional[str] = Field(None, description="Draft clarification letter if needed")


class BulkSubmissionSignals(BaseModel):
    """Signals of bulk/template submission (informational only)."""
    detected: bool = Field(..., description="Whether bulk/template signals detected")
    signals: Optional[list[str]] = Field(None, description="Specific signals detected")
    confidence: Optional[Confidence] = Field(None, description="Confidence in bulk detection")
    note: str = Field(
        default="This is informational only. Bulk/templated requests remain valid and must be processed according to FOI/EIR requirements.",
        description="Reminder that bulk signals do not affect validity"
    )


class Summary(BaseModel):
    """Human-readable summary for staff."""
    one_line: str = Field(..., max_length=150, description="One-line summary")
    key_topics: Optional[list[str]] = Field(None, description="Key topics or themes")
    recommended_action: Optional[str] = Field(None, description="Recommended next action")


class Metadata(BaseModel):
    """Processing metadata."""
    model_version: Optional[str] = Field(None, description="Version of triage model")
    processing_mode: ProcessingMode = Field(..., description="Live or mock mode")
    input_character_count: Optional[int] = Field(None, description="Character count of input")
    input_word_count: Optional[int] = Field(None, description="Word count of input")


class TriageOutput(BaseModel):
    """Complete triage output for an FOI/complaint submission."""
    triage_id: str = Field(..., pattern=r"^TRG-[0-9]{8}-[A-Z0-9]{6}$", description="Unique triage ID")
    timestamp: datetime = Field(..., description="When triage was performed")
    extracted_asks: list[ExtractedAsk] = Field(..., min_length=1, description="Extracted questions/requests")
    classification: Classification = Field(..., description="Submission classification")
    routing: Routing = Field(..., description="Suggested routing")
    flags: Flags = Field(..., description="Priority and safeguarding flags")
    cost_limit_assessment: CostLimitAssessment = Field(..., description="Cost limit assessment")
    bulk_submission_signals: BulkSubmissionSignals = Field(..., description="Bulk submission signals")
    summary: Optional[Summary] = Field(None, description="Human-readable summary")
    metadata: Optional[Metadata] = Field(None, description="Processing metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "triage_id": "TRG-20261021-ABC123",
                "timestamp": "2026-10-21T10:30:00Z",
                "extracted_asks": [
                    {
                        "ask_id": 1,
                        "summary": "All emails about waste collection changes",
                        "source_quote": "I want to see all emails...",
                        "specificity": "broad",
                        "estimated_scope": "wide"
                    }
                ],
                "classification": {
                    "primary_type": "foi_request",
                    "confidence": "high",
                    "rationale": "Request for recorded information held by public authority"
                }
            }
        }
