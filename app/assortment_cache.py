import json
import os
from typing import Any

def _id_from_href(href: str) -> str:
    return href.rstrip("/").split("/")[-1]

class AssortmentCache:
    def __init__(self, ms, cache_path: str, article2meta: dict[str, dict]):
        self.ms = ms
        self.cache_path = cache_path
        self.article2meta = article2meta  # <-- главное: готовая карта
        self._cache: dict[str, Any] = {}
        self._dirty = False
        self._load()

    def _load(self):
        if not os.path.exists(self.cache_path):
            self._cache = {}
            return
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                self._cache = json.load(f) or {}
        except Exception:
            self._cache = {}

    def save(self):
        if not self._dirty:
            return
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        tmp = self.cache_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.cache_path)
        self._dirty = False

    def get_meta(self, article: str) -> dict[str, Any] | None:
        m = self.article2meta.get(article)
        if not m:
            return None
        return {"href": m["href"], "type": m["type"]}

    def get_bundle_components(self, article: str) -> list[dict[str, Any]] | None:
        """
        Возвращает список компонентов bundle:
          [{"qty": <float>, "meta": {"href":..., "type":...}}, ...]
        Кэшируем в файле, чтобы не дергать bundle каждый запуск.
        """
        ent = self._cache.get(article)
        if ent and "components" in ent:
            return ent["components"]

        meta = self.get_meta(article)
        if not meta or meta.get("type") != "bundle":
            return None

        bundle_id = _id_from_href(meta["href"])
        b = self.ms.get_bundle(bundle_id)
        comps = (((b or {}).get("components") or {}).get("rows")) or []
        comp_rows = []
        for c in comps:
            qty = float(c.get("quantity") or 0)
            a = (c.get("assortment") or {}).get("meta") or {}
            if not a.get("href") or not a.get("type") or qty <= 0:
                continue
            comp_rows.append({
                "qty": qty,
                "meta": {"href": a["href"].split("?")[0], "type": a["type"]},
            })

        self._cache[article] = {"components": comp_rows}
        self._dirty = True
        return comp_rows
