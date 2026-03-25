#!/usr/bin/env python3
"""
HWPX 문서 생성기
사용법: python generator.py output.hwpx "문서 제목" "본문 내용" [A4|B4] [1|2]

실제 한글 프로그램에서 생성한 빈 문서를 기반으로 section만 교체하는 방식.
표, 수식(HWP equation script) 지원.
"""
import zipfile
import html as html_mod
import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).parent


def read_base(name: str) -> str:
    return (TEMPLATES / f"base-{name}").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 수식 (HWP Equation Script)
# ---------------------------------------------------------------------------

_eq_counter = 0

def _next_eq_id() -> int:
    global _eq_counter
    _eq_counter += 1
    return _eq_counter

def _match_brace(s: str, start: int) -> str:
    """중첩 중괄호를 지원하는 매칭. s[start]가 '{'일 때 대응하는 '}'까지 추출."""
    if start >= len(s) or s[start] != '{':
        return ''
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '{': depth += 1
        elif s[i] == '}': depth -= 1
        if depth == 0:
            return s[start+1:i]
    return s[start+1:]


def latex_to_hwp(latex: str) -> str:
    """LaTeX → HWP equation script 변환. 중첩 중괄호 지원."""
    s = latex.strip().strip("$")

    # 반복 적용 (중첩 처리)
    for _ in range(5):
        # \frac{...}{...} → {...} over {...}
        m = re.search(r'\\frac\s*\{', s)
        if m:
            num = _match_brace(s, m.end()-1)
            rest_start = m.end() + len(num)  # } 다음
            m2 = re.search(r'\{', s[rest_start:])
            if m2:
                den = _match_brace(s, rest_start + m2.start())
                end_pos = rest_start + m2.start() + len(den) + 2
                s = s[:m.start()] + '{' + num + '} over {' + den + '}' + s[end_pos:]
                continue

        # \sqrt{...} → sqrt {...}
        m = re.search(r'\\sqrt\s*\{', s)
        if m:
            content = _match_brace(s, m.end()-1)
            end_pos = m.end() + len(content)
            s = s[:m.start()] + 'sqrt {' + content + '}' + s[end_pos:]
            continue

        # \text{...} → "..."
        m = re.search(r'\\text\s*\{', s)
        if m:
            content = _match_brace(s, m.end()-1)
            end_pos = m.end() + len(content)
            s = s[:m.start()] + '"' + content + '"' + s[end_pos:]
            continue

        # \mathrm{...} → "..."
        m = re.search(r'\\mathrm\s*\{', s)
        if m:
            content = _match_brace(s, m.end()-1)
            end_pos = m.end() + len(content)
            s = s[:m.start()] + '"' + content + '"' + s[end_pos:]
            continue

        break

    # 단순 치환
    s = re.sub(r'\\left\s*\\\{', 'left lbrace ', s)
    s = re.sub(r'\\right\s*\\\}', 'right rbrace ', s)
    s = re.sub(r'\\left\s*', 'left ', s)
    s = re.sub(r'\\right\s*', 'right ', s)
    s = s.replace('\\{', 'lbrace ').replace('\\}', 'rbrace ')
    s = re.sub(r'\\to(?![a-z])', 'rightarrow ', s)
    s = s.replace('\\quad', '~~').replace('\\qquad', '~~~~')
    s = re.sub(r'\\[,;:!]', '~', s)
    # 나머지 \command → command
    s = re.sub(r'\\([a-zA-Z]+)', r'\1 ', s)
    # 숫자 → rm{...}, 괄호/점/쉼표 → rm{...}
    # +, -, = 등 연산자는 HWP가 자동으로 로마체 처리하므로 rm 불필요
    s = re.sub(r'(\d+\.?\d*)', r' rm{\1} ', s)
    s = re.sub(r'([().,])', r' rm{\1} ', s)
    # 연속 rm 합치기: rm{1} rm{.} rm{5} → rm{1.5}
    for _ in range(5):
        s = re.sub(r'rm\{([^}]*)\}\s*rm\{([^}]*)\}', r'rm{\1\2}', s)
    return re.sub(r'\s+', ' ', s).strip()


def build_equation(script: str, width: int = 14000) -> str:
    """HWP equation XML."""
    eid = _next_eq_id()
    return (f'<hp:equation id="{eid}" zOrder="0" numberingType="EQUATION" '
            f'textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
            f'dropcapstyle="None" version="" baseLine="86" textColor="#000000" '
            f'baseUnit="1100" lineMode="CHAR" font="HYhwpEQ">'
            f'<hp:sz width="{width}" widthRelTo="ABSOLUTE" '
            f'height="3000" heightRelTo="ABSOLUTE" protect="0"/>'
            f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" '
            f'allowOverlap="0" holdAnchorAndSO="0" '
            f'vertRelTo="PAPER" horzRelTo="COLUMN" '
            f'vertAlign="BOTTOM" horzAlign="LEFT" '
            f'vertOffset="850" horzOffset="0"/>'
            f'<hp:outMargin left="56" right="56" top="56" bottom="56"/>'
            f'<hp:script>{html_mod.escape(script)}</hp:script>'
            f'</hp:equation>')


def build_equation_para(latex: str) -> str:
    """LaTeX 수식을 독립 paragraph로."""
    script = latex_to_hwp(latex)
    width = max(len(script) * 600, 3000)
    eq_xml = build_equation(script, min(width, 40000))
    return (f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="0">{eq_xml}<hp:t/></hp:run></hp:p>')


# ---------------------------------------------------------------------------
# 표 (Table)
# ---------------------------------------------------------------------------

def build_table(rows: list[list[str]], col_widths: list[int] | None = None) -> str:
    """2D 배열 → HWP 표 XML.
    rows: [["셀1", "셀2"], ["셀3", "셀4"]]
    col_widths: 각 열 너비 (HWP 단위). None이면 균등 분배.
    """
    n_rows = len(rows)
    n_cols = max(len(r) for r in rows) if rows else 0
    if n_cols == 0:
        return ''

    total_width = 42000  # A4 본문 영역 대략
    if col_widths is None:
        col_widths = [total_width // n_cols] * n_cols

    row_height = 1200  # 기본 행 높이

    # 열 정의
    cols_xml = ''.join(f'<hp:tr><hp:tc colAddr="{c}" colSpan="1" rowSpan="1" width="{col_widths[c]}" '
                       for c in range(n_cols))
    # 전체 표 생성
    cell_xmls = []
    for r, row in enumerate(rows):
        for c in range(n_cols):
            cell_text = html_mod.escape(row[c]) if c < len(row) else ''
            cell_xmls.append(
                f'<hp:tc colAddr="{c}" rowAddr="{r}" colSpan="1" rowSpan="1" '
                f'width="{col_widths[c % len(col_widths)]}" height="{row_height}" header="0" '
                f'borderFillIDRef="1" '
                f'editableAtFormMode="0">'
                f'<hp:cellMargin left="170" right="170" top="57" bottom="57"/>'
                f'<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" '
                f'vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" '
                f'textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
                f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                f'<hp:run charPrIDRef="0"><hp:t>{cell_text}</hp:t></hp:run></hp:p>'
                f'</hp:subList>'
                f'</hp:tc>'
            )

    # 행으로 묶기
    row_xmls = []
    idx = 0
    for r in range(n_rows):
        cells = ''.join(cell_xmls[idx:idx + n_cols])
        row_xmls.append(f'<hp:tr><hp:trPr height="{row_height}"/>{cells}</hp:tr>')
        idx += n_cols

    table_xml = (
        f'<hp:tbl id="0" zOrder="0" numberingType="TABLE" '
        f'textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" '
        f'dropcapstyle="None" pageBreak="CELL" repeatHeader="1" rowCount="{n_rows}" colCount="{n_cols}" '
        f'cellSpacing="0" borderFillIDRef="1">'
        f'<hp:sz width="{total_width}" widthRelTo="ABSOLUTE" height="{row_height * n_rows}" heightRelTo="ABSOLUTE" protect="0"/>'
        f'<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
        f'vertRelTo="PAPER" horzRelTo="COLUMN" vertAlign="BOTTOM" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
        f'<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
        f'<hp:inMargin left="170" right="170" top="57" bottom="57"/>'
        + ''.join(row_xmls)
        + '</hp:tbl>'
    )

    return (f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="0">{table_xml}<hp:t/></hp:run></hp:p>')


# ---------------------------------------------------------------------------
# 단락 (Paragraph)
# ---------------------------------------------------------------------------

def build_text_para(text: str) -> str:
    """텍스트 paragraph. $...$는 인라인 수식으로 변환."""
    parts = re.split(r'(\$[^$]+\$)', text)
    runs = []
    for part in parts:
        if part.startswith('$') and part.endswith('$'):
            script = latex_to_hwp(part[1:-1])
            width = max(len(script) * 600, 3000)
            eq = build_equation(script, min(width, 18000))
            runs.append(f'<hp:run charPrIDRef="0">{eq}<hp:t/></hp:run>')
        elif part:
            runs.append(f'<hp:run charPrIDRef="0"><hp:t>{html_mod.escape(part)}</hp:t></hp:run>')

    return (f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            + ''.join(runs) + '</hp:p>')


def build_empty_para() -> str:
    return ('<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            '<hp:run charPrIDRef="0"><hp:t/></hp:run></hp:p>')


# ---------------------------------------------------------------------------
# 섹션 조립
# ---------------------------------------------------------------------------

def make_section(title: str, body: str, paper: str = "A4", columns: int = 1) -> str:
    """기존 section에서 secPr 추출, 용지/단수 교체, 본문 조립."""
    global _eq_counter
    _eq_counter = 0

    base = read_base("section.xml")

    first_p_match = re.search(r'(<hp:p[^>]*>.*?</hp:p>)', base, re.DOTALL)
    first_p = first_p_match.group(1) if first_p_match else ''

    if paper == "B4":
        first_p = re.sub(r'width="59528"', 'width="72851"', first_p)
        first_p = re.sub(r'height="84188"', 'height="103181"', first_p)
        first_p = re.sub(r'top="5668"', 'top="7086"', first_p)
        first_p = re.sub(r'bottom="4252"', 'bottom="5668"', first_p)

    if columns > 1:
        first_p = first_p.replace('colCount="1"', f'colCount="{columns}"')

    root_match = re.search(r'(<hs:sec[^>]+>)', base)
    root_tag = root_match.group(1) if root_match else ''
    xml_decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'

    paras = []
    paras.append(build_text_para(title))
    paras.append(build_empty_para())
    for line in body.split("\n"):
        line = line.strip()
        if line:
            paras.append(build_text_para(line))

    return f'{xml_decl}{root_tag}{first_p}{"".join(paras)}</hs:sec>'


# ---------------------------------------------------------------------------
# 공개 API (스킬에서 import 가능)
# ---------------------------------------------------------------------------

def generate_hwpx(output_path: str, title: str, body: str,
                  paper: str = "A4", columns: int = 1):
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", read_base("mimetype"), compress_type=zipfile.ZIP_STORED)
        zf.writestr("version.xml", read_base("version.xml"))
        zf.writestr("settings.xml", read_base("settings.xml"))
        zf.writestr("META-INF/container.xml", read_base("container.xml"))
        zf.writestr("META-INF/container.rdf", read_base("container.rdf"))
        zf.writestr("META-INF/manifest.xml", read_base("manifest.xml"))
        zf.writestr("Contents/content.hpf", read_base("content.hpf"))
        zf.writestr("Contents/header.xml", read_base("header.xml"))
        zf.writestr("Contents/section0.xml", make_section(title, body, paper, columns))
        zf.writestr("Preview/PrvText.txt", title)

    print(f"생성 완료: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python generator.py output.hwpx '제목' '본문' [A4|B4] [1|2]")
        print("  본문에 $수식$을 넣으면 HWP 수식으로 변환됩니다.")
        sys.exit(1)

    out = sys.argv[1]
    t = sys.argv[2]
    b = sys.argv[3] if len(sys.argv) > 3 else ""
    p = sys.argv[4] if len(sys.argv) > 4 else "A4"
    c = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    generate_hwpx(out, t, b, p, c)
