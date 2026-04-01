# 스케줄 등록 프롬프트

Claude Code Cloud Scheduled Tasks (`claude.ai/code/scheduled`)에 등록할 스케줄 목록.

## 데이터 소스

- **당일 시장 데이터**: `https://totalr.vercel.app/api/market` (기본) 또는 `?type=detail` (종목 상세 포함)
- **과거 분석 데이터**: `posts/` 디렉토리의 기존 daily briefing, weekly review 글에서 축적된 데이터를 참조
- **글 포맷 참조**: `posts/` 의 기존 글(frontmatter, JSON-LD schema, 마크다운 구조)을 동일하게 따를 것
- **프롬프트 가이드라인**: `tools/content-generator/content_generator/prompts/` 의 각 타입별 txt 파일 참조

---

## 1. 데일리 브리핑 (평일 16:00 KST)

이름: `daily-content`
cron: `0 16 * * 1-5` (평일 매일)

```
blog-est 레포에서 다음을 수행해줘:

1. https://totalr.vercel.app/api/market?type=detail 에서 KOSPI/KOSDAQ 시장 데이터를 가져와서 파싱해.
   - 지수 정보 (종가, 등락률)
   - 상승/하락 상위 종목 (종목명, 가격, 등락률)
   - 시총 상위 종목 상세 (PER, PBR, 외국인비율, 거래대금 등)
   - 섹터별 그룹핑

2. tools/content-generator/content_generator/prompts/daily_briefing.txt 가이드라인을 읽고,
   posts/ 의 기존 글 포맷(frontmatter, JSON-LD schema)을 참고해서 오늘자 daily_briefing 글을 생성해.
   - 제공된 데이터에 없는 수치는 절대 만들어내지 말 것
   - 제목은 구체적 종목명/수치 포함, 질문형이나 대시(—) 활용

3. 파일명: posts/YYYY-MM-DD-daily-briefing.md

4. python3 scripts/update_sidebar.py && python3 scripts/update_sitemap.py

5. git add posts/ _sidebar.md sitemap.xml
   커밋 메시지: "content: daily briefing for YYYY-MM-DD"

6. git push origin main
```

---

## 2. 주간 리뷰 (금요일 16:00 KST)

이름: `weekly-review`
cron: `0 16 * * 5` (매주 금요일)

```
blog-est 레포에서 다음을 수행해줘:

1. https://totalr.vercel.app/api/market?type=detail 에서 최신 시장 데이터를 가져와.

2. posts/ 디렉토리에서 이번 주(월~금) 작성된 daily-briefing 글들을 모두 읽어.
   각 글에서 지수 등락, 특징주, 섹터 동향, 시장 심리를 추출해서 주간 흐름을 정리해.

3. tools/content-generator/content_generator/prompts/weekly_review.txt 가이드라인을 읽고,
   posts/ 의 기존 글 포맷(frontmatter, JSON-LD schema)을 참고해서 주간 리뷰를 생성해.
   - 일별 흐름 서술은 실제 daily 글의 데이터를 인용
   - 주간 종합 등락률은 월요일 시가 vs 금요일 종가로 계산

4. 파일명: posts/YYYY-MM-DD-weekly-review.md

5. python3 scripts/update_sidebar.py && python3 scripts/update_sitemap.py

6. git add posts/ _sidebar.md sitemap.xml
   커밋 메시지: "content: weekly review for YYYY-MM-DD"

7. git push origin main
```

---

## 3. 월간 리뷰 (매월 1일 09:00 KST)

이름: `monthly-review`
cron: `0 0 1 * *` (매월 1일)

```
blog-est 레포에서 다음을 수행해줘:

1. https://totalr.vercel.app/api/market?type=detail 에서 최신 시장 데이터를 가져와.

2. posts/ 디렉토리에서 지난달 작성된 모든 글(daily-briefing, weekly-review, std-analysis)을 읽어.
   각 글에서 지수, 특징주, 섹터, 시장 심리 데이터를 추출해서 월간 흐름을 정리해.

3. tools/content-generator/content_generator/prompts/monthly_review.txt 가이드라인을 읽고,
   posts/ 의 기존 글 포맷(frontmatter, JSON-LD schema)을 참고해서 월간 리뷰를 생성해.
   - 주차별 흐름은 weekly-review 글 데이터 인용
   - 월간 등락률은 첫 거래일 시가 vs 마지막 거래일 종가
   - 월간 Best/Worst 종목은 daily 글들에서 반복 등장한 종목 기준

4. 파일명: posts/YYYY-MM-DD-monthly-review.md

5. python3 scripts/update_sidebar.py && python3 scripts/update_sitemap.py

6. git add posts/ _sidebar.md sitemap.xml
   커밋 메시지: "content: monthly review for {지난달}"

7. git push origin main
```

---

## 4. 투자 전략 브리핑 (매월 15일 16:00 KST)

이름: `monthly-strategy`
cron: `0 16 15 * *` (매월 15일)

```
blog-est 레포에서 투자 전략 브리핑을 작성해줘:

1. https://totalr.vercel.app/api/market?type=detail 에서 최신 시장 데이터를 가져와.

2. posts/ 디렉토리에서 이번 달 1일~14일 작성된 daily-briefing 글들을 모두 읽어.
   각 글에서 지수, 등락주, 섹터 동향을 추출해서 이번 달 전반기 흐름을 파악해.

3. posts/ 의 기존 글 포맷(frontmatter, JSON-LD schema)을 참고해서 투자 전략 글을 작성해.

   파일명: posts/YYYY-MM-15-investment-strategy.md

   본문 구조:
   - 도입: 이번 달 전반기 시장 핵심 숫자 요약
   - 시장 체온 체크: daily 글들의 지수 흐름으로 과열/중립/냉각 진단, 공격 vs 방어 판단
   - 섹터 비중 전략: daily 글들에서 반복 강세/약세 섹터 추출, 비중 확대/축소 제안 (ETF 상품명 포함)
   - ETF 투자자 포지션: 포트폴리오 비중 조정 제안, 로테이션 방향
   - 개별주 투자자 포지션: 현금 비중, 매수 검토 조건, 익절/손절 기준
   - 보수적 투자자 포지션: 시총 상위 종목의 PER/PBR/배당수익률 데이터 활용
   - 이번 달 하반기 주요 변수
   - 면책조항

   작성 규칙:
   - 모든 제안에 데이터 근거 필수 (daily 글에서 인용)
   - 매수/매도 추천 금지, 포지션 방향과 비율은 구체적 제안
   - 감정 배제, 숫자 중심, 1500~2500자
   - 이모지 사용 금지

4. python3 scripts/update_sidebar.py && python3 scripts/update_sitemap.py

5. git add posts/ _sidebar.md sitemap.xml
   커밋 메시지: "content: investment strategy briefing for YYYY-MM-15"

6. git push origin main
```
