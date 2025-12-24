from typing import Any, Dict, Tuple

def _id_from_href(href: str) -> str:
    return href.split("?")[0].rstrip("/").split("/")[-1]

def build_id_to_article(ms, include_bundles: bool = True) -> Dict[str, str]:
    """
    Собираем отображение: product_or_bundle_id -> article
    Пагинацией, чтобы не долбить API по одному.
    """
    id2a: Dict[str, str] = {}

    # products
    offset = 0
    limit = 1000
    while True:
        data = ms.list_products(offset=offset, limit=limit)
        rows = (data or {}).get("rows") or []
        for r in rows:
            meta = (r.get("meta") or {})
            href = meta.get("href")
            article = r.get("article")
            if href and article:
                id2a[_id_from_href(href)] = str(article)
        if len(rows) < limit:
            break
        offset += limit

    if include_bundles:
        offset = 0
        while True:
            data = ms.list_bundles(offset=offset, limit=limit)
            rows = (data or {}).get("rows") or []
            for r in rows:
                meta = (r.get("meta") or {})
                href = meta.get("href")
                article = r.get("article")
                if href and article:
                    id2a[_id_from_href(href)] = str(article)
            if len(rows) < limit:
                break
            offset += limit

    return id2a

def extract_need_by_article(rep: dict[str, Any], store_ids: set[str], id2article: Dict[str, str]) -> Dict[str, Dict[str, int]]:
    """
    Твой формат:
      row.meta.href = .../entity/product/<id>?expand=...
      row.stockByStore[]: { meta.href=.../entity/store/<id>, stock, reserve }
    В отчете нет article, поэтому маппим по id2article.
    """
    out: Dict[str, Dict[str, int]] = {}
    rows = (rep or {}).get("rows") or []

    for r in rows:
        meta = (r.get("meta") or {})
        href = meta.get("href") or ""
        if not href:
            continue
        obj_id = _id_from_href(href)
        article = id2article.get(obj_id)
        if not article:
            # товар без артикула нам не нужен
            continue

        sbs = r.get("stockByStore") or []
        per: Dict[str, int] = {}
        for x in sbs:
            sm = x.get("meta") or {}
            sh = sm.get("href") or ""
            if not sh:
                continue
            sid = _id_from_href(sh)
            if sid not in store_ids:
                continue
            stock = float(x.get("stock") or 0)
            reserve = float(x.get("reserve") or 0)
            need = int(stock - reserve)
            if need < 0:
                need = 0
            per[sid] = need

        out[article] = per

    return out
