# Repository Guidelines

## Project Structure & Module Organization
- Root content lives in Markdown files: `home.md` (landing), `_sidebar.md` (global nav), and `posts/*.md` (articles).
- `index.html` boots Docsify and contains SEO/meta tags, JSON-LD, and script includes.
- Styling is split between theme CSS (`yntkc-*.css`) and local overrides in `styles.css`.
- Static site helpers live at the root: `robots.txt` and `sitemap.xml`. Vendor assets are in `vendor/`.

## Build, Test, and Development Commands
- `npm install -g docsify-cli` (one-time) installs the local preview server.
- `docsify serve .` runs the site at `http://localhost:3000` for manual review.
- Deployment has no build step: push to `main` and GitHub Pages serves from `/(root)`.

## Coding Style & Naming Conventions
- Use Markdown for content; keep headings concise and use relative links within the site.
- Posts follow a kebab-case slug: `posts/<topic-slug>.md`.
- Keep `index.html` formatting consistent (2-space indentation) and avoid non-ASCII where possible.
- Put custom CSS in `styles.css`; avoid editing theme CSS unless updating the theme itself.

## Testing Guidelines
- No automated tests are configured. Validate changes by:
  - Running `docsify serve .` and clicking through the sidebar and new links.
  - Checking mobile/desktop layout after CSS changes.
  - Confirming SEO tags and JSON-LD in `index.html` when metadata changes.

## Commit & Pull Request Guidelines
- Commit history uses short messages like `update - <detail>`; follow the same pattern.
- PRs should include a brief summary, list of pages updated, and screenshots for visual/CSS changes.
- Note any sitemap or metadata updates in the PR description.

## 한국어 규칙 안내
- 신규 글은 `posts/<topic-slug>.md`에 추가하고 `_sidebar.md` 링크를 갱신합니다.
- 미리보기는 `docsify serve .`로 확인하고 모바일/데스크톱 레이아웃을 점검합니다.
- SEO 변경 시 `index.html`의 canonical/OG/Twitter URL과 JSON-LD를 검토합니다.
- 커밋 메시지는 `update - <detail>` 형식을 유지합니다.

## Content & SEO Notes
- Keep `robots.txt` and `sitemap.xml` in sync with new posts.
- Replace canonical/OG/Twitter URLs in `index.html` with the real domain when publishing.
