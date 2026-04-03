# claude-hwpx-plugin

A Claude Code plugin for reading, writing, and converting HWP/HWPX documents — the dominant document format in South Korea used by government, education, and enterprise.

한국에서 가장 많이 쓰이는 문서 포맷 HWP/HWPX를 Claude Code에서 읽고, 쓰고, 변환할 수 있게 해주는 플러그인입니다.

---

## Why? | 왜 필요한가?

Virtually all official documents in South Korea are stored in HWP format (Hancom Office Hangul). Government agencies, schools, law firms, and corporations all produce and consume HWP files daily. Converting these documents to usable data has been painful due to the proprietary format and poor tooling around math formula extraction.

This plugin teaches Claude Code the HWP/HWPX file structure, equation script syntax, and XML schema so it can work with Korean documents natively.

## Installation | 설치

### Option 1: Marketplace (Recommended)

```bash
# Add marketplace
/plugin marketplace add hohyon-ryu/claude-hwpx-plugin

# Install plugin
/plugin install hwpx
```

### Option 2: settings.json

Add to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "hwpx": {
      "source": { "source": "github", "repo": "hohyon-ryu/claude-hwpx-plugin" }
    }
  },
  "enabledPlugins": {
    "hwpx@hwpx": true
  }
}
```

### Option 3: Local Testing

```bash
git clone https://github.com/hohyon-ryu/claude-hwpx-plugin.git
claude --plugin-dir ./claude-hwpx-plugin
```

## Quick Reference

| Task | Command |
|------|---------|
| Read HWPX → Markdown | `python scripts/reader.py doc.hwpx output.md` |
| Create HWPX | `python scripts/generator.py out.hwpx "Title" "Body"` |
| Validate HWPX | `python scripts/validate.py doc.hwpx` |
| Read legacy HWP | `pip install pyhwp && hwp5txt doc.hwp` |
| Use skill | Mention HWP/HWPX/한글 in conversation — skill auto-activates |

## Skill: `/hwpx:hwpx`

A single unified skill that handles all HWP/HWPX operations:

- **Read**: Extract text, equations (→ LaTeX), images, tables from HWPX files
- **Write**: Generate HWPX with equations, tables, images, multi-column layouts
- **Convert**: Bidirectional HWPX ↔ Markdown conversion
- **Edit**: Unpack → edit XML → repack workflow

The skill auto-activates when you mention HWP, HWPX, 한글, or Hancom documents.

## Scripts

| File | Purpose |
|------|---------|
| `scripts/reader.py` | HWPX/HWP5 → Markdown converter |
| `scripts/generator.py` | Markdown/text → HWPX generator |
| `scripts/validate.py` | HWPX structure validator |

## Templates

| File | Purpose |
|------|---------|
| `templates/base-header.xml` | Font definitions, styles, character properties |
| `templates/base-section.xml` | Section template with page/column settings |
| `templates/base-content.hpf` | OPF package manifest |
| `templates/base-container.xml` | OPF container |
| `templates/sample-a4.hwpx` | A4 single-column sample |
| `templates/sample-b4-2col.hwpx` | B4 2-column exam paper sample |

## HWP Equation Syntax

HWP uses its own equation syntax, **not LaTeX**:

```
LaTeX                    HWP Equation Script
─────────────────────    ─────────────────────
\frac{a}{b}          →  {a} over {b}
\sqrt{x}             →  sqrt {x}
\text{cm}            →  "cm"
\overline{AB}        →  rm bar{AB}
\triangle ABC        →  rm triangle ABC
\cdot                →  cdot (NOT bullet)
\to                  →  `->` (backtick spacing)
```

See the full conversion table in [SKILL.md](skills/hwpx/SKILL.md).

## Conversion Quality

| Method | Text | Equations | Tables | Images |
|--------|------|-----------|--------|--------|
| hwp5txt (pyhwp) | ✅ | ❌ | △ | ❌ |
| hwp5html → pandoc | ✅ | △ | ✅ | ✅ |
| **HWPX → reader.py** | ✅ | **✅ LaTeX** | ✅ | ✅ |

**Best quality**: HWP → Save as HWPX in 한글 → `reader.py`

## Use Cases

- **Government**: Convert HWP official documents to Markdown/data
- **Education**: Auto-generate exam papers in HWPX (B4 2-column)
- **Legal**: Digitize and structure legal documents
- **Archive**: Batch-convert HWP documents to Markdown

## Requirements

- Claude Code
- Python 3.8+ (for scripts)
- `pyhwp` (optional, for HWP5 binary): `pip install pyhwp`
- `pandoc` (optional, for HTML→Markdown)

## License

MIT

## Author

**유호현 (Hohyon Ryu)** — [@hohyon-ryu](https://github.com/hohyon-ryu)
