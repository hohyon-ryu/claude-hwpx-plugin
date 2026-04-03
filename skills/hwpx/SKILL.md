---
name: hwpx
description: "Use this skill whenever the user wants to create, read, edit, or manipulate HWP/HWPX documents (한글 문서). Triggers include: any mention of 'HWP', 'HWPX', '한글', '한컴', 'Hancom', '.hwp', '.hwpx', or requests to produce Korean-standard documents with equations, tables, multi-column layouts, or government/education formatting. Also use when extracting text or equations from HWP/HWPX files, converting between HWP/HWPX and Markdown, working with HWP equation scripts, or generating Korean exam papers (시험지). If the user asks for a document in HWP/HWPX format, use this skill. Do NOT use for DOCX, PDF, or general document tasks unrelated to HWP/HWPX."
license: MIT
---

# HWPX creation, reading, and conversion

## Overview

A .hwpx file is a ZIP archive containing XML files — Hancom Office's Open XML format (한글 2014+). The older .hwp format is OLE2 binary (한글 97–2014).

## Quick Reference

| Task | Approach |
|------|----------|
| Read/analyze content | `python scripts/reader.py doc.hwpx` or unpack for raw XML |
| Create new document | `python scripts/generator.py` — see Creating New Documents below |
| Edit existing document | Unzip → edit XML → rezip — see Editing Existing Documents below |
| Convert HWPX → Markdown | `python scripts/reader.py doc.hwpx output.md` |
| Convert Markdown → HWPX | `python scripts/generator.py output.hwpx "Title" "body text"` |
| Convert legacy .hwp | `pip install pyhwp && hwp5txt doc.hwp` or LibreOffice |
| Validate HWPX | `python scripts/validate.py doc.hwpx` |

### Converting Legacy .hwp to .hwpx

Legacy `.hwp` files (OLE2 binary) cannot be directly edited as XML:

```bash
# Text extraction only (no formatting)
pip install pyhwp
hwp5txt document.hwp > output.txt

# Via LibreOffice (limited equation support)
libreoffice --headless --convert-to docx document.hwp
```

**Best quality path:** Open in 한글 program → Save As HWPX → use reader.py

### Reading Content

```bash
# Markdown extraction with equations preserved as LaTeX
python scripts/reader.py document.hwpx output.md

# Raw XML access
unzip document.hwpx -d unpacked/
cat unpacked/Contents/section0.xml
```

### Validation

```bash
python scripts/validate.py document.hwpx
```

---

## Creating New Documents

Generate .hwpx files with Python using `scripts/generator.py`.

### Basic Usage

```bash
python scripts/generator.py output.hwpx "문서 제목" "본문 내용" [A4|B4] [1|2]
```

- Paper sizes: `A4` (default), `B4` (Korean exam paper standard)
- Columns: `1` (default), `2` (newspaper-style, for exam papers)

### Programmatic Usage

```python
from generator import generate_hwpx, build_text_para, build_equation_para, build_table, build_empty_para

# Simple document
generate_hwpx("output.hwpx", "제목", "본문 텍스트\n두 번째 줄")

# With inline equations (use $...$ in text)
generate_hwpx("output.hwpx", "수학 문제", "이차방정식 $x^2 + 3x + 2 = 0$을 풀어라.")

# B4 2-column exam paper
generate_hwpx("exam.hwpx", "2024학년도 수학 시험", body_text, "B4", 2)
```

### Custom Section Assembly

For complex documents, build sections manually:

```python
from generator import make_section, build_text_para, build_equation_para, build_table, build_empty_para
import zipfile

paras = []
paras.append(build_text_para("1. 다음 방정식을 풀어라."))
paras.append(build_empty_para())
paras.append(build_equation_para(r"\frac{x+1}{x-1} = 3"))
paras.append(build_empty_para())
paras.append(build_table([["x", "y"], ["1", "2"], ["3", "4"]]))

body = "\n".join(paras)
# Then use make_section() and assemble the ZIP
```

### Page Size

```xml
<!-- A4 (default) -->
<hp:pagePr landscape="WIDELY" width="59528" height="84188">
  <hp:margin header="4252" footer="4252" gutter="0"
             left="8504" right="8504" top="5668" bottom="4252"/>
</hp:pagePr>

<!-- B4 JIS (Korean exam paper standard) -->
<hp:pagePr landscape="WIDELY" width="72851" height="103181">
  <hp:margin header="4252" footer="4252" gutter="0"
             left="8504" right="8504" top="7086" bottom="5668"/>
</hp:pagePr>
```

**Units:** 1 HWP unit = 1/7200 inch. 8504 units ≈ 30mm.

### Multi-Column Layout

```xml
<!-- 2-column newspaper style -->
<hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="2" sameSz="1" sameGap="2268"/>
```

### Fonts & Styles

```xml
<!-- Font declaration in header.xml -->
<hh:fontface lang="HANGUL" fontCnt="2">
  <hh:font id="0" face="신명중명조" type="TTF" isEmbedded="0"/>
  <hh:font id="1" face="나눔고딕" type="TTF" isEmbedded="0"/>
</hh:fontface>

<!-- Character property: 10pt body text -->
<hh:charPr id="0" height="1000" textColor="#000000">
  <hh:fontRef hangul="0" latin="0"/>
</hh:charPr>

<!-- Character property: 11pt bold -->
<hh:charPr id="2" height="1100" textColor="#000000">
  <hh:fontRef hangul="0" latin="0"/>
  <hh:bold/>
</hh:charPr>
```

**height units:** 100 = 1pt. `1000` = 10pt, `1100` = 11pt.

---

## HWP Equation Script

**CRITICAL: HWP equations are NOT LaTeX.** They use a completely different syntax.

### LaTeX → HWP Conversion Table

| LaTeX | HWP Equation Script | Notes |
|-------|---------------------|-------|
| `\frac{a}{b}` | `{a} over {b}` | Fraction |
| `\sqrt{x}` | `sqrt {x}` | Square root |
| `\text{cm}` | `"cm"` | Text in quotes |
| `\mathrm{log}` | `"log"` | Roman text |
| `\left(` | `left (` | Left delimiter |
| `\right)` | `right )` | Right delimiter |
| `\left\{` | `left lbrace` | Left curly brace |
| `\right\}` | `right rbrace` | Right curly brace |
| `\{` | `lbrace` | Standalone curly brace |
| `\}` | `rbrace` | Standalone curly brace |
| `\left\|` | `LEFT \|` | Absolute value (UPPERCASE LEFT/RIGHT) |
| `\right\|` | `RIGHT \|` | Absolute value |
| `\to` | `` `->`  `` | Arrow with backtick spacing |
| `\cdot` | `cdot` | Dot product (NOT bullet!) |
| `\cdots` | `` `cdots`  `` | Ellipsis with backtick spacing |
| `\overline{AB}` | `rm bar{AB}` | Line segment (rm for geometry) |
| `\vec{AB}` | `vec{rm AB it}` | Vector |
| `\triangle ABC` | `rm triangle ABC` | Triangle |
| `\angle ABC` | `rm ANGLE ABC` | Angle |
| `\quad` | `~~` | Wide space |
| `\qquad` | `~~~~` | Very wide space |
| `\,` `\;` `\:` `\!` | `~` | Thin space |
| `\alpha` | `alpha` | Greek (no backslash) |
| `\sin` | `` `sin`  `` | Function with backtick spacing |
| `\therefore` | `therefore~` | With trailing space |
| `\because` | `because~` | With trailing space |

### MathON Rules (Korean Math Standard)

**These rules are mandatory for Korean education documents (시험지, 교과서).**

HWP equations render letters in italic by default. Use `rm` (roman/upright) explicitly where required.

#### rm (Roman/Upright) — Use for:

| Target | Example | HWP Script |
|--------|---------|------------|
| Geometry vertices | A, B, C, P, Q | `rmA`, `rmB`, `rmABCD` |
| Triangle | △ABC | `rm triangle ABC` |
| Line segment | AB̄ | `rm bar{AB}` or `bar{rmPQ}` |
| Angle | ∠ABC | `rm ANGLE ABC` |
| Units | cm, kg, L | `` `rmcm `` (with `` ` `` spacing before) |
| Probability symbols | P, C, H, B, N, E | `{rmP}`, `{rmC}`, `{rmN}`, `{rmE}` |
| Congruence conditions | SSS, SAS | `rmSSS`, `rmSAS` |
| Numbers | 1, 2, 3.14 | `rm{1}`, `rm{3.14}` (auto-handled) |

#### it (Italic) — Default for:

| Target | Example | HWP Script |
|--------|---------|------------|
| Variables | a, b, x, y | `a`, `b`, `x`, `y` (no prefix needed) |
| Negative after inequality | x < -2 | `x<it-2` (use `it` instead of space) |
| Negative after limit arrow | lim(x→-2) | `lim_{x->it-2}` |

#### Mixed rm/it Patterns (Probability/Statistics)

| Expression | HWP Script |
|-----------|------------|
| Permutation ₙPᵣ | `_{it n}{rmP}_{it r}` |
| Combination ₙCᵣ | `_{it n}{rmC}_{it r}` |
| Probability P(X=r) | `{rmP}{it(X=r)}` |
| Binomial B(n,p) | `{rmB}{it(n,~p)}` |
| Normal N(m,σ²) | `{rmN}{it(m,~sigma^2)}` |
| Expected value E(X) | `{rmE}{it(X)}` |

### Spacing Rules

| Position | Symbol | Example |
|----------|--------|---------|
| Before units | `` ` `` | ``150`rmkg`` |
| After comma | `~` | `(a,~b)` |
| Around cdots | `` ` `` | `` `cdots` `` |
| After therefore/because | `~` | `therefore~a=b` |
| Ordered pairs | `~` | `(a,~b)` |
| Set elements | `~` | `LEFT { a,~b,~c RIGHT }` |
| Between points | `~` | `rmP,~Q` |
| Cases alignment | `~~` | `cases{ax+b~~&(x ne 1)}` |
| Coordinate comma | `` ` `` | ``rmA(-2,`` `-1)`` |
| Trig/log functions | `` ` `` | `` `sin` ``, `` `log` `` |

---

## HWPX File Structure

```
document.hwpx (ZIP)
├── META-INF/
│   └── container.xml          # OPF container (root file path)
├── Contents/
│   ├── content.hpf            # OPF package manifest (file list)
│   ├── header.xml             # Document settings (fonts, styles, paragraph properties)
│   ├── section0.xml           # Main content (paragraphs, equations, images, tables)
│   └── section1.xml           # Additional sections (optional)
├── BinData/                   # Image file storage
│   ├── image1.png
│   └── image2.png
├── Preview/
│   └── PrvText.txt            # Preview text
├── settings.xml               # Application settings
└── mimetype                   # "application/hwp+zip"
```

## XML Reference

### Namespaces

```
hp = http://www.hancom.co.kr/hwpml/2011/paragraph  (body content)
hh = http://www.hancom.co.kr/hwpml/2011/head       (header/styles)
hs = http://www.hancom.co.kr/hwpml/2011/section     (sections)
hc = http://www.hancom.co.kr/hwpml/2011/core        (core)
ha = http://www.hancom.co.kr/hwpml/2011/app          (application)
```

### Text Paragraph

```xml
<hp:p id="0" paraPrIDRef="0" styleIDRef="0"
     pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="1">
    <hp:t>문제 텍스트입니다.</hp:t>
  </hp:run>
</hp:p>
```

### Inline Equation in Text

**CRITICAL: An empty `<hp:t/>` MUST follow every equation element.**

```xml
<hp:p id="0" paraPrIDRef="0" styleIDRef="0"
     pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="1">
    <hp:t>이차방정식 </hp:t>
  </hp:run>
  <hp:run charPrIDRef="1">
    <hp:equation id="0" zOrder="0" numberingType="EQUATION"
        textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0"
        dropcapstyle="None" version="" baseLine="86" textColor="#000000"
        baseUnit="1100" lineMode="CHAR" font="HYhwpEQ">
        <hp:sz width="14000" widthRelTo="ABSOLUTE"
               height="3000" heightRelTo="ABSOLUTE" protect="0"/>
        <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1"
                allowOverlap="0" holdAnchorAndSO="0"
                vertRelTo="PAPER" horzRelTo="COLUMN"
                vertAlign="BOTTOM" horzAlign="LEFT"
                vertOffset="850" horzOffset="0"/>
        <hp:outMargin left="56" right="56" top="56" bottom="56"/>
        <hp:script>x^rm{2}+rm{3}x+rm{2}=rm{0}</hp:script>
    </hp:equation>
    <hp:t/>
  </hp:run>
  <hp:run charPrIDRef="1">
    <hp:t>을 풀어라.</hp:t>
  </hp:run>
</hp:p>
```

**Key equation attributes:**
- `width`: Equation width (HWP units, ~600 per character)
- `height`: Equation height (default 3000)
- `baseLine`: Baseline offset (86 = body text alignment)
- `treatAsChar="1"`: Inline equation
- `font="HYhwpEQ"`: HWP equation font (required)

### Tables

**CRITICAL: Table cells use `borderFillIDRef="3"` for standard solid-line borders.**

```xml
<hp:tbl id="0" zOrder="0" numberingType="TABLE"
    textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0"
    dropcapstyle="None" pageBreak="CELL" repeatHeader="1"
    rowCnt="2" colCnt="3" cellSpacing="0" borderFillIDRef="3" noAdjust="0">
  <hp:sz width="42000" widthRelTo="ABSOLUTE"
         height="3600" heightRelTo="ABSOLUTE" protect="0"/>
  <hp:pos treatAsChar="1" .../>
  <hp:outMargin left="0" right="0" top="0" bottom="0"/>
  <hp:inMargin left="0" right="0" top="0" bottom="0"/>
  <hp:tr>
    <hp:tc name="" header="0" hasMargin="0" protect="0" editable="0"
           dirty="0" borderFillIDRef="3">
      <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK"
                  vertAlign="CENTER" ...>
        <hp:p ...><hp:run charPrIDRef="0"><hp:t>Cell</hp:t></hp:run></hp:p>
      </hp:subList>
      <hp:cellAddr colAddr="0" rowAddr="0"/>
      <hp:cellSpan colSpan="1" rowSpan="1"/>
      <hp:cellSz width="14000" height="1800"/>
      <hp:cellMargin left="141" right="141" top="141" bottom="141"/>
    </hp:tc>
  </hp:tr>
</hp:tbl>
```

**Table width calculation:** Default total width 42000. Column widths = `total_width / n_cols`.

### Images

1. Add image to `BinData/` in ZIP
2. Register in `Contents/content.hpf`:
```xml
<opf:item id="img1" href="BinData/image1.png" media-type="image/png"/>
```
3. Reference in section XML:
```xml
<hp:pic id="0" zOrder="0" numberingType="PICTURE"
    textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES">
  <hp:imgRect>
    <hp:orgSz width="28000" height="28000"/>
    <hp:curSz width="0" height="0"/>
  </hp:imgRect>
  <hp:sz width="28000" widthRelTo="ABSOLUTE"
         height="28000" heightRelTo="ABSOLUTE" protect="0"/>
  <hp:pos treatAsChar="1" .../>
  <hp:img bright="0" contrast="0" effect="REAL_PIC" binaryItemIDRef="1"/>
</hp:pic>
```

### Endnotes (Solutions/Explanations)

Endnotes auto-place at document end — useful for exam solutions:

```xml
<hp:run charPrIDRef="1">
  <hp:ctrl>
    <hp:endNote number="1" suffixChar="41" instId="2000000000">
      <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="TOP">
        <hp:p ...>
          <hp:run charPrIDRef="0">
            <hp:ctrl>
              <hp:autoNum num="1" numType="ENDNOTE">
                <hp:autoNumFormat type="DIGIT"/>
              </hp:autoNum>
            </hp:ctrl>
          </hp:run>
          <hp:run charPrIDRef="2">
            <hp:t>정답: 42</hp:t>
          </hp:run>
        </hp:p>
      </hp:subList>
    </hp:endNote>
  </hp:ctrl>
</hp:run>
```

### Page Breaks & Column Breaks

```xml
<!-- Page break -->
<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="1" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0"><hp:t/></hp:run>
</hp:p>

<!-- Column break -->
<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="1" merged="0">
  <hp:run charPrIDRef="0"><hp:t/></hp:run>
</hp:p>
```

### content.hpf (OPF Package Manifest)

Register all files:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<opf:package xmlns:opf="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="1.0">
  <opf:manifest>
    <opf:item id="header" href="Contents/header.xml" media-type="application/xml"/>
    <opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/>
    <opf:item id="img1" href="BinData/image1.png" media-type="image/png"/>
  </opf:manifest>
  <opf:spine>
    <opf:itemref idref="header"/>
    <opf:itemref idref="section0"/>
  </opf:spine>
</opf:package>
```

---

## Editing Existing Documents

**Follow all 3 steps in order.**

### Step 1: Unpack

```bash
mkdir unpacked
unzip document.hwpx -d unpacked/
```

### Step 2: Edit XML

Edit files in `unpacked/Contents/`. Key files:
- `section0.xml` — main body content
- `header.xml` — fonts, styles, paragraph properties

**Use the Edit tool directly for string replacement. Do not write Python scripts.**

### Step 3: Repack

```bash
cd unpacked
zip -r ../output.hwpx . -x ".*"
```

**CRITICAL: The `mimetype` file must be the first entry and stored uncompressed:**
```bash
cd unpacked
zip -0 ../output.hwpx mimetype
zip -r ../output.hwpx . -x mimetype ".*"
```

---

## Converting Between Formats

### HWPX → Markdown

```bash
python scripts/reader.py document.hwpx output.md
```

Extracts text, equations (as LaTeX `$...$`), and images.

### Markdown → HWPX

```bash
python scripts/generator.py output.hwpx "Title" "Body text with $equations$"
```

Supports inline `$...$` equations auto-converted to HWP equation script.

### Conversion Quality Comparison

| Method | Text | Equations | Tables | Images | Formatting |
|--------|------|-----------|--------|--------|------------|
| hwp5txt (HWP5) | ✅ | ❌ | △ | ❌ | ❌ |
| hwp5html → pandoc | ✅ | △ | ✅ | ✅ | △ |
| LibreOffice → pandoc | ✅ | ❌ | ✅ | ✅ | △ |
| **reader.py (HWPX)** | ✅ | **✅ LaTeX** | ✅ | ✅ | △ |

**Best quality path:** HWP → 한글에서 HWPX 저장 → reader.py (equations preserved as LaTeX)

---

## Critical Rules

- **Empty `<hp:t/>` after equations** — Without it, equations won't display
- **UTF-8 encoding** — Use `html.escape()` for XML content
- **binaryItemIDRef matching** — Image refs must match content.hpf IDs
- **`<hp:colPr>` inside `<hp:secPr>`** — Multi-column fails otherwise
- **Equation width** — ~600 HWP units per character, minimum 3000, max ~18000 for 2-column
- **borderFillIDRef="3"** — Required for table cell borders to render
- **rm vs it** — Variables: italic (default). Geometry vertices, units, probability symbols: roman (`rm`)
- **`cdot` not `bullet`** — Always use `cdot` for dot product
- **Unit spacing** — Backtick (`` ` ``) between number and unit is mandatory
- **HWP equations are NOT LaTeX** — Completely different syntax; never mix them

## Common Mistakes & Debugging

1. **Equation not displaying**: Missing `<hp:t/>` after `<hp:equation>` element
2. **Korean text garbled**: XML encoding not UTF-8, or missing `html.escape()`
3. **Image not showing**: `binaryItemIDRef` doesn't match content.hpf `id`
4. **2-column layout broken**: `<hp:colPr>` not inside `<hp:secPr>`
5. **Page break not working**: Use `pageBreak="1"` attribute on `<hp:p>`
6. **Column break not working**: Use `columnBreak="1"` attribute on `<hp:p>`
7. **Table borders missing**: `borderFillIDRef` not set to "3" (solid line)
8. **Equation too wide**: Max ~18000 for 2-column, ~40000 for single column
9. **rm/it confusion**: Variables are italic, geometry vertices/units/probability are roman
10. **Bullet instead of cdot**: Use `cdot` for dot product, never `bullet`

## Dependencies

- **Python 3.8+**: Required for scripts
- **pyhwp**: `pip install pyhwp` (HWP5 binary reading only)
- **LibreOffice**: Optional, for .hwp → .docx conversion
- **pandoc**: Optional, for HTML → Markdown conversion
