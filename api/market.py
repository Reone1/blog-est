"""
Vercel Serverless Function - 네이버 시장 데이터 프록시

Claude Code 스케줄 태스크에서 사용하는 시장 데이터 API.
네이버 Finance 모바일 API를 프록시하여 KOSPI/KOSDAQ 데이터를 제공합니다.

엔드포인트:
  GET /api/market              — 전체 시장 데이터 (기본)
  GET /api/market?type=detail  — 시총 상위 20종목 개별 상세 포함
"""

import json
from http.client import HTTPSConnection
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://m.stock.naver.com/",
}

# 시총 상위 주요 종목 (섹터 태깅용)
SECTOR_MAP = {
    "005930": "반도체", "000660": "반도체", "005935": "반도체",
    "005380": "자동차", "000270": "자동차", "012330": "자동차",
    "373220": "2차전지", "006400": "2차전지",
    "207940": "바이오", "068270": "바이오",
    "012450": "방산", "079550": "방산",
    "034020": "에너지", "009540": "건설",
    "055550": "금융", "105560": "금융",
    "035420": "IT/플랫폼", "035720": "IT/플랫폼",
    "402340": "지주/투자",
}


def _naver_get(path: str) -> dict | list | None:
    conn = HTTPSConnection("m.stock.naver.com", timeout=10)
    conn.request("GET", f"/api{path}", headers=NAVER_HEADERS)
    resp = conn.getresponse()
    data = resp.read().decode("utf-8")
    conn.close()
    if resp.status != 200:
        return None
    return json.loads(data)


def _stock_detail(code: str) -> dict | None:
    """개별 종목 상세 (PER, PBR, 배당, 거래대금 등)"""
    return _naver_get(f"/stock/{code}/basic")


def _collect_market(market: str) -> dict:
    """단일 시장 데이터 수집"""
    m = {}
    m["basic"] = _naver_get(f"/index/{market}/basic")
    m["rise"] = _naver_get(f"/stocks/up/{market}?page=1&pageSize=10")
    m["fall"] = _naver_get(f"/stocks/down/{market}?page=1&pageSize=10")
    m["market_cap"] = _naver_get(f"/stocks/marketValue/{market}?page=1&pageSize=20")
    return m


def _enrich_with_details(data: dict) -> dict:
    """시총 상위 종목에 개별 상세 데이터 + 섹터 태깅 추가"""
    for market in ["KOSPI", "KOSDAQ"]:
        mc = data.get(market, {}).get("market_cap", {})
        stocks = mc.get("stocks", []) if isinstance(mc, dict) else []

        enriched = []
        for stock in stocks[:20]:
            code = stock.get("itemCode", "")
            detail = _stock_detail(code)
            if detail:
                stock["detail"] = {
                    "per": detail.get("per"),
                    "pbr": detail.get("pbr"),
                    "dividendYield": detail.get("dividendYield"),
                    "accumulatedTradingValue": detail.get("accumulatedTradingValue"),
                    "accumulatedTradingVolume": detail.get("accumulatedTradingVolume"),
                    "foreignRatio": detail.get("foreignRatio"),
                    "high52wPrice": detail.get("high52wPrice"),
                    "low52wPrice": detail.get("low52wPrice"),
                    "marketValue": detail.get("marketValue"),
                }
            stock["sector"] = SECTOR_MAP.get(code, "기타")
            enriched.append(stock)

        if isinstance(mc, dict):
            mc["stocks"] = enriched

    return data


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            data_type = query.get("type", ["basic"])[0]

            data = {}
            for market in ["KOSPI", "KOSDAQ"]:
                data[market] = _collect_market(market)

            # detail 모드: 시총 상위 종목 개별 상세 추가
            if data_type == "detail":
                data = _enrich_with_details(data)

            self._respond(200, data)
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _respond(self, status: int, body: dict):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "s-maxage=300, stale-while-revalidate=60")
        self.end_headers()
        self.wfile.write(payload)
