import check_traceability

def _brain(tmp_path):
    roles = tmp_path / "brain" / "roles"; roles.mkdir(parents=True)
    (tmp_path / "brain" / "projects").mkdir()
    (roles / "acme.md").write_text(
        "## Bullets\n- Cut thermal risk 40% by redesigning the pack [metric: 40%]\n",
        encoding="utf-8")
    return tmp_path / "brain"

def test_grounded_bullet_traces(tmp_path):
    brain = _brain(tmp_path)
    resume = "- Reduced thermal risk 40% by redesigning the pack\n"
    assert check_traceability.untraceable(resume, brain) == []

def test_fabricated_bullet_flagged(tmp_path):
    brain = _brain(tmp_path)
    resume = "- Won the Nobel Prize in Physics for cold fusion\n"
    flagged = check_traceability.untraceable(resume, brain)
    assert len(flagged) == 1

def test_ventures_checked_references_exempt(tmp_path):
    brain = _brain(tmp_path)  # existing helper; corpus has the thermal-risk bullet
    resume = (
        "## Businesses Owned & Operated\n- Founded a company that cured cancer overnight\n"
        "## References\n- Jane Smith — VP, Acme — (555) 555-0100\n")
    flagged = check_traceability.untraceable(resume, brain)
    # the fabricated venture bullet IS flagged (Businesses is an accomplishment section)
    assert any("cured cancer" in f for f in flagged)
    # the reference line is NOT flagged (References is exempt)
    assert not any("jane smith" in f for f in flagged)

def test_only_experience_section_bullets_are_checked(tmp_path):
    brain = _brain(tmp_path)  # reuse the existing helper (corpus has the thermal-risk bullet)
    resume = (
        "## Skills\n- Fabricated skill nobody has\n"
        "## Work Experience\n### Role\n- Reduced thermal risk 40% by redesigning the pack\n"
        "- Won the Nobel Prize in Physics\n"
        "## Education\n- Made-up University\n")
    flagged = check_traceability.untraceable(resume, brain)
    # Skills + Education lines are NOT checked (grounded in their own corpus files)
    assert "fabricated skill nobody has" not in flagged
    assert "made-up university" not in flagged
    # A fabricated Work Experience bullet IS flagged; the grounded one is not
    assert any("nobel" in f for f in flagged)
    assert not any("thermal risk" in f for f in flagged)
