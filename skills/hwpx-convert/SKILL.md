---
name: hwpx-convert
description: HWPX를 Markdown으로, 또는 Markdown을 HWPX로 변환합니다. 한글 문서 데이터화, 문서 포맷 변환에 사용합니다.
allowed-tools: Read, Write, Bash, Grep, Glob
---

# HWPX ↔ Markdown 변환

$ARGUMENTS

## HWPX → Markdown

### 처리 절차

1. **HWPX 압축 해제** (ZIP)
2. **section XML 파싱** — `<hp:t>` 텍스트, `<hp:script>` 수식 추출
3. **수식 변환** — HWP equation script → LaTeX (`$...$`)
4. **이미지 추출** — BinData/ → 별도 디렉토리로 복사
5. **표 변환** — `<hp:tbl>` → Markdown 표
6. **구조화** — 단락, 제목, 목록으로 정리

### 수식 변환 (HWP → LaTeX)

```
{a} over {b}        → \frac{a}{b}
sqrt {x}            → \sqrt{x}
"텍스트"            → \text{텍스트}
left ( ... right )  → \left( ... \right)
lbrace ... rbrace   → \{ ... \}
rightarrow          → \to
rm{3.14}            → 3.14
alpha, beta, theta  → \alpha, \beta, \theta
sum, int, prod      → \sum, \int, \prod
x^rm{2}             → x^{2}
x_rm{1}             → x_{1}
~~                  → \quad
~~~~                → \qquad
```

### Node.js 변환 스크립트 템플릿

```javascript
const JSZip = require("jszip");
const fs = require("fs");

async function hwpxToMarkdown(hwpxPath) {
  const data = fs.readFileSync(hwpxPath);
  const zip = await JSZip.loadAsync(data);

  // section XML 읽기
  const sectionXml = await zip.file("Contents/section0.xml")?.async("text");
  if (!sectionXml) throw new Error("section0.xml not found");

  // 텍스트 추출 (정규식 기반)
  const texts = [];
  const textRegex = /<hp:t>(.*?)<\/hp:t>/gs;
  const eqRegex = /<hp:script>(.*?)<\/hp:script>/gs;

  // ... 파싱 로직
  return markdown;
}
```

### Python 변환 스크립트 템플릿

```python
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def hwpx_to_markdown(hwpx_path: str) -> str:
    ns = {
        'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    }

    with zipfile.ZipFile(hwpx_path) as zf:
        with zf.open('Contents/section0.xml') as f:
            tree = ET.parse(f)

    root = tree.getroot()
    lines = []

    for p in root.iter(f'{{{ns["hp"]}}}p'):
        line_parts = []
        for run in p.iter(f'{{{ns["hp"]}}}run'):
            # 텍스트
            for t in run.iter(f'{{{ns["hp"]}}}t'):
                if t.text:
                    line_parts.append(t.text)
            # 수식
            for eq in run.iter(f'{{{ns["hp"]}}}script'):
                if eq.text:
                    latex = hwp_script_to_latex(eq.text)
                    line_parts.append(f'${latex}$')
        if line_parts:
            lines.append(''.join(line_parts))

    return '\n\n'.join(lines)
```

## Markdown → HWPX

### 처리 절차

1. **Markdown 파싱** — 제목, 단락, 수식, 이미지, 표 분리
2. **수식 변환** — LaTeX → HWP equation script
3. **XML 생성** — header.xml + section0.xml
4. **이미지 처리** — Markdown 이미지 → BinData/
5. **ZIP 패키징** — HWPX 파일로 압축

### LaTeX → HWP 변환

```
\frac{a}{b}          → {a} over {b}
\sqrt{x}             → sqrt {x}
\text{cm}            → "cm"
\left( ... \right)   → left ( ... right )
\{ ... \}            → lbrace ... rbrace
\to                  → rightarrow
\alpha, \beta        → alpha, beta (백슬래시 제거)
숫자 3.14            → rm{3.14}
괄호 (, ), =, +, -   → rm{(}, rm{)}, rm{=}, rm{+}, rm{-}
```

## 대량 변환 (배치 처리)

```bash
# 디렉토리 내 모든 HWPX 파일을 Markdown으로 변환
for f in *.hwpx; do
  echo "변환 중: $f"
  node convert.js "$f" "${f%.hwpx}.md"
done
```

## HWP → Markdown (가장 흔한 사용 사례)

HWP5 바이너리를 직접 Markdown으로 변환하는 경우:

```bash
# 방법 1: pyhwp (텍스트만, 수식 제한적)
pip install pyhwp
hwp5txt document.hwp > output.txt
# 텍스트를 기반으로 Markdown 정리 필요

# 방법 2: pyhwp HTML → Markdown (수식 일부 보존)
hwp5html document.hwp --output output.html
# html2text 또는 pandoc으로 변환
pandoc output.html -t markdown -o output.md

# 방법 3: LibreOffice → DOCX → Markdown
libreoffice --headless --convert-to docx document.hwp
pandoc document.docx -t markdown -o output.md

# 방법 4: 대량 배치 (디렉토리 전체)
for f in *.hwp; do
  hwp5txt "$f" > "${f%.hwp}.md"
  echo "변환: $f → ${f%.hwp}.md"
done
```

**각 방법의 품질:**

| 방법 | 텍스트 | 수식 | 표 | 이미지 | 서식 |
|------|--------|------|-----|--------|------|
| hwp5txt | ✅ | ❌ | △ | ❌ | ❌ |
| hwp5html → pandoc | ✅ | △ | ✅ | ✅ | △ |
| LibreOffice → pandoc | ✅ | ❌ | ✅ | ✅ | △ |
| HWPX reader.py | ✅ | ✅ LaTeX | ✅ | ✅ | △ |

**최고 품질 경로:** HWP → 한글에서 HWPX 저장 → reader.py로 Markdown 변환 (수식이 LaTeX로 보존됨)

## HWP → HWPX 직접 변환 (현실적 제약)

**HWP5(.hwp) → HWPX(.hwpx) 직접 변환 CLI 도구는 존재하지 않습니다.**

| 방법 | 서식 보존 | 수식 보존 | 자동화 | 비고 |
|------|----------|----------|--------|------|
| 한글 프로그램 "다른 이름으로 저장" | ✅ 완벽 | ✅ | ❌ 수동 | Windows 전용 |
| 한글 매크로/ActiveX 자동화 | ✅ 완벽 | ✅ | ✅ | Windows + 한글 설치 필수 |
| pyhwp → 텍스트 → HWPX 재생성 | ❌ 손실 | △ 부분 | ✅ | 크로스플랫폼 |
| LibreOffice → DOCX | △ 부분 | ❌ | ✅ | HWPX 출력 미지원 |

**권장 경로:**
- 소량: 한글 프로그램에서 수동 변환
- 대량 자동화 (Windows): 한글 ActiveX 매크로
  ```python
  # Windows에서 한글 프로그램 자동화 (win32com)
  import win32com.client
  hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
  hwp.Open("input.hwp")
  hwp.SaveAs("output.hwpx", "HWPX")
  hwp.Quit()
  ```
- 대량 자동화 (Mac/Linux): pyhwp로 텍스트 추출 → HWPX 재생성 (서식 손실 감수)

## 주의사항

- HWP5 바이너리(.hwp)와 HWPX(.hwpx)는 완전히 다른 포맷
- HWP5는 OLE2 compound document, HWPX는 ZIP+XML (Open XML 계열)
- 한글 2014 이상에서 HWPX 지원, 이전 버전은 HWP5만
- 공공기관 문서는 대부분 HWP5 → pyhwp 또는 한글 프로그램 필요
- pyhwp는 HWP5 읽기 전용, 쓰기 미지원
- LibreOffice는 HWP 열기 가능하나 수식/서식 손실 큼
