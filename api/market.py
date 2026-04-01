"""
Vercel Serverless Function - 네이버 시장 데이터 프록시

Claude Code 세션에서 직접 네이버 API를 호출할 수 없으므로,
Vercel을 프록시로 사용하여 시장 데이터를 수집합니다.
"""

import json
from http.client import HTTPSConnection
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


NAVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://m.stock.naver.com/",
}

MARKET_TYPES = {"KOSPI", "KOSDAQ"}


def _naver_get(path: str) -> dict:
    conn = HTTPSConnection("m.stock.naver.com", timeout=10)
    conn.request("GET", path, headers=NAVER_HEADERS)
    resp = conn.getresponse()
    data = resp.read().decode("utf-8")
    conn.close()
    if resp.status != 200:
        raise Exception(f"Naver API {resp.status}: {data[:200]}")
    return json.loads(data)


def _collect_market_data(market_type: str) -> dict:
    result = {}
    result["basic"] = _naver_get(f"/api/index/{market_type}/basic")
    for category in ["rise", "fall", "volume"]:
        result[category] = _naver_get(
            f"/api/index/{market_type}/ranking/{category}?page=1&pageSize=5"
        )
    return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            market = query.get("market", ["KOSPI"])[0].upper()

            if market not in MARKET_TYPES:
                self._respond(400, {"error": f"Invalid market: {market}"})
                return

            data = {}
            for m in MARKET_TYPES:
                data[m] = _collect_market_data(m)

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
