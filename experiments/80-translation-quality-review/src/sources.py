"""Pages opened for this starter. The assistant does not download them again.

Opened on 26 November 2026. Quotes are the words copied below.
This is context for a bilingual review of public information.
It is not legal advice, and it is not a finding that a duty was met
or that a standard applies to any body.
"""

from __future__ import annotations

OPENED_ON = "2026-11-26"

MEASURE_1_1 = "The Welsh language has official status in Wales."
MEASURE_1_4 = "This Measure does not affect the status of the English language in Wales."
STANDARDS_1_1 = "The title of these Regulations is the Welsh Language Standards (No. 1) Regulations 2015."
STANDARDS_1_3 = "These Regulations apply in relation to Wales."
ACCESS_1_1 = (
    "These Regulations may be cited as the Public Sector Bodies "
    "(Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018."
)
ACCESS_1_2 = "These Regulations come into force on 23rd September 2018."


def uk_context() -> dict:
    return {
        "opened_on": OPENED_ON,
        "legal_advice": False,
        "duty_decided": False,
        "quotes": [
            {
                "source": "Welsh Language (Wales) Measure 2011",
                "section": "section 1(1)",
                "url": "https://www.legislation.gov.uk/mwa/2011/1/section/1",
                "text": MEASURE_1_1,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "Section 1(2), section 1(3), and section 1(4) were on the same page. "
                    "Section 1(3)(e) names standards of conduct for delivering services, "
                    "making policy, and exercising functions. It is not quoted in full. "
                    "This starter does not decide that a standard applies to a body."
                ),
            },
            {
                "source": "Welsh Language (Wales) Measure 2011",
                "section": "section 1(4)",
                "url": "https://www.legislation.gov.uk/mwa/2011/1/section/1",
                "text": MEASURE_1_4,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "The rest of section 1 was on the page and is not quoted.",
            },
            {
                "source": "The Welsh Language Standards (No. 1) Regulations 2015",
                "section": "regulation 1(1)",
                "url": "https://www.legislation.gov.uk/wsi/2015/996/regulation/1",
                "text": STANDARDS_1_1,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "Regulation 1(2), regulation 1(4), and regulation 1(5) were on the page "
                    "and are not quoted. The service standards in the schedule were not opened."
                ),
            },
            {
                "source": "The Welsh Language Standards (No. 1) Regulations 2015",
                "section": "regulation 1(3)",
                "url": "https://www.legislation.gov.uk/wsi/2015/996/regulation/1",
                "text": STANDARDS_1_3,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "This is application. It is not a finding that a council must translate a particular page.",
            },
            {
                "source": "The Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018",
                "section": "regulation 1(1)",
                "url": "https://www.legislation.gov.uk/uksi/2018/952/regulation/1",
                "text": ACCESS_1_1,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": (
                    "S.I. 2018/852 was opened the same day. That page says those regulations "
                    "are revoked and the citation text is not on the page. The operative "
                    "wording of the revoked instrument is unverified. Regulation 1(2) of "
                    "S.I. 2018/952 was on the page that was quoted."
                ),
            },
            {
                "source": "The Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018",
                "section": "regulation 1(2)",
                "url": "https://www.legislation.gov.uk/uksi/2018/952/regulation/1",
                "text": ACCESS_1_2,
                "verified_on": OPENED_ON,
                "unverified": False,
                "note": "The accessibility requirements in later regulations were not opened. No duty is decided here.",
            },
        ],
        "not_opened": [
            "UK GDPR Article 5, Article 6, Article 9, and Article 22A were not opened on 26 November 2026.",
            "The schedule of Welsh Language Standards (No. 1) Regulations 2015 was not opened.",
            "Later Welsh Language Standards regulations were not opened.",
            "The accessibility requirements after regulation 1 of S.I. 2018/952 were not opened.",
        ],
    }
