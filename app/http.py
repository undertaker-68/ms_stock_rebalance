import requests
from typing import Any

class HttpError(RuntimeError):
    pass

def request_json(method: str, url: str, *, headers: dict[str, str] | None = None, json: Any | None = None, timeout: int = 60) -> Any:
    r = requests.request(method, url, headers=headers, json=json, timeout=timeout)
    if r.status_code >= 400:
        raise HttpError(f"{method} {url} -> {r.status_code}: {r.text[:500]}")
    if not r.text:
        return None
    return r.json()
