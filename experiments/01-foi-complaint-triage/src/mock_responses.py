"""Mock responses for offline/demo mode.

These provide realistic triage outputs without requiring Azure AI credentials.
Used for demonstrations, testing, and CI/CD pipelines.
"""

from datetime import datetime
import hashlib
import re
from typing import Any


def generate_triage_id() -> str:
    """Generate a mock triage ID."""
    date_str = datetime.now().strftime("%Y%m%d")
    return f"TRG-{date_str}-MOCK01"


def detect_classification(text: str) -> dict[str, Any]:
    """Simple rule-based classification for mock mode."""
    text_lower = text.lower()
    
    indicators = []
    primary_type = "other"
    confidence = "medium"
    
    foi_signals = [
        "freedom of information", "foi", "i request information",
        "copies of", "disclose", "recorded information", "i want to know",
        "i also want to know", "how many", "what is your"
    ]
    eir_signals = [
        "environmental information", "pollution levels", "emissions", 
        "contamination", "planning application", "air quality", 
        "water quality", "under eir", "environmental information regulations",
        "ecological survey", "wildlife habitat"
    ]
    sar_signals = [
        "my personal data", "information about me", "my records",
        "subject access", "data protection", "gdpr", "my medical records",
        "her complete medical records", "his complete medical records"
    ]
    complaint_signals = [
        "to complain", "my complaint", "i complain", "unacceptable", "failed to", "disgusted",
        "appalled", "unhappy", "dissatisfied", "disgraceful", "terrible",
        "ridiculous", "please help me", "waiting over", "waiting for",
        "no food", "medication", "this is wrong", "bins haven't", 
        "not been collected", "i am scared", "please sort this out"
    ]
    
    foi_count = sum(1 for s in foi_signals if s in text_lower)
    eir_count = sum(1 for s in eir_signals if s in text_lower)
    sar_count = sum(1 for s in sar_signals if s in text_lower)
    complaint_count = sum(1 for s in complaint_signals if s in text_lower)
    
    max_count = max(foi_count, eir_count, sar_count, complaint_count)
    
    if max_count == 0:
        primary_type = "other"
        confidence = "low"
    elif eir_count > 0 and eir_count >= foi_count:
        primary_type = "eir_request"
        confidence = "high" if eir_count >= 2 else "medium"
        indicators = [s for s in eir_signals if s in text_lower][:3]
    elif foi_count == max_count:
        primary_type = "foi_request"
        confidence = "high" if foi_count >= 2 else "medium"
        indicators = [s for s in foi_signals if s in text_lower][:3]
    elif sar_count == max_count:
        primary_type = "subject_access_request"
        confidence = "high" if sar_count >= 2 else "medium"
        indicators = [s for s in sar_signals if s in text_lower][:3]
    elif complaint_count == max_count:
        primary_type = "complaint"
        confidence = "high" if complaint_count >= 2 else "medium"
        indicators = [s for s in complaint_signals if s in text_lower][:3]
    
    if complaint_count >= 2 and (foi_count >= 2 or eir_count >= 2 or sar_count >= 1):
        primary_type = "mixed"
        confidence = "high"
    elif complaint_count > 0 and (foi_count >= 2 or eir_count >= 2 or sar_count >= 1):
        primary_type = "mixed"
        confidence = "medium"
    
    return {
        "primary_type": primary_type,
        "confidence": confidence,
        "rationale": f"Mock classification based on keyword analysis. Detected signals for {primary_type}.",
        "indicators": indicators if indicators else None
    }


def detect_urgency_flags(text: str) -> dict[str, Any]:
    """Detect urgency and safeguarding signals for mock mode."""
    text_lower = text.lower()
    
    critical_signals = [
        "risk to life", "danger", "emergency", "safeguarding concern",
        "child protection", "suicide", "self-harm", "harm myself",
        "i am scared", "no food", "medication running out",
        "cannot leave my bed", "screaming and crying", "children look thin",
        "daddy gets angry", "worried about their safety", "report something about",
        "help these children", "scared to go home", "vulnerable adult",
        "carer has not come"
    ]
    elevated_signals = [
        "legal action", "considering legal", "solicitor", "court proceedings", 
        "journalist", "newspaper", "deadline", "copied my mp", 
        "contacting the press", "mental distress", "can't pay my rent", 
        "can't feed my kids", "stopped without warning", "put her life at risk", 
        "premature discharge", "very worried about their"
    ]
    
    has_critical = any(s in text_lower for s in critical_signals)
    has_elevated = any(s in text_lower for s in elevated_signals)
    
    if has_critical:
        return {
            "urgency_level": "critical",
            "urgency_reasons": [s for s in critical_signals if s in text_lower],
            "safeguarding_concern": True,
            "safeguarding_details": "Potential safeguarding or safety concern detected - requires immediate human review",
            "requires_immediate_human_review": True,
            "escalation_reason": "Safety/safeguarding language detected",
            "vulnerability_indicators": [s for s in critical_signals if s in text_lower],
            "legal_action_mentioned": "legal" in text_lower or "court" in text_lower,
            "media_interest_indicated": any(s in text_lower for s in ["media", "journalist", "newspaper", "press"])
        }
    elif has_elevated:
        return {
            "urgency_level": "elevated",
            "urgency_reasons": [s for s in elevated_signals if s in text_lower],
            "safeguarding_concern": False,
            "requires_immediate_human_review": False,
            "legal_action_mentioned": "legal" in text_lower or "court" in text_lower or "solicitor" in text_lower,
            "media_interest_indicated": any(s in text_lower for s in ["media", "journalist", "newspaper", "press"])
        }
    else:
        return {
            "urgency_level": "standard",
            "safeguarding_concern": False,
            "requires_immediate_human_review": False,
            "legal_action_mentioned": False,
            "media_interest_indicated": False
        }


def assess_cost_limit(text: str, asks: list) -> dict[str, Any]:
    """Assess likelihood of exceeding cost limit for mock mode."""
    text_lower = text.lower()
    
    broad_signals = [
        "all documents", "all emails", "all correspondence", "everything",
        "any and all", "complete records", "all communications",
        "last ten years", "last 10 years", "since 2010", "all time"
    ]
    
    scope_concerns = []
    for signal in broad_signals:
        if signal in text_lower:
            scope_concerns.append(f"Request includes broad scope: '{signal}'")
    
    ask_count = len(asks)
    if ask_count > 5:
        scope_concerns.append(f"Request contains {ask_count} distinct asks")
    
    word_count = len(text.split())
    if word_count > 500:
        scope_concerns.append(f"Request is lengthy ({word_count} words)")
    
    likely_exceeds = len(scope_concerns) >= 2
    
    result = {
        "likely_exceeds_limit": likely_exceeds,
        "assessment_rationale": f"Mock assessment based on {len(scope_concerns)} scope concerns detected." if scope_concerns else "Request appears reasonably scoped.",
        "scope_concerns": scope_concerns if scope_concerns else None,
        "clarification_needed": likely_exceeds
    }
    
    if likely_exceeds:
        result["refinement_suggestions"] = [
            "Consider specifying a narrower date range",
            "Focus on specific types of documents rather than 'all'",
            "Identify the specific decision or event of interest"
        ]
        result["draft_clarification_letter"] = generate_clarification_letter(scope_concerns)
    
    return result


def generate_clarification_letter(concerns: list[str]) -> str:
    """Generate a polite clarification letter following ICO guidance."""
    return """Dear Requester,

Thank you for your request for information.

We are writing to ask if you could help us by providing some additional clarity, which will help us respond to your request more effectively.

Your request covers a broad scope, and we want to ensure we provide you with the most relevant information. To help us do this, it would be helpful if you could:

- Specify a particular time period you are most interested in
- Clarify which specific documents or types of records would be most useful
- Let us know if there is a particular decision, event, or issue you are researching

This will help us locate the information you need more efficiently and ensure our response is as helpful as possible.

If you would find it easier to discuss this over the phone, please let us know and we can arrange a convenient time to call.

We look forward to hearing from you.

Kind regards,
[Information Governance Team]"""


def detect_bulk_signals(text: str) -> dict[str, Any]:
    """Detect bulk/template submission signals for mock mode."""
    text_lower = text.lower()
    
    template_signals = [
        "in accordance with section",
        "pursuant to section", "section 1(1)", "section 10 of the act",
        "cite the specific exemption", "public interest favours"
    ]
    
    detected_signals = [s for s in template_signals if s in text_lower]
    detected = len(detected_signals) >= 2
    
    return {
        "detected": detected,
        "signals": detected_signals if detected else None,
        "confidence": "medium" if detected else None,
        "note": "This is informational only. Bulk/templated requests remain valid and must be processed according to FOI/EIR requirements."
    }


def extract_asks(text: str) -> list[dict[str, Any]]:
    """Extract asks/questions from text for mock mode."""
    sentences = re.split(r'[.!?]', text)
    
    question_words = ["what", "when", "where", "who", "why", "how", "which", "please provide", "i request", "i want", "i would like"]
    
    asks = []
    ask_id = 1
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:
            continue
            
        sentence_lower = sentence.lower()
        is_ask = any(qw in sentence_lower for qw in question_words) or sentence.endswith("?")
        
        if is_ask:
            specificity = "specific"
            if any(w in sentence_lower for w in ["all", "any", "everything", "complete"]):
                specificity = "broad"
            elif any(w in sentence_lower for w in ["might", "maybe", "possibly", "anything"]):
                specificity = "unclear"
            
            scope = "moderate"
            if "all" in sentence_lower:
                scope = "wide" if "year" in sentence_lower or "since" in sentence_lower else "moderate"
            if any(w in sentence_lower for w in ["every", "complete", "entire"]):
                scope = "very_wide"
            
            asks.append({
                "ask_id": ask_id,
                "summary": sentence[:200] if len(sentence) > 200 else sentence,
                "source_quote": sentence,
                "specificity": specificity,
                "date_range_specified": any(w in sentence_lower for w in ["year", "month", "date", "since", "between", "from", "to"]),
                "estimated_scope": scope
            })
            ask_id += 1
            
            if ask_id > 10:
                break
    
    if not asks:
        asks.append({
            "ask_id": 1,
            "summary": "General information request",
            "source_quote": text[:200] if len(text) > 200 else text,
            "specificity": "unclear",
            "date_range_specified": False,
            "estimated_scope": "moderate"
        })
    
    return asks


def suggest_routing(classification: dict, text: str) -> dict[str, Any]:
    """Suggest routing based on classification and content for mock mode."""
    text_lower = text.lower()
    
    routing_keywords = {
        "social_services": ["social services", "adult social care", "children services", 
                          "carer has not come", "neighbour's children", "child protection", 
                          "safeguarding", "children look", "report something about"],
        "benefits": ["benefits", "universal credit", "housing benefit", "dwp", "sanctioned", 
                    "sanction", "my claim", "credit was stopped"],
        "housing": ["housing department", "tenant", "landlord", "homelessness", "council house", 
                   "damp", "repairs to our council", "housing service"],
        "planning": ["planning", "development", "building", "construction", "planning application", 
                    "green belt", "planning department"],
        "finance": ["council tax", "business rates", "payment", "invoice", "budget", "expenditure",
                   "consultants", "spending"],
        "highways": ["road repairs", "pothole", "traffic", "parking", "highway", "roads in my area",
                    "potholes"],
        "waste_services": ["waste", "bin collection", "bins", "rubbish", "recycling", "refuse", 
                          "haven't been collected", "bins haven't"],
        "environmental_health": ["noise", "food safety", "pest", "air quality monitoring"],
        "education": ["school", "education", "academy", "pupil", "student"],
        "health": ["nhs", "hospital", "gp surgery", "medical records", "patient", "admitted", 
                  "a&e", "general hospital"]
    }
    
    detected_dept = "Information Governance"
    for dept, keywords in routing_keywords.items():
        if any(kw in text_lower for kw in keywords):
            detected_dept = dept.replace("_", " ").title()
            break
    
    primary_type = classification.get("primary_type", "other")
    
    if primary_type == "subject_access_request":
        team = "Data Protection Team"
    elif primary_type == "complaint":
        team = "Complaints Team"
    else:
        team = "FOI/EIR Team"
    
    return {
        "suggested_department": detected_dept,
        "suggested_team": team,
        "alternative_routes": [
            {
                "department": "Information Governance",
                "team": "Central FOI Team",
                "reason": "If primary department unable to respond"
            }
        ],
        "external_referral_needed": "nhs" in text_lower or "dwp" in text_lower or "police" in text_lower or "hospital" in text_lower,
        "external_referral_suggestion": "NHS Trust" if ("nhs" in text_lower or "hospital" in text_lower) else ("DWP" if "dwp" in text_lower else None)
    }


def generate_mock_response(text: str) -> dict[str, Any]:
    """Generate a complete mock triage response."""
    classification = detect_classification(text)
    asks = extract_asks(text)
    flags = detect_urgency_flags(text)
    cost_assessment = assess_cost_limit(text, asks)
    bulk_signals = detect_bulk_signals(text)
    routing = suggest_routing(classification, text)
    
    key_topics = []
    topic_keywords = ["housing", "planning", "health", "education", "benefits", "environment", "transport"]
    text_lower = text.lower()
    for topic in topic_keywords:
        if topic in text_lower:
            key_topics.append(topic.title())
    
    return {
        "triage_id": generate_triage_id(),
        "timestamp": datetime.now().isoformat(),
        "extracted_asks": asks,
        "classification": classification,
        "routing": routing,
        "flags": flags,
        "cost_limit_assessment": cost_assessment,
        "bulk_submission_signals": bulk_signals,
        "summary": {
            "one_line": f"{classification['primary_type'].replace('_', ' ').title()} with {len(asks)} distinct ask(s)",
            "key_topics": key_topics if key_topics else ["General"],
            "recommended_action": "Immediate human review required" if flags.get("requires_immediate_human_review") else "Standard processing"
        },
        "metadata": {
            "model_version": "mock-v0.1",
            "processing_mode": "mock",
            "input_character_count": len(text),
            "input_word_count": len(text.split())
        }
    }
