#!/usr/bin/env python3
"""
HWPX 문서 생성기 — 최소 작동 예제
사용법: python generator.py output.hwpx "문서 제목" "본문 내용"
"""
import zipfile
import sys
from pathlib import Path

TEMPLATES = Path(__file__).parent


def read_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


HEADER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<hh:head xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head"
         xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core"
         xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
         version="1.5" secCnt="1">
  <hh:beginNum page="1" footnote="1" endnote="1" pic="1" tbl="1" equation="1"/>
  <hh:refList>
    <hh:fontfaces itemCnt="1">
      <hh:fontface lang="HANGUL" fontCnt="1">
        <hh:font id="0" face="\\ub098\\ub214\\uace0\\ub515" type="TTF" isEmbedded="0"/>
      </hh:fontface>
    </hh:fontfaces>
    <hh:borderFills itemCnt="1">
      <hh:borderFill id="1" threeD="0" shadow="0" centerLine="NONE" breakCellSeparateLine="0">
        <hh:slash type="NONE" Crooked="0" isCounter="0"/>
        <hh:backSlash type="NONE" Crooked="0" isCounter="0"/>
        <hh:leftBorder type="NONE" width="0.1 mm" color="#000000"/>
        <hh:rightBorder type="NONE" width="0.1 mm" color="#000000"/>
        <hh:topBorder type="NONE" width="0.1 mm" color="#000000"/>
        <hh:bottomBorder type="NONE" width="0.1 mm" color="#000000"/>
        <hh:diagonal type="SOLID" width="0.1 mm" color="#000000"/>
      </hh:borderFill>
    </hh:borderFills>
    <hh:charProperties itemCnt="1">
      <hh:charPr id="0" height="1000" textColor="#000000" shadeColor="none"
                 useFontSpace="0" useKerning="0" symMark="NONE" borderFillIDRef="1">
        <hh:fontRef hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:ratio hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
        <hh:spacing hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:relSz hangul="100" latin="100" hanja="100" japanese="100" other="100" symbol="100" user="100"/>
        <hh:offset hangul="0" latin="0" hanja="0" japanese="0" other="0" symbol="0" user="0"/>
        <hh:underline type="NONE" shape="SOLID" color="#000000"/>
        <hh:strikeout shape="NONE" color="#000000"/>
        <hh:outline type="NONE"/>
        <hh:shadow type="NONE" color="#C0C0C0" offsetX="10" offsetY="10"/>
      </hh:charPr>
    </hh:charProperties>
    <hh:tabProperties itemCnt="1">
      <hh:tabPr id="0" autoTabLeft="0" autoTabRight="0"/>
    </hh:tabProperties>
    <hh:numberings itemCnt="0"/>
    <hh:bullets itemCnt="0"/>
    <hh:paraProperties itemCnt="1">
      <hh:paraPr id="0" tabPrIDRef="0" condense="0" fontLineHeight="0"
                 snapToGrid="1" suppressLineNumbers="0" checked="0">
        <hh:align horizontal="LEFT" vertical="BASELINE"/>
        <hh:heading type="NONE" idRef="0" level="0"/>
        <hh:breakSetting breakLatinWord="KEEP_WORD" breakNonLatinWord="KEEP_WORD"
                         widowOrphan="0" keepWithNext="0" keepLines="0"
                         pageBreakBefore="0" lineWrap="BREAK"/>
        <hh:autoSpacing eAsianEng="0" eAsianNum="0"/>
      </hh:paraPr>
    </hh:paraProperties>
    <hh:styles itemCnt="1">
      <hh:style id="0" type="PARA" name="\\ubc14\\ud0d5\\uae00" engName="Normal"
                paraPrIDRef="0" charPrIDRef="0" nextStyleIDRef="0"
                langID="1042" lockForm="0"/>
    </hh:styles>
  </hh:refList>
</hh:head>"""


def make_section(title: str, body: str, paper: str = "A4", columns: int = 1) -> str:
    """섹션 XML 생성. paper: 'A4' | 'B4', columns: 1 | 2"""
    if paper == "B4":
        page_pr = '<hp:pagePr landscape="WIDELY" width="72851" height="103181" gutterType="LEFT_ONLY">' \
                  '<hp:margin header="4252" footer="4252" gutter="0" left="8504" right="8504" top="7086" bottom="5668"/>' \
                  '</hp:pagePr>'
    else:
        page_pr = '<hp:pagePr landscape="WIDELY" width="59528" height="84188" gutterType="LEFT_ONLY">' \
                  '<hp:margin header="4252" footer="4252" gutter="0" left="8504" right="8504" top="5668" bottom="4252"/>' \
                  '</hp:pagePr>'

    col_type = "NEWSPAPER" if columns > 1 else "NONE"

    # XML escape
    import html
    title_esc = html.escape(title)
    body_esc = html.escape(body)

    paragraphs = []
    # Title
    paragraphs.append(f'''  <hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0"><hp:t>{title_esc}</hp:t></hp:run>
  </hp:p>''')
    # Empty line
    paragraphs.append('''  <hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0"><hp:t/></hp:run>
  </hp:p>''')
    # Body paragraphs
    for line in body_esc.split("\\n"):
        if line.strip():
            paragraphs.append(f'''  <hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0"><hp:t>{line}</hp:t></hp:run>
  </hp:p>''')

    body_xml = "\n".join(paragraphs)

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<hs:sec xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app"
        xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
        xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"
        xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core"
        xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head">
  <hp:p id="0" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
    <hp:run charPrIDRef="0">
      <hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="0" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0">
        <hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/>
        <hp:colPr id="" type="{col_type}" layout="LEFT" colCount="{columns}" sameSz="1" sameGap="2268"/>
        <hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>
        {page_pr}
      </hp:secPr>
    </hp:run>
  </hp:p>
{body_xml}
</hs:sec>'''


def generate_hwpx(output_path: str, title: str, body: str,
                  paper: str = "A4", columns: int = 1):
    """HWPX 파일 생성"""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype은 압축 없이
        zf.writestr("mimetype", read_template("mimetype"), compress_type=zipfile.ZIP_STORED)
        zf.writestr("version.xml", read_template("version.xml"))
        zf.writestr("settings.xml", read_template("settings.xml"))
        zf.writestr("META-INF/container.xml", read_template("container.xml"))
        zf.writestr("META-INF/manifest.xml", read_template("manifest.xml"))
        zf.writestr("Contents/content.hpf", read_template("content.hpf"))
        zf.writestr("Contents/header.xml", HEADER_XML)
        zf.writestr("Contents/section0.xml", make_section(title, body, paper, columns))

    print(f"생성 완료: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python generator.py output.hwpx '제목' '본문'")
        sys.exit(1)

    out = sys.argv[1]
    t = sys.argv[2]
    b = sys.argv[3] if len(sys.argv) > 3 else ""
    generate_hwpx(out, t, b)
