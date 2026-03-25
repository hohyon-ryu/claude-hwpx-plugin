# claude-hwpx-plugin

A Claude Code plugin for reading, writing, and converting HWP/HWPX documents — the dominant document format in South Korea used by government, education, and enterprise.

한국에서 가장 많이 쓰이는 문서 포맷 HWP/HWPX를 Claude Code에서 읽고, 쓰고, 변환할 수 있게 해주는 플러그인입니다.

---

## Why? | 왜 필요한가?

Virtually all official documents in South Korea are stored in HWP format (Hancom Office Hangul). Government agencies, schools, law firms, and corporations all produce and consume HWP files daily. Converting these documents to usable data has been painful due to the proprietary format and poor tooling around math formula extraction.

This plugin teaches Claude Code the HWP/HWPX file structure, equation script syntax, and XML schema so it can work with Korean documents natively.

한국의 공공기관, 학교, 기업에서 생산되는 문서의 상당수가 HWP(한글) 형식입니다. 이 문서들을 데이터로 활용하려면 텍스트 추출, 수식 변환, 포맷 변환이 필요하지만, 기존 도구들은 수식 처리가 불완전하고 자동화가 어렵습니다.

이 플러그인을 설치하면 Claude Code가 HWP/HWPX 파일 구조, HWP 수식 문법, XML 스키마를 이해하게 되어 한글 문서 관련 작업을 즉시 수행할 수 있습니다.

## 설치 | Installation

```bash
git clone https://github.com/hohyon-ryu/claude-hwpx-plugin.git
claude --plugin-dir ./claude-hwpx-plugin
```

## 스킬 | Skills

### `/hwpx:hwpx-read` — 문서 읽기 | Read Documents

HWP/HWPX 파일에서 텍스트, 수식, 이미지, 표를 추출합니다.

Extract text, equations, images, and tables from HWP/HWPX files.

```
/hwpx:hwpx-read 공문서.hwpx
/hwpx:hwpx-read contract.hwp
```

- **HWPX**: ZIP 해제 → XML 파싱 → 텍스트/수식 추출
- **HWP5 (바이너리)**: `pyhwp` 활용 (`pip install pyhwp`)
- **수식**: HWP equation script → LaTeX 자동 변환

### `/hwpx:hwpx-write` — 문서 생성 | Generate Documents

HWPX 파일을 프로그래밍으로 생성합니다.

Programmatically create HWPX files.

```
/hwpx:hwpx-write B4 2단 시험지 만들어줘
/hwpx:hwpx-write A4 report template
```

- B4/A4 용지, 1단/2단 레이아웃
- LaTeX → HWP equation script 수식 변환
- 이미지 삽입, 미주(해설), 표
- 한글 폰트 설정 (신명중명조, 나눔고딕 등)

### `/hwpx:hwpx-convert` — 포맷 변환 | Format Conversion

HWP/HWPX ↔ Markdown 양방향 변환.

Bidirectional HWP/HWPX ↔ Markdown conversion.

```
/hwpx:hwpx-convert report.hwpx → markdown
/hwpx:hwpx-convert *.hwp → markdown (배치)
/hwpx:hwpx-convert document.md → hwpx
```

## 포함된 도구 | Included Tools

`templates/` 디렉토리에 즉시 실행 가능한 스크립트가 포함되어 있습니다.

| 파일 | 설명 | Description |
|------|------|-------------|
| `reader.py` | HWPX/HWP5 → Markdown 변환기 | HWPX/HWP5 → Markdown converter |
| `generator.py` | Markdown → HWPX 생성기 | Markdown → HWPX generator |
| `*.xml` | HWPX 뼈대 템플릿 | HWPX skeleton templates |

```bash
# HWPX → Markdown
python templates/reader.py input.hwpx output.md

# HWPX 생성
python templates/generator.py output.hwpx "제목" "본문"
```

## HWP → Markdown 변환 가이드 | Conversion Guide

가장 흔한 사용 사례입니다. 방법별 품질 비교:

| 방법 | 텍스트 | 수식 | 표 | 이미지 |
|------|--------|------|-----|--------|
| `hwp5txt` (pyhwp) | ✅ | ❌ | △ | ❌ |
| `hwp5html` → pandoc | ✅ | △ | ✅ | ✅ |
| HWPX → `reader.py` | ✅ | ✅ LaTeX | ✅ | ✅ |

수식이 중요한 경우: HWP → 한글에서 HWPX로 저장 → `reader.py`가 최고 품질.

For math-heavy docs: Save as HWPX in Hangul → use `reader.py` for best quality.

## HWP → HWPX 변환 | HWP to HWPX

직접 변환 CLI 도구는 존재하지 않습니다. No direct CLI conversion tool exists.

- **소량**: 한글 프로그램에서 "다른 이름으로 저장" → HWPX
- **대량 (Windows)**: 한글 ActiveX 매크로 자동화
- **Mac/Linux**: `pyhwp`로 텍스트 추출 → HWPX 재생성 (서식 손실)

## HWP 수식 문법 | HWP Equation Syntax

HWP는 LaTeX가 아닌 자체 수식 문법을 사용합니다.

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

## HWP 포맷 버전 | Format Versions

| 버전 | 시기 | 포맷 |
|------|------|------|
| HWP 1.x–3.x | 1989–2001 | 독자 바이너리 (거의 멸종) |
| **HWP 5.x** | 2002–현재 | **OLE2 compound document** |
| **HWPX** | 2014–현재 | **ZIP+XML** (Open XML 계열) |

현재 유통되는 .hwp 파일의 99%는 HWP5입니다.

## 활용 사례 | Use Cases

- **공공기관 | Government**: HWP 공문서를 Markdown/데이터로 변환하여 검색·분석
- **교육 | Education**: 시험지·교안을 HWPX로 자동 생성
- **법률 | Legal**: 법률 문서 데이터화 및 구조화
- **아카이브 | Archive**: 대량 HWP 문서 일괄 Markdown 변환

## 시스템 요구사항 | Requirements

- Claude Code
- Python 3.8+ (templates 스크립트 실행 시)
- `pyhwp` (HWP5 읽기 시): `pip install pyhwp`
- `pandoc` (HTML→Markdown 변환 시, 선택)

## 라이선스 | License

MIT

## 작성자 | Author

**유호현 (Hohyon Ryu)**
- GitHub: [@hohyon-ryu](https://github.com/hohyon-ryu)
