#!/usr/bin/env python3
"""
HWPX 문서 생성기
사용법: python generator.py output.hwpx "문서 제목" "본문 내용" [A4|B4] [1|2]

실제 한글 프로그램에서 생성한 빈 문서를 기반으로 section만 교체하는 방식.
"""
import zipfile
import html as html_mod
import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).parent


def read_base(name: str) -> str:
    return (TEMPLATES / f"base-{name}").read_text(encoding="utf-8")


def read_base_bytes(name: str) -> bytes:
    return (TEMPLATES / f"base-{name}").read_bytes()


def make_section(title: str, body: str, paper: str = "A4", columns: int = 1) -> str:
    """기존 section에서 secPr만 추출하고, 본문을 교체."""
    base = read_base("section.xml")

    # secPr 블록 추출
    match = re.search(r'(<[^>]*:secPr[^>]*>.*?</[^>]*:secPr>)', base, re.DOTALL)
    secpr = match.group(1) if match else ''

    # 용지 크기 교체
    if paper == "B4":
        secpr = re.sub(r'width="59528"', 'width="72851"', secpr)
        secpr = re.sub(r'height="84188"', 'height="103181"', secpr)
        secpr = re.sub(r'top="5668"', 'top="7086"', secpr)
        secpr = re.sub(r'bottom="4252"', 'bottom="5668"', secpr)

    # 단수 교체
    if columns > 1:
        secpr = re.sub(r'type="NONE"', 'type="NEWSPAPER"', secpr)
        secpr = re.sub(r'colCount="1"', f'colCount="{columns}"', secpr)

    # 루트 태그 + 네임스페이스 추출
    root_match = re.match(r'(<[^>]+>)', base)
    root_tag = root_match.group(1) if root_match else ''
    close_match = re.search(r'(</[^>]+>)\s*$', base)
    close_tag = close_match.group(1) if close_match else '</hs:sec>'

    # 본문 생성
    title_esc = html_mod.escape(title)
    paras = []
    paras.append(f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                 f'<hp:run charPrIDRef="0"><hp:t>{title_esc}</hp:t></hp:run></hp:p>')
    paras.append('<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                 '<hp:run charPrIDRef="0"><hp:t/></hp:run></hp:p>')
    for line in body.split("\n"):
        line = line.strip()
        if line:
            line_esc = html_mod.escape(line)
            paras.append(f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                         f'<hp:run charPrIDRef="0"><hp:t>{line_esc}</hp:t></hp:run></hp:p>')

    body_xml = "".join(paras)

    return (f'{root_tag}'
            f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="0">{secpr}</hp:run></hp:p>'
            f'{body_xml}'
            f'{close_tag}')


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
        sys.exit(1)

    out = sys.argv[1]
    t = sys.argv[2]
    b = sys.argv[3] if len(sys.argv) > 3 else ""
    p = sys.argv[4] if len(sys.argv) > 4 else "A4"
    c = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    generate_hwpx(out, t, b, p, c)
