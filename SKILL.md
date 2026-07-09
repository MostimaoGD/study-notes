---
name: study-literature-notes
description: Audit and study textbooks, papers, course materials, and long learning documents (.pdf, .docx, .md, .txt, .pptx). Use when Codex needs to decide whether an uploaded learning file is readable, detect oversized or scanned/image-heavy files, automatically plan and extract all chapters/sections/chunks from readable files, identify important formulas and visuals, and create Chinese evidence-backed illustrated Markdown notes with source anchors, formula derivations, Mermaid diagrams, and ASCII sketches.
---

# Study Literature Notes

## Core Workflow

Use this skill to study textbooks, academic papers, course handouts, and long-form learning materials. Always audit first.

1. Run `scripts/audit_document.py <file>` first.
2. Read the audit result before continuing.
3. If `fit_status` is `unreadable`, stop. Explain why the text cannot be trusted and ask for OCR text, a readable version, or a smaller readable range.
4. For every readable file (`fits`, `borderline`, or `oversize`), run `scripts/plan_chapter_batches.py <file>` to identify all chapters, paper sections, slide groups, or automatic chunks.
5. Extract all planned items by default with `scripts/extract_range.py <file> --plan-json chapter-plan.json --all-items --output-dir extracted-items`.
6. Use `scripts/extract_visuals.py` for PDF/PPTX files that may contain important figures, tables, diagrams, formulas, or visual explanations.
7. Read `references/note-template.md` before creating final notes.
8. Create Markdown note file(s) only by default. Do not render a PDF unless the user explicitly asks for PDF/export; then `scripts/render_note_pdf.py` may be used as an optional final step.

Do not skip the audit unless the user provides a very small pasted excerpt directly in the chat.

## Audit Policy

Treat the audit as a reliability gate, not as a batching decision:

- `fits`: still run chapter/section planning, then extract all planned items. A single full-document Markdown note is acceptable only when the whole extracted document comfortably fits and the user wants one file.
- `borderline`: run planning and extract all planned items. Generate notes from the extracted Markdown files, usually one chapter/section/chunk at a time.
- `oversize`: do not attempt one monolithic full-context summary. Run planning and extract all planned items first, then create Markdown notes from those extracted units with clear source anchors.
- `unreadable`: do not claim full understanding. Explain whether the problem is low text extraction, scan risk, unsupported content, or parsing failure.

The first user-facing response after an audit should include:

- file type and page/slide/paragraph count
- estimated tokens
- text extraction quality
- scan/image risk
- whether full-file reading is safe
- planned extraction strategy

## Planning And Extraction

For any readable document, run:

```bash
scripts/plan_chapter_batches.py <file> --json-output chapter-plan.json --markdown-output chapter-plan.md
scripts/extract_range.py <file> --plan-json chapter-plan.json --all-items --output-dir extracted-items
```

Use the planning fallback order exactly:

1. PDF bookmarks/outlines
2. visible table of contents
3. body headings
4. paper sections such as Abstract, Introduction, Methods, Results, Discussion, Conclusion, References
5. automatic token/page/paragraph chunks

Respect the plan's `confidence`:

- `high`: treat items as real chapters or sections.
- `medium`: treat items as inferred headings or paper sections and mention that they were inferred.
- `low`: treat items as automatic chunks. Do not call them chapters.

If an item is marked `chapter_oversize`, use the generated sub-parts or page chunks. Do not force a whole-chapter summary. The legacy `--batch-id` path is only for explicit compatibility or when the user asks for a batch.

## Note Requirements

Write notes in Chinese by default. The note should be evidence-backed and illustrated, not a generic summary.

Save final notes as Markdown (`.md`). For long documents, prefer an index Markdown file plus one Markdown note per chapter/section/chunk.

Include:

- knowledge framework
- key concepts and definitions
- important claims and conclusions
- terminology table
- important formulas with symbol meanings, applicable conditions, key derivation steps, and source anchors
- important visuals recreated as Mermaid diagrams or ASCII line sketches
- evidence table
- confusing points and unresolved questions

Exclude by default:

- review questions
- follow-up study plans
- motivational advice or generic learning suggestions
- PDF output

## Evidence Rules

Be strict about source traceability:

- Attach page, slide, paragraph, section, or heading anchors to important claims.
- Mark any model-supplied derivation step with the exact Chinese label defined in `references/note-template.md`.
- Mark any point inferred from nearby text with the exact Chinese label defined in `references/note-template.md`.
- Mark visual interpretation uncertainty when the image has no extractable caption or readable surrounding text.
- Never claim that image text was read when OCR was not used.

## Formula Rules

For important formulas, provide:

- original formula written as Markdown math, using inline `$...$` or display `$$...$$`
- symbol table
- assumptions and applicable conditions
- key derivation steps
- final meaning in plain language
- source anchor

Do not put formulas in fenced `text` code blocks. Use fenced text only for raw OCR fragments that cannot be reliably converted, pseudocode, or ASCII sketches. When PDF extraction breaks a formula, rewrite the clean study version in Markdown math and mark any reconstruction as `补充推导` or `推断`.

Use key-step derivations by default. Do not expand into a long proof unless the user asks.

## Visual Rules

Use Mermaid plus ASCII:

- Use Mermaid for conceptual structures, flows, causal chains, hierarchies, and comparisons.
- Use ASCII line sketches for simplified versions of source figures, tables, axes, processes, and layouts.
- Give every recreated visual a title, source anchor, and one-sentence explanation.
- State that the recreated visual is a simplified study diagram, not a faithful reproduction of the original figure.

## Scripts

- `scripts/audit_document.py`: audit file type, text extraction quality, scan risk, estimated tokens, and fit status.
- `scripts/plan_chapter_batches.py`: plan all chapters, paper sections, slide groups, or automatic chunks; batch fields are retained only for compatibility.
- `scripts/extract_range.py`: extract selected pages, slides, headings, paragraphs, or all planned items with source anchors.
- `scripts/extract_visuals.py`: identify important PDF/PPTX visual candidates, captions, nearby text, and uncertainty.
- `scripts/render_note_pdf.py`: optional Markdown-to-PDF export only when the user explicitly requests PDF.

All scripts can be run with `--help`.
