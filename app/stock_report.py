from typing import Any

def _store_id_from_meta(meta: dict[str, Any] | None) -> str | None:
    if not meta:
        return None
    href = meta.get("href") or ""
    if not href:
        return None
    return href.rstrip("/").split("/")[-1]

def extract_need_by_article(rep: dict[str, Any], store_ids: set[str]) -> dict[str, dict[str, int]]:
    """
    Возвращает: article -> {store_id: need_int}
    need = stock - reserve
    """
    out: dict[str, dict[str, int]] = {}
    rows = (rep or {}).get("rows") or []

    for r in rows:
        article = r.get("article")
        if not article:
            continue

        # В отчёте встречаются разные структуры; поддержим 2 варианта:
        # 1) r["stockByStore"] = [{store: {meta}, stock, reserve, ...}, ...]
        # 2) r["stockByStore"] может называться иначе — попробуем несколько ключей
        sbs = r.get("stockByStore") or r.get("stockByStoreRows") or r.get("stockByStoreData")
        if not sbs:
            continue

        per: dict[str, int] = {}
        for x in sbs:
            store_meta = (x.get("store") or {}).get("meta") or x.get("storeMeta") or None
            sid = _store_id_from_meta(store_meta)
            if not sid or sid not in store_ids:
                continue
            stock = float(x.get("stock") or 0)
            reserve = float(x.get("reserve") or 0)
            need = int(stock - reserve)
            if need < 0:
                need = 0
            per[sid] = need

        # если по нужным складам вообще нет данных — пропускаем
        if any(sid in per for sid in store_ids):
            out[str(article)] = per

    return out
