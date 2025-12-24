from dataclasses import dataclass
from typing import Any, Iterable
from app.http import request_json, HttpError

@dataclass
class OzonClient:
    client_id: str
    api_key: str

    def _headers(self) -> dict[str, str]:
        return {
            "Client-Id": str(self.client_id),
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def iter_offer_ids(self, visibility: list[str], page_limit: int = 1000) -> Iterable[str]:
        """
        Ozon Seller API: /v3/product/list
        visibility в запросе должен быть ОДНИМ enum значением, поэтому делаем запрос по каждому
        visibility отдельно и возвращаем offer_id.
        """
        url = "https://api-seller.ozon.ru/v3/product/list"

        for vis in visibility:
            last_id = ""
            while True:
                payload: dict[str, Any] = {
                    "filter": {"visibility": vis},
                    "last_id": last_id,
                    "limit": page_limit,
                }
                try:
                    data = request_json("POST", url, headers=self._headers(), json=payload)
                except HttpError as e:
                    # Если Ozon не принимает enum (или другой 400) — просто пропускаем этот vis
                    print(f"[OZON] skip visibility={vis} due to error: {e}")
                    break

                items = (data or {}).get("result", {}).get("items", []) or []
                for it in items:
                    oid = it.get("offer_id")
                    if oid:
                        yield str(oid)

                last_id = (data or {}).get("result", {}).get("last_id") or ""
                if not last_id:
                    break
