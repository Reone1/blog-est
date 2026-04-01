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
