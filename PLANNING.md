# AI 투자정보 블로그 자동화 시스템 기획서

## 1. 프로젝트 개요

### 1.1 목표
AI(Claude API)를 활용하여 매일 투자정보를 분석하고 블로그 형태로 자동 배포하는 시스템 구축

### 1.2 핵심 요구사항
- **AI 모델**: Claude API (Anthropic)
- **인프라**: GitHub Actions 기반 자동화
- **워크플로우**: AI 생성 → 리뷰(PR) → 승인 후 배포
- **콘텐츠 유형**:
  - 시장 데일리 브리핑
  - 섹터/테마 분석
  - 개별 종목 리포트
  - 주간/월간 리뷰
  - 표준편차 매매 기법 기반 분석

---

## 2. 현재 시스템 분석

### 2.1 기존 구성요소

```
blog-est/
├── 📄 Docsify 블로그 (프론트엔드)
│   ├── index.html      # 진입점, SEO 설정
│   ├── home.md         # 홈페이지
│   ├── posts/*.md      # 블로그 포스트
│   └── _sidebar.md     # 네비게이션
│
└── 🔧 tools/stock-researcher/ (데이터 수집)
    ├── cli.py          # CLI 인터페이스
    ├── mcp_server.py   # MCP 서버 (Claude 연동)
    ├── kr_market.py    # 한국 시장 데이터 (pykrx)
    └── us_market.py    # 미국 시장 데이터 (yfinance)
```

### 2.2 현재 기능
| 모듈 | 기능 | 상태 |
|------|------|------|
| stock-researcher | 시가총액 TOP, 급등/급락주, 섹터별 조회 | ✅ 완료 |
| Docsify 블로그 | 마크다운 렌더링, SEO | ✅ 완료 |
| 콘텐츠 생성 | AI 기반 자동 생성 | ❌ 미구현 |
| 자동화 파이프라인 | 스케줄링, PR 생성 | ❌ 미구현 |

### 2.3 Gap 분석
1. **데이터 수집 확장 필요**: 표준편차/변동성 지표 추가
2. **AI 콘텐츠 생성기 필요**: Claude API 연동 모듈
3. **자동화 파이프라인 필요**: GitHub Actions 워크플로우
4. **리뷰 시스템 필요**: Draft PR 생성 및 승인 프로세스

---

## 3. 목표 시스템 아키텍처

### 3.1 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Scheduler)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Daily 08:00 │  │ Weekly Mon  │  │ Monthly 1st │              │
│  │   KST       │  │   09:00     │  │   09:00     │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Content Generator                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Data Collector  │──│ Prompt Builder  │──│ Claude API       │ │
│  │ (stock-research)│  │ (templates)     │  │ (content gen)    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Post Processor                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Markdown Gen    │──│ Sidebar Update  │──│ Sitemap Update   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘ │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Review & Deploy                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Create PR       │──│ Human Review    │──│ Merge & Deploy   │ │
│  │ (draft)         │  │ (approve/edit)  │  │ (GitHub Pages)   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 데이터 플로우

```
[Market Data Sources]
        │
        ▼
┌───────────────────┐
│  pykrx (한국)     │──┐
│  yfinance (미국)  │  │
└───────────────────┘  │
        │              │
        ▼              ▼
┌───────────────────────────────────────┐
│        Aggregated Market Data          │
│  - 지수 데이터 (KOSPI, KOSDAQ, S&P500) │
│  - 급등/급락 종목                      │
│  - 섹터별 동향                         │
│  - 표준편차/변동성 지표                │
│  - 거래량 분석                         │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│        Content Type Router             │
├───────────────────────────────────────┤
│  daily_briefing   → 매일 장마감 후    │
│  sector_analysis  → 주 2-3회          │
│  stock_report     → 주요 이벤트 시    │
│  weekly_review    → 매주 금요일       │
│  monthly_review   → 매월 첫째 주      │
│  std_analysis     → 매일 (변동성 기반)│
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│         Prompt Template               │
│  + 시장 데이터                        │
│  + 콘텐츠 유형별 지침                 │
│  + 톤/스타일 가이드                   │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│         Claude API                    │
│  model: claude-sonnet-4-20250514      │
│  max_tokens: 4000                     │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│         Generated Markdown            │
│  posts/YYYY-MM-DD-{type}.md          │
└───────────────────────────────────────┘
```

---

## 4. 컴포넌트 상세 설계

### 4.1 데이터 수집 확장 (stock-researcher 업그레이드)

#### 신규 기능 추가
```python
# 추가 모듈: stock_researcher/analytics.py

class MarketAnalytics:
    """시장 분석 지표 계산"""

    def get_volatility_analysis(self, ticker: str, period: int = 20) -> dict:
        """표준편차 기반 변동성 분석"""
        # - 20일 이동 표준편차
        # - 볼린저 밴드 위치
        # - 변동성 백분위

    def get_std_signals(self, market: str = "kr") -> list[StdSignal]:
        """표준편차 매매 시그널 생성"""
        # - 2σ 이탈 종목 탐지
        # - 평균 회귀 가능성 판단

    def get_market_breadth(self, market: str = "kr") -> dict:
        """시장 심리 지표"""
        # - 상승/하락 종목 비율
        # - 신고가/신저가 종목
        # - 거래대금 집중도
```

#### 데이터 모델 확장
```python
# stock_researcher/models.py 확장

@dataclass
class VolatilityData:
    ticker: str
    std_20d: float          # 20일 표준편차
    std_60d: float          # 60일 표준편차
    bollinger_position: float  # 볼린저 밴드 내 위치 (0-1)
    zscore: float           # Z-score
    signal: str             # "oversold" | "neutral" | "overbought"

@dataclass
class MarketBreadth:
    date: str
    advance_decline_ratio: float
    new_highs: int
    new_lows: int
    volume_breadth: float
```

### 4.2 콘텐츠 생성기 (신규)

#### 디렉토리 구조
```
tools/content-generator/
├── pyproject.toml
├── content_generator/
│   ├── __init__.py
│   ├── generator.py        # 메인 생성기
│   ├── prompts/            # 프롬프트 템플릿
│   │   ├── daily_briefing.txt
│   │   ├── sector_analysis.txt
│   │   ├── stock_report.txt
│   │   ├── weekly_review.txt
│   │   ├── monthly_review.txt
│   │   └── std_analysis.txt
│   ├── templates/          # 마크다운 템플릿
│   │   └── post_template.md
│   └── claude_client.py    # Claude API 클라이언트
└── tests/
```

#### 핵심 클래스
```python
# content_generator/generator.py

class ContentGenerator:
    def __init__(self, claude_api_key: str):
        self.claude = ClaudeClient(api_key=claude_api_key)
        self.stock_researcher = StockResearcher()

    async def generate_daily_briefing(self, date: str) -> BlogPost:
        """데일리 브리핑 생성"""
        # 1. 시장 데이터 수집
        market_data = await self._collect_market_data(date)

        # 2. 프롬프트 구성
        prompt = self._build_prompt("daily_briefing", market_data)

        # 3. Claude API 호출
        content = await self.claude.generate(prompt)

        # 4. 마크다운 포맷팅
        return self._format_post(content, "daily", date)

    async def generate_std_analysis(self, date: str) -> BlogPost:
        """표준편차 기반 매매 분석"""
        # 표준편차 시그널 수집
        signals = self.stock_researcher.get_std_signals()

        # 분석 콘텐츠 생성
        ...
```

#### 프롬프트 템플릿 예시
```
# prompts/daily_briefing.txt

당신은 한국 주식시장 전문 애널리스트입니다.

오늘의 시장 데이터를 바탕으로 투자자들에게 유용한 데일리 브리핑을 작성해주세요.

## 데이터
{market_data}

## 작성 가이드라인
1. 객관적 사실 중심의 분석
2. 주요 지수 동향 요약 (2-3문장)
3. 특이 섹터/테마 분석
4. 급등락 주요 종목 및 이유 추정
5. 다음 거래일 주목 포인트

## 형식
- 마크다운 형식
- 총 800-1200자
- 표는 3개 이하
- 투자 권유가 아닌 정보 제공 목적 명시

## 면책 조항
글 말미에 "본 콘텐츠는 투자 권유가 아닌 정보 제공 목적으로 작성되었습니다." 포함
```

### 4.3 자동화 워크플로우 (GitHub Actions)

#### 워크플로우 파일
```yaml
# .github/workflows/generate-content.yml

name: Generate Daily Content

on:
  schedule:
    # 한국 시간 오후 4시 (장마감 후)
    - cron: '0 7 * * 1-5'  # UTC 07:00 = KST 16:00
  workflow_dispatch:
    inputs:
      content_type:
        description: '콘텐츠 유형'
        required: true
        default: 'daily_briefing'
        type: choice
        options:
          - daily_briefing
          - sector_analysis
          - std_analysis
          - weekly_review

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ./tools/stock-researcher
          pip install -e ./tools/content-generator

      - name: Generate content
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python -m content_generator generate \
            --type ${{ inputs.content_type || 'daily_briefing' }} \
            --output posts/

      - name: Update sidebar
        run: python scripts/update_sidebar.py

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "content: Add ${{ inputs.content_type }} for $(date +%Y-%m-%d)"
          title: "[AI Generated] ${{ inputs.content_type }} - $(date +%Y-%m-%d)"
          body: |
            ## 자동 생성된 콘텐츠

            - **유형**: ${{ inputs.content_type }}
            - **생성일**: $(date +%Y-%m-%d)

            ### 리뷰 체크리스트
            - [ ] 내용 정확성 확인
            - [ ] 문법/맞춤법 검토
            - [ ] 면책조항 포함 확인
            - [ ] 링크/이미지 정상 동작

            ---
            🤖 이 PR은 AI에 의해 자동 생성되었습니다.
          branch: content/auto-${{ github.run_id }}
          draft: true
          labels: |
            ai-generated
            needs-review
```

#### 주간/월간 워크플로우
```yaml
# .github/workflows/generate-review.yml

name: Generate Weekly/Monthly Review

on:
  schedule:
    # 금요일 오후 5시 (주간 리뷰)
    - cron: '0 8 * * 5'  # UTC 08:00 = KST 17:00
    # 매월 1일 오전 9시 (월간 리뷰)
    - cron: '0 0 1 * *'  # UTC 00:00 = KST 09:00

jobs:
  weekly:
    if: github.event.schedule == '0 8 * * 5'
    # ... 주간 리뷰 생성

  monthly:
    if: github.event.schedule == '0 0 1 * *'
    # ... 월간 리뷰 생성
```

### 4.4 포스트 프로세서

#### Sidebar 자동 업데이트
```python
# scripts/update_sidebar.py

def update_sidebar():
    """새 포스트를 _sidebar.md에 추가"""
    posts = get_recent_posts(limit=10)

    sidebar_content = """
# 한국 주식시장 분석

* [홈](home.md)
* [소개](about.md)

## 최근 글

"""
    for post in posts:
        sidebar_content += f"* [{post.title}](posts/{post.filename})\n"

    write_file("_sidebar.md", sidebar_content)
```

#### Sitemap 업데이트
```python
# scripts/update_sitemap.py

def update_sitemap():
    """sitemap.xml 업데이트"""
    posts = get_all_posts()
    # ... sitemap 생성
```

---

## 5. 콘텐츠 유형별 상세

### 5.1 시장 데일리 브리핑
| 항목 | 내용 |
|------|------|
| 생성 주기 | 매일 장마감 후 (평일) |
| 데이터 소스 | KOSPI/KOSDAQ 지수, 거래량, 외국인/기관 수급 |
| 분량 | 800-1200자 |
| 포맷 | 지수 요약 → 특징주 분석 → 내일 포인트 |

### 5.2 섹터/테마 분석
| 항목 | 내용 |
|------|------|
| 생성 주기 | 주 2-3회 (테마 이슈 발생 시) |
| 데이터 소스 | 섹터별 ETF, 관련 종목군 |
| 분량 | 1500-2500자 |
| 포맷 | 테마 개요 → 핵심 종목 → 투자 포인트 |

### 5.3 개별 종목 리포트
| 항목 | 내용 |
|------|------|
| 생성 주기 | 실적 발표, 주요 이벤트 시 |
| 데이터 소스 | 재무제표, 밸류에이션, 차트 |
| 분량 | 2000-3000자 |
| 포맷 | 기업 개요 → 실적 분석 → 밸류에이션 → 리스크 |

### 5.4 주간/월간 리뷰
| 항목 | 내용 |
|------|------|
| 생성 주기 | 금요일 / 매월 1일 |
| 데이터 소스 | 주간/월간 시장 데이터 집계 |
| 분량 | 2000-3500자 |
| 포맷 | 기간 요약 → 주요 이슈 → 다음 기간 전망 |

### 5.5 표준편차 매매 분석 (신규)
| 항목 | 내용 |
|------|------|
| 생성 주기 | 매일 |
| 데이터 소스 | 20/60일 표준편차, 볼린저 밴드, Z-score |
| 분량 | 600-1000자 |
| 포맷 | 과매도 종목 → 과매수 종목 → 평균회귀 시그널 |

---

## 6. 개발 우선순위 및 일정

### Phase 1: 기반 구축 (1-2주)
- [ ] stock-researcher 변동성 분석 기능 추가
- [ ] content-generator 기본 구조 설계
- [ ] Claude API 클라이언트 구현

### Phase 2: 콘텐츠 생성기 개발 (2-3주)
- [ ] 프롬프트 템플릿 작성 (5종)
- [ ] 데일리 브리핑 생성기 구현
- [ ] 표준편차 분석 생성기 구현
- [ ] 마크다운 포맷팅 및 후처리

### Phase 3: 자동화 파이프라인 (1-2주)
- [ ] GitHub Actions 워크플로우 작성
- [ ] Sidebar/Sitemap 자동 업데이트 스크립트
- [ ] PR 자동 생성 설정

### Phase 4: 테스트 및 안정화 (1주)
- [ ] 전체 파이프라인 테스트
- [ ] 에러 핸들링 및 알림
- [ ] 문서화

---

## 7. 기술 스택 요약

| 영역 | 기술 |
|------|------|
| 언어 | Python 3.11+, Golang (향후 확장) |
| AI | Claude API (Anthropic) |
| 데이터 | pykrx, yfinance, pandas |
| 블로그 | Docsify, GitHub Pages |
| 자동화 | GitHub Actions |
| 패키지 관리 | uv / pip |

---

## 8. 환경 변수 및 시크릿

```bash
# GitHub Secrets에 설정 필요
ANTHROPIC_API_KEY=sk-ant-...  # Claude API 키
```

---

## 9. 리스크 및 고려사항

### 9.1 법적 고려
- 모든 콘텐츠에 투자 면책조항 필수 포함
- 특정 종목 매수/매도 추천 금지
- 데이터 출처 명시

### 9.2 기술적 고려
- API 호출 제한 관리 (Claude API rate limit)
- 데이터 소스 장애 대응 (pykrx, yfinance)
- 장시간 콘텐츠 생성 시 GitHub Actions timeout

### 9.3 품질 관리
- 생성된 콘텐츠 사람이 반드시 리뷰
- 팩트체크 자동화 고려 (주가 데이터 검증)
- 톤앤매너 일관성 유지

---

## 10. 다음 단계

1. **즉시**: 이 기획서 리뷰 및 피드백
2. **이번 주**: Phase 1 개발 착수
3. **2주 내**: 첫 번째 자동 생성 콘텐츠 테스트

---

*최종 수정: 2026-02-02*
