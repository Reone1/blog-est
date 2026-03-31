# 새 도메인 런칭 플레이북

새로운 블로그 도메인(니치)을 추가할 때 따르는 실행 가이드.
각 도메인은 `sites/<domain>/` 아래에서 독립적으로 관리되며, 이 문서의 체크리스트를 순서대로 수행한다.

> **현재 운영 중**: finance (totalr.vercel.app)
> **다음 런칭 대상**: tech → health (순서)

---

## 1. 도메인 선정 기준

새 니치를 선정할 때 아래 기준으로 평가한다.

| 기준 | 조건 | 비고 |
|------|------|------|
| 검색 수요 | 월간 검색량 1만+ 키워드가 50개 이상 | Ahrefs, Ubersuggest 등 |
| 경쟁도 | KD(Keyword Difficulty) 30 이하 키워드 비율 40%+ | 롱테일 위주 진입 가능 |
| 수익화 경로 | 제휴 프로그램 or 광고 단가(CPC) $1+ | 최소 1개 수익 채널 확보 |
| AI 생성 적합성 | 팩트 기반 콘텐츠 가능, 주관적 의견 최소 | YMYL 주의 |
| 에버그린 비율 | 콘텐츠의 60%+ 가 시간에 덜 민감 | 유지보수 비용 절감 |

### 선정 프로세스

```
1. 후보 니치 3~5개 브레인스토밍
2. 각 니치별 시드 키워드 20개 수집
3. 키워드 도구로 볼륨/경쟁도 조사
4. 위 기준표로 점수화 (5점 척도)
5. 총점 상위 1~2개 선정
```

---

## 2. 키워드 리서치 전략

### 2.1 시드 키워드 수집

| 소스 | 방법 | 목표 수량 |
|------|------|----------|
| 경쟁사 분석 | 상위 10개 사이트의 인기 글 URL 수집 → 키워드 추출 | 50개 |
| 자동완성 | Google Autocomplete, People Also Ask 크롤링 | 30개 |
| 커뮤니티 | Reddit, Quora, 포럼에서 자주 묻는 질문 수집 | 20개 |
| AI 브레인스토밍 | Claude에 니치 관련 롱테일 키워드 생성 요청 | 30개 |

### 2.2 키워드 필터링 기준

```yaml
# agent.yaml keywords 섹션에 반영
keywords:
  strategy: "longtail"
  min_volume: 100          # 최소 월간 검색량
  max_difficulty: 30       # 최대 키워드 난이도
  min_word_count: 3        # 3단어 이상 (롱테일)
  intent_filter:
    - "informational"      # 정보성 쿼리 우선
    - "commercial"         # 구매 의도 쿼리 (제휴용)
  exclude_patterns:
    - "reddit"
    - "forum"
    - "{current_year} 이전 연도"
```

### 2.3 키워드 분류 및 관리

수집된 키워드는 `sites/<domain>/keywords/seed.yaml`에 카테고리별로 정리한다.

```
sites/<domain>/keywords/
├── seed.yaml              # 시드 키워드 (수동 큐레이션)
├── generated/             # 크롤러가 확장한 키워드 (자동)
│   └── YYYY-MM.yaml
└── used.yaml              # 이미 글로 작성한 키워드 (중복 방지)
```

### 2.4 키워드 우선순위 매트릭스

| 우선순위 | 볼륨 | 난이도 | 용도 |
|---------|------|--------|------|
| P0 (즉시) | 100~500 | KD ≤ 15 | 초기 인덱싱용, 빠른 랭킹 가능 |
| P1 (1개월 내) | 500~2000 | KD ≤ 25 | 트래픽 확보 핵심 |
| P2 (3개월 내) | 2000+ | KD ≤ 30 | 도메인 권한 축적 후 공략 |
| P3 (보류) | any | KD > 30 | 권한 성장 후 재평가 |

---

## 3. 콘텐츠 시딩 전략

### 3.1 초기 콘텐츠 구성 (런칭 전 준비)

사이트 공개 전에 최소 콘텐츠를 확보한다.

| 단계 | 글 수 | 콘텐츠 유형 | 키워드 우선순위 | 기간 |
|------|-------|------------|---------------|------|
| 시딩 (비공개) | 10~15편 | pillar 3 + supporting 10 | P0 | 1~2주 |
| 런칭 | 15편+ | 위 시딩분 공개 | P0 | D-day |
| 램프업 1개월 | +20편 | supporting + P1 키워드 | P0~P1 | 1개월 |
| 안정화 | +10편/월 | 혼합 | P1~P2 | 2개월~ |

### 3.2 Pillar-Cluster 구조

각 니치에 3~5개 pillar 주제를 설정하고, 하위 supporting 글을 클러스터로 연결한다.

```
Pillar: "Kubernetes Cost Optimization"
  ├── Supporting: "how to reduce kubernetes node costs"
  ├── Supporting: "kubernetes spot instance best practices"
  ├── Supporting: "kubernetes resource limits vs requests explained"
  └── Supporting: "top kubernetes cost monitoring tools 2026"
```

pillar 글에서 supporting 글로 내부 링크를 걸어 토픽 권한을 집중시킨다.

### 3.3 콘텐츠 품질 체크리스트

각 글 발행 전 확인:

- [ ] 타겟 키워드가 제목(H1), 첫 문단, H2 1개 이상에 포함
- [ ] 메타 description 155자 이내, 키워드 포함
- [ ] 내부 링크 2개 이상 (pillar ↔ supporting)
- [ ] 이미지 alt 태그에 키워드 반영
- [ ] 1200자 이상 (thin content 방지)
- [ ] 면책조항/출처 표시 (니치별 규정 준수)

---

## 4. 배포 주기 & 램프업

### 4.1 단계별 배포 빈도

```
[시딩]     ──── 매일 2~3편 (비공개, 1~2주간) ────────┐
[런칭]     ──── 15편 일괄 공개 ────────────────────────┤
[램프업]   ──── 매일 1편 (첫 1개월) ───────────────────┤
[안정화]   ──── 주 3편 (2~3개월) ──────────────────────┤
[크루즈]   ──── 주 2편 + 기존 글 업데이트 1편 (4개월~) ─┘
```

### 4.2 콘텐츠 캘린더 템플릿

| 요일 | 콘텐츠 유형 | 비고 |
|------|------------|------|
| 월 | how-to / explainer | 정보성 (트래픽 핵심) |
| 수 | comparison / listicle | 상업성 (제휴 수익) |
| 금 | explainer / research-digest | 권한 구축 |
| (선택) 화/목 | 램프업 기간에만 추가 발행 | P0 키워드 소진용 |

### 4.3 발행 시간

| 타겟 | 발행 시간 (UTC) | 이유 |
|------|----------------|------|
| 글로벌 영어 | 06:00~08:00 | 미국 동부 아침 + 유럽 오후 |
| 한국어 | 07:00 (16:00 KST) | 퇴근 시간대 트래픽 |

---

## 5. 자동화 셋업 체크리스트

새 도메인 추가 시 아래 순서로 자동화를 구성한다.

### 5.1 인프라 셋업

- [ ] `sites/<domain>/config.yaml` 작성
- [ ] `sites/<domain>/agent.yaml` 작성
- [ ] `sites/<domain>/keywords/seed.yaml` 시드 키워드 등록
- [ ] `sites/<domain>/templates/` 글 템플릿 작성
- [ ] `sites/<domain>/docs/` Docsify 초기 구조 생성
  - [ ] `index.html`, `_sidebar.md`, `home.md`, `styles.css`
  - [ ] `robots.txt`, `sitemap.xml`
  - [ ] Vercel Analytics 스크립트 삽입

### 5.2 Vercel 배포

- [ ] Vercel 프로젝트 생성 (`vercel link --project <name>`)
- [ ] Root Directory 설정 (`sites/<domain>/docs`)
- [ ] 커스텀 도메인 연결 (선택)
- [ ] 배포 테스트 (push → 자동 배포 확인)

### 5.3 스케줄 등록

- [ ] 콘텐츠 생성 스케줄 (Cowork or GitHub Actions)
- [ ] 키워드 크롤링 스케줄 (주 1회)
- [ ] 성과 리포트 스케줄 (주 1회)

### 5.4 모니터링

- [ ] Vercel Analytics 대시보드 확인
- [ ] Google Search Console 등록
- [ ] 스케줄 실패 알림 설정

---

## 6. 성과 추적 & 반복 개선

### 6.1 KPI

| 지표 | 측정 주기 | 목표 (3개월) | 목표 (6개월) |
|------|----------|-------------|-------------|
| 인덱싱 페이지 수 | 주간 | 30+ | 60+ |
| 월간 오가닉 트래픽 | 월간 | 500+ | 3000+ |
| 평균 게시물 순위 | 월간 | 30위 이내 | 15위 이내 |
| 클릭률 (CTR) | 월간 | 2%+ | 4%+ |
| 제휴 전환 | 월간 | 첫 전환 발생 | 월 $50+ |

### 6.2 월간 리뷰 프로세스

```
매월 1일:
  1. Search Console 데이터 다운로드
  2. 상위 20개 글 성과 분석
  3. 저성과 글 식별 → 업데이트 or 병합 결정
  4. 고성과 카테고리 → 키워드 확장
  5. 다음 달 콘텐츠 캘린더 조정
  6. KPI 대비 진행 상황 기록 (아래 트래커에 업데이트)
```

### 6.3 콘텐츠 업데이트 정책

| 조건 | 액션 |
|------|------|
| 3개월간 조회수 0 | 키워드 재검토 → 리라이트 or 삭제 |
| 순위 11~20위 정체 | 콘텐츠 보강 (길이 추가, 내부 링크 강화) |
| 순위 1~3위 | 제휴 링크 삽입 검토, 관련 클러스터 확장 |
| 6개월 이상 미업데이트 | 정보 최신성 점검 → 날짜 및 데이터 갱신 |

---

## 7. 도메인별 런칭 트래커

각 도메인의 진행 상황을 여기서 추적한다.

### 7.1 finance (운영 중)

| 항목 | 상태 | 날짜 | 비고 |
|------|------|------|------|
| 도메인 선정 | ✅ | - | 한국 주식시장 분석 |
| config.yaml | ✅ | - | totalr.vercel.app |
| agent.yaml | ✅ | - | finance-writer |
| 시드 키워드 | ⬜ | - | 시장 데이터 기반 자동 생성 중 |
| 초기 시딩 | ✅ | - | Python CLI로 운영 |
| Vercel 배포 | ✅ | - | totalr.vercel.app |
| 스케줄 자동화 | ✅ | - | Cowork 스케줄 3개 |
| Search Console | ⬜ | - | TODO |
| 월간 KPI 리뷰 | ⬜ | - | TODO |

### 7.2 tech (다음 런칭)

| 항목 | 상태 | 날짜 | 비고 |
|------|------|------|------|
| 도메인 선정 | ✅ | - | AI, 소프트웨어, 클라우드 |
| config.yaml | ✅ | - | 도메인/URL 미설정 |
| agent.yaml | ✅ | - | tech-writer |
| 시드 키워드 | ⬜ | - | seed.yaml 미작성 |
| 키워드 리서치 | ⬜ | - | 섹션 2 절차 수행 필요 |
| 초기 시딩 (10~15편) | ⬜ | - | |
| Docsify 구조 생성 | ⬜ | - | sites/tech/docs/ |
| Vercel 프로젝트 생성 | ⬜ | - | |
| 스케줄 등록 | ⬜ | - | |
| 런칭 | ⬜ | - | |
| Search Console 등록 | ⬜ | - | |

### 7.3 health (예정)

| 항목 | 상태 | 날짜 | 비고 |
|------|------|------|------|
| 도메인 선정 | ✅ | - | 웰니스, 영양, 수면, 피트니스 |
| config.yaml | ✅ | - | 도메인/URL 미설정 |
| agent.yaml | ✅ | - | health-writer |
| 시드 키워드 | ⬜ | - | |
| 키워드 리서치 | ⬜ | - | |
| 초기 시딩 | ⬜ | - | |
| Docsify 구조 생성 | ⬜ | - | |
| Vercel 프로젝트 생성 | ⬜ | - | |
| 스케줄 등록 | ⬜ | - | |
| 런칭 | ⬜ | - | |

---

## 8. 새 도메인 추가 시 Quick Start

```bash
# 1. 이 플레이북의 섹션 1(도메인 선정) 완료

# 2. 디렉토리 및 설정 파일 생성
mkdir -p sites/<domain>/{keywords,templates,docs/posts}
# config.yaml, agent.yaml 작성 (기존 사이트 참고)

# 3. 시드 키워드 수집 (섹션 2 절차)
# sites/<domain>/keywords/seed.yaml 작성

# 4. 초기 콘텐츠 시딩 (섹션 3 절차)
# P0 키워드로 10~15편 생성

# 5. Docsify 셋업
# sites/<domain>/docs/ 에 index.html, _sidebar.md 등 구성

# 6. Vercel 배포 (섹션 5.2)
# vercel link → Root Directory 설정 → 배포 확인

# 7. 스케줄 등록 (섹션 5.3)
# Cowork schedule 또는 GitHub Actions 워크플로우

# 8. 런칭 → 섹션 4 배포 주기에 따라 운영
# 9. 매월 섹션 6 리뷰 프로세스 수행
```

---

*최종 수정: 2026-03-31*
