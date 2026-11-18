import csv
import sqlite3

DB = 'db/watch_store.db'

def read_csv(path):
    with open(path, encoding='utf-8-sig') as f:   # utf-8-sig — BOM из Excel-CSV
        return list(csv.DictReader(f))

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# Сессии (450)
cur.executemany("""INSERT OR REPLACE INTO analytics_sessions VALUES (?,?,?,?,?)""",
    [(int(r['session_id']), int(r['user_id']), r['session_start'],
      r['device_type'], r['traffic_source']) for r in read_csv('db/Sessions_analytics.csv')])

# Заказы (150)
cur.executemany("""INSERT OR REPLACE INTO analytics_orders VALUES (?,?,?,?,?,?)""",
    [(int(r['order_id']), int(r['user_id']), int(r['session_id']),
      r['order_date'], r['status'], int(r['discount_percent']))
     for r in read_csv('db/Orders_analytics.csv')])

# Состав заказов (225)
cur.executemany("""INSERT OR REPLACE INTO analytics_order_items VALUES (?,?,?,?,?)""",
    [(int(r['order_item_id']), int(r['order_id']), int(r['model_id']),
      int(r['quantity']), float(r['unit_price'])) for r in read_csv('db/Order_items_analytics.csv')])

# Справочник моделей (31)
cur.executemany("""INSERT OR REPLACE INTO analytics_models VALUES (?,?,?)""",
    [(int(r['model_id']), r['model_name'], r['category'])
     for r in read_csv('db/Watch_models_analytics.csv')])

# Контроль связности
orphans = cur.execute("""
    SELECT COUNT(*) FROM analytics_order_items oi
    LEFT JOIN analytics_orders o ON o.order_id = oi.order_id
    WHERE o.order_id IS NULL""").fetchone()[0]
print('Сиротских строк состава:', orphans)   # ожидается 0

conn.commit()
for t in ('analytics_sessions', 'analytics_orders', 'analytics_order_items', 'analytics_models'):
    print(f"{t}: {cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]}")
conn.close()
