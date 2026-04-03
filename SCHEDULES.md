# 스케줄 등록 프롬프트

Claude Code Cloud Scheduled Tasks (`claude.ai/code/scheduled`)에 등록할 스케줄 목록.

## 데이터 소스

- **시장 데이터 API**: `https://totalr.vercel.app/api/market`
  - 지수 기본 (종가, 등락률)
  - 상승/하락 Top 10 종목
  - 시총 Top 20 종목
  - **투자자별 수급** (개인/외국인/기관 순매매)
  - **프로그램 매매** 동향
  - **상승/하락/상한/하한 종목수**
  - **79개 업종별 등락률**
  - `?type=detail` 추가 시: 시총 상위 종목 PER/PBR/배당/외국인비율 포함
- **글 포맷**: 트리거 프롬프트에 템플릿 직접 포함 (파일 읽기 불필요)
- **템플릿 원본**: `tools/content-generator/content_generator/templates/`

---

## 1. 데일리 브리핑 (평일 07:00 UTC / 16:00 KST)

이름: `daily-content`
cron: `0 7 * * 1-5` (평일 매일)

```
blog-est 레포에서 다음을 수행해줘:

1. https://totalr.vercel.app/api/market 에서 KOSPI/KOSDAQ 시장 데이터를 가져와서 파싱해.

2. 아래 템플릿과 가이드라인에 따라 오늘자 daily briefing 글을 바로 작성해. 다른 파일을 읽지 말고 이 프롬프트의 정보만으로 작성할 것.

파일명: posts/YYYY-MM-DD-daily-briefing.md

## 포맷 템플릿

---
title: "{제목}"
date: {YYYY-MM-DDTHH:MM:SS}
tags: ['한국주식', '시장분석', '데일리', '시황']
summary: "{3-4문장 핵심 요약}"
type: daily_briefing
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{제목}",
  "description": "{summary와 동일}",
  "datePublished": "{YYYY-MM-DD}",
  "dateModified": "{YYYY-MM-DD}",
  "author": { "@type": "Organization", "name": "스토쿼트" },
  "publisher": { "@type": "Organization", "name": "스토쿼트", "logo": { "@type": "ImageObject", "url": "https://totalr.vercel.app/assets/logo.svg" } },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://totalr.vercel.app/posts/{YYYY-MM-DD}-daily-briefing" },
  "image": "https://totalr.vercel.app/assets/og-image.svg"
}
</script>

# {제목}

{도입 단락 2-3문장}

## 주요 지수 동향
### KOSPI: {종가} ({등락률}%)
{장중 흐름, 업종별 분석 3-4문장}
### KOSDAQ: {종가} ({등락률}%)
{특징 2-3문장}

## {핵심 이슈 섹션}
{당일 시장을 움직인 악재/호재. H3 소제목으로 분리. 각 3-4문장.}

## 대형주 등락 현황
| 종목명 | 등락률 | 배경 |
|--------|--------|------|

## 상한가/하한가 종목
{테마별 테이블 + 원인}

## 업종 동향
{API의 industry 데이터에서 강세/약세 상위 5개 업종 테이블}

## 수급 동향
| 투자주체 | 순매매 | 비고 |
|----------|--------|------|
| 외국인 | {API investor.foreignValue} | |
| 개인 | {API investor.personalValue} | |
| 기관 | {API investor.institutionalValue} | |
{수급 해석 2-3문장}

## 내일 주목 포인트
{3-4개 H3 소제목. 각 2-3문장.}

---
**면책 조항**: 본 콘텐츠는 투자 권유가 아닌 정보 제공 목적으로 작성되었습니다. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.

## 작성 규칙
- 제목: 핵심 종목명/수치 포함, 대시(—) 활용, 이모지 금지
- 총 4,000-6,000자
- 표 2-3개 (종목 테이블, 수급 테이블)
- 전문적이되 읽기 쉬운 문체
- 데이터에 없는 내용을 지어내지 말 것

3. python3 scripts/update_sidebar.py && python3 scripts/update_sitemap.py && python3 scripts/update_home.py
4. git add 후 커밋 메시지: "content: daily briefing for YYYY-MM-DD"
5. git push origin main
```

---

## 2. 주간 리뷰 (금요일 07:00 UTC / 16:00 KST)

이름: `weekly-review`
cron: `0 7 * * 5` (매주 금요일)

```
blog-est 레포에서 다음을 수행해줘:

1. https://totalr.vercel.app/api/market 에서 최신 시장 데이터를 가져와.

2. posts/ 디렉토리에서 이번 주 작성된 daily briefing 글들의 제목(title)과 핵심 요약(summary)만 확인해서 주간 흐름을 파악해. 본문 전체를 읽을 필요 없이 frontmatter만 확인할 것.

3. 아래 템플릿과 가이드라인에 따라 주간 리뷰를 바로 작성해.

파일명: posts/YYYY-MM-DD-weekly-review.md

## 포맷 템플릿

---
title: "{제목}"
date: {YYYY-MM-DDTHH:MM:SS}
tags: ['한국주식', '시장분석', '주간리뷰', '시황']
summary: "{4-5문장 주간 총평}"
type: weekly_review
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{제목}",
  "description": "{summary와 동일}",
  "datePublished": "{YYYY-MM-DD}",
  "dateModified": "{YYYY-MM-DD}",
  "author": { "@type": "Organization", "name": "스토쿼트" },
  "publisher": { "@type": "Organization", "name": "스토쿼트", "logo": { "@type": "ImageObject", "url": "https://totalr.vercel.app/assets/logo.svg" } },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://totalr.vercel.app/posts/{YYYY-MM-DD}-weekly-review" },
  "image": "https://totalr.vercel.app/assets/og-image.svg"
}
</script>

# {제목}

{주간 총평 4-5문장}

## 주간 지수 동향
### KOSPI 주간 흐름
{일별 흐름, 주간 종합 등락률, 기술적 분석 3-4문장}
### KOSDAQ 주간 흐름
{일별 흐름, 주간 종합 등락률 2-3문장}

## 주간 주요 이슈
### {이슈 1}
{배경, 시장 영향, 향후 시사점 3-4문장}
{이슈 2~5 동일 구조}

## 섹터 성과 분석
### 강세 섹터
| 섹터 | 주간 등락률 | 원인 |
|------|-----------|------|
### 약세 섹터
| 섹터 | 주간 등락률 | 원인 |
|------|-----------|------|
{섹터 로테이션 분석 2-3문장}

## 주간 특징주
### 상승률 Top 5
| 종목명 | 등락률 | 상승 원인 |
|--------|--------|----------|
### 하락률 Top 5
| 종목명 | 등락률 | 하락 원인 |
|--------|--------|----------|

## 수급 분석
| 투자주체 | 주간 순매매 | 주요 매매 종목 |
|----------|-----------|--------------|
| 외국인 | | |
| 기관 | | |
| 개인 | | |
{수급 해석 2-3문장}

## 다음 주 전망
### 주요 이벤트
{국내외 이벤트 목록}
### 기술적 전망
{예상 레인지, 지지/저항선}
### 모니터링 포인트
{3-5개 항목}

---
**면책 조항**: 본 콘텐츠는 투자 권유가 아닌 정보 제공 목적으로 작성되었습니다. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.

## 작성 규칙
- 제목: 주간 핵심 수치와 다음 주 전망 포함, 이모지 금지
- 총 5,000-7,000자
- 주간 성과 테이블, 섹터 비교 테이블 필수
- 차분하고 분석적인 문체
- 데이터에 없는 내용을 지어내지 말 것

4. python3 scripts/update_sidebar.py && python3 scripts/update_sitemap.py && python3 scripts/update_home.py
5. git add 후 커밋 메시지: "content: weekly review for YYYY-MM-DD"
6. git push origin main
```

---

## 3. 월간 리뷰 + 투자 전략 (매월 1일/15일 00:00 UTC / 09:00 KST)

이름: `monthly-review-and-strategy`
cron: `0 0 1,15 * *` (매월 1일, 15일)

```
blog-est 레포에서 다음을 순서대로 실행해줘:

1. pip install -e ./tools/content-generator

2. 오늘 날짜를 확인해서 작업을 결정해:

   A) 매월 1일인 경우 — 월간 리뷰 작성:
      - python -m content_generator.cli generate --type monthly_review --output posts/

   B) 매월 15일인 경우 — 투자 전략 브리핑 작성:
      - 먼저 시장 데이터를 수집해:
        a) https://totalr.vercel.app/api/market 에서 최신 KOSPI/KOSDAQ 데이터를 가져와
        b) posts/ 디렉토리에서 이번 달 1일~14일 작성된 daily briefing 글들을 모두 읽어서 시장 흐름을 파악해
      - 수집한 데이터를 기반으로 posts/ 에 마크다운 글 작성:
        파일명: posts/YYYY-MM-15-investment-strategy.md
        frontmatter:
          title: "{MM}월 중간점검 — 시장 데이터가 말하는 포지션 전략"
          date: {오늘 날짜}
          type: investment_strategy
          category: 투자 전략
        기존 posts/ 글의 frontmatter, JSON-LD schema 포맷을 동일하게 따를 것.
        본문 구조:
        - 도입: 이번 달 전반기 시장 핵심 숫자 요약
        - 시장 체온 체크: 과열/중립/냉각 데이터 진단, 공격 vs 방어 판단
        - 섹터 비중 전략: 비중 확대/축소/관망 섹터 (구체적 ETF 상품명 포함)
        - ETF 투자자 포지션: 포트폴리오 비중 조정 제안, 로테이션 방향
        - 개별주 투자자 포지션: 현금 비중 %, 매수 검토 조건, 익절/손절 기준
        - 보수적 투자자 포지션: 채권형 ETF 매력도, 배당수익률 vs 예금금리, 비율 제안
        - 이번 달 하반기 주요 변수: 실적 발표, 금리, 정책, 옵션 만기
        - 면책조항
        작성 규칙:
        - 모든 제안에 데이터 근거 필수
        - 매수/매도 추천 금지, 포지션 방향과 비율은 구체적 제안
        - 감정 배제, 숫자 중심, 1500~2500자

3. python3 scripts/update_sidebar.py
4. python3 scripts/update_sitemap.py
5. python3 scripts/update_home.py
6. 변경된 파일을 git add 후 커밋:
   - 1일인 경우: "content: monthly review for {지난달}"
   - 15일인 경우: "content: investment strategy briefing for {오늘 날짜}"
7. git push origin main
```
