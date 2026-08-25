from app.models import JobObservation
from app.pipeline import build_employers


def job(title, industry):
    return JobObservation(
        employer="Example Employer",
        title=title,
        location="La Crosse, WI",
        industry=industry,
        posted_at=None,
        source="test",
        source_url="https://example.com/job",
        external_id=title.lower().replace(" ", "-"),
        verified=True,
    )


def test_pipeline_drops_out_of_scope_jobs():
    employers = build_employers([
        job("Operations Manager", "operations"),
        job("Cashier", "operations"),
        job("Teacher", "operations"),
    ])
    assert len(employers) == 1
    assert [o.title for o in employers[0].observations] == ["Operations Manager"]
