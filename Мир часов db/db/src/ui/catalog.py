from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QLineEdit, QComboBox, QPushButton, QScrollArea, QFrame)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import sqlite3
from styles import STYLE, fmt_price

class CatalogWindow(QWidget):
    def __init__(self, user, db_path='db/watch_store.db'):
        super().__init__()
        self.db_path, self.user = db_path, user
        self.setWindowTitle(f"Мир часов — Каталог ({user['role']})")
        self.setStyleSheet(STYLE)
        root = QVBoxLayout(self)
        header = QLabel("Каталог товаров"); header.setObjectName("Header")
        filt = QHBoxLayout()
        self.search = QLineEdit(placeholderText="Поиск по наименованию")
        self.category = QComboBox()
        btn_find = QPushButton("Найти")
        btn_orders = QPushButton("Мои заказы")
        btn_exit = QPushButton("Выход")
        for w in (self.search, self.category, btn_find, btn_orders, btn_exit):
            filt.addWidget(w)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        self.grid_host = QWidget(); self.grid = QGridLayout(self.grid_host)
        scroll.setWidget(self.grid_host)
        root.addWidget(header); root.addLayout(filt); root.addWidget(scroll)
        btn_find.clicked.connect(self.load_catalog)
        btn_exit.clicked.connect(self.close)
        btn_orders.clicked.connect(self.open_orders)
        self.load_catalog()

    def load_catalog(self):
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w: w.deleteLater()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        if self.category.count() == 0:
            self.category.addItem("Все категории", None)
            for cid, name in cur.execute("SELECT category_id, name FROM categories"):
                self.category.addItem(name, cid)
        sql = """SELECT m.model_id, m.name, IFNULL(m.image_name,'picture.png'), m.base_price,
                        IFNULL(cat.name,''), IFNULL(man.name,''),
                        IFNULL((SELECT SUM(quantity) FROM stock_items s WHERE s.model_id=m.model_id),0)
                 FROM models m
                 LEFT JOIN categories cat ON cat.category_id=m.category_id
                 LEFT JOIN manufacturers man ON man.manufacturer_id=m.manufacturer_id
                 WHERE m.name LIKE ?"""
        params = [f"%{self.search.text().strip()}%"]
        if self.category.currentData():
            sql += " AND m.category_id = ?"
            params.append(self.category.currentData())
        for i, row in enumerate(cur.execute(sql, params)):
            self.grid.addWidget(self._card(*row), i // 3, i % 3)
        conn.close()

    def _card(self, mid, name, img, price, cat, mfr, stock):
        frame = QFrame()
        frame.setObjectName("CardLow" if stock <= 3 else "Card")   # подсветка #ff8080
        lay = QVBoxLayout(frame); lay.setContentsMargins(8, 8, 8, 8)
        pm = QPixmap(f"resources/{img}")
        if pm.isNull(): pm = QPixmap("resources/picture.png")      # «Радуга» и отсутствующие
        pic = QLabel(); pic.setPixmap(pm.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        pic.setAlignment(Qt.AlignCenter)
        stock_text = "Нет в наличии" if stock == 0 else f"Остаток: {stock}"
        lay.addWidget(pic)
        lay.addWidget(QLabel(f"<b>{name}</b><br>{cat} · {mfr}"))
        lay.addWidget(QLabel(f"{fmt_price(price)}<br>{stock_text}"))
        btn = QPushButton("Подробнее"); btn.setObjectName("Accent")
        btn.clicked.connect(lambda _, m=mid: self.open_model(m))
        lay.addWidget(btn)
        return frame

    def open_model(self, model_id):
        from order_form import OrderForm
        OrderForm(self.user, model_id, self.db_path, self).exec()
        self.load_catalog()                                        # обновить остатки

    def open_orders(self):
        from orders_list import OrdersListWindow
        OrdersListWindow(self.user, self.db_path).show()
