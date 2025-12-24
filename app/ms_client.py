from app.http import request_json
from typing import Any
import urllib.parse

class MoySkladClient:
    def __init__(self, token: str):
        self.token = token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        }

    def report_stock_by_store(self) -> Any:
        url = "https://api.moysklad.ru/api/remap/1.2/report/stock/bystore"
        return request_json("GET", url, headers=self._headers())

    def list_products(self, offset: int = 0, limit: int = 1000, expand: str | None = None) -> Any:
        base = "https://api.moysklad.ru/api/remap/1.2/entity/product"
        qs = f"offset={offset}&limit={limit}"
        if expand:
            qs += "&expand=" + urllib.parse.quote(expand, safe=",().")
        return request_json("GET", f"{base}?{qs}", headers=self._headers())

    def list_bundles(self, offset: int = 0, limit: int = 1000, expand: str | None = None) -> Any:
        base = "https://api.moysklad.ru/api/remap/1.2/entity/bundle"
        qs = f"offset={offset}&limit={limit}"
        if expand:
            qs += "&expand=" + urllib.parse.quote(expand, safe=",().")
        return request_json("GET", f"{base}?{qs}", headers=self._headers())

    def get_bundle(self, bundle_id: str) -> Any:
        url = f"https://api.moysklad.ru/api/remap/1.2/entity/bundle/{bundle_id}"
        return request_json("GET", url, headers=self._headers())

    def create_move(self, payload: dict[str, Any]) -> Any:
        url = "https://api.moysklad.ru/api/remap/1.2/entity/move"
        return request_json("POST", url, headers=self._headers(), json=payload)
