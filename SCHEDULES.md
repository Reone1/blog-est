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
   - 이번 달 1일~14일 코스피/코스닥 흐름
   - 외국인/기관 수급 동향
   - 주요 섹터별 등락률
   - 금리/환율/유가 등 매크로 지표

3. 수집한 데이터를 기반으로 posts/ 에 아래 형식의 마크다운 글을 작성해:

   파일명: posts/YYYY-MM-15-investment-strategy.md

   frontmatter:
   ---
   title: "{MM}월 중간점검 — 투자 스타일별 전략 브리핑"
   date: {오늘 날짜}
   type: investment_strategy
   category: 투자 전략
   ---

   본문 구조:
   - 도입: 이번 달 전반기 시장 요약 (2~3문장)
   - ## ETF 투자자: 현재 시장에서 어떤 ETF 비중 조정이 유리한지 (방어 vs 성장, 섹터 ETF 로테이션, 구체적 상품명 포함)
   - ## 개별주 투자자: 실적/수급/모멘텀 기반 종목 방향성, 현금 비중 조절 제안
   - ## 보수적 투자자: 배당주, 채권형 ETF, 현금 비중 등 안정적 전략
   - ## 이번 달 하반기 주목 포인트: 실적 발표, 정책 이벤트, 글로벌 변수
   - 면책조항

   작성 규칙:
   - 데이터 기반 분석, 감정 배제
   - 구체적인 ETF/종목명 언급 가능하되 "매수/매도 추천"은 하지 않음
   - "~를 검토해볼 만하다", "~에 비중을 높이는 전략이 유효해 보인다" 등 제안 톤
   - 1500~2500자

4. python scripts/update_sidebar.py
5. python scripts/update_sitemap.py
6. python scripts/update_home.py
7. 변경된 파일을 git add 후 커밋 메시지: "content: investment strategy briefing for {오늘 날짜}"
8. git push origin main
```
