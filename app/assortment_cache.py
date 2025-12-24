import json
import os
from typing import Any

from app.ms_client import MoySkladClient

def _id_from_href(href: str) -> str:
    # .../entity/product/<id> or .../entity/bundle/<id>
    return href.rstrip("/").split("/")[-1]

class AssortmentCache:
    def __init__(self, ms: MoySkladClient, cache_path: str):
        self.ms = ms
        self.cache_path = cache_path
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

    def get(self, article: str) -> dict[str, Any] | None:
        return self._cache.get(article)

    def get_or_fetch(self, article: str) -> dict[str, Any] | None:
        v = self._cache.get(article)
        if v is not None:
            return v

        data = self.ms.list_assortment_by_article(article, limit=10)
        rows = (data or {}).get("rows") or []
        # берем первый совпавший (обычно один)
        if not rows:
            self._cache[article] = None
            self._dirty = True
            return None

        meta = (rows[0].get("meta") or {})
        if not meta.get("href") or not meta.get("type"):
            self._cache[article] = None
            self._dirty = True
            return None

        entry: dict[str, Any] = {
            "meta": {"href": meta["href"], "type": meta["type"]},
        }

        # если это комплект — подтянем компоненты
        if meta["type"] == "bundle":
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
                    "meta": {"href": a["href"], "type": a["type"]},
                })
            entry["components"] = comp_rows

        self._cache[article] = entry
        self._dirty = True
        return entry
