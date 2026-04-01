# 스케줄 등록 프롬프트

Claude Code `/schedule` 명령어로 등록할 스케줄 목록.
등록 전 `pip install -e ./tools/content-generator` 가 세션 내에서 실행 가능해야 함.

---

## 1. 데일리 브리핑 + 표준편차 분석 (평일 16:00 KST)

```
/schedule create --cron "0 16 * * 1-5" --name "daily-content"
```

프롬프트:
```
blog-est 레포에서 다음을 순서대로 실행해줘:

1. pip install -e ./tools/content-generator
2. python -m content_generator.cli generate --type daily_briefing --output posts/
3. python -m content_generator.cli generate --type std_analysis --output posts/
4. python scripts/update_sidebar.py
5. python scripts/update_sitemap.py
6. python scripts/update_home.py
7. 변경된 파일을 git add 후 커밋 메시지: "content: daily briefing + std analysis for {오늘 날짜}"
8. git push origin main
```

---

## 2. 주간 리뷰 (금요일 16:00 KST)

```
/schedule create --cron "0 16 * * 5" --name "weekly-review"
```

프롬프트:
```
blog-est 레포에서 다음을 순서대로 실행해줘:

1. pip install -e ./tools/content-generator
2. python -m content_generator.cli generate --type weekly_review --output posts/
3. python scripts/update_sidebar.py
4. python scripts/update_sitemap.py
5. python scripts/update_home.py
6. 변경된 파일을 git add 후 커밋 메시지: "content: weekly review for {오늘 날짜}"
7. git push origin main
```

---

## 3. 월간 리뷰 (매월 1일 00:00 KST)

```
/schedule create --cron "0 0 1 * *" --name "monthly-review"
```

프롬프트:
```
blog-est 레포에서 다음을 순서대로 실행해줘:

1. pip install -e ./tools/content-generator
2. python -m content_generator.cli generate --type monthly_review --output posts/
3. python scripts/update_sidebar.py
4. python scripts/update_sitemap.py
5. python scripts/update_home.py
6. 변경된 파일을 git add 후 커밋 메시지: "content: monthly review for {지난달}"
7. git push origin main
```

---

## 4. 투자 전략 브리핑 (매월 15일 16:00 KST)

```
/schedule create --cron "0 16 15 * *" --name "monthly-strategy"
```

프롬프트:
```
blog-est 레포에서 투자 스타일별 전략 브리핑을 작성해줘.

1. pip install -e ./tools/content-generator

2. 먼저 최근 시장 데이터를 수집해:
   - 이번 달 1일~14일 코스피/코스닥 흐름 (등락률, 거래대금 추이)
   - 외국인/기관 수급 동향 (순매수 상위 섹터)
   - 섹터별 등락률 TOP 5 / BOTTOM 5
   - 금리/환율/유가 등 매크로 지표 변화
   - 주요 섹터 ETF 수익률 비교

3. 수집한 데이터를 기반으로 posts/ 에 아래 형식의 마크다운 글을 작성해:

   파일명: posts/YYYY-MM-15-investment-strategy.md

   frontmatter:
   ---
   title: "{MM}월 중간점검 — 시장 데이터가 말하는 포지션 전략"
   date: {오늘 날짜}
   type: investment_strategy
   category: 투자 전략
   ---

   본문 구조:

   - 도입: 이번 달 전반기 시장 핵심 숫자 요약 (지수 등락, 수급 방향, 변동성 수준)

   - ## 시장 체온 체크
     현재 시장이 어떤 국면인지 데이터로 진단 (과열/중립/냉각).
     코스피 이동평균선 대비 위치, VIX 수준, 외국인 수급 방향 등을 근거로.
     이 국면에서 공격적 포지션이 유리한지, 방어적 포지션이 유리한지 판단.

   - ## 섹터 비중 전략
     이번 달 섹터별 수익률과 수급 데이터를 기반으로:
     - 비중 확대 검토 섹터 (상승 모멘텀 + 외국인/기관 순매수 유입)
     - 비중 축소 검토 섹터 (하락 전환 + 수급 이탈)
     - 관망 섹터 (방향성 불분명)
     구체적인 섹터 ETF 상품명 포함 (KODEX, TIGER 등).

   - ## ETF 투자자 포지션
     현재 시장 국면에 맞는 ETF 포트폴리오 비중 조정 제안.
     예: "방어형 40% → 30%, 성장형 30% → 40%로 비중 이동 검토"
     섹터 ETF 로테이션 방향, 레버리지/인버스 활용 여부.

   - ## 개별주 투자자 포지션
     실적 시즌/수급/모멘텀 기반으로:
     - 현금 비중 제안 (예: "변동성 확대 구간이므로 현금 30% 유지 권장")
     - 매수 검토 조건 (예: "외국인 5일 연속 순매수 + 20일선 지지 확인 시")
     - 익절/손절 기준 제안
     - 주목할 테마/업종

   - ## 보수적 투자자 포지션
     금리 환경 기반 채권형 ETF 매력도.
     고배당주 현황 (배당수익률 vs 예금금리 비교).
     현금+배당+채권 비율 제안.

   - ## 이번 달 하반기 주요 변수
     실적 발표 일정, 금리 결정, 정책 이벤트, 옵션 만기 등
     각 이벤트가 포지션에 미칠 영향 간략 분석.

   - 면책조항

   작성 규칙:
   - 모든 제안은 반드시 데이터 근거를 함께 제시 (예: "코스피 20일선 2,580 대비 현재 2,650으로 +2.7% 위에 위치")
   - 매수/매도 추천은 하지 않되, 포지션 방향과 비율은 구체적으로 제안
   - "~를 검토해볼 만하다", "~비중을 높이는 전략이 유효해 보인다" 등 제안 톤
   - 감정 배제, 숫자 중심
   - 1500~2500자

4. python scripts/update_sidebar.py
5. python scripts/update_sitemap.py
6. python scripts/update_home.py
7. 변경된 파일을 git add 후 커밋 메시지: "content: investment strategy briefing for {오늘 날짜}"
8. git push origin main
```
