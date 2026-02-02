# Stock Researcher

한국/미국 증시 리서치 도구 (CLI + MCP 서버)

## 기능

- 🏆 **시가총액 TOP**: 미국/한국 시가총액 상위 종목
- 📈 **급등주/급락주**: 당일 등락률 상위 종목
- 🔥 **거래량 TOP**: 거래량 급증 종목
- 🏭 **섹터별 조회**: 반도체, AI, 바이오, 배터리 등 테마별 상위 종목
- 🔍 **종목 검색**: 티커/종목명으로 검색

## 설치

```bash
cd tools/stock-researcher
pip install -e .
```

MCP 서버 기능도 사용하려면:
```bash
pip install -e ".[mcp]"
```

## CLI 사용법

### 시가총액 TOP
```bash
# 미국 시가총액 TOP 10
stock top --market us

# 한국 시가총액 TOP 10
stock top --market kr

# 한국 TOP 20
stock top --market kr --limit 20
```

### 급등/급락/거래량 TOP
```bash
# 미국 급등/급락/거래량 TOP
stock movers --market us

# 한국 급등/급락/거래량 TOP
stock movers --market kr
```

### 섹터별 조회
```bash
# 미국 반도체 TOP 10
stock sector semiconductor --market us

# 미국 AI 관련주 TOP 10
stock sector ai --market us

# 한국 2차전지 TOP 10
stock sector battery --market kr

# 사용 가능한 섹터 목록
stock sectors
```

### 종목 검색
```bash
# 종목 검색
stock search "삼성전자"
stock search NVDA
```

### 시장 요약
```bash
# 전체 시장 요약
stock summary

# 미국만
stock summary --market us
```

## 지원 섹터

| 섹터 | 설명 | 미국 | 한국 |
|------|------|------|------|
| `technology` | 기술/IT | ✅ | ⚠️ |
| `semiconductor` | 반도체 | ✅ | ✅ |
| `ai` | 인공지능 | ✅ | ⚠️ |
| `healthcare` | 헬스케어 | ✅ | ⚠️ |
| `bio` | 바이오 | ✅ | ✅ |
| `financials` | 금융 | ✅ | ⚠️ |
| `energy` | 에너지 | ✅ | ⚠️ |
| `ev` | 전기차 | ✅ | ⚠️ |
| `battery` | 배터리/2차전지 | ✅ | ✅ |

✅ 지원 | ⚠️ 제한적 지원 (ETF 기반)

## MCP 서버 사용

### Claude Desktop 설정

`claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "stock-researcher": {
      "command": "python",
      "args": ["-m", "stock_researcher.mcp_server"],
      "cwd": "/path/to/stock-researcher"
    }
  }
}
```

### 제공되는 MCP 도구

| 도구 | 설명 |
|------|------|
| `stock_top_market_cap` | 시가총액 상위 종목 |
| `stock_top_movers` | 급등/급락/거래량 TOP |
| `stock_sector_top` | 섹터별 상위 종목 |
| `stock_search` | 종목 검색 |
| `stock_market_summary` | 시장 요약 |
| `stock_available_sectors` | 섹터 목록 |

### Claude에서 사용 예시

```
"미국 반도체 섹터 TOP 10 보여줘"
"오늘 한국 시장 급등주 알려줘"
"NVDA 주식 정보 검색해줘"
```

## 데이터 소스

- **미국**: [yfinance](https://github.com/ranaroussi/yfinance) (Yahoo Finance)
- **한국**: [pykrx](https://github.com/sharebook-kr/pykrx) (KRX 공식 데이터)

## Python API

```python
from stock_researcher import kr_market, us_market

# 미국 시가총액 TOP 10
us_stocks = us_market.get_top_by_market_cap(limit=10)
for stock in us_stocks:
    print(f"{stock.symbol}: {stock.name} - ${stock.price:,.2f}")

# 한국 급등주
kr_movers = kr_market.get_top_movers(market_type="KOSPI", limit=10)
for stock in kr_movers.gainers:
    print(f"{stock.name}: {stock.change_percent:+.2f}%")

# 섹터별 조회
ai_stocks = us_market.get_sector_top("ai", limit=10)
```

## 개발

```bash
# 개발 의존성 설치
pip install -e ".[dev]"

# 린트
ruff check .

# 테스트
pytest
```

## 라이선스

MIT
