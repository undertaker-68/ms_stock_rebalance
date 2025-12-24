from typing import Any, Dict, Tuple

def _id_from_href(href: str) -> str:
    return href.split("?")[0].rstrip("/").split("/")[-1]

def build_catalog(ms, include_bundles: bool = True) -> Tuple[Dict[str, str], Dict[str, dict]]:
    """
    Возвращает:
      id2article: object_id -> article
      article2meta: article -> {"href":..., "type":...}
    """
    id2a: Dict[str, str] = {}
    a2m: Dict[str, dict] = {}

    def ingest(rows: list[dict]):
        for r in rows:
            meta = (r.get("meta") or {})
            href = meta.get("href")
            typ = meta.get("type")
            article = r.get("article")
            if not href or not typ or not article:
                continue
            obj_id = _id_from_href(href)
            art = str(article)
            id2a[obj_id] = art
            a2m[art] = {"href": href.split("?")[0], "type": typ}

    # products
    offset = 0
    limit = 1000
    while True:
        data = ms.list_products(offset=offset, limit=limit)
        rows = (data or {}).get("rows") or []
        ingest(rows)
        if len(rows) < limit:
            break
        offset += limit

    if include_bundles:
        offset = 0
        while True:
            data = ms.list_bundles(offset=offset, limit=limit)
            rows = (data or {}).get("rows") or []
            ingest(rows)
            if len(rows) < limit:
                break
            offset += limit

    return id2a, a2m
