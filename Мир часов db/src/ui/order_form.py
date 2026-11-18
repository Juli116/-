import PySide6.QtWidgets # pyright: ignore[reportMissingImports]
from PySide6.QtGui import QPixmap # pyright: ignore[reportMissingImports]
from PySide6.QtCore import Qt # pyright: ignore[reportMissingImports]
import sqlite3
from datetime import date
import ctypes
import logic.check_order # pyright: ignore[reportMissingImports]

class OrderForm(PySide6.QtWidgets.QDialog):
    def __init__(self, user, model_id, db_path, parent=None):
        super().__init__(parent)
        self.db_path, self.user, self.model_id = db_path, user, model_id
        self.setWindowTitle("Мир часов — Оформление заказа")
        self.setStyleSheet(styles.STYLE)
        conn = sqlite3.connect(db_path); cur = conn.cursor()
        cur.execute("SELECT name, IFNULL(image_name,'picture.png'), base_price FROM models WHERE model_id=?",
                    (model_id,))
        self.name, img, self.base_price = cur.fetchone()
        self.variants = cur.execute("""
            SELECT s.variant_id, v.name, s.quantity FROM stock_items s
            JOIN variants v ON v.variant_id = s.variant_id
            WHERE s.model_id=? AND s.quantity > 0""", (model_id,)).fetchall()
        conn.close()
        lay = PySide6.QtWidgets.QVBoxLayout(self)
        pic = PySide6.QtWidgets.QLabel(); pm = QPixmap(f"resources/{img}")
        if pm.isNull(): pm = QPixmap("resources/picture.png")
        pic.setPixmap(pm.scaled(180, 180, Qt.KeepAspectRatio))
        lay.addWidget(pic)
        lay.addWidget(PySide6.QtWidgets.QLabel(f"<b>{self.name}</b> — {styles.fmt_price(self.base_price)}"))
        self.cb_variant = PySide6.QtWidgets.QComboBox()
        for vid, vname, q in self.variants:
            self.cb_variant.addItem(f"{vname} (осталось {q})", vid)
        self.qty = PySide6.QtWidgets.QSpinBox(); self.qty.setRange(1, 999)
        btn = PySide6.QtWidgets.QPushButton("Оформить заказ"); btn.setObjectName("Accent"); btn.clicked.connect(self.submit)
        for w in (PySide6.QtWidgets.QLabel("Вариант исполнения:"), self.cb_variant,
                  PySide6.QtWidgets.QLabel("Количество:"), self.qty, btn):
            lay.addWidget(w)
        if not self.variants:
            PySide6.QtWidgets.QMessageBox.warning(self, "Ошибка",
                "Доступных вариантов нет.\nВыберите другую модель или вернитесь в каталог.")
            self.setEnabled(False)

    def submit(self):
        if not self.variants:
            return
        vid = self.cb_variant.currentData()
        q = self.qty.value()
        stock = next(v[2] for v in self.variants if v[0] == vid)
        res = logic.check_order.check_order(vid, q, stock)
        if res != "OK":
            PySide6.QtWidgets.QMessageBox.warning(self, "Ошибка", res + "\nИсправьте данные и повторите.")
            return
        conn = sqlite3.connect(self.db_path); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO orders(user_id, order_date) VALUES (?,?)",
                        (self.user['id'], date.today().isoformat()))
            order_id = cur.lastrowid
            cur.execute("""INSERT INTO order_items(order_id, model_id, variant_id, quantity, unit_price)
                           VALUES (?,?,?,?,?)""", (order_id, self.model_id, vid, q, self.base_price))
            cur.execute("""UPDATE stock_items SET quantity = quantity - ?
                           WHERE model_id=? AND variant_id=?""", (q, self.model_id, vid))
            conn.commit()
            PySide6.QtWidgets.QMessageBox.information(self, "Заказ оформлен", f"Заказ №{order_id} создан.\nОстаток обновлён.")
            self.accept()
        except sqlite3.Error as e:
            conn.rollback()
            PySide6.QtWidgets.QMessageBox.critical(self, "Ошибка базы данных", f"{e}\nЗаказ не сохранён, попробуйте ещё раз.")
        finally:
            conn.close()
