import importlib.util
import sys
import pytest
import ats_preview

def test_returns_hint_when_pyresparser_absent(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "pyresparser", None)  # force ImportError
    result = ats_preview.extract_fields(tmp_path / "x.docx")
    assert result["available"] is False and "hint" in result

@pytest.mark.skipif(importlib.util.find_spec("pyresparser") is None,
                    reason="pyresparser not installed")
def test_extracts_fields_when_available(tmp_path):
    import render_docx
    docx = tmp_path / "r.docx"
    render_docx.render_resume("# Jane Doe\njane@example.com\n## Skills\n- Python\n", docx)
    result = ats_preview.extract_fields(docx)
    assert result["available"] is True and "fields" in result
