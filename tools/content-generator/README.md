# Content Generator

AI 기반 투자정보 블로그 콘텐츠 생성기

## 기능

- Claude API를 활용한 자동 콘텐츠 생성
- 다양한 콘텐츠 유형 지원
  - 시장 데일리 브리핑
  - 표준편차 매매 분석
  - 섹터/테마 분석
  - 주간/월간 리뷰
  - 개별 종목 리포트

## 설치

```bash
pip install -e .
```

## 사용법

```bash
# 환경변수 설정
export ANTHROPIC_API_KEY=your-api-key

# 데일리 브리핑 생성
generate --type daily_briefing --output posts/

# 표준편차 분석 생성
generate --type std_analysis --output posts/

# 사용 가능한 콘텐츠 유형 확인
generate list-types

# API 연결 테스트
generate test-connection
```

## 환경변수

- `ANTHROPIC_API_KEY`: Claude API 키 (필수)

## 라이선스

MIT
