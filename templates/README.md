# HWPX 템플릿

즉시 사용 가능한 HWPX XML 템플릿 모음.
스킬에서 `${CLAUDE_SKILL_DIR}/../templates/` 경로로 참조합니다.

## 파일 목록

| 파일 | 설명 |
|------|------|
| `mimetype` | HWPX MIME 타입 |
| `version.xml` | HWP 버전 정보 |
| `settings.xml` | 문서 설정 |
| `container.xml` | OPF 컨테이너 |
| `manifest.xml` | 매니페스트 |
| `header-a4.xml` | A4 단일단 문서 헤더 |
| `header-b4.xml` | B4 시험지 헤더 |
| `content.hpf` | OPF 패키지 (섹션/이미지 등록) |
| `section-empty.xml` | 빈 섹션 (A4, 1단) |
| `section-b4-2col.xml` | B4 2단 섹션 |
| `generator.js` | Node.js HWPX 생성 스크립트 |
| `generator.py` | Python HWPX 생성 스크립트 |
