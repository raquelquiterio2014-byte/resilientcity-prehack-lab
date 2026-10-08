from datetime import datetime, timedelta
import pytest
from resilientcity.field_cases import FieldCase, FieldEvidenceItem, HistoricalOutcome
from resilientcity.shadow_mode import HumanBaseline, cutoff_snapshot, compare_case, aggregate

T=datetime(2026, 9, 1, 12)
def case():
    return FieldCase(case_id="V6-TEST",title="Urban road flood incident",location="Test District",
        evidence_cutoff=T,
        evidence=[
            FieldEvidenceItem(evidence_id="e1",claim="Rain 45 mm",source_type="weather",observed_at=T-timedelta(minutes=5),structured_data={"rainfall_mm":45}),
            FieldEvidenceItem(evidence_id="e2",claim="Road flooded",source_type="roads",observed_at=T+timedelta(minutes=5),structured_data={"road_status":"flooded"}),
            FieldEvidenceItem(evidence_id="e3",claim="Undated report",source_type="social",structured_data={"road_status":"closed"}),
        ],
        later_outcome=HistoricalOutcome(summary="Road flooding confirmed later"))
def review(**kwargs):
    values=dict(case_id="V6-TEST",reviewer_id="human-1",evidence_cutoff=T,
        priority="INSUFFICIENT_EVIDENCE",escalate=True,evidence_ids=["e1"],
        next_action="Verify road status",rationale="Road evidence not available yet",
        review_time_seconds=120,outcome_blinded=True)
    values.update(kwargs)
    return HumanBaseline(**values)
def test_snapshot_blocks_future_and_undated():
    snap=cutoff_snapshot(case())
    assert [e["evidence_id"] for e in snap["evidence"]]==["e1"]
    assert "later_outcome" not in str(snap)
def test_blinded_comparison_keeps_outcome_outside_agents():
    r=compare_case(case(),review())
    assert r.case_id=="V6-TEST"
    assert r.evidence_ids_available==["e1"]
    assert r.evaluation_status=="OUTCOME_DOCUMENTED"
    assert r.later_outcome_summary=="Road flooding confirmed later"
    assert aggregate([r])["cases"]==1
def test_reject_future_evidence_citation():
    with pytest.raises(ValueError,match="unavailable"):
        compare_case(case(),review(evidence_ids=["e2"]))
def test_reject_unblinded_review():
    with pytest.raises(ValueError,match="blinded"):
        compare_case(case(),review(outcome_blinded=False))
def test_reject_mismatched_cutoff():
    with pytest.raises(ValueError,match="cutoff"):
        compare_case(case(),review(evidence_cutoff=T-timedelta(days=1)))
