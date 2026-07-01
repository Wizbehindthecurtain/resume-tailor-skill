import render_docx

def test_render_and_parse_back_keeps_keywords(tmp_path):
    md = ("# Jane Doe\n## Skills\n- Python (PYTHON)\n- Kubernetes\n"
          "## Work Experience\n### Engineer — Acme — 03/2022\n- Cut risk 40%\n")
    out = tmp_path / "r.docx"
    render_docx.render_resume(md, out)
    assert out.exists()
    text = render_docx.extract_text(out)
    for kw in ("Python", "Kubernetes", "Acme", "40%"):
        assert kw in text

def test_main_extract(tmp_path, capsys):
    out = tmp_path / "r.docx"
    render_docx.render_resume("# Jane\n- Python\n", out)
    rc = render_docx.main(["--extract", str(out)])
    assert rc == 0 and "Python" in capsys.readouterr().out
