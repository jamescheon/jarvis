import json
import os
import re
import urllib.parse
import urllib.request

CLIENT_ID = os.environ.get("NAVER_SEARCH_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("NAVER_SEARCH_CLIENT_SECRET", "")

LOCAL_TOOL = {
    "name": "naver_local_search",
    "description": "네이버 지역 검색으로 카페, 맛집, 병원 등 특정 지역의 실제 업체 목록을 리뷰(방문자 리뷰) "
    "수 기준 인기순으로 조회합니다. '가장 인기 있는/많이 찾는/검색되는 OO' 같은 질문에 사용하세요.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "예: '원주 카페', '강남 파스타'"},
        },
        "required": ["query"],
    },
}


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "")


def local_search(query: str) -> str:
    if not (CLIENT_ID and CLIENT_SECRET):
        return "네이버 검색 API 키가 설정되지 않았습니다."

    url = "https://openapi.naver.com/v1/search/local.json?" + urllib.parse.urlencode(
        {"query": query, "display": 5, "sort": "comment"}
    )
    req = urllib.request.Request(
        url,
        headers={
            "X-Naver-Client-Id": CLIENT_ID,
            "X-Naver-Client-Secret": CLIENT_SECRET,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return f"지역 검색 실패: {exc}"

    items = data.get("items", [])
    if not items:
        return f'"{query}"에 대한 검색 결과가 없습니다.'

    results = [
        {
            "name": _strip_tags(item.get("title")),
            "category": item.get("category"),
            "address": item.get("roadAddress") or item.get("address"),
        }
        for item in items
    ]
    return json.dumps(results, ensure_ascii=False)
