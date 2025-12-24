from typing import Any, Dict, List, Tuple
from app.ms_client import MoySkladClient
from app.assortment_cache import AssortmentCache

def store_meta(store_id: str) -> dict[str, Any]:
    return {"meta": {"href": f"https://api.moysklad.ru/api/remap/1.2/entity/store/{store_id}", "type": "store"}}

def org_meta(org_id: str) -> dict[str, Any]:
    return {"meta": {"href": f"https://api.moysklad.ru/api/remap/1.2/entity/organization/{org_id}", "type": "organization"}}

def move_state_meta_for_move(state_id: str) -> dict[str, Any]:
    return {"meta": {"href": f"https://api.moysklad.ru/api/remap/1.2/entity/move/metadata/states/{state_id}", "type": "state"}}

def move_state_for_target(cfg, target_store_id: str) -> str | None:
    if target_store_id == cfg.store_ozon:
        return cfg.state_to_ozon
    if target_store_id == cfg.store_wb:
        return cfg.state_to_wb
    if target_store_id == cfg.store_yandex:
        return cfg.state_to_yandex
    if target_store_id == cfg.store_sklad:
        return cfg.state_to_sklad
    return None

def chunked(lst: List[Any], n: int) -> List[List[Any]]:
    return [lst[i:i+n] for i in range(0, len(lst), n)]

def create_moves(
    *,
    ms: MoySkladClient,
    cache: AssortmentCache,
    cfg,
    grouped: Dict[Tuple[str, str], List[dict]],
    dry_run: bool,
    max_positions: int,
) -> None:
    for (source_id, target_id), lines in grouped.items():
        total = sum(int(x.get("qty") or 0) for x in lines)
        print(f"[PLAN] Move {source_id} -> {target_id} lines={len(lines)} total_qty={total}")

        if dry_run:
            continue

        positions = []
        skipped = 0
        for ln in lines:
            art = ln["article"]
            qty = int(ln["qty"])
            if qty <= 0:
                continue

            meta = cache.get_meta(art)
            if not meta:
                skipped += 1
                continue

            positions.append({
                "assortment": {"meta": meta},
                "quantity": qty
            })

        if not positions:
            print(f"[SKIP] No positions after meta resolve, skipped={skipped}")
            continue

        for part in chunked(positions, max_positions):
            payload: dict[str, Any] = {
                "organization": org_meta(cfg.ms_org_id),
                "sourceStore": store_meta(source_id),
                "targetStore": store_meta(target_id),
                "positions": {"rows": part},
            }

            st = move_state_for_target(cfg, target_id)
            if st:
                payload["state"] = move_state_meta_for_move(st)

            print(f"[SEND] creating move {source_id} -> {target_id} positions={len(part)} skipped={skipped}")

            try:
                ms.create_move(payload)
                print("[OK] created move")
            except Exception as e:
                print(f"[ERR] create move failed: {e}")
                continue
