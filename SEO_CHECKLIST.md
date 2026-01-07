# SEO 체크리스트

새로운 콘텐츠를 추가할 때 반드시 확인해야 할 SEO 최적화 항목입니다.

---

## 포스트 작성 시 필수 체크리스트

### 1. Front Matter 메타데이터 (필수)

모든 포스트 파일 최상단에 YAML Front Matter를 추가합니다:

```yaml
---
title: "포스트 제목 (60자 이내 권장)"
description: "포스트 요약 설명 (155자 이내)"
date: YYYY-MM-DD
author: "한국 주식시장 분석 블로그"
category: "카테고리명"
tags: ["태그1", "태그2", "태그3"]
image: "https://reone1.github.io/blog-est/assets/포스트-og-image.png"
---
```

### 2. Article Schema (필수)

Front Matter 바로 아래에 JSON-LD 구조화 데이터를 추가합니다:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "포스트 제목",
  "description": "포스트 요약 설명",
  "image": "https://reone1.github.io/blog-est/assets/포스트-og-image.png",
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "author": {
    "@type": "Person",
    "name": "한국 주식시장 분석 블로그",
    "url": "https://reone1.github.io/blog-est/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "한국 주식시장 분석 블로그",
    "logo": {
      "@type": "ImageObject",
      "url": "https://reone1.github.io/blog-est/assets/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://reone1.github.io/blog-est/#/posts/파일명"
  },
  "keywords": ["키워드1", "키워드2", "키워드3"]
}
</script>
```

### 3. sitemap.xml 업데이트 (필수)

새 포스트 추가 시 `sitemap.xml`에 URL을 등록합니다:

```xml
<url>
  <loc>https://reone1.github.io/blog-est/#/posts/새-포스트-파일명</loc>
  <lastmod>YYYY-MM-DD</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

### 4. _sidebar.md 업데이트 (필수)

사이드바에 새 포스트 링크를 추가합니다:

```markdown
- [포스트 제목](posts/파일명.md)
```

---

## 콘텐츠 작성 가이드라인

### 제목 최적화
- [ ] H1 태그는 페이지당 1개만 사용
- [ ] 제목에 핵심 키워드 포함
- [ ] 60자 이내로 작성

### 본문 구조
- [ ] H2, H3 태그로 명확한 계층 구조 유지
- [ ] 첫 단락에 핵심 키워드 자연스럽게 포함
- [ ] 표, 리스트, 인용구로 가독성 향상
- [ ] 내부 링크 (다른 포스트) 적극 활용

### 이미지 최적화
- [ ] 의미 있는 파일명 사용 (`image-001.png` ❌ → `etf-performance-chart.png` ✅)
- [ ] alt 텍스트 필수 작성
- [ ] 이미지 용량 최적화 (WebP 권장, 500KB 이하)

---

## 배포 전 최종 체크

### 기술 SEO
- [ ] 모든 URL이 정상 작동하는지 확인
- [ ] sitemap.xml에 새 URL 추가됨
- [ ] _sidebar.md에 링크 추가됨
- [ ] Front Matter 메타데이터 완성
- [ ] Article Schema JSON-LD 추가

### 콘텐츠 품질
- [ ] 제목이 명확하고 클릭을 유도하는지
- [ ] 설명이 콘텐츠를 정확히 요약하는지
- [ ] 본문이 충분한 가치를 제공하는지 (최소 800자 권장)
- [ ] 오탈자 및 문법 오류 검수

---

## 정기 점검 항목 (월 1회)

### sitemap.xml 점검
- [ ] 모든 포스트 URL이 등록되어 있는지 확인
- [ ] lastmod 날짜가 최신인지 확인
- [ ] 삭제된 포스트 URL 제거

### Schema 검증
- Google Rich Results Test로 구조화 데이터 검증:
  https://search.google.com/test/rich-results

### 검색 콘솔 점검
- Google Search Console에서 색인 상태 확인
- 크롤링 오류 해결

---

## 포스트 템플릿

새 포스트 작성 시 아래 템플릿을 복사하여 사용하세요:

```markdown
---
title: ""
description: ""
date: YYYY-MM-DD
author: "한국 주식시장 분석 블로그"
category: ""
tags: []
image: "https://reone1.github.io/blog-est/assets/og-image.png"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "",
  "description": "",
  "image": "https://reone1.github.io/blog-est/assets/og-image.png",
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "author": {
    "@type": "Person",
    "name": "한국 주식시장 분석 블로그",
    "url": "https://reone1.github.io/blog-est/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "한국 주식시장 분석 블로그",
    "logo": {
      "@type": "ImageObject",
      "url": "https://reone1.github.io/blog-est/assets/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://reone1.github.io/blog-est/#/posts/파일명"
  },
  "keywords": []
}
</script>

# 제목

## 서론

본문 내용...

## 본론

### 소제목 1

내용...

### 소제목 2

내용...

## 결론

요약 및 마무리...
```

---

## AI SEO 최적화 팁

AI 검색엔진(ChatGPT, Perplexity, Claude 등)에서 콘텐츠가 잘 인용되려면:

1. **명확한 질문-답변 구조**: 독자가 가질 수 있는 질문에 직접 답하는 형식
2. **데이터 기반 분석**: 수치, 통계, 팩트를 풍부하게 포함
3. **전문성 표현**: 출처 명시, 전문 용어 적절히 사용
4. **구조화된 정보**: 표, 리스트, 요약 박스 활용
5. **고유한 인사이트**: 다른 곳에서 찾기 어려운 독자적 분석

---

## 파일 체크리스트

| 파일 | 수정 필요 | 체크 |
|------|----------|------|
| `posts/새포스트.md` | Front Matter + Schema | [ ] |
| `_sidebar.md` | 링크 추가 | [ ] |
| `sitemap.xml` | URL 추가 | [ ] |
| `assets/` | OG 이미지 (선택) | [ ] |
