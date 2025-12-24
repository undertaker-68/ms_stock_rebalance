from typing import Any, Dict, Tuple
import os

def _id_from_href(href: str) -> str:
    return href.split("?")[0].rstrip("/").split("/")[-1]

def _extract_price_from_saleprices(obj: dict, price_type_name: str) -> int | None:
    # salePrices: [{"value": 110000, "priceType": {"name": "Цена продажи", ...}}, ...]
    sps = obj.get("salePrices") or []
    for sp in sps:
        pt = sp.get("priceType") or {}
        name = pt.get("name")
        if name == price_type_name:
            v = sp.get("value")
            if isinstance(v, (int, float)):
                return int(v)
    return None

def build_catalog(ms, include_bundles: bool = True) -> Tuple[Dict[str, str], Dict[str, dict], Dict[str, int]]:
    """
    Возвращает:
      id2article: object_id -> article
      article2meta: article -> {"href":..., "type":...}
      article2price: article -> price(int, копейки) по типу цены MS_PRICE_TYPE_NAME (default: "Цена продажи")
    """
    id2a: Dict[str, str] = {}
    a2m: Dict[str, dict] = {}
    a2p: Dict[str, int] = {}

    price_type_name = os.getenv("MS_PRICE_TYPE_NAME", "Цена продажи")

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

            p = _extract_price_from_saleprices(r, price_type_name)
            if p is not None:
                a2p[art] = p

    expand = "salePrices.priceType"

    # products
    offset = 0
    limit = 1000
    while True:
        data = ms.list_products(offset=offset, limit=limit, expand=expand)
        rows = (data or {}).get("rows") or []
        ingest(rows)
        if len(rows) < limit:
            break
        offset += limit

    if include_bundles:
        offset = 0
        while True:
            data = ms.list_bundles(offset=offset, limit=limit, expand=expand)
            rows = (data or {}).get("rows") or []
            ingest(rows)
            if len(rows) < limit:
                break
            offset += limit

    return id2a, a2m, a2p
