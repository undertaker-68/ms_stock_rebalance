from dataclasses import dataclass
from dotenv import load_dotenv
import os

@dataclass
class OzonCabinet:
    client_id: str
    api_key: str

@dataclass
class Config:
    ms_token: str
    ms_org_id: str

    store_sklad: str
    store_ozon: str
    store_wb: str
    store_yandex: str

    state_to_ozon: str | None
    state_to_wb: str | None
    state_to_yandex: str | None
    state_to_sklad: str | None

    ozon1: OzonCabinet
    ozon2: OzonCabinet
    ozon_visibility: list[str]

    state_path: str
    cache_path: str
    move_max_positions: int
    ozon_page_limit: int

def _req(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

def load_config() -> Config:
    load_dotenv()

    cfg = Config(
        ms_token=_req("MS_TOKEN"),
        ms_org_id=_req("MS_ORG_ID"),

        store_sklad=_req("MS_STORE_SKLAD"),
        store_ozon=_req("MS_STORE_OZON"),
        store_wb=_req("MS_STORE_WB"),
        store_yandex=_req("MS_STORE_YANDEX"),

        state_to_ozon=os.getenv("MS_STATE_TO_OZON"),
        state_to_wb=os.getenv("MS_STATE_TO_WB"),
        state_to_yandex=os.getenv("MS_STATE_TO_YANDEX"),
        state_to_sklad=os.getenv("MS_STATE_TO_SKLAD"),

        ozon1=OzonCabinet(
            client_id=_req("OZON1_CLIENT_ID"),
            api_key=_req("OZON1_API_KEY"),
        ),
        ozon2=OzonCabinet(
            client_id=_req("OZON2_CLIENT_ID"),
            api_key=_req("OZON2_API_KEY"),
        ),

        ozon_visibility=[s.strip() for s in _req("OZON_VISIBILITY").split(",") if s.strip()],
        state_path=os.getenv("STATE_PATH", "./state/state.json"),
        cache_path=os.getenv("CACHE_PATH", "./state/assortment_cache.json"),
        move_max_positions=int(os.getenv("MOVE_MAX_POSITIONS", "500")),
        ozon_page_limit=int(os.getenv("OZON_PAGE_LIMIT", "1000")),
    )
    return cfg
