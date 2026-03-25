# claude-hwpx-plugin

A Claude Code plugin for reading, writing, and converting HWP/HWPX documents — the dominant document format in South Korea used by government, education, and enterprise.

한국에서 가장 많이 쓰이는 문서 포맷 HWP/HWPX를 Claude Code에서 읽고, 쓰고, 변환할 수 있게 해주는 플러그인입니다.

## Why?

Millions of documents in South Korea are stored in HWP format (Hancom Office Hangul). Government agencies, schools, law firms, and corporations all produce and consume HWP files daily. Converting these documents to usable data — extracting text, math equations, tables, and images — has been painful due to the proprietary format and poor tooling around math formula extraction.

This plugin teaches Claude Code the HWP/HWPX file structure, equation script syntax, and XML schema so it can work with Korean documents natively.

## Installation

```bash
git clone https://github.com/hohyon-ryu/claude-hwpx-plugin.git
claude --plugin-dir ./claude-hwpx-plugin
```

## Skills

### `/hwpx:hwpx-read` — Read Documents

Extract text, equations, images, and tables from HWP/HWPX files.

```
/hwpx:hwpx-read document.hwpx
/hwpx:hwpx-read contract.hwp
```

- **HWPX**: Unzip → parse XML → extract text and equations
- **HWP5 (binary)**: Uses `pyhwp` (`pip install pyhwp`)
- **Equations**: HWP equation script → LaTeX auto-conversion

### `/hwpx:hwpx-write` — Generate Documents

Programmatically create HWPX files.

```
/hwpx:hwpx-write B4 2-column exam paper
/hwpx:hwpx-write A4 report template
```

- B4/A4 paper sizes, 1 or 2 column layouts
- LaTeX → HWP equation script conversion
- Image embedding, endnotes, tables
- Korean font configuration (Shin Myeong Joong Myeong Jo, NanumGothic, etc.)

### `/hwpx:hwpx-convert` — Format Conversion

Bidirectional HWP/HWPX ↔ Markdown conversion.

```
/hwpx:hwpx-convert report.hwpx → markdown
/hwpx:hwpx-convert *.hwp → markdown (batch)
/hwpx:hwpx-convert document.md → hwpx
```

## Included Tools

Ready-to-run scripts in `templates/`:

| File | Description |
|------|-------------|
| `reader.py` | HWPX/HWP5 → Markdown converter |
| `generator.py` | Markdown → HWPX generator |
| `*.xml` | HWPX skeleton templates (header, section, content.hpf, etc.) |

```bash
# HWPX → Markdown
python templates/reader.py input.hwpx output.md

# Generate HWPX
python templates/generator.py output.hwpx "Title" "Body text"
```

## HWP → Markdown Guide

The most common use case. Quality comparison by method:

| Method | Text | Equations | Tables | Images |
|--------|------|-----------|--------|--------|
| `hwp5txt` (pyhwp) | ✅ | ❌ | △ | ❌ |
| `hwp5html` → pandoc | ✅ | △ | ✅ | ✅ |
| HWPX → `reader.py` | ✅ | ✅ LaTeX | ✅ | ✅ |

**Best quality for math-heavy docs**: Save as HWPX in Hangul → use `reader.py`.

## HWP → HWPX Conversion

No direct CLI conversion tool exists.

- **Small batch**: Open in Hangul, "Save As" → HWPX
- **Large batch (Windows)**: Hangul ActiveX macro automation
- **Mac/Linux**: Extract text via `pyhwp` → regenerate HWPX (formatting loss)

## HWP Equation Syntax Reference

HWP uses its own equation syntax, not LaTeX:

```
LaTeX                    HWP Equation Script
─────────────────────    ─────────────────────
\frac{a}{b}          →  {a} over {b}
\sqrt{x}             →  sqrt {x}
\text{cm}            →  "cm"
\left( \right)       →  left ( right )
\alpha, \theta       →  alpha, theta
```

## HWP Format Versions

| Version | Era | Format |
|---------|-----|--------|
| HWP 1.x–3.x | 1989–2001 | Proprietary binary (rare) |
| **HWP 5.x** | 2002–present | **OLE2 compound document** |
| **HWPX** | 2014–present | **ZIP+XML** (Open XML-like) |

99% of .hwp files in circulation are HWP5.

## Use Cases

- **Government**: Convert HWP official documents to Markdown for search and analysis
- **Education**: Auto-generate exam papers and lesson plans as HWPX
- **Legal**: Digitize and structure legal documents
- **Archive**: Batch-convert large HWP document collections to Markdown

## Requirements

- Claude Code
- Python 3.8+ (for template scripts)
- `pyhwp` (for HWP5 binary reading): `pip install pyhwp`
- `pandoc` (optional, for HTML→Markdown)

## License

MIT

## Author

**유호현 (Hohyon Ryu)**
- GitHub: [@hohyon-ryu](https://github.com/hohyon-ryu)
