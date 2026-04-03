# blog-est 모노레포 아키텍처 설계

## 1. 프로젝트 개요

영어 글로벌 타겟 SEO 콘텐츠를 자동 생성·발행하는 모노레포 시스템.
각 사이트(tech, health, finance)는 독립 도메인으로 운영되며, 공통 파이프라인을 공유한다.

### 목표

1. 모노레포 구조로 여러 블로그 운영 (Vercel에 사이트별 배포)
2. 각 블로그가 하나의 도메인 관리 (tech, health, finance)
3. 에이전트/스킬 기반 콘텐츠 자동화
4. Vercel 분석 및 리포팅을 통한 고도화

### 현재 상태

현재 finance 사이트(주식 블로그)가 Python 기반(`content_generator`)으로 운영 중이며,
Cowork 스케줄 3개가 등록되어 자동화되고 있다.
향후 Go 기반 `core/` 엔진으로 점진적 전환 예정.

| 구분 | 현재 (Python) | 목표 (Go) |
|------|---------------|-----------|
| 콘텐츠 생성 | `content_generator.cli` | `core/writer/` |
| 사이드바/사이트맵 | `scripts/update_sidebar.py` | `core/publisher/sidebar.go` |
| 스케줄링 | Cowork 스케줄 | Cowork 스케줄 + GitHub Actions |
| 배포 | Vercel (직접 push → 자동 배포) | Vercel (PR 머지 → 자동 배포) |

---

## 2. 디렉토리 구조

### 현재 구조 (Phase 1 완료 상태)

finance 사이트의 Docsify 콘텐츠는 루트에 유지한다 (Vercel `totalr` 프로젝트로 자동 배포).
sites/ 아래에는 설정 파일(config.yaml, agent.yaml)만 두고, 새 사이트(tech, health)는 docs/를 별도로 구성한다.

```
blog-est/
│
│  ── [finance 사이트 콘텐츠 - 루트에서 서빙] ──
├── index.html                      # Docsify 엔트리 (finance)
├── home.md                         # 홈페이지
├── about.md                        # 소개 페이지
├── _sidebar.md                     # 사이드바 (자동 생성)
├── posts/                          # 생성된 블로그 글
├── assets/                         # 이미지, 파비콘
├── styles.css                      # 커스텀 스타일
├── yntkc-vue.css                   # Docsify 테마
├── sitemap.xml                     # 사이트맵
├── robots.txt
├── .nojekyll
│
│  ── [사이트별 설정] ──
├── sites/
│   ├── finance/                    # 투자·시장 데이터 (현재 운영 중)
│   │   ├── config.yaml             # ✅ 사이트 인프라 설정
│   │   ├── agent.yaml              # ✅ 에이전트 행동 설정
│   │   ├── keywords/               # 키워드 리스트
│   │   └── templates/              # 글 템플릿
│   │
│   ├── tech/                       # AI·소프트웨어 (Phase 2에서 구현)
│   │   ├── config.yaml             # ✅ 사이트 설정
│   │   ├── agent.yaml              # ✅ 에이전트 설정
│   │   ├── keywords/
│   │   ├── templates/
│   │   └── docs/                   # Docsify 콘텐츠 (별도 루트)
│   │
│   └── health/                     # 웰니스·과학 (Phase 3에서 구현)
│       ├── config.yaml             # ✅ 사이트 설정
│       ├── agent.yaml              # ✅ 에이전트 설정
│       ├── keywords/
│       ├── templates/
│       └── docs/
│
│  ── [Go 공통 엔진] ──
├── core/
│   ├── config/                     # ✅ 설정 로더 (구현 완료)
│   │   ├── types.go                # 타입 정의 (SiteConfig, AgentConfig)
│   │   ├── loader.go               # YAML 파서 & 사이트 디스커버리
│   │   └── loader_test.go          # 테스트
│   ├── writer/                     # Claude API 콘텐츠 생성 (Phase 2)
│   ├── publisher/                  # 발행 엔진 (Phase 2)
│   ├── crawler/                    # 키워드 수집 (Phase 3)
│   ├── analyzer/                   # Vercel 분석 (Phase 4)
│   └── scheduler/                  # 스케줄링 (Phase 4)
│
│  ── [CLI 엔트리포인트] ──
├── cmd/
│   ├── generate/main.go            # ✅ 콘텐츠 생성 CLI (스켈레톤)
│   ├── crawl/                      # 키워드 크롤링 (Phase 3)
│   ├── publish/                    # 발행 (Phase 2)
│   └── report/                     # 분석 리포트 (Phase 4)
│
│  ── [기존 Python 도구 (레거시)] ──
├── tools/
│   ├── content-generator/          # Python 콘텐츠 생성기 (현재 운영)
│   └── stock-researcher/           # Python 주식 데이터 수집기
├── scripts/
│   ├── update_sidebar.py           # 사이드바 업데이트
│   └── update_sitemap.py           # 사이트맵 업데이트
│
│  ── [프로젝트 설정] ──
├── .github/workflows/
│   ├── generate-daily.yml
│   └── generate-review.yml
├── go.mod
├── Makefile
├── PLANNING.md
├── ARCHITECTURE.md
└── README.md
```

---

## 3. YAML 스키마 정의

### 3.1 config.yaml — 사이트 인프라 설정

```yaml
# sites/tech/config.yaml
site:
  name: "tech-insights"
  domain: "tech.example.com"          # Vercel 커스텀 도메인
  language: "en"

deploy:
  platform: "vercel"
  framework: "docsify"
  root: "./docs"                       # Docsify 콘텐츠 루트
  build_command: ""                    # Docsify는 빌드 불필요 (정적)
  output_directory: "./docs"

publish:
  target: "docsify"                    # docsify | wordpress
  # WordPress 레거시 설정 (선택)
  wordpress:
    url: ""
    username: ""
    password_env: ""                   # 환경변수 참조

schedule:
  content_generation: "0 6 * * *"      # 매일 06:00 UTC
  keyword_crawl: "0 0 * * 1"           # 매주 월요일
  report: "0 9 * * 5"                  # 매주 금요일

seo:
  sitemap: true
  robots_txt: true
  canonical_base: "https://tech.example.com"
```

### 3.2 agent.yaml — 에이전트 행동 설정

```yaml
# sites/tech/agent.yaml
agent:
  name: "tech-writer"
  model: "claude-sonnet-4-20250514"

persona:
  tone: "analytical, developer-friendly"
  audience: "tech-savvy adults, developers, early adopters"
  style: "data-driven, concise, no fluff"
  niche: "AI, software engineering, cloud infrastructure, emerging tech"

content:
  types:
    - "how-to"          # 실습형 가이드
    - "explainer"        # 개념 설명
    - "comparison"       # 데이터 기반 비교
    - "listicle"         # 도구/리소스 목록
  word_count:
    min: 1200
    max: 2000
  structure:
    include_toc: true
    include_tldr: true
    include_code_examples: true

rules:
  must:
    - "cite official documentation or data sources"
    - "include practical examples or code snippets"
    - "use H2/H3 for clear section hierarchy"
  avoid:
    - "opinion-based reviews without data"
    - "product comparisons without benchmarks"
    - "medical or legal advice"
    - "first-person subjective statements"

keywords:
  strategy: "longtail"
  min_volume: 100
  max_difficulty: 30                   # 경쟁도 낮은 키워드 우선
  seed_file: "./keywords/seed.yaml"

affiliate:
  programs:
    - name: "AWS"
      id: "aws-affiliate-123"
      categories: ["cloud", "infrastructure"]
    - name: "Datadog"
      id: "datadog-partner-456"
      categories: ["monitoring", "observability"]
  disclosure: "This post contains affiliate links. We may earn a commission at no extra cost to you."
  placement: "contextual"              # contextual | footer | sidebar
```

### 3.3 seed.yaml — 시드 키워드

```yaml
# sites/tech/keywords/seed.yaml
categories:
  - name: "AI Tools"
    keywords:
      - "best open source llm frameworks 2026"
      - "how to deploy ai model on kubernetes"
      - "ai monitoring tools comparison"

  - name: "Cloud Infrastructure"
    keywords:
      - "kubernetes cost optimization guide"
      - "aws vs gcp for startups 2026"
      - "terraform vs pulumi comparison"

  - name: "Developer Productivity"
    keywords:
      - "best cli tools for developers"
      - "how to automate code review"
```

---

## 4. Go Core 파이프라인 아키텍처

### 4.1 핵심 인터페이스

```go
// core/crawler/crawler.go
type Crawler interface {
    // 시드 키워드로부터 롱테일 키워드 확장
    Expand(ctx context.Context, seeds []string) ([]Keyword, error)
    // 키워드 경쟁도/볼륨 분석
    Analyze(ctx context.Context, keyword string) (*KeywordMetrics, error)
}

type Keyword struct {
    Term       string  `yaml:"term"`
    Volume     int     `yaml:"volume"`
    Difficulty float64 `yaml:"difficulty"`
    Category   string  `yaml:"category"`
}
```

```go
// core/writer/writer.go
type Writer interface {
    // agent.yaml 설정 + 키워드로 글 생성
    Generate(ctx context.Context, req GenerateRequest) (*Post, error)
}

type GenerateRequest struct {
    SiteName  string
    Agent     AgentConfig
    Keyword   Keyword
    Template  string   // 템플릿 이름
}

type Post struct {
    Title       string
    Slug        string
    Content     string   // Markdown
    Meta        PostMeta
    GeneratedAt time.Time
}

type PostMeta struct {
    Description    string   `yaml:"description"`
    Keywords       []string `yaml:"keywords"`
    ReadTime       int      `yaml:"read_time_min"`
    AffiliateLinks []string `yaml:"affiliate_links,omitempty"`
}
```

```go
// core/publisher/publisher.go
type Publisher interface {
    // 생성된 포스트를 대상 플랫폼에 발행
    Publish(ctx context.Context, site SiteConfig, post *Post) error
}
```

```go
// core/analyzer/analyzer.go
type Analyzer interface {
    // 사이트 성과 데이터 수집
    Fetch(ctx context.Context, site SiteConfig, period Period) (*SiteMetrics, error)
    // 성과 기반 키워드/콘텐츠 추천
    Recommend(ctx context.Context, metrics *SiteMetrics) ([]Recommendation, error)
}

type SiteMetrics struct {
    PageViews      map[string]int     // path → views
    TopPages       []PageMetric
    BounceRate     float64
    AvgTimeOnPage  time.Duration
}

type Recommendation struct {
    Type    string   // "new_keyword" | "update_post" | "remove_post"
    Target  string
    Reason  string
    Score   float64
}
```

### 4.2 파이프라인 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                      Scheduler (cron)                        │
└──────────┬──────────────────────────────────┬───────────────┘
           │                                  │
           ▼                                  ▼
┌──────────────────┐              ┌────────────────────┐
│  Keyword Crawl   │              │  Analytics Report  │
│  (weekly)        │              │  (weekly)          │
└────────┬─────────┘              └─────────┬──────────┘
         │                                  │
         ▼                                  ▼
┌──────────────────┐              ┌────────────────────┐
│  sites/*/keywords│              │  Recommendation    │
│  /generated/     │              │  → 다음 키워드 선정  │
└────────┬─────────┘              └─────────┬──────────┘
         │                                  │
         └──────────────┬───────────────────┘
                        ▼
          ┌──────────────────────┐
          │  Content Generation  │
          │  (daily)             │
          │                      │
          │  for each site:      │
          │    load agent.yaml   │
          │    pick keyword      │
          │    select template   │
          │    call Claude API   │
          │    → Post{.md}       │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  GitHub PR 생성       │
          │  (review gate)       │
          └──────────┬───────────┘
                     │ merge
                     ▼
          ┌──────────────────────┐
          │  Docsify Publish     │
          │  + Sidebar Update    │
          │  → Vercel 자동 배포    │
          └──────────────────────┘
```

### 4.3 CLI 사용 예시

```bash
# 전체 사이트 콘텐츠 생성
go run cmd/generate/main.go --all

# 특정 사이트만
go run cmd/generate/main.go --site tech

# 키워드 크롤링
go run cmd/crawl/main.go --site tech --limit 50

# 발행 (Docsify markdown + sidebar 업데이트)
go run cmd/publish/main.go --site tech --post posts/2026-03-31-ai-monitoring.md

# 성과 리포트
go run cmd/report/main.go --site tech --period weekly
```

---

## 5. Vercel 배포 전략

### 5.1 현재 배포 구조

| Vercel 프로젝트 | GitHub 레포 | 도메인 | 용도 |
|----------------|------------|--------|------|
| **totalr** | `Reone1/blog-est` (main) | `totalr.vercel.app` | finance 사이트 (운영) |
| blog-est | `Reone1/blog-est` (main) | `blog-est.vercel.app` | 테스트 (삭제 예정) |

현재 finance 사이트는 레포 루트에서 Docsify를 서빙하며, GitHub push → Vercel 자동 배포.

### 5.2 도메인별 멀티 프로젝트 구조 (목표)

각 관심 도메인(finance, tech, health)은 독립 Vercel 프로젝트로 배포한다.
하나의 GitHub 레포(`Reone1/blog-est`)에서 Root Directory 설정으로 사이트를 분리한다.

```
Reone1/blog-est (GitHub repo)
│
├── (root)               →  Vercel Project: "totalr"        → totalr.vercel.app       (finance)
├── sites/tech/docs/     →  Vercel Project: "totalr-tech"   → totalr-tech.vercel.app  (tech)
└── sites/health/docs/   →  Vercel Project: "healthem"      → healthem.vercel.app     (health)
```

Vercel에서 동일 레포를 여러 프로젝트로 연결할 때:
- 각 프로젝트의 **Root Directory** 설정을 다르게 지정
- finance: `/` (루트), tech: `sites/tech/docs`, health: `sites/health/docs`
- 커스텀 도메인은 각 프로젝트에 개별 연결

### 5.3 Vercel 프로젝트 생성 방법

```bash
# 1. Vercel CLI로 새 프로젝트 연결 (tech 사이트 예시)
cd sites/tech/docs
vercel link --project totalr-tech --scope reone1s-projects

# 2. Root Directory 설정
# Vercel Dashboard → Project Settings → General → Root Directory
# → sites/tech/docs

# 3. 커스텀 도메인 연결 (선택)
vercel domains add tech.totalr.com --project totalr-tech
```

### 5.4 배포 플로우

```
git push origin main
  ↓
Vercel: 각 프로젝트별 Root Directory 변경 감지
  ↓
변경된 사이트만 자동 빌드/배포
  ↓
totalr.vercel.app        (finance 변경 시)
totalr-tech.vercel.app   (tech 변경 시)
healthem.vercel.app      (health 변경 시)
```

Vercel은 같은 레포에 연결된 여러 프로젝트를 자동으로 감지하여
해당 Root Directory에 변경이 있을 때만 배포한다.

### 5.5 Vercel Analytics 연동

각 사이트의 Docsify `index.html`에 Vercel Analytics 스크립트를 삽입하여 페이지별 트래픽을 추적한다.
`core/analyzer/`에서 Vercel Analytics API를 호출하여 사이트별 성과 데이터를 수집하고,
이를 기반으로 키워드 전략을 자동 조정한다.

현재 finance 사이트에는 이미 Analytics가 삽입되어 있다:
```html
<!-- Vercel Analytics -->
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
```

---

## 6. 스케줄링 & 자동화 전략

### 6.1 Cowork 스케줄 (현재 운영 중)

finance 사이트는 Cowork 스케줄로 자동화되어 있다.
Python CLI(`content_generator`)를 직접 호출하며, git push → Vercel 자동 배포한다.

| 스케줄 ID | 주기 | 시간 (KST) | 동작 |
|-----------|------|-----------|------|
| `daily-blog-briefing` | 매일 | 16:00 | 데일리 브리핑 생성 → 섹터 분석 조건부 생성 → push |
| `weekly-blog-review` | 매주 금 | 16:00 | 주간 리뷰 생성 → push |
| `monthly-blog-review` | 매월 말일 | 16:00 | 월간 리뷰 생성 → push |

#### 데일리 브리핑 파이프라인 (상세)

```
16:00 KST 트리거
  ↓
1단계: 데일리 브리핑 생성
  python -m content_generator.cli generate --type daily_briefing --output posts/
  ↓
2단계: 섹터 분석 분기 판단
  생성된 브리핑을 읽고 아래 조건 체크:
  - 특정 섹터 ±3% 이상 괴리
  - 외국인/기관 집중 매수/매도
  - 정책/규제 변화 영향
  - 테마주 동시 급등/급락
  → 트리거 시: sector_analysis 추가 생성
  → 미트리거: 브리핑만
  ↓
3단계: sidebar/sitemap 업데이트
  python scripts/update_sidebar.py
  python scripts/update_sitemap.py
  ↓
4단계: Git push (→ Vercel 자동 배포)
  git add posts/ _sidebar.md sitemap.xml
  git commit -m "content: daily briefing for $(date)"
  git push origin main
```

#### 주간/월간 리뷰 파이프라인

```
금요일 16:00 / 매월 말일 16:00 KST 트리거
  ↓
콘텐츠 생성 (weekly_review | monthly_review)
  ↓
sidebar/sitemap 업데이트
  ↓
Git push (→ Vercel 자동 배포)
```

### 6.2 스케줄 확장 계획 (Go 전환 후)

Go 엔진 전환 후에는 Cowork 스케줄과 GitHub Actions를 병행 운영한다.

| 레이어 | 역할 | 도구 |
|--------|------|------|
| **Cowork 스케줄** | 콘텐츠 생성 트리거, 조건부 분기 판단 | Cowork `schedule` 스킬 |
| **GitHub Actions** | CI/CD, Vercel 배포, 코드 품질 체크 | `.github/workflows/` |
| **Go Scheduler** | 키워드 크롤링, 분석 리포트 등 백그라운드 작업 | `core/scheduler/` |

전환 후 스케줄 구성:

| 스케줄 | 주기 | 플랫폼 | 동작 |
|--------|------|--------|------|
| 데일리 콘텐츠 | 매일 16:00 KST | Cowork | 각 사이트별 콘텐츠 생성 → PR |
| 주간 리뷰 | 매주 금 16:00 KST | Cowork | 주간 리뷰 생성 → PR |
| 월간 리뷰 | 매월 말일 16:00 KST | Cowork | 월간 리뷰 생성 → PR |
| 키워드 크롤링 | 매주 월 00:00 | GitHub Actions | `go run cmd/crawl/` |
| 성과 리포트 | 매주 금 09:00 | GitHub Actions | `go run cmd/report/` |
| 자동 배포 | PR merge | GitHub Actions | Vercel CLI 배포 |

### 6.3 Cowork 스킬 활용

| 스킬 | 용도 |
|------|------|
| `schedule` | 콘텐츠 생성/리뷰 스케줄 태스크 등록 및 관리 |
| `xlsx` | 키워드 리서치 결과, 성과 리포트를 스프레드시트로 출력 |
| `docx` | 월간 종합 리포트 문서 생성 |

### 6.4 피드백 루프

```
Vercel Analytics → core/analyzer → Recommendation
  → 키워드 우선순위 조정
  → 저성과 콘텐츠 업데이트 제안
  → 고성과 카테고리 확장
  → 다음 스케줄 실행 시 반영
```

---

## 7. 구현 우선순위 (로드맵)

### Phase 0: 현재 운영 유지 (진행 중)
- [x] finance 사이트 Python 파이프라인 운영
- [x] Cowork 스케줄 3개 등록 (데일리/주간/월간)
- [x] Vercel 자동 배포 (totalr.vercel.app)
- [ ] 안정성 모니터링 (스케줄 실패 알림 확인)

### Phase 1: 모노레포 구조화 (1~2주)
- [ ] blog-est 레포를 모노레포 구조로 리팩토링
  - 기존 코드를 `sites/finance/`로 이동
  - `config.yaml`, `agent.yaml` 스키마 적용
- [ ] Go 모듈 초기화 (`go.mod`, `core/config/`)
- [ ] config.yaml / agent.yaml 파서 구현 (Go)
- [ ] 기존 Python 스크립트는 `sites/finance/scripts/`에 유지 (하위 호환)

### Phase 2: Go 엔진 구축 + tech 사이트 (2~3주)
- [ ] `core/writer/` — Claude API Writer 구현
- [ ] `core/publisher/` — Docsify Publisher 구현
- [ ] tech 사이트 셋업 + agent.yaml 작성
- [ ] tech 사이트 end-to-end 동작 확인
- [ ] Cowork 스케줄을 Go CLI 호출로 전환 시작

### Phase 3: Vercel 배포 전환 (3~4주)
- [ ] Vercel 멀티 프로젝트 셋업 (tech, finance)
- [ ] GitHub Actions 배포 워크플로우
- [ ] finance 사이트 Vercel 프로젝트 정리 (테스트 blog-est 삭제, totalr 유지)
- [ ] health 사이트 추가
- [ ] 키워드 Crawler 구현 (`core/crawler/`)

### Phase 4: 분석 & 고도화 (4~6주)
- [ ] Vercel Analytics 연동 (`core/analyzer/`)
- [ ] 성과 분석 & 리포터
- [ ] 키워드 자동 추천 시스템
- [ ] 콘텐츠 자동 업데이트 파이프라인

### Phase 5: 확장 (6주~)
- [ ] 제휴 링크 자동 삽입 고도화
- [ ] A/B 테스트 (제목, 구조)
- [ ] 뉴스레터 자동화
- [ ] 추가 니치 사이트 확장

### 전환 전략: Python → Go 점진적 마이그레이션

```
Phase 0~1: Python 유지, 모노레포 구조만 정리
  finance/ → 기존 Python CLI 그대로 운영
  Cowork 스케줄 → python -m content_generator.cli ...

Phase 2: Go 엔진 병행 운영
  tech/ → Go CLI로 콘텐츠 생성 (새 사이트)
  finance/ → Python CLI 유지 (기존 사이트)
  Cowork 스케줄 → 사이트별 다른 CLI 호출

Phase 3~: finance도 Go로 전환
  finance/ → Go CLI로 전환
  Python 스크립트 → deprecated → 삭제
  Cowork 스케줄 → go run cmd/generate/ --site finance
```
