# ms_stock_rebalance

Скрипт перераспределения остатков между 4 складами в МойСклад по пропорциям:
- СКЛАД 75%
- OZON 10%
- WB 10%
- YANDEX 5%

Источник остатков: МойСклад (stock - reserve).
Список обрабатываемых товаров: offer_id из Ozon (2 кабинета), visibility: VISIBLE + READY_TO_SELL.

Запуск: cron раз в 5 часов.
Ошибки по отдельным операциям: пропускаем и продолжаем.

## Быстрый старт
```bash
cd /root/ms_stock_rebalance
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env

python -m app.main


---

## 2) Код (минимальный каркас, который уже запускается)
Я сейчас дам рабочий “скелет” проекта: он умеет
- читать `.env`,
- сходить в Ozon и собрать offer_id (2 кабинета),
- сходить в МойСклад и получить отчёт по остаткам,
- подготовить базу для следующего шага (планер и перемещения добавим дальше).

### 2.1 `app/__init__.py`
```bash
cat > app/__init__.py <<'EOF'
