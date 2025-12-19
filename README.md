# Docsify Blog

Docsify(문서화 툴)을 사용해 GitHub Pages에서 바로 쓸 수 있는 블로그 기본 템플릿입니다.

## 시작하기

- 로컬 프리뷰: `npx docsify serve .`
- 배포: GitHub Pages에서 루트 또는 `docs/` 폴더를 선택하면 바로 동작합니다.

## 구조

- `index.html` — Docsify 설정
- `_sidebar.md` — 전역 사이드바 내비게이션
- `coverpage.md` — 첫 화면 히어로 영역
- `posts/` — 블로그 글 폴더

## 최근 글

<div class="doc-cards">
  <a class="doc-card" href="posts/hello-world.md">
    <h3>첫 포스트: 시작하기</h3>
    <p class="meta">Docsify 설치와 글 작성 흐름</p>
  </a>
  <a class="doc-card" href="posts/theme-notes.md">
    <h3>테마 커스터마이징</h3>
    <p class="meta">색상·폰트 조정 가이드</p>
  </a>
</div>

## 다음 단계

- `coverpage.md`의 타이틀과 링크를 프로젝트에 맞게 수정하세요.
- `posts/`에 마크다운 파일을 추가하면 자동으로 블로그 글로 노출됩니다.
- 필요하면 `styles.css`에서 색상이나 폰트를 변경해 브랜드를 맞출 수 있습니다.
