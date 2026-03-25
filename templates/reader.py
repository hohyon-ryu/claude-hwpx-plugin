#!/usr/bin/env python3
"""
HWPX 문서 읽기 — 텍스트, 수식, 이미지 추출하여 Markdown으로 변환
사용법: python reader.py input.hwpx [output.md]
"""
import zipfile
import re
import sys
from pathlib import Path


# HWP equation script → LaTeX 변환
def hwp_eq_to_latex(script: str) -> str:
    s = script.strip()
    # over → frac
    s = re.sub(r'\{([^}]*)\}\s*over\s*\{([^}]*)\}', r'\\frac{\1}{\2}', s)
    # sqrt
    s = re.sub(r'sqrt\s*\{([^}]*)\}', r'\\sqrt{\1}', s)
    # "text" → \text{text}
    s = re.sub(r'"([^"]*)"', r'\\text{\1}', s)
    # left/right
    s = s.replace('left (', '\\left(').replace('right )', '\\right)')
    s = s.replace('left lbrace', '\\left\\{').replace('right rbrace', '\\right\\}')
    s = s.replace('lbrace', '\\{').replace('rbrace', '\\}')
    # arrows
    s = s.replace('rightarrow', '\\to')
    # spaces
    s = s.replace('~~~~', '\\qquad').replace('~~', '\\quad').replace('~', '\\,')
    # rm{...} → 숫자/기호는 그대로
    s = re.sub(r'rm\{([^}]*)\}', r'\1', s)
    # 나머지 keyword → \keyword
    keywords = ['alpha', 'beta', 'gamma', 'delta', 'theta', 'lambda',
                'mu', 'sigma', 'omega', 'pi', 'sum', 'int', 'prod',
                'infty', 'times', 'div', 'pm', 'leq', 'geq', 'neq',
                'sin', 'cos', 'tan', 'log', 'ln', 'lim']
    for kw in keywords:
        s = re.sub(rf'\b{kw}\b', f'\\\\{kw}', s)
    return s


def extract_hwpx(hwpx_path: str) -> str:
    """HWPX → Markdown 변환"""
    ns = {
        'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    }

    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(hwpx_path) as zf:
        # 모든 section 파일 찾기
        section_files = sorted([n for n in zf.namelist() if n.startswith('Contents/section') and n.endswith('.xml')])
        if not section_files:
            return "# 섹션 파일을 찾을 수 없습니다."

        lines = []
        for sf in section_files:
            with zf.open(sf) as f:
                tree = ET.parse(f)
            root = tree.getroot()

            for p in root.iter(f'{{{ns["hp"]}}}p'):
                parts = []
                for run in p.findall(f'.//{{{ns["hp"]}}}run'):
                    # 텍스트
                    for t in run.findall(f'{{{ns["hp"]}}}t'):
                        if t.text:
                            parts.append(t.text)
                    # 수식
                    for eq in run.findall(f'.//{{{ns["hp"]}}}script'):
                        if eq.text:
                            latex = hwp_eq_to_latex(eq.text)
                            parts.append(f'${latex}$')
                    # 이미지
                    for img in run.findall(f'.//{{{ns["hp"]}}}img'):
                        ref = img.get('binaryItemIDRef', '')
                        parts.append(f'![이미지](BinData/image{ref}.png)')

                line = ''.join(parts).strip()
                if line:
                    lines.append(line)

        # 이미지 추출
        images = [n for n in zf.namelist() if n.startswith('BinData/')]
        if images:
            out_dir = Path(hwpx_path).stem + '_images'
            Path(out_dir).mkdir(exist_ok=True)
            for img_name in images:
                with zf.open(img_name) as src:
                    (Path(out_dir) / Path(img_name).name).write_bytes(src.read())
            lines.append(f'\n---\n이미지 {len(images)}개 추출: ./{out_dir}/')

    return '\n\n'.join(lines)


def extract_hwp5(hwp_path: str) -> str:
    """HWP5 바이너리 → 텍스트 (pyhwp 사용)"""
    import subprocess
    try:
        result = subprocess.run(['hwp5txt', hwp_path], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        return f"hwp5txt 실패: {result.stderr}"
    except FileNotFoundError:
        return "pyhwp가 설치되어 있지 않습니다. pip install pyhwp"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python reader.py input.hwpx [output.md]")
        print("        python reader.py input.hwp   [output.md]")
        sys.exit(1)

    input_path = sys.argv[1]
    is_hwp5 = input_path.lower().endswith('.hwp')

    if is_hwp5:
        markdown = extract_hwp5(input_path)
    else:
        markdown = extract_hwpx(input_path)

    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(markdown, encoding='utf-8')
        print(f"변환 완료: {sys.argv[2]}")
    else:
        print(markdown)
