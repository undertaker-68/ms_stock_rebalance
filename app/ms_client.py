from app.http import request_json
from typing import Any

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

    def list_products(self, offset: int = 0, limit: int = 1000) -> Any:
        url = f"https://api.moysklad.ru/api/remap/1.2/entity/product?offset={offset}&limit={limit}"
        return request_json("GET", url, headers=self._headers())

    def list_bundles(self, offset: int = 0, limit: int = 1000) -> Any:
        url = f"https://api.moysklad.ru/api/remap/1.2/entity/bundle?offset={offset}&limit={limit}"
        return request_json("GET", url, headers=self._headers())

    def list_assortment_by_article(self, article: str, limit: int = 1) -> Any:
        url = "https://api.moysklad.ru/api/remap/1.2/entity/assortment"
        params = f"?filter=article={article}&limit={limit}"
        return request_json("GET", url + params, headers=self._headers())

    def get_bundle(self, bundle_id: str) -> Any:
        url = f"https://api.moysklad.ru/api/remap/1.2/entity/bundle/{bundle_id}"
        return request_json("GET", url, headers=self._headers())

    def create_move(self, payload: dict[str, Any]) -> Any:
        url = "https://api.moysklad.ru/api/remap/1.2/entity/move"
        return request_json("POST", url, headers=self._headers(), json=payload)
