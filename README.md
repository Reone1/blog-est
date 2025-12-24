# blog-est (docsify)

개발/운영자를 위한 README입니다. 페이지에 노출되는 홈 콘텐츠는 `home.md`에서 관리합니다.

## 로컬 미리보기

- 선행 설치(1회): `npm install -g docsify-cli`
- 실행: `docsify serve .`
- 확인: `http://localhost:3000`

## 배포 (GitHub Pages)

1. main 브랜치에 push.
2. GitHub `Settings → Pages`에서 Source를 `Deploy from a branch`, `Branch = main`, `/(root)`로 설정.
3. 빌드 완료 후 `https://reone1.github.io/blog-est/`에서 확인.
4. 커스텀 도메인 사용 시 동일 화면에서 `Custom domain` 설정 후 DNS에 CNAME을 `username.github.io`로 추가.

## 콘텐츠 관리

- 사이트 홈: `home.md`
- 사이드바: `_sidebar.md` (루트 공용)
- 커버페이지: `_coverpage.md`
- 포스트: `posts/*.md`
- 스타일: `styles.css` (테마 기본은 `yntkc-*` CSS 참조)

## SEO/정책 파일

- `robots.txt`, `sitemap.xml`, `.nojekyll` 유지
- `index.html`의 메타/구조화 데이터 갱신 시 canonical/og/twitter URL과 썸네일을 실주소로 교체 필요

## TODO 아이디어

- 포스트별 Article JSON-LD 추가
- `sitemap.xml`에 새 포스트 반영 자동화 (스クリپ트화)
- 대표 썸네일(og/twitter) 교체 및 alt 텍스트 보강
