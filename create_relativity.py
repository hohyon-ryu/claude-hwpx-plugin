#!/usr/bin/env python3
"""상대성 이론 HWPX 문서 생성"""
import sys
sys.path.insert(0, "scripts")
from generator import (
    generate_hwpx, make_section, build_text_para, build_heading_para,
    build_equation_para, build_table, build_empty_para,
    STYLE_BODY, STYLE_H1, STYLE_H2, STYLE_H3, STYLE_BOLD, STYLE_H1_BLUE, STYLE_SMALL,
    _build_runs, build_equation, latex_to_hwp, read_base, _eq_counter
)
import generator
import re
import zipfile
import html as html_mod


def build_section_body():
    paras = []

    # ── 서론 ──
    paras.append(build_text_para(
        "아인슈타인의 상대성 이론은 20세기 물리학의 근본을 바꾼 혁명적 이론이다. "
        "1905년 특수 상대성 이론, 1915년 일반 상대성 이론이 발표되었으며, "
        "시간·공간·중력·에너지에 대한 인류의 이해를 완전히 재정립하였다."
    ))
    paras.append(build_empty_para())

    # ── 1. 특수 상대성 이론 ──
    paras.append(build_heading_para("1. 특수 상대성 이론 (Special Relativity)", level=2))
    paras.append(build_empty_para())

    paras.append(build_text_para(
        "특수 상대성 이론은 두 가지 공준(postulate)에 기반한다: "
        "(1) 모든 관성 좌표계에서 물리 법칙은 동일하다. "
        "(2) 진공에서의 빛의 속력은 관측자의 운동 상태와 무관하게 일정하다."
    ))
    paras.append(build_empty_para())

    # 1.1 로렌츠 인수
    paras.append(build_heading_para("1.1 로렌츠 인수 (Lorentz Factor)", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "물체의 속도 $v$가 빛의 속도 $c$에 가까워질수록 시간과 공간이 변형된다. "
        "이를 기술하는 핵심 인수는 다음과 같다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"\gamma = \frac{1}{\sqrt{1 - \frac{v^2}{c^2}}}"
    ))
    paras.append(build_empty_para())

    # 1.2 시간 팽창
    paras.append(build_heading_para("1.2 시간 팽창 (Time Dilation)", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "움직이는 관측자의 시간은 정지 관측자에 비해 느리게 흐른다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"\Delta t' = \gamma \Delta t = \frac{\Delta t}{\sqrt{1 - \frac{v^2}{c^2}}}"
    ))
    paras.append(build_empty_para())

    # 1.3 길이 수축
    paras.append(build_heading_para("1.3 길이 수축 (Length Contraction)", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "운동 방향으로의 길이는 정지 상태 대비 수축한다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"L' = \frac{L}{\gamma} = L \sqrt{1 - \frac{v^2}{c^2}}"
    ))
    paras.append(build_empty_para())

    # 1.4 질량-에너지 등가
    paras.append(build_heading_para("1.4 질량-에너지 등가 원리", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "물리학에서 가장 유명한 공식. 질량과 에너지는 본질적으로 같은 물리량이다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(r"E = mc^2"))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "운동하는 물체의 총 에너지는 정지 에너지와 운동 에너지의 합이다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"E^2 = (pc)^2 + (mc^2)^2"
    ))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "여기서 $p$는 상대론적 운동량이며 다음과 같다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"p = \gamma m v = \frac{mv}{\sqrt{1 - \frac{v^2}{c^2}}}"
    ))
    paras.append(build_empty_para())

    # 1.5 로렌츠 변환
    paras.append(build_heading_para("1.5 로렌츠 변환 (Lorentz Transformation)", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "관성 좌표계 사이의 시공간 좌표 변환이다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"x' = \gamma (x - vt)"
    ))
    paras.append(build_equation_para(
        r"t' = \gamma \left( t - \frac{vx}{c^2} \right)"
    ))
    paras.append(build_empty_para())

    # 테이블: 로렌츠 인수 값
    paras.append(build_heading_para("1.6 속도별 로렌츠 인수 값", level=3))
    paras.append(build_empty_para())
    paras.append(build_table([
        ["속도 (v/c)", "로렌츠 인수 γ", "시간 팽창 비율", "길이 수축 비율"],
        ["0.10", "1.005", "0.5%", "99.5%"],
        ["0.50", "1.155", "15.5%", "86.6%"],
        ["0.80", "1.667", "66.7%", "60.0%"],
        ["0.90", "2.294", "129.4%", "43.6%"],
        ["0.95", "3.203", "220.3%", "31.2%"],
        ["0.99", "7.089", "608.9%", "14.1%"],
        ["0.999", "22.366", "2136.6%", "4.5%"],
    ]))
    paras.append(build_empty_para())

    # ── 2. 민코프스키 시공간 ──
    paras.append(build_heading_para("2. 민코프스키 시공간", level=2))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "특수 상대성 이론의 기하학적 해석으로, 3차원 공간과 시간을 통합한 4차원 시공간이다. "
        "두 사건 사이의 시공간 간격(spacetime interval)은 불변량이다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2"
    ))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "4-벡터 표기로는 다음과 같이 쓸 수 있다. 여기서 메트릭 텐서는 다음과 같다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"ds^2 = \eta_{\mu \nu} dx^{\mu} dx^{\nu}"
    ))
    paras.append(build_empty_para())

    # ── 3. 일반 상대성 이론 ──
    paras.append(build_heading_para("3. 일반 상대성 이론 (General Relativity)", level=2))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "일반 상대성 이론은 중력을 시공간의 곡률로 해석한다. "
        "질량과 에너지가 시공간을 휘게 하고, 휘어진 시공간이 물체의 운동을 결정한다."
    ))
    paras.append(build_empty_para())

    # 3.1 아인슈타인 장 방정식
    paras.append(build_heading_para("3.1 아인슈타인 장 방정식", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "일반 상대성 이론의 핵심. 시공간의 기하학(좌변)과 물질-에너지 분포(우변)를 연결한다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"R_{\mu \nu} - \frac{1}{2} R g_{\mu \nu} + \Lambda g_{\mu \nu} = \frac{8 \pi G}{c^4} T_{\mu \nu}"
    ))
    paras.append(build_empty_para())

    # 테이블: 장 방정식 각 항의 의미
    paras.append(build_table([
        ["기호", "명칭", "물리적 의미"],
        ["R_μν", "리치 텐서 (Ricci Tensor)", "시공간 곡률의 축약"],
        ["R", "리치 스칼라 (Ricci Scalar)", "곡률의 스칼라 값"],
        ["g_μν", "메트릭 텐서 (Metric Tensor)", "시공간 거리 구조 정의"],
        ["Λ", "우주 상수 (Cosmological Constant)", "진공 에너지, 우주 팽창 가속"],
        ["G", "뉴턴 중력 상수", "6.674 × 10⁻¹¹ N·m²/kg²"],
        ["T_μν", "에너지-운동량 텐서", "물질·에너지 분포"],
    ]))
    paras.append(build_empty_para())

    # 3.2 측지선 방정식
    paras.append(build_heading_para("3.2 측지선 방정식 (Geodesic Equation)", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "휘어진 시공간에서 자유 낙하하는 물체의 경로를 기술한다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"\frac{d^2 x^{\mu}}{d \tau^2} + \Gamma^{\mu}_{\alpha \beta} \frac{dx^{\alpha}}{d \tau} \frac{dx^{\beta}}{d \tau} = 0"
    ))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "여기서 $\\Gamma^{\\mu}_{\\alpha \\beta}$는 크리스토펠 기호(Christoffel symbol)로 "
        "메트릭 텐서로부터 계산된다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"\Gamma^{\mu}_{\alpha \beta} = \frac{1}{2} g^{\mu \lambda} \left( \frac{\partial g_{\lambda \alpha}}{\partial x^{\beta}} + \frac{\partial g_{\lambda \beta}}{\partial x^{\alpha}} - \frac{\partial g_{\alpha \beta}}{\partial x^{\lambda}} \right)"
    ))
    paras.append(build_empty_para())

    # 3.3 슈바르츠실트 해
    paras.append(build_heading_para("3.3 슈바르츠실트 계량 (Schwarzschild Metric)", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "구대칭 비회전 질량 주변의 시공간을 기술하는 정확한 해이다. 블랙홀 물리학의 기초가 된다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"ds^2 = -\left(1 - \frac{2GM}{c^2 r}\right) c^2 dt^2 + \left(1 - \frac{2GM}{c^2 r}\right)^{-1} dr^2 + r^2 d\Omega^2"
    ))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "슈바르츠실트 반지름은 사건의 지평선(event horizon)을 결정한다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"r_s = \frac{2GM}{c^2}"
    ))
    paras.append(build_empty_para())

    # 테이블: 천체별 슈바르츠실트 반지름
    paras.append(build_table([
        ["천체", "질량 (kg)", "슈바르츠실트 반지름", "실제 반지름"],
        ["지구", "5.97 × 10²⁴", "8.87 mm", "6,371 km"],
        ["태양", "1.99 × 10³⁰", "2.95 km", "696,000 km"],
        ["Sgr A* (은하 중심)", "~8.2 × 10³⁶", "~1,200만 km", "사건 지평선 내"],
    ]))
    paras.append(build_empty_para())

    # ── 4. 중력파 ──
    paras.append(build_heading_para("4. 중력파 (Gravitational Waves)", level=2))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "가속하는 질량이 시공간에 잔물결을 만들어 빛의 속도로 전파한다. "
        "2015년 LIGO에 의해 최초 직접 검출되었다."
    ))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "선형화된 아인슈타인 방정식에서 중력파의 파동 방정식은 다음과 같다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"\Box \bar{h}_{\mu \nu} = -\frac{16 \pi G}{c^4} T_{\mu \nu}"
    ))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "여기서 $\\Box$는 달랑베르 연산자(d'Alembertian)이다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"\Box = -\frac{1}{c^2} \frac{\partial^2}{\partial t^2} + \nabla^2"
    ))
    paras.append(build_empty_para())

    # ── 5. 우주론 ──
    paras.append(build_heading_para("5. 우주론적 응용", level=2))
    paras.append(build_empty_para())

    paras.append(build_heading_para("5.1 프리드만 방정식 (Friedmann Equations)", level=3))
    paras.append(build_empty_para())
    paras.append(build_text_para(
        "균질 등방 우주의 팽창을 기술한다. 현대 우주론의 기본 방정식이다."
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"\left( \frac{\dot{a}}{a} \right)^2 = \frac{8 \pi G}{3} \rho - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}"
    ))
    paras.append(build_empty_para())
    paras.append(build_equation_para(
        r"\frac{\ddot{a}}{a} = -\frac{4 \pi G}{3} \left( \rho + \frac{3p}{c^2} \right) + \frac{\Lambda c^2}{3}"
    ))
    paras.append(build_empty_para())

    # 테이블: 주요 우주론 파라미터
    paras.append(build_table([
        ["파라미터", "기호", "측정값 (Planck 2018)"],
        ["허블 상수", "H₀", "67.4 ± 0.5 km/s/Mpc"],
        ["바리온 밀도", "Ω_b", "0.0493 ± 0.0006"],
        ["암흑물질 밀도", "Ω_c", "0.265 ± 0.007"],
        ["암흑에너지 밀도", "Ω_Λ", "0.685 ± 0.007"],
        ["우주 나이", "t₀", "13.80 ± 0.02 Gyr"],
    ]))
    paras.append(build_empty_para())

    # ── 6. 핵심 공식 요약 ──
    paras.append(build_heading_para("6. 핵심 공식 요약", level=2))
    paras.append(build_empty_para())

    paras.append(build_table([
        ["이론", "핵심 공식", "의미"],
        ["질량-에너지 등가", "E = mc²", "질량은 에너지의 한 형태"],
        ["로렌츠 인수", "γ = 1/√(1-v²/c²)", "고속 운동의 시공간 변형 척도"],
        ["시간 팽창", "Δt' = γΔt", "운동하면 시간이 느려짐"],
        ["길이 수축", "L' = L/γ", "운동 방향 길이가 줄어듦"],
        ["에너지-운동량 관계", "E² = (pc)² + (mc²)²", "상대론적 에너지 완전 관계식"],
        ["아인슈타인 장 방정식", "G_μν + Λg_μν = (8πG/c⁴)T_μν", "시공간 곡률 = 에너지 분포"],
        ["슈바르츠실트 반지름", "r_s = 2GM/c²", "블랙홀 사건 지평선 크기"],
        ["프리드만 방정식", "(ȧ/a)² = 8πGρ/3 - kc²/a²", "우주 팽창 역학"],
    ]))
    paras.append(build_empty_para())

    paras.append(build_text_para(
        "상대성 이론은 GPS 위성 보정, 입자 가속기, 블랙홀 관측, 중력파 검출 등 "
        "현대 과학기술 전반에 필수적인 이론적 기반을 제공하고 있다.",
        STYLE_SMALL
    ))

    return "\n".join(paras)


def main():
    output = "relativity.hwpx"
    title = "상대성 이론: 시공간과 중력의 물리학"

    generator._eq_counter = 0
    body_xml = build_section_body()

    # make_section을 직접 사용하지 않고, section XML을 직접 조립
    base = read_base("section.xml")
    first_p_match = re.search(r'(<hp:p[^>]*>.*?</hp:p>)', base, re.DOTALL)
    first_p = first_p_match.group(1) if first_p_match else ''

    root_match = re.search(r'(<hs:sec[^>]+>)', base)
    root_tag = root_match.group(1) if root_match else ''
    xml_decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'

    # 타이틀
    title_para = build_heading_para(title, level=1)
    subtitle_para = build_text_para(
        "Einstein's Theory of Relativity — 특수 상대성 이론과 일반 상대성 이론의 수학적 기술",
        STYLE_SMALL
    )

    section_xml = (
        f'{xml_decl}{root_tag}{first_p}'
        f'{title_para}'
        f'{subtitle_para}'
        f'{build_empty_para()}'
        f'{body_xml}'
        f'</hs:sec>'
    )

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", read_base("mimetype"), compress_type=zipfile.ZIP_STORED)
        zf.writestr("version.xml", read_base("version.xml"))
        zf.writestr("settings.xml", read_base("settings.xml"))
        zf.writestr("META-INF/container.xml", read_base("container.xml"))
        zf.writestr("META-INF/container.rdf", read_base("container.rdf"))
        zf.writestr("META-INF/manifest.xml", read_base("manifest.xml"))
        zf.writestr("Contents/content.hpf", read_base("content.hpf"))
        zf.writestr("Contents/header.xml", read_base("header.xml"))
        zf.writestr("Contents/section0.xml", section_xml)
        zf.writestr("Preview/PrvText.txt", title)

    print(f"생성 완료: {output}")


if __name__ == "__main__":
    main()
