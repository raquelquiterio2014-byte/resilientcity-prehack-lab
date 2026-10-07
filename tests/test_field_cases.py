from datetime import datetime, timezone

from resilientcity.field_cases import (
    FieldCase, FieldEvidenceItem, HistoricalOutcome
)


def dt(hour: int):
    return datetime(2026, 1, 1, hour, tzinfo=timezone.utc)


def test_later_evidence_is_excluded_from_llm_payload():
    case = FieldCase(
        case_id="FIELD-001",
        title="Historical flood case",
        location="Test City",
        evidence_cutoff=dt(10),
        evidence=[
            FieldEvidenceItem(
                evidence_id="E1", claim="Heavy rain reported",
                source_type="official_bulletin", observed_at=dt(9)
            ),
            FieldEvidenceItem(
                evidence_id="E2", claim="Road later confirmed closed",
                source_type="road_record", observed_at=dt(11)
            ),
        ],
        later_outcome=HistoricalOutcome(summary="Flooding later confirmed"),
    )
    payload = case.llm_payload()
    assert [item["evidence_id"] for item in payload["evidence"]] == ["E1"]
    assert "later_outcome" not in payload


def test_partner_outcome_is_evaluator_only():
    case = FieldCase(
        case_id="FIELD-002",
        title="Messy evidence case",
        location="Test City",
        evidence_cutoff=dt(10),
        later_outcome=HistoricalOutcome(
            summary="Documented later outcome",
            independent_label="HUMAN_REVIEW_REQUIRED",
        ),
    )
    assert case.later_outcome.independent_label == "HUMAN_REVIEW_REQUIRED"
    assert "later_outcome" not in case.llm_payload()
