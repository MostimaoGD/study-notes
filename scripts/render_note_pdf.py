#!/usr/bin/env python
"""Render a Chinese Markdown study note to a simple PDF reading copy."""

from __future__ import annotations

import argparse
import html
import re
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer


def read_text_file(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "utf-16"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def register_cjk_font() -> str:
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        return "STSong-Light"
    except Exception:
        pass
    for font_name, font_path in (
        ("MicrosoftYaHei", r"C:\Windows\Fonts\msyh.ttc"),
        ("SimSun", r"C:\Windows\Fonts\simsun.ttc"),
        ("SimHei", r"C:\Windows\Fonts\simhei.ttf"),
    ):
        try:
            if Path(font_path).exists():
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
        except Exception:
            continue
    return "Helvetica"


def build_styles(font_name: str) -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    base = ParagraphStyle(
        "CJKBody",
        parent=sample["BodyText"],
        fontName=font_name,
        fontSize=10.5,
        leading=16,
        spaceAfter=5,
        wordWrap="CJK",
    )
    return {
        "body": base,
        "h1": ParagraphStyle("CJKH1", parent=base, fontSize=20, leading=26, spaceBefore=8, spaceAfter=10),
        "h2": ParagraphStyle("CJKH2", parent=base, fontSize=16, leading=22, spaceBefore=10, spaceAfter=7),
        "h3": ParagraphStyle("CJKH3", parent=base, fontSize=13, leading=18, spaceBefore=8, spaceAfter=5),
        "quote": ParagraphStyle(
            "CJKQuote",
            parent=base,
            leftIndent=8 * mm,
            textColor=colors.HexColor("#444444"),
            borderColor=colors.HexColor("#D0D7DE"),
            borderWidth=0.5,
            borderPadding=4,
            backColor=colors.HexColor("#F6F8FA"),
        ),
        "code": ParagraphStyle(
            "CJKCode",
            parent=base,
            fontName=font_name,
            fontSize=8.5,
            leading=12,
            leftIndent=4 * mm,
            rightIndent=2 * mm,
            backColor=colors.HexColor("#F6F8FA"),
            borderColor=colors.HexColor("#D0D7DE"),
            borderWidth=0.25,
            borderPadding=5,
        ),
    }


def wrap_code(text: str, width: int = 92) -> str:
    wrapped: list[str] = []
    for line in text.splitlines() or [""]:
        if len(line) <= width:
            wrapped.append(line)
        else:
            wrapped.extend(textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False) or [""])
    return "\n".join(wrapped)


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    safe = html.escape(text)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
    safe = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", safe)
    return Paragraph(safe, style)


def flush_table(table_lines: list[str], story: list, styles: dict[str, ParagraphStyle]) -> None:
    if table_lines:
        story.append(Preformatted(wrap_code("\n".join(table_lines)), styles["code"]))
        story.append(Spacer(1, 3 * mm))
        table_lines.clear()


def markdown_to_story(markdown: str, styles: dict[str, ParagraphStyle]) -> list:
    story: list = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    table_lines: list[str] = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            flush_table(table_lines, story, styles)
            if in_code:
                if code_lang.lower() == "mermaid":
                    story.append(paragraph("Mermaid 图（文本备份）", styles["body"]))
                story.append(Preformatted(wrap_code("\n".join(code_lines)), styles["code"]))
                story.append(Spacer(1, 4 * mm))
                code_lines = []
                code_lang = ""
                in_code = False
            else:
                in_code = True
                code_lang = line.strip("`").strip()
            continue

        if in_code:
            code_lines.append(line)
            continue

        if line.startswith("|") and line.endswith("|"):
            table_lines.append(line)
            continue
        flush_table(table_lines, story, styles)

        if not line.strip():
            story.append(Spacer(1, 2.5 * mm))
            continue
        if line == "\\pagebreak":
            story.append(PageBreak())
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            style = styles["h1"] if level == 1 else styles["h2"] if level == 2 else styles["h3"]
            story.append(paragraph(text, style))
            continue

        if line.startswith(">"):
            story.append(paragraph(line.lstrip("> ").strip(), styles["quote"]))
            continue

        story.append(paragraph(line, styles["body"]))

    flush_table(table_lines, story, styles)
    if code_lines:
        story.append(Preformatted(wrap_code("\n".join(code_lines)), styles["code"]))
    return story


def render_pdf(markdown_path: Path, output_path: Path) -> None:
    font_name = register_cjk_font()
    styles = build_styles(font_name)
    markdown = read_text_file(markdown_path)
    story = markdown_to_story(markdown, styles)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=markdown_path.stem,
    )
    doc.build(story)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a Markdown study note to PDF.")
    parser.add_argument("markdown_file")
    parser.add_argument("--output", help="Output PDF path. Defaults to the Markdown filename with .pdf.")
    args = parser.parse_args(argv)

    markdown_path = Path(args.markdown_file)
    output_path = Path(args.output) if args.output else markdown_path.with_suffix(".pdf")
    render_pdf(markdown_path, output_path)
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
