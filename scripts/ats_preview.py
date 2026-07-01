#!/usr/bin/env python3
"""Stage-2 ATS field-extraction PROXY using spaCy. Non-blocking; degrades if deps absent.

Approximates the field extraction that proprietary engines (Sovren/Textkernel,
HireAbility, Affinda) perform. Those are closed-source and cannot run locally; this is a
labeled proxy built on spaCy NER + regex, informational only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

_HINT = ("Install the field-preview extra to enable the ATS field preview: "
         "pip install spacy && python -m spacy download en_core_web_sm")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"\+?\d[\d\s().\-]{7,}\d")

def _text_from_docx(docx_path) -> str:
    from docx import Document
    doc = Document(str(docx_path))
    return "\n".join(p.text for p in doc.paragraphs)

def extract_fields(docx_path) -> dict:
    try:
        import spacy
    except Exception:
        return {"available": False, "hint": _HINT}
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        return {"available": False, "hint": _HINT}
    try:
        text = _text_from_docx(docx_path)
    except Exception as e:
        return {"available": False, "error": f"could not read {docx_path}: {e}"}
    doc = nlp(text)
    persons = [e.text for e in doc.ents if e.label_ == "PERSON"]
    orgs = sorted({e.text for e in doc.ents if e.label_ == "ORG"})
    dates = [e.text for e in doc.ents if e.label_ == "DATE"]
    return {"available": True, "fields": {
        "name": persons[0] if persons else None,
        "emails": sorted(set(_EMAIL.findall(text))),
        "phones": sorted({p.strip() for p in _PHONE.findall(text)}),
        "organizations": orgs,
        "dates": dates,
    }}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ATS field-extraction proxy (Stage 2, spaCy).")
    parser.add_argument("docx", type=Path)
    args = parser.parse_args(argv)
    json.dump(extract_fields(args.docx), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
