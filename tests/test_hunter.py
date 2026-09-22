from app.hunter import VerifiedContact, hunter_record, rank_contacts


def test_rank_contacts_prefers_recruiting_roles():
    contacts = [
        VerifiedContact("acme", "Ops Lead", "Operations Leader", "https://example.com/ops", "2026-09-21"),
        VerifiedContact("acme", "HR Lead", "Talent Acquisition Manager", "https://example.com/hr", "2026-09-21"),
    ]
    ranked = rank_contacts(contacts)
    assert ranked[0].name == "HR Lead"


def test_hunter_never_invents_missing_contact():
    prospect = {"slug": "acme", "employer": "Acme"}
    result = hunter_record(prospect, [])
    assert result["contact"] is None
    assert result["hunter_status"] == "needs_research"


def test_hunter_preserves_verified_source():
    prospect = {"slug": "acme"}
    contact = VerifiedContact("acme", "HR Lead", "HR Manager", "https://example.com/hr", "2026-09-21")
    result = hunter_record(prospect, [contact])
    assert result["contact"]["source_url"] == "https://example.com/hr"
