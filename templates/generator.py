#!/usr/bin/env python3
"""
HWPX 문서 생성기
사용법: python generator.py output.hwpx "문서 제목" "본문 내용" [A4|B4] [1|2]
"""
import zipfile
import html
import sys
from pathlib import Path

TEMPLATES = Path(__file__).parent


def read_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def read_template_bytes(name: str) -> bytes:
    return (TEMPLATES / name).read_bytes()


def make_section(title: str, body: str, paper: str = "A4", columns: int = 1) -> str:
    if paper == "B4":
        page_pr = ('<hp:pagePr landscape="WIDELY" width="72851" height="103181" gutterType="LEFT_ONLY">'
                   '<hp:margin header="4252" footer="4252" gutter="0" left="8504" right="8504" top="7086" bottom="5668"/>'
                   '</hp:pagePr>')
    else:
        page_pr = ('<hp:pagePr landscape="WIDELY" width="59528" height="84188" gutterType="LEFT_ONLY">'
                   '<hp:margin header="4252" footer="4252" gutter="0" left="8504" right="8504" top="5668" bottom="4252"/>'
                   '</hp:pagePr>')

    col_type = "NEWSPAPER" if columns > 1 else "NONE"
    title_esc = html.escape(title)
    body_esc = html.escape(body)

    paragraphs = []
    paragraphs.append(f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                      f'<hp:run charPrIDRef="0"><hp:t>{title_esc}</hp:t></hp:run></hp:p>')
    paragraphs.append('<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                      '<hp:run charPrIDRef="0"><hp:t/></hp:run></hp:p>')
    for line in body_esc.split("\\n"):
        line = line.strip()
        if line:
            paragraphs.append(f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                              f'<hp:run charPrIDRef="0"><hp:t>{line}</hp:t></hp:run></hp:p>')

    body_xml = "".join(paragraphs)

    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
            f'<hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
            f'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
            f'xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" '
            f'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
            f'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" '
            f'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" '
            f'xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar">'
            f'<hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="0">'
            f'<hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="0" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0">'
            f'<hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/>'
            f'<hp:colPr id="" type="{col_type}" layout="LEFT" colCount="{columns}" sameSz="1" sameGap="2268"/>'
            f'<hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>'
            f'{page_pr}'
            f'</hp:secPr>'
            f'</hp:run></hp:p>'
            f'{body_xml}'
            f'</hs:sec>')


def generate_hwpx(output_path: str, title: str, body: str,
                  paper: str = "A4", columns: int = 1):
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/hwp+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("version.xml", read_template("version-real.xml"))
        zf.writestr("settings.xml", read_template("settings-real.xml"))
        zf.writestr("META-INF/container.xml", read_template("container-real.xml"))
        zf.writestr("META-INF/container.rdf", read_template("container-real.rdf"))
        zf.writestr("META-INF/manifest.xml", read_template("manifest-real.xml"))
        zf.writestr("Contents/content.hpf", read_template("content-real.hpf"))
        zf.writestr("Contents/header.xml", read_template("header-real.xml"))
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
