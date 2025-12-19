# 첫 포스트: 시작하기

Docsify 기반 블로그 템플릿이 준비됐습니다. 여기서 새 글을 작성해 보세요.

## 글 작성 방법

1. `posts/` 폴더에 새 마크다운 파일을 만듭니다. 예) `2024-hello.md`
2. `_sidebar.md`에 링크를 추가하면 사이드바에 나타납니다.
3. 커버 페이지나 홈에서 원하는 곳으로 연결하세요.

```bash
# 예시
echo "# 새 글" > posts/2024-new.md
```

## 마크다운 예시

- **굵게**, _기울임_, ~~취소선~~
- [링크](https://docsify.js.org)와 이미지
- 코드 블록:

```javascript
const greet = (name) => `Hello, ${name}!`;
console.log(greet('Docsify'));
```
