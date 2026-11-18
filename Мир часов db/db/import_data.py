import pandas  as pd # type: ignore
import sqlite3
from datetime import datetime

DB = 'db/watch_store.db'


def xl(path):
    return pd.read_excel(path)


def run():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(open('db/schema.sql', encoding='utf-8').read())
    cur = conn.cursor()

    # 1. Варианты исполнения
    for v in xl('db/import/Variants_import.xlsx')['Вариант исполнения']:
        cur.execute("INSERT INTO variants(name) VALUES (?)", (v,))

    # 2. Пользователи: ФИО собираем из трёх колонок, пароль NULL, роль «Клиент»
    fio_map = {}
    for _, r in xl('db/import/Users_import.xlsx').iterrows():
        fio = f"{r['Фамилия']} {r['Имя']} {r['Отчество']}"
        role = 'Клиент' if r['Роль'] == 'Авторизованный пользователь' else r['Роль']
        cur.execute("INSERT INTO users(login, password, full_name, role) VALUES (?,?,?,?)",
                    (r['Логин'], None, fio, role))
        fio_map[fio] = cur.lastrowid

    # 3. Модели: пустое изображение → NULL (проверка pd.isna обязательна!)
    cat_map, model_map = {}, {}
    for _, r in xl('db/import/Products_import.xlsx').iterrows():
        cur.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (r['Категория'],))
        cid = cur.execute("SELECT category_id FROM categories WHERE name=?",
                          (r['Категория'],)).fetchone()[0]
        cur.execute("INSERT OR IGNORE INTO subcategories(category_id, name) VALUES (?,?)",
                    (cid, r['Подкатегория']))
        sid = cur.execute("SELECT subcategory_id FROM subcategories WHERE category_id=? AND name=?",
                          (cid, r['Подкатегория'])).fetchone()[0]
        cur.execute("INSERT OR IGNORE INTO manufacturers(name) VALUES (?)", (r['Производство'],))
        mfr_id = cur.execute("SELECT manufacturer_id FROM manufacturers WHERE name=?",
                             (r['Производство'],)).fetchone()[0]
        img = None if pd.isna(r['Изображение']) else str(r['Изображение']).strip()
        cur.execute("""INSERT INTO models(name, manufacturer_id, category_id, subcategory_id,
                       image_name, description, composition, base_price)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (r['Наименование товара'], mfr_id, cid, sid, img,
                     r['Описание'], r['Состав'], float(r['Цена'])))
        key = (r['Наименование товара'], r['Производство'])
        model_map[key] = cur.lastrowid
        cat_map[key] = r['Категория']

    # 4. Остатки (значения готовые — списаний при импорте НЕТ)
    for _, r in xl('db/import/Stock_Items_import.xlsx').iterrows():
        mid = model_map[(r['Наименование товара'], r['Производство'])]
        vid = cur.execute("SELECT variant_id FROM variants WHERE name=?",
                          (r['Вариант исполнения'],)).fetchone()[0]
        cur.execute("INSERT INTO stock_items(model_id, variant_id, quantity) VALUES (?,?,?)",
                    (mid, vid, int(r['Количество доступное для заказа'])))

    # 5. Заказы: группировка по номеру, сверка даты/ФИО/категории
    buf, seen = {}, set()
    for _, r in xl('db/import/Orders_import.xlsx').iterrows():
        oid = int(r['Номер заказа'])
        ds = r['Дата заказа'].strftime('%d.%m.%Y')       # Excel-дата → строка
        if oid in seen:
            assert buf[oid]['date'] == ds and buf[oid]['fio'] == r['ФИО'], \
                f"Заказ {oid}: дата/ФИО не совпадают между строками"
        else:
            seen.add(oid)
            buf[oid] = {'date': ds, 'fio': r['ФИО'], 'items': []}
        key = (r['Наименование товара'], r['Производство'])
        assert cat_map[key] == r['Категория'], f"Заказ {oid}: категория не совпадает с каталогом"
        vid = cur.execute("SELECT variant_id FROM variants WHERE name=?",
                          (r['Вариант исполнения'],)).fetchone()[0]
        price = float(str(r['Цена за единицу']).replace(',', ''))   # "2,060.00" → 2060.0
        buf[oid]['items'].append((model_map[key], vid, int(r['Количество']), price))

    for oid, d in sorted(buf.items()):
        iso = datetime.strptime(d['date'], '%d.%m.%Y').strftime('%Y-%m-%d')
        cur.execute("INSERT INTO orders(user_id, order_date) VALUES (?,?)", (fio_map[d['fio']], iso))
        odb = cur.lastrowid
        for mid, vid, q, price in d['items']:
            cur.execute("""INSERT INTO order_items(order_id, model_id, variant_id, quantity, unit_price)
                           VALUES (?,?,?,?,?)""", (odb, mid, vid, q, price))

    conn.commit()
    print('=== Импорт завершён ===')
    for t in ('users', 'categories', 'subcategories', 'manufacturers', 'variants',
              'models', 'stock_items', 'orders', 'order_items'):
        print(f"{t}: {cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]}")
    conn.close()


if __name__ == '__main__':
    run()
