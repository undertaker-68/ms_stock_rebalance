from typing import Dict
import math

def _id_from_href(href: str) -> str:
    return href.rstrip("/").split("/")[-1]

def apply_bundle_current(
    *,
    articles: set[str],
    store_ids: set[str],
    current_by_article: Dict[str, Dict[str, int]],
    cache,
    id2article: Dict[str, str],
    article2meta: Dict[str, dict],
) -> None:
    """
    Для bundle-артикулов пересчитываем current_by_article[article][store]
    как min floor(need_component_store / qty_component) по всем компонентам.
    """
    for art in list(articles):
        meta = article2meta.get(art)
        if not meta or meta.get("type") != "bundle":
            continue

        comps = cache.get_bundle_components(art) or []
        if not comps:
            # нет компонентов — не трогаем
            continue

        per_store = {}
        for sid in store_ids:
            mins = []
            for c in comps:
                qty = float(c.get("qty") or 0)
                m = c.get("meta") or {}
                href = m.get("href") or ""
                if qty <= 0 or not href:
                    continue
                comp_id = _id_from_href(href)
                comp_article = id2article.get(comp_id)
                if not comp_article:
                    mins = []
                    break
                comp_need = int((current_by_article.get(comp_article) or {}).get(sid, 0))
                mins.append(math.floor(comp_need / qty))
            if mins:
                per_store[sid] = max(0, int(min(mins)))
            else:
                per_store[sid] = 0

        current_by_article[art] = per_store
