#!/usr/bin/env python3
"""
HWPX 문서 유효성 검사
사용법: python validate.py document.hwpx
"""
import zipfile
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


REQUIRED_FILES = [
    "mimetype",
    "META-INF/container.xml",
    "Contents/content.hpf",
    "Contents/header.xml",
]

EXPECTED_MIMETYPE = "application/hwp+zip"

NS = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hh': 'http://www.hancom.co.kr/hwpml/2011/head',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
}


def validate(hwpx_path: str) -> list[str]:
    errors = []
    warnings = []
    path = Path(hwpx_path)

    if not path.exists():
        return [f"File not found: {hwpx_path}"]

    if not zipfile.is_zipfile(hwpx_path):
        return [f"Not a valid ZIP file: {hwpx_path}"]

    with zipfile.ZipFile(hwpx_path) as zf:
        names = zf.namelist()

        # 1. Required files
        for req in REQUIRED_FILES:
            if req not in names:
                errors.append(f"Missing required file: {req}")

        # 2. At least one section file
        sections = [n for n in names if n.startswith('Contents/section') and n.endswith('.xml')]
        if not sections:
            errors.append("No section files found (Contents/section*.xml)")

        # 3. mimetype content
        if "mimetype" in names:
            mt = zf.read("mimetype").decode("utf-8").strip()
            if mt != EXPECTED_MIMETYPE:
                errors.append(f"Invalid mimetype: '{mt}' (expected '{EXPECTED_MIMETYPE}')")

        # 4. Validate XML files
        for name in names:
            if name.endswith('.xml') or name.endswith('.hpf'):
                try:
                    with zf.open(name) as f:
                        ET.parse(f)
                except ET.ParseError as e:
                    errors.append(f"XML parse error in {name}: {e}")

        # 5. Check equations have trailing <hp:t/>
        for sf in sections:
            try:
                with zf.open(sf) as f:
                    content = f.read().decode('utf-8')
                # Check for equation without trailing <hp:t/>
                import re
                bad_eqs = re.findall(r'</hp:equation>\s*</hp:run>', content)
                if bad_eqs:
                    warnings.append(f"{sf}: {len(bad_eqs)} equation(s) missing trailing <hp:t/> after </hp:equation>")
            except Exception:
                pass

        # 6. Check image references
        for sf in sections:
            try:
                with zf.open(sf) as f:
                    content = f.read().decode('utf-8')
                img_refs = re.findall(r'binaryItemIDRef="(\d+)"', content)
                bindata_files = [n for n in names if n.startswith('BinData/')]
                if img_refs and not bindata_files:
                    warnings.append(f"{sf}: Image references found but BinData/ is empty")
            except Exception:
                pass

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("사용법: python validate.py document.hwpx")
        sys.exit(1)

    hwpx_path = sys.argv[1]
    result = validate(hwpx_path)

    if isinstance(result, list):
        # Fatal error (not a zip, etc.)
        for e in result:
            print(f"ERROR: {e}")
        sys.exit(1)

    errors, warnings = result

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
    if warnings:
        for w in warnings:
            print(f"WARNING: {w}")

    if not errors and not warnings:
        print(f"VALID: {hwpx_path}")
        sys.exit(0)
    elif not errors:
        print(f"\nVALID with warnings: {hwpx_path}")
        sys.exit(0)
    else:
        print(f"\nINVALID: {hwpx_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
