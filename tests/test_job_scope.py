from app.job_scope import is_in_scope


def test_focused_industries_are_in_scope():
    assert is_in_scope("Operations Manager", "operations")
    assert is_in_scope("Production Supervisor", "manufacturing")
    assert is_in_scope("Warehouse Manager", "warehouse")
    assert is_in_scope("Maintenance Technician", "skilled trades")
    assert is_in_scope("Hotel General Manager", "hospitality")
    assert is_in_scope("Director of Operations", "leadership")


def test_out_of_scope_roles_are_rejected():
    assert not is_in_scope("Teacher", "operations")
    assert not is_in_scope("Cashier", "operations")
    assert not is_in_scope("Retail Associate", "leadership")
    assert not is_in_scope("Registered Nurse", "operations")


def test_unknown_industry_is_rejected():
    assert not is_in_scope("Software Developer", "technology")
