---
name: hwpx-read
description: HWP/HWPX 파일을 읽고 텍스트, 수식, 이미지, 표를 추출합니다. 한글 문서 분석이 필요할 때 사용합니다.
allowed-tools: Read, Bash, Grep, Glob
---

# HWPX 문서 읽기

HWPX 파일에서 내용을 추출합니다.

대상 파일: $ARGUMENTS

## 처리 절차

### 1단계: 파일 형식 확인

HWPX는 ZIP 아카이브입니다. 먼저 압축을 풀어 구조를 확인하세요.

```bash
# HWPX 파일 구조 확인
unzip -l "$FILE"

# 임시 디렉토리에 압축 해제
TMPDIR=$(mktemp -d)
unzip -o "$FILE" -d "$TMPDIR"
```

**HWP(구 바이너리 포맷)인 경우:**
- HWP5 바이너리는 직접 파싱 불가
- `hwp5txt` 도구 필요: `pip install pyhwp && hwp5txt "$FILE"`
- 또는 LibreOffice로 변환: `libreoffice --headless --convert-to docx "$FILE"`

### 2단계: 섹션 XML 파싱

본문은 `Contents/section0.xml`에 있습니다.

```bash
cat "$TMPDIR/Contents/section0.xml"
```

### 3단계: 텍스트 추출

XML에서 텍스트 노드를 추출합니다:
- `<hp:t>텍스트</hp:t>` — 일반 텍스트
- `<hp:script>수식</hp:script>` — HWP 수식 (equation script)
- `<hp:img binaryItemIDRef="N"/>` — 이미지 참조 (BinData/ 디렉토리)

### 4단계: 수식 변환

HWP equation script → LaTeX 변환:

| HWP Script | LaTeX |
|-----------|-------|
| `{a} over {b}` | `\frac{a}{b}` |
| `sqrt {x}` | `\sqrt{x}` |
| `"cm"` | `\text{cm}` |
| `left (` | `\left(` |
| `right )` | `\right)` |
| `lbrace` | `\{` |
| `rbrace` | `\}` |
| `rightarrow` | `\to` |
| `~~` | `\quad` |
| `alpha`, `beta`, `theta` | `\alpha`, `\beta`, `\theta` |
| `rm{3.14}` | `3.14` (숫자는 로마체) |
| `sum`, `int`, `prod` | `\sum`, `\int`, `\prod` |

### 5단계: 이미지 추출

```bash
# BinData 디렉토리에서 이미지 파일 복사
ls "$TMPDIR/BinData/"
```

### 출력 형식

Markdown으로 정리하여 출력합니다:
- 텍스트는 그대로
- 수식은 `$...$` (인라인) 또는 `$$...$$` (블록)
- 이미지는 `![설명](경로)`
- 표는 Markdown 표 형식

## XML 네임스페이스 참조

```
hp = http://www.hancom.co.kr/hwpml/2011/paragraph  (본문)
hh = http://www.hancom.co.kr/hwpml/2011/head       (헤더)
hs = http://www.hancom.co.kr/hwpml/2011/section     (섹션)
hc = http://www.hancom.co.kr/hwpml/2011/core        (코어)
```

## 핵심 XML 요소

- `<hp:p>` — 단락 (paragraph)
- `<hp:run>` — 텍스트 런 (글자 속성 단위)
- `<hp:t>` — 텍스트 내용
- `<hp:equation>` → `<hp:script>` — 수식
- `<hp:tbl>` — 표
- `<hp:pic>` → `<hp:img>` — 이미지
- `<hp:endNote>` — 미주 (각주/해설)
- `<hp:ctrl>` — 컨트롤 요소 (번호매기기, 미주 등)
