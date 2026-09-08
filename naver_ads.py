import base64
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request

CUSTOMER_ID = os.environ.get("NAVER_AD_CUSTOMER_ID", "")
ACCESS_LICENSE = os.environ.get("NAVER_AD_ACCESS_LICENSE", "")
SECRET_KEY = os.environ.get("NAVER_AD_SECRET_KEY", "")

VOLUME_TOOL = {
    "name": "naver_search_volume",
    "description": "네이버에서 특정 키워드의 최근 한 달간 PC/모바일 검색량을 조회합니다. "
    "특정 단어, 브랜드, 상품명의 네이버 검색량이나 검색 순위를 물어볼 때 사용하세요.",
    "input_schema": {
        "type": "object",
        "properties": {
            "keyword": {"type": "string", "description": "검색량을 조회할 키워드"},
        },
        "required": ["keyword"],
    },
}


def _signed_headers(method: str, uri: str) -> dict:
    timestamp = str(int(time.time() * 1000))
    message = f"{timestamp}.{method}.{uri}"
    signature = base64.b64encode(
        hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    return {
        "X-Timestamp": timestamp,
        "X-API-KEY": ACCESS_LICENSE,
        "X-Customer": CUSTOMER_ID,
        "X-Signature": signature,
    }


def search_volume(keyword: str) -> str:
    if not (CUSTOMER_ID and ACCESS_LICENSE and SECRET_KEY):
        return "네이버 검색광고 API 키가 설정되지 않았습니다."

    uri = "/keywordstool"
    query = urllib.parse.urlencode({"hintKeywords": keyword, "showDetail": "1"})
    url = f"https://api.naver.com{uri}?{query}"
    req = urllib.request.Request(url, headers=_signed_headers("GET", uri))
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return f"검색량 조회 실패: {exc}"

    items = data.get("keywordList", [])[:5]
    if not items:
        return f'"{keyword}"에 대한 검색량 데이터를 찾지 못했습니다.'

    results = [
        {
            "keyword": item.get("relKeyword"),
            "monthly_pc_searches": item.get("monthlyPcQcCnt"),
            "monthly_mobile_searches": item.get("monthlyMobileQcCnt"),
        }
        for item in items
    ]
    return json.dumps(results, ensure_ascii=False)
