# Study Literature Notes

`study-literature-notes` is a Codex skill for studying textbooks, papers, course materials, slide decks, and other long learning documents. It audits the source file first, extracts all planned chapters, sections, slide groups, or chunks, and then creates Chinese Markdown study notes with evidence anchors, formula explanations, Mermaid diagrams, and ASCII sketches.

This README is human-facing documentation. Codex uses `SKILL.md` as the executable instruction source when the skill triggers.

## When To Use

Use this skill when you want Codex to:

- Study a PDF, DOCX, Markdown, TXT, or PPTX learning file.
- Decide whether a file is readable before summarizing it.
- Avoid information loss in oversized documents.
- Extract all chapters, sections, slide groups, or chunks before writing notes.
- Create Chinese evidence-backed notes instead of a generic summary.
- Preserve source anchors for claims, formulas, figures, and tables.
- Recreate important visuals as Mermaid diagrams or ASCII sketches.

Typical requests:

```text
Use $study-literature-notes to study this textbook and create chapter notes.
用 study-literature-notes 处理这篇论文，生成有证据锚点的中文笔记。
这个 PDF 很大，帮我分章提取并写学习笔记。
```

## Core Workflow

The skill always starts with an audit unless the user only provides a very small pasted excerpt.

1. Audit the document:

   ```bash
   scripts/audit_document.py <file>
   ```

2. Read the audit result and decide whether the extracted text is trustworthy.

3. If the file is readable, plan chapters, sections, slide groups, or automatic chunks:

   ```bash
   scripts/plan_chapter_batches.py <file> --json-output chapter-plan.json --markdown-output chapter-plan.md
   ```

4. Extract every planned item by default:

   ```bash
   scripts/extract_range.py <file> --plan-json chapter-plan.json --all-items --output-dir extracted-items
   ```

5. For PDF or PPTX files with important diagrams, tables, figures, or formulas, extract visual candidates:

   ```bash
   scripts/extract_visuals.py <file>
   ```

6. Read `references/note-template.md` before writing final notes.

7. Create Markdown notes. Export PDF only when the user explicitly asks for it.

## File Size Strategy

The audit result controls how the skill prevents missing information:

| Status | Strategy |
| --- | --- |
| `fits` | Still plan and extract the document. A single full-document Markdown note is acceptable when the content comfortably fits and the user wants one file. |
| `borderline` | Plan and extract all items. Usually write notes one chapter, section, or chunk at a time. |
| `oversize` | Do not summarize the whole file in one pass. Plan all items, extract all items, and write notes from the extracted units. |
| `unreadable` | Stop. Explain why the text cannot be trusted and ask for OCR text, a readable file, or a smaller readable range. |

In short: small files may become one complete note; large files are split into chapter, section, or chunk notes, while still covering the whole file.

## Planning Order

When creating the extraction plan, the skill uses this fallback order:

1. PDF bookmarks or outlines
2. Visible table of contents
3. Body headings
4. Paper sections such as Abstract, Introduction, Methods, Results, Discussion, Conclusion, and References
5. Automatic token, page, paragraph, or slide chunks

The plan confidence matters:

- `high`: treat items as real chapters or sections.
- `medium`: treat items as inferred headings or paper sections and say they were inferred.
- `low`: treat items as automatic chunks. Do not call them chapters.

If one chapter is itself oversized, use its generated sub-parts or page chunks instead of forcing a whole-chapter note.

## Expected Outputs

For short or clean files, the output can be:

```text
notes.md
```

For long files, prefer:

```text
notes-index.md
chapter-01.md
chapter-02.md
section-abstract.md
chunk-001.md
```

The exact filenames can follow the document structure, but the notes should preserve source anchors so the user can trace important points back to the original material.

## Note Content Requirements

Final notes are written in Chinese by default and should include:

- Knowledge framework
- Key concepts and definitions
- Important claims and conclusions
- Terminology table
- Important formulas with symbols, assumptions, derivation steps, plain-language meaning, and source anchors
- Important visuals recreated as Mermaid diagrams or ASCII sketches
- Evidence table
- Confusing points and unresolved questions

Exclude by default:

- Review questions
- Follow-up study plans
- Motivational advice
- PDF output

## Evidence Rules

The notes should be traceable, not merely fluent.

- Attach page, slide, paragraph, section, or heading anchors to important claims.
- Mark model-supplied derivation steps with the label defined in `references/note-template.md`.
- Mark nearby-text interpretations with the label defined in `references/note-template.md`.
- State uncertainty when interpreting visuals without readable captions or surrounding text.
- Never claim that image text was read if OCR was not used.

## Formula Rules

For each important formula, include:

- Original formula
- Symbol table
- Assumptions and applicable conditions
- Key derivation steps
- Plain-language meaning
- Source anchor

Use key-step derivations by default. Do not expand into a long proof unless the user asks.

## Visual Rules

Use Mermaid for conceptual structures, flows, causal chains, hierarchies, and comparisons.

Use ASCII sketches for simplified versions of source figures, tables, axes, processes, or layouts.

Every recreated visual should have:

- A title
- A source anchor
- A one-sentence explanation
- A note that it is a simplified study diagram, not a faithful reproduction of the original figure

## Script Reference

| Script | Purpose |
| --- | --- |
| `scripts/audit_document.py` | Audits file type, text extraction quality, scan risk, estimated tokens, and fit status. |
| `scripts/plan_chapter_batches.py` | Plans chapters, paper sections, slide groups, or automatic chunks. |
| `scripts/extract_range.py` | Extracts selected pages, slides, headings, paragraphs, or all planned items with source anchors. |
| `scripts/extract_visuals.py` | Identifies important PDF/PPTX visual candidates, captions, nearby text, and uncertainty. |
| `scripts/render_note_pdf.py` | Optionally exports Markdown notes to PDF only when the user explicitly requests PDF. |

Each script supports:

```bash
scripts/<script-name>.py --help
```

## Failure Handling

If extraction is weak, scanned, image-heavy, or unsupported, the skill should say so directly. It should not pretend to understand the whole document. Ask for one of the following instead:

- OCR text
- A readable source file
- A smaller readable page range
- Screenshots or images of specific pages if visual interpretation is needed

## Maintainer Notes

- Keep `SKILL.md` as the source of truth for agent behavior.
- Keep this README focused on human orientation and usage.
- Update this README when scripts, required outputs, or the audit/planning policy changes.