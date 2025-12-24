# 한국 주식시장 분석 블로그

코스피·코스닥 상장사의 실적 리뷰, 밸류에이션 체크, 섹터 흐름을 다룹니다. 데이터 기반 리포트와 간결한 인사이트를 제공하는 것을 목표로 합니다.

## 다루는 내용

- 분기/연간 실적 리뷰 및 컨퍼런스콜 핵심 요약
- 섹터·테마 모니터링(2차전지, 반도체, 바이오, 방산 등)
- 밸류에이션 멀티플 변화와 수급·수익률 스냅샷
- 투자 체크리스트, 리스크 팩터와 투자 아이디어 트래킹

## 최근 글

<div class="doc-cards">
  <a class="doc-card" href="#/posts/hello-world">
    <h3>시장 오프닝(샘플)</h3>
    <p class="meta">블로그 구조와 분석 포맷 안내</p>
  </a>
  <a class="doc-card" href="#/posts/theme-notes">
    <h3>테마/팩터 메모(샘플)</h3>
    <p class="meta">주요 섹터 체크리스트와 TODO</p>
  </a>
</div>

## 새 리포트 발행 방법

1. `posts/` 폴더에 새 마크다운 파일을 만듭니다. 예) `2024-q2-earnings.md`
2. `_sidebar.md`에 링크를 추가해 사이드바에 노출합니다.
3. 필요한 경우 README의 카드 섹션에 주요 글을 추가합니다.

## GitHub Pages 배포 가이드

Docsify는 정적 파일만 있으면 실행되므로 별도 빌드가 필요 없습니다.

1. GitHub에 이 프로젝트를 새 저장소로 push합니다.
2. 저장소 `Settings` → `Pages`로 이동합니다.
3. **Source**를 `Deploy from a branch`로, **Branch**를 `main` / `/ (root)`로 지정하고 저장합니다.
4. 잠시 후 표시되는 `https://{username}.github.io/{repo}` 주소로 접속해 확인합니다.
5. 커스텀 도메인이 있다면 동일 페이지에서 `Custom domain`을 설정하고, DNS에 CNAME 레코드를 `username.github.io`로 추가합니다.

로컬 미리보기: `npm install -g docsify-cli` 후 `docsify serve .` 실행. 기본 포트는 `http://localhost:3000`입니다.
