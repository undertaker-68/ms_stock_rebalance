from app.config import load_config
from app.ozon_client import OzonClient
from app.ms_client import MoySkladClient

def main():
    cfg = load_config()

    oz1 = OzonClient(cfg.ozon1.client_id, cfg.ozon1.api_key)
    oz2 = OzonClient(cfg.ozon2.client_id, cfg.ozon2.api_key)

    offer_ids = set()
    for oid in oz1.iter_offer_ids(cfg.ozon_visibility, page_limit=cfg.ozon_page_limit):
        offer_ids.add(oid)
    for oid in oz2.iter_offer_ids(cfg.ozon_visibility, page_limit=cfg.ozon_page_limit):
        offer_ids.add(oid)

    print(f"Ozon offer_ids total: {len(offer_ids)}")

    ms = MoySkladClient(cfg.ms_token)
    rep = ms.report_stock_by_store()
    # пока просто подтверждаем, что отчёт пришёл
    stores = (rep or {}).get("rows") or []
    print(f"MS stock report rows: {len(stores)}")

    # Дальше: планирование и создание перемещений (добавим следующим коммитом)
    print("OK: skeleton run finished")

if __name__ == "__main__":
    main()
