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
