#!/usr/bin/env python3
"""Stage-2 ATS field-extraction PROXY (spaCy/pyresparser). Non-blocking; degrades if absent.

This approximates the field extraction that proprietary engines (Sovren/Textkernel,
HireAbility, Affinda) perform. Those engines are closed-source and cannot run locally;
this is a labeled proxy, informational only.
"""
import argparse
import json
import sys
from pathlib import Path

_HINT = ("Install the field-preview extra to enable the ATS field preview: "
         "pip install spacy pyresparser && python -m spacy download en_core_web_sm")

def extract_fields(docx_path) -> dict:
    try:
        from pyresparser import ResumeParser
    except Exception:
        return {"available": False, "hint": _HINT}
    data = ResumeParser(str(docx_path)).get_extracted_data() or {}
    return {"available": True, "fields": {
        "name": data.get("name"),
        "email": data.get("email"),
        "mobile_number": data.get("mobile_number"),
        "skills": data.get("skills", []),
        "designation": data.get("designation", []),
        "company_names": data.get("company_names", []),
    }}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ATS field-extraction proxy (Stage 2).")
    parser.add_argument("docx", type=Path)
    args = parser.parse_args(argv)
    json.dump(extract_fields(args.docx), sys.stdout, indent=2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
