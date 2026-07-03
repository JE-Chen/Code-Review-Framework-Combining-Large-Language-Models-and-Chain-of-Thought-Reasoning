from prthinker.evidence_binding import bind_evidence, finding_delta, gateable
from prthinker.schemas import Evidence, InlineFinding


def test_stable_ids_binding_and_delta():
    base = InlineFinding(path="a.py", line=2, comment="bug")
    same = InlineFinding(path="a.py", line=2, comment=" bug ")
    new = InlineFinding(path="b.py", line=3, comment="new bug")
    assert base.finding_id == same.finding_id
    evidence = Evidence(kind="test", status="confirmed", tool="pytest")
    assert bind_evidence([new], evidence, finding_id=new.finding_id)
    assert gateable([base, new]) == [new]
    delta = finding_delta([base], [same, new])
    assert delta.introduced == (new.finding_id,) and delta.persisting == (
        base.finding_id,
    )
