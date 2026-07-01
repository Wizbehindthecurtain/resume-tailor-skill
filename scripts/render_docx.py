#!/usr/bin/env python3
"""Render resume Markdown to a single-column ATS-friendly DOCX, and extract text back."""
import argparse
import sys
from pathlib import Path
from docx import Document

def render_resume(markdown_text: str, out_path) -> None:
    doc = Document()
    for raw in markdown_text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.startswith("- "):
            doc.add_paragraph(line[2:], style="List Bullet")
        else:
            doc.add_paragraph(line)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))

def extract_text(docx_path) -> str:
    doc = Document(str(docx_path))
    return "\n".join(p.text for p in doc.paragraphs)

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render resume Markdown to DOCX, or extract text.")
    parser.add_argument("--in", dest="in_path", type=Path)
    parser.add_argument("--out", dest="out_path", type=Path)
    parser.add_argument("--extract", dest="extract_path", type=Path)
    args = parser.parse_args(argv)
    if args.extract_path:
        sys.stdout.write(extract_text(args.extract_path))
        return 0
    if args.in_path and args.out_path:
        render_resume(args.in_path.read_text(encoding="utf-8"), args.out_path)
        sys.stdout.write(str(args.out_path))
        return 0
    parser.error("provide --in and --out to render, or --extract to extract")

if __name__ == "__main__":
    raise SystemExit(main())
