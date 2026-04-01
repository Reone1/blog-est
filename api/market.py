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


def _naver_get(path: str) -> dict | list | None:
    conn = HTTPSConnection("m.stock.naver.com", timeout=10)
    conn.request("GET", f"/api{path}", headers=NAVER_HEADERS)
    resp = conn.getresponse()
    data = resp.read().decode("utf-8")
    conn.close()
    if resp.status != 200:
        return None
    return json.loads(data)


def _collect_all() -> dict:
    """KOSPI + KOSDAQ 전체 데이터 수집"""
    result = {}

    for market in ["KOSPI", "KOSDAQ"]:
        m = {}

        # 지수 기본 정보
        m["basic"] = _naver_get(f"/index/{market}/basic")

        # 상승 종목
        m["rise"] = _naver_get(f"/stocks/up/{market}?page=1&pageSize=10")

        # 하락 종목
        m["fall"] = _naver_get(f"/stocks/down/{market}?page=1&pageSize=10")

        # 시가총액 상위
        m["market_cap"] = _naver_get(f"/stocks/marketValue/{market}?page=1&pageSize=10")

        result[market] = m

    return result


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = _collect_all()
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
