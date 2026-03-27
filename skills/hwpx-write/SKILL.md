---
name: hwpx-write
description: HWPX(한글 문서) 파일을 프로그래밍으로 생성합니다. HWP equation script 문법, HWPX XML 구조, 수식/이미지/레이아웃 패턴을 숙지하고 있습니다.
---

# HWPX 문서 생성

$ARGUMENTS

## HWPX 파일 구조

HWPX는 한컴오피스 한글의 문서 포맷. ZIP 아카이브 안에 XML 파일들로 구성.

```
document.hwpx (ZIP)
├── META-INF/
│   └── container.xml         # OPF 컨테이너 (루트 파일 경로)
├── Contents/
│   ├── content.hpf           # OPF 패키지 (모든 파일 목록)
│   ├── header.xml            # 문서 설정 (폰트, 스타일, 단락속성)
│   ├── section0.xml          # 본문 내용 (단락, 수식, 이미지)
│   └── section1.xml          # 추가 섹션 (필요시)
├── BinData/                  # 이미지 파일 저장소
│   ├── image1.png
│   └── image2.png
├── Preview/
│   └── PrvText.txt           # 미리보기 텍스트
├── settings.xml              # 문서 설정
└── mimetype                  # application/hwp+zip
```

## HWP Equation Script (수식 문법)

**핵심: HWP 수식은 LaTeX가 아닙니다.** 별도 문법을 사용합니다.

### LaTeX → HWP 변환 규칙

| LaTeX | HWP Equation Script | 설명 |
|-------|---------------------|------|
| `\frac{a}{b}` | `{a} over {b}` | 분수 |
| `\sqrt{x}` | `sqrt {x}` | 제곱근 |
| `\text{cm}` | `"cm"` | 텍스트 (큰따옴표) |
| `\mathrm{log}` | `"log"` | 로마체 텍스트 |
| `\left(` | `left (` | 왼쪽 구분자 |
| `\right)` | `right )` | 오른쪽 구분자 |
| `\left\{` | `left lbrace` | 왼쪽 중괄호 |
| `\right\}` | `right rbrace` | 오른쪽 중괄호 |
| `\{` | `lbrace` | 중괄호 (단독) |
| `\}` | `rbrace` | 중괄호 (단독) |
| `\left\|` | `LEFT \|` | 절댓값 왼쪽 |
| `\right\|` | `RIGHT \|` | 절댓값 오른쪽 |
| `\to` | `` `->`  `` | 명제 화살표 (간격 포함) |
| `\cdot` | `cdot` | 내적 (bullet 아님!) |
| `\cdots` | `` `cdots`  `` | 생략점 (앞뒤 ` 간격) |
| `\overline{AB}` | `rm bar{AB}` | 선분 (도형이므로 rm) |
| `\vec{AB}` | `vec{rm AB it}` | 벡터 |
| `\triangle ABC` | `rm triangle ABC` | 삼각형 |
| `\angle ABC` | `rm ANGLE ABC` | 각도 |
| `\quad` | `~~` | 넓은 공백 |
| `\qquad` | `~~~~` | 매우 넓은 공백 |
| `\,` `\;` `\:` `\!` | `~` | 미세 공백 |
| `\alpha` | `alpha` | 그리스 문자 (백슬래시 제거) |
| `\sin` | `` `sin`  `` | 함수명 (앞뒤 ` 간격) |
| `\therefore` | `therefore~` | therefore (뒤에 ~ 간격) |
| `\because` | `because~` | because (뒤에 ~ 간격) |

## MathON 수식 작성 규칙 (rm/it)

**이 규칙은 한국 수학 시험지 작성의 표준입니다. 반드시 준수하세요.**

### rm(로마체) vs it(이태릭체) 구분

HWP 수식에서 알파벳은 기본적으로 이태릭체(it)로 렌더링됩니다. 로마체가 필요한 경우 `rm`을 명시적으로 사용해야 합니다.

### rm(로마체) 사용 대상

| 대상 | 예시 | HWP Script |
|------|------|------------|
| **도형 꼭짓점 대문자** | A, B, C, P, Q | `rmA`, `rmB`, `rmABCD` |
| **삼각형** | 삼각형 ABC | `rm triangle ABC` |
| **선분** | 선분 AB | `rm bar{AB}` 또는 `bar{rmPQ}` |
| **각도** | 각 A, 각 ABC | `rm ANGLE A`, `rm ANGLE ABC` |
| **단위** | cm, m, kg, L | `` `rmcm ``, `` `rmkg `` (앞에 `` ` `` 간격) |
| **확률/통계 기호** | P, C, H, B, N, E | `{rmP}`, `{rmC}`, `{rmN}`, `{rmE}` |
| **합동 조건** | SSS, SAS | `rmSSS`, `rmSAS` |
| **숫자** | 1, 2, 3.14 | `rm{1}`, `rm{3.14}` (자동 처리) |

### it(이태릭체) 사용 대상 (기본값)

| 대상 | 예시 | HWP Script |
|------|------|------------|
| **변수** | a, b, x, y | `a`, `b`, `x`, `y` (별도 지정 불필요) |
| **부등호 뒤 음수** | x < -2 | `x<it-2` (띄어쓰기 대신 it) |
| **극한 화살표 뒤 음수** | lim(x->-2) | `lim_{x->it-2}` |

### rm/it 혼합 패턴 (확률/통계)

| 표현 | HWP Script |
|------|------------|
| 순열 nPr | `_{it n}{rmP}_{it r}` |
| 조합 nCr | `_{it n}{rmC}_{it r}` |
| 중복조합 nHr | `_{it n}{rmH}_{it r}` |
| 확률 P(X=r) | `{rmP}{it(X=r)}` |
| 이항분포 B(n,p) | `{rmB}{it(n,~p)}` |
| 정규분포 N(m,sigma^2) | `{rmN}{it(m,~sigma^2)}` |
| 기댓값 E(X) | `{rmE}{it(X)}` |

## 간격 규칙

| 위치 | 기호 | 예시 |
|------|------|------|
| 단위 앞 | `` ` `` | ``150`rmkg`` |
| 쉼표 뒤 | `~` | `(a,~b)` |
| cdots 앞뒤 | `` ` `` | `` `cdots` `` |
| therefore/because 뒤 | `~` | `therefore~a=b` |
| 순서쌍 | `~` | `(a,~b)` |
| 집합 원소 | `~` | `LEFT { a,~b,~c RIGHT }` |
| 두 점 | `~` | `rmP,~Q` |
| cases 정렬 | `~~` | `cases{ax+b~~&(x ne 1)}` |
| 좌표 쉼표 뒤 | ` `` ` | ``rmA(-2,`` `-1)`` |
| 삼각함수/로그 앞뒤 | `` ` `` | `` `sin` ``, `` `log` `` |

## 기호 규칙

| 기호 | HWP Script | 주의사항 |
|------|------------|----------|
| 절댓값 | `LEFT \| RIGHT \|` | 반드시 대문자 LEFT/RIGHT |
| 명제 화살표 | `` p`->`q `` | backtick 간격 포함 |
| 내적 | `cdot` | bullet 아님! |
| 여집합 | 소문자 `c` | |
| 수직 | `bot` | `rmbar AB bot barCD` |
| 연립방정식 번호 | 원문자 (수식 밖 바탕글) | 수식 안에 넣지 않음 |

## 배치/서식 규칙

- **서체**: 나눔고딕 10pt, 수식 크기 11pt, 수식 서체 HYhwpEQ
- **문제-보기 사이**: Enter 한 줄
- **보기 간격**: 탭 3번
- **소문항**: (1), (2)로 통일
- **해설**: 통수식 금지, 등호 단위로 끊어서
- **정답**: bold 처리 안 함
- **cases 정렬**: `~~`로 조건식 위치 통일
- **독립줄 수식**: tab 들여쓰기
- **해설 경우 나눔**: 로마자 문자표 사용

## 수식 XML 구조

```xml
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
    <hp:script>{a} over {b}</hp:script>
</hp:equation>
```

**주요 속성:**
- `width`: 수식 너비 (HWP 단위, 글자당 ~600)
- `height`: 수식 높이 (기본 3000)
- `baseLine`: 기준선 오프셋 (86 = 본문 정렬)
- `treatAsChar="1"`: 인라인 수식
- `font="HYhwpEQ"`: HWP 전용 수식 폰트

## 단락(Paragraph) XML 구조

### 텍스트 단락

```xml
<hp:p id="0" paraPrIDRef="0" styleIDRef="0"
     pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="1">
    <hp:t>문제 텍스트입니다.</hp:t>
  </hp:run>
</hp:p>
```

### 텍스트 + 인라인 수식 혼합

```xml
<hp:p id="0" paraPrIDRef="0" styleIDRef="0"
     pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="1">
    <hp:t>이차방정식 </hp:t>
  </hp:run>
  <hp:run charPrIDRef="1">
    <hp:equation ...>
      <hp:script>x^rm{2}+rm{3}x+rm{2}=rm{0}</hp:script>
    </hp:equation>
    <hp:t/>
  </hp:run>
  <hp:run charPrIDRef="1">
    <hp:t>을 풀어라.</hp:t>
  </hp:run>
</hp:p>
```

**규칙:** 수식 다음에는 반드시 빈 `<hp:t/>`가 필요합니다.

## 페이지 설정

### B4 용지 (JIS, 한국 시험지 표준)

```xml
<hp:pagePr landscape="WIDELY" width="72851" height="103181" gutterType="LEFT_ONLY">
  <hp:margin header="4252" footer="4252" gutter="0"
             left="8504" right="8504" top="7086" bottom="5668"/>
</hp:pagePr>
```

### A4 용지

```xml
<hp:pagePr landscape="WIDELY" width="59528" height="84188" gutterType="LEFT_ONLY">
  <hp:margin header="4252" footer="4252" gutter="0"
             left="8504" right="8504" top="5668" bottom="4252"/>
</hp:pagePr>
```

**단위:** 1 HWP unit = 1/7200 인치. 8504 units = 30mm.

### 2단 레이아웃 (신문식)

```xml
<hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="2" sameSz="1" sameGap="2268"/>
```

## 폰트 설정

### header.xml의 fontface

```xml
<hh:fontface lang="HANGUL" fontCnt="2">
  <hh:font id="0" face="신명중명조" type="TTF" isEmbedded="0"/>
  <hh:font id="1" face="나눔고딕" type="TTF" isEmbedded="0"/>
</hh:fontface>
```

### charPr (문자 속성)

```xml
<!-- 본문: 신명중명조 10pt -->
<hh:charPr id="0" height="1000" textColor="#000000">
  <hh:fontRef hangul="0" latin="0" .../>
</hh:charPr>

<!-- 정답: 신명중명조 11pt bold -->
<hh:charPr id="2" height="1100" textColor="#000000">
  <hh:fontRef hangul="0" latin="0" .../>
  <hh:bold/>
</hh:charPr>
```

**height 단위:** 100 = 1pt. `1000` = 10pt, `1100` = 11pt.

### paraPr (단락 속성)

```xml
<hh:paraPr id="0">
  <hh:align horizontal="LEFT" vertical="BASELINE"/>
  <hh:lineSpacing type="PERCENT" value="160" unit="HWPUNIT"/>
</hh:paraPr>
```

## 이미지 삽입

### BinData에 이미지 파일 추가 (ZIP에 넣기)

```javascript
zip.file("BinData/image1.png", pngBuffer);
```

### 이미지 참조 XML

```xml
<hp:pic id="0" zOrder="0" numberingType="PICTURE"
    textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES">
  <hp:imgRect>
    <hp:orgSz width="28000" height="28000"/>
    <hp:curSz width="0" height="0"/>
  </hp:imgRect>
  <hp:imgClip/>
  <hp:sz width="28000" widthRelTo="ABSOLUTE"
         height="28000" heightRelTo="ABSOLUTE" protect="0"/>
  <hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1"
          allowOverlap="0" holdAnchorAndSO="0"
          vertRelTo="PAPER" horzRelTo="COLUMN"
          vertAlign="BOTTOM" horzAlign="LEFT"
          vertOffset="0" horzOffset="0"/>
  <hp:outMargin left="0" right="0" top="0" bottom="0"/>
  <hp:imgDim dimwidth="0" dimheight="0"/>
  <hp:img bright="0" contrast="0" effect="REAL_PIC"
       binaryItemIDRef="1"/>
</hp:pic>
```

**binaryItemIDRef**: content.hpf에 등록된 BinData ID와 매칭.

## Endnote (미주 -- 해설/풀이)

문제 번호에 endnote를 연결하면 문서 끝에 해설이 자동 배치됩니다.

```xml
<hp:run charPrIDRef="1">
  <hp:ctrl>
    <hp:endNote number="1" suffixChar="41" instId="2000000000">
      <hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK"
                  vertAlign="TOP" ...>
        <!-- 여기에 해설 내용 -->
        <hp:p ...>
          <hp:run charPrIDRef="0">
            <hp:ctrl>
              <hp:autoNum num="1" numType="ENDNOTE">
                <hp:autoNumFormat type="DIGIT" .../>
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

## content.hpf (OPF 패키지)

모든 파일을 등록:

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

## XML 네임스페이스

```
hh = http://www.hancom.co.kr/hwpml/2011/head
hp = http://www.hancom.co.kr/hwpml/2011/paragraph
hs = http://www.hancom.co.kr/hwpml/2011/section
hc = http://www.hancom.co.kr/hwpml/2011/core
ha = http://www.hancom.co.kr/hwpml/2011/app
```

## 흔한 실수 & 디버깅

1. **수식이 표시 안 됨**: `<hp:t/>` 누락 -- 수식 뒤에 반드시 빈 `<hp:t/>` 필요
2. **한글 깨짐**: XML 인코딩이 UTF-8인지 확인, `escapeXml()` 적용
3. **이미지 안 보임**: `binaryItemIDRef`와 content.hpf의 `id` 불일치
4. **2단 레이아웃 안 됨**: `<hp:colPr>`가 `<hp:secPr>` 안에 있어야 함
5. **pageBreak 안 됨**: `<hp:p>` 의 `pageBreak="1"` 속성
6. **columnBreak 안 됨**: `<hp:p>` 의 `columnBreak="1"` 속성
7. **수식 너비 계산**: 글자당 ~600 HWP 단위, 최소 3000, 2단일 때 최대 ~18000
8. **rm/it 혼동**: 변수는 it(기본), 도형꼭짓점/단위/확률기호는 rm
9. **bullet 사용**: 내적은 반드시 `cdot`, `bullet` 사용 금지
10. **단위 간격 누락**: 숫자와 단위 사이에 `` ` `` 간격 필수
