from dataclasses import dataclass
from typing import Dict, List, Tuple
import math

@dataclass
class MoveLine:
    article: str
    qty: int  # qty "штук товара" (или "комплектов" если это bundle)

@dataclass
class PlannedMove:
    source_store: str
    target_store: str
    lines: List[MoveLine]

def targets_for_total(total: int, store_sklad: str, store_ozon: str, store_wb: str, store_yandex: str) -> Dict[str, int]:
    """
    Возвращает целевое распределение по складам.
    Исключения для total<=4 + далее проценты (75/10/10/5), округление вниз, остаток на СКЛАД.
    """
    if total <= 0:
        return {store_sklad: 0, store_ozon: 0, store_wb: 0, store_yandex: 0}

    if total == 1:
        return {store_sklad: 0, store_ozon: 1, store_wb: 0, store_yandex: 0}
    if total == 2:
        return {store_sklad: 0, store_ozon: 1, store_wb: 1, store_yandex: 0}
    if total == 3:
        return {store_sklad: 0, store_ozon: 1, store_wb: 1, store_yandex: 1}
    if total == 4:
        return {store_sklad: 1, store_ozon: 1, store_wb: 1, store_yandex: 1}

    # проценты
    oz = math.floor(total * 0.10)
    wb = math.floor(total * 0.10)
    ya = math.floor(total * 0.05)
    sk = total - (oz + wb + ya)  # остаток на СКЛАД
    return {store_sklad: sk, store_ozon: oz, store_wb: wb, store_yandex: ya}

def plan_moves_for_article(
    article: str,
    current: Dict[str, int],
    targets: Dict[str, int],
) -> List[Tuple[str, str, int]]:
    """
    Возвращает список перемещений (source, target, qty) для одного артикула.
    """
    stores = set(targets.keys())
    cur = {s: int(current.get(s, 0)) for s in stores}
    tgt = {s: int(targets.get(s, 0)) for s in stores}

    delta = {s: tgt[s] - cur[s] for s in stores}
    needers = [(s, delta[s]) for s in stores if delta[s] > 0]
    donors = [(s, -delta[s]) for s in stores if delta[s] < 0]

    # простая жадная стыковка доноров с получателями
    moves: List[Tuple[str, str, int]] = []
    i = 0
    j = 0
    while i < len(donors) and j < len(needers):
        ds, dqty = donors[i]
        ns, nqty = needers[j]
        x = min(dqty, nqty)
        if x > 0:
            moves.append((ds, ns, x))
            dqty -= x
            nqty -= x
        donors[i] = (ds, dqty)
        needers[j] = (ns, nqty)
        if donors[i][1] == 0:
            i += 1
        if needers[j][1] == 0:
            j += 1

    return moves

def group_moves(
    per_article_moves: Dict[str, List[Tuple[str, str, int]]],
) -> Dict[Tuple[str, str], List[MoveLine]]:
    """
    Группируем по паре (source,target) и собираем линии.
    """
    out: Dict[Tuple[str, str], List[MoveLine]] = {}
    for art, moves in per_article_moves.items():
        for s, t, q in moves:
            out.setdefault((s, t), []).append(MoveLine(article=art, qty=int(q)))
    return out
