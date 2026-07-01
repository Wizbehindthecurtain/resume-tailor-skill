import importlib.util
import sys
import pytest
import ats_preview

def test_returns_hint_when_spacy_absent(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "spacy", None)  # force `import spacy` to fail
    result = ats_preview.extract_fields(tmp_path / "x.docx")
    assert result["available"] is False and "hint" in result

def _model_available():
    if importlib.util.find_spec("spacy") is None:
        return False
    import spacy
    try:
        spacy.load("en_core_web_sm")
        return True
    except Exception:
        return False

@pytest.mark.skipif(not _model_available(), reason="spaCy en_core_web_sm not installed")
def test_extracts_fields_when_available(tmp_path):
    import render_docx
    docx = tmp_path / "r.docx"
    render_docx.render_resume(
        "# Jane Doe\njane@example.com\n## Work Experience\n- Built X at Acme Corp\n", docx)
    result = ats_preview.extract_fields(docx)
    assert result["available"] is True and "fields" in result
    assert "jane@example.com" in result["fields"]["emails"]
