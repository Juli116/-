import sqlite3

def calculate_price(cur, model_id, base_price):
    cur.execute("""SELECT COUNT(*) FROM order_items oi
                   JOIN orders o ON o.order_id = oi.order_id
                   WHERE oi.model_id = ? AND o.order_date >= DATE('now', '-1 month')""",
                (model_id,))
    return round(base_price * 0.75, 2) if cur.fetchone()[0] == 0 else base_price


def calculate_price_detailed(cur, model_id, base_price):
    """Возвращает (name, final_price, discount_size) — по домашнему заданию."""
    row = cur.execute("SELECT name FROM models WHERE model_id=?", (model_id,)).fetchone()
    name = row[0] if row else '—'
    cur.execute("""SELECT COUNT(*) FROM order_items oi
                   JOIN orders o ON o.order_id = oi.order_id
                   WHERE oi.model_id = ? AND o.order_date >= DATE('now', '-1 month')""",
                (model_id,))
    has_orders = cur.fetchone()[0] != 0
    return name, (base_price if has_orders else round(base_price * 0.75, 2)), (0 if has_orders else 25)
