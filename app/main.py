import os
from app.config import load_config
from app.ozon_client import OzonClient
from app.ms_client import MoySkladClient
from app.assortment_cache import AssortmentCache
from app.stock_report import extract_need_by_article
from app.planner import targets_for_total, plan_moves_for_article, group_moves
from app.state_store import load_state, save_state

def main():
    cfg = load_config()
    dry_run = os.getenv("DRY_RUN", "1").strip() != "0"

    oz1 = OzonClient(cfg.ozon1.client_id, cfg.ozon1.api_key)
    oz2 = OzonClient(cfg.ozon2.client_id, cfg.ozon2.api_key)

    offer_ids = set()
    for oid in oz1.iter_offer_ids(cfg.ozon_visibility, page_limit=cfg.ozon_page_limit):
        offer_ids.add(oid)
    for oid in oz2.iter_offer_ids(cfg.ozon_visibility, page_limit=cfg.ozon_page_limit):
        offer_ids.add(oid)

    print(f"Ozon offer_ids total: {len(offer_ids)}")

    ms = MoySkladClient(cfg.ms_token)
    cache = AssortmentCache(ms, cfg.cache_path)

    rep = ms.report_stock_by_store()
    store_ids = {cfg.store_sklad, cfg.store_ozon, cfg.store_wb, cfg.store_yandex}
    need_map = extract_need_by_article(rep, store_ids)
    print(f"MS stock report articles parsed: {len(need_map)}")

    # Берём только артикула из Ozon
    filtered = {a: need_map.get(a, {}) for a in offer_ids}
    print(f"Articles to process (ozon ∩ ms_report): {sum(1 for a in filtered if filtered[a] is not None)}")

    # state: чтобы потом перейти на режим "только изменившиеся"
    state = load_state(cfg.state_path)
    prev = state.get("last_need") or {}

    per_article_moves = {}
    changed = 0

    for article, cur in filtered.items():
        # cur может быть {}, если в отчете не было строки — считаем нулём
        cur_full = {sid: int(cur.get(sid, 0)) for sid in store_ids}
        total = sum(cur_full.values())

        tgt = targets_for_total(total, cfg.store_sklad, cfg.store_ozon, cfg.store_wb, cfg.store_yandex)

        # фильтр "изменилось ли"
        cur_sig = {k: cur_full[k] for k in sorted(cur_full.keys())}
        tgt_sig = {k: tgt[k] for k in sorted(tgt.keys())}
        key = article

        if prev.get(key) == {"cur": cur_sig, "tgt": tgt_sig}:
            continue

        changed += 1
        moves = plan_moves_for_article(article, cur_full, tgt)
        if moves:
            per_article_moves[article] = moves

        prev[key] = {"cur": cur_sig, "tgt": tgt_sig}

    print(f"Changed articles: {changed}")
    grouped = group_moves(per_article_moves)
    print(f"Planned move directions: {len(grouped)}")

    # преобразуем к формату mover
    grouped_lines = {}
    total_lines = 0
    for (s, t), lines in grouped.items():
        grouped_lines[(s, t)] = [{"article": ln.article, "qty": ln.qty} for ln in lines]
        total_lines += len(lines)

    print(f"Planned lines total: {total_lines}")
    print(f"DRY_RUN={1 if dry_run else 0}")

    from app.mover import create_moves
    create_moves(
        ms=ms,
        cache=cache,
        cfg=cfg,
        grouped=grouped_lines,
        dry_run=dry_run,
        max_positions=cfg.move_max_positions,
    )

    cache.save()
    state["last_need"] = prev
    save_state(cfg.state_path, state)

    print("DONE")

if __name__ == "__main__":
    main()
