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
        # Остатки по складам (стандартный отчёт)
        url = "https://api.moysklad.ru/api/remap/1.2/report/stock/bystore"
        return request_json("GET", url, headers=self._headers())

    def list_assortment_by_article(self, article: str, limit: int = 1) -> Any:
        # Ищем товар/комплект по артикулу
        url = "https://api.moysklad.ru/api/remap/1.2/entity/assortment"
        # фильтр: article=...
        params = f"?filter=article={article}&limit={limit}"
        return request_json("GET", url + params, headers=self._headers())
