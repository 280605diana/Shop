import tkinter as tk
from tkinter import filedialog, messagebox
from db import get_connection
from PIL import Image, ImageTk
import io
import customtkinter as ctk
from datetime import datetime
from theme import *

ctk.set_appearance_mode("light")


class ClientApp(ctk.CTkToplevel):
    def __init__(self, master, user_id: int, client_id: int):
        super().__init__(master)
        self.user_id = user_id
        self.client_id = client_id
        self.title("Электронный магазин – Клиент")
        self.geometry("1400x750")
        self.configure(fg_color=BG_MAIN)

        # Центрирование окна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.cart = []  # список (id_товара, количество)
        self.current_order_details = {}  # для хранения деталей текущего заказа
        self.selected_product_id = None
        self.selected_payment_id = None
        self.current_view = "catalog"

        # Основная сетка
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---------- ЛЕВЫЙ САЙДБАР ----------
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=ACCENT_DARK,
            border_width=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # Заголовок
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="👤 Панель клиента",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        )
        self.logo_label.grid(row=0, column=0, padx=25, pady=(25, 15), sticky="w")

        # Кнопки навигации
        nav_buttons = [
            ("🛍️ Каталог", self.show_catalog),
            ("📦 Мои заказы", self.show_orders),
            ("💳 Платёжные данные", self.show_payment),
            ("👤 Профиль", self.show_profile),
        ]

        for i, (text, cmd) in enumerate(nav_buttons, start=1):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=cmd,
                font=ctk.CTkFont(size=14, weight="bold"),
                height=45,
                fg_color="transparent",
                text_color="white",
                hover_color=ACCENT,
                anchor="w",
                corner_radius=8,
                border_width=1,
                border_color=ACCENT_LIGHT
            )
            btn.grid(row=i, column=0, padx=20, pady=6, sticky="ew")

        # Разделитель
        separator = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color=ACCENT_LIGHT)
        separator.grid(row=len(nav_buttons) + 1, column=0, padx=20, pady=20, sticky="ew")

        # Корзина и обновление
        cart_btn = ctk.CTkButton(
            self.sidebar_frame,
            text=f"🛒 Корзина ({len(self.cart)})",
            command=self._view_cart,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color=ACCENT_LIGHT,
            hover_color=HOVER_LIGHT,
            text_color=ACCENT_DARK,
            corner_radius=8
        )
        cart_btn.grid(row=len(nav_buttons) + 2, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.refresh_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🔄 Обновить",
            command=self.refresh_current_view,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color=ACCENT_LIGHT,
            hover_color=HOVER_LIGHT,
            text_color=ACCENT_DARK,
            corner_radius=8
        )
        self.refresh_btn.grid(row=len(nav_buttons) + 3, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Кнопка выхода
        logout_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="Выход",
            command=self.destroy,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#ff6b6b",
            hover_color="#ff5252",
            text_color="white",
            corner_radius=8
        )
        logout_btn.grid(row=len(nav_buttons) + 4, column=0, padx=20, pady=(0, 20), sticky="ew")

        # ---------- ОСНОВНАЯ ОБЛАСТЬ ----------
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=BG_MAIN, border_width=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Динамически настраиваем колонки в зависимости от вкладки
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Заголовок текущего раздела
        self.view_title = ctk.CTkLabel(
            self.main_frame,
            text="🛍️ Каталог товаров",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=ACCENT_DARK
        )
        self.view_title.grid(row=0, column=0, padx=15, pady=(0, 20), sticky="w")

        # Четыре "экрана" (фреймы)
        self.frame_catalog = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_orders = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_payment = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_profile = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        # Внутренняя сетка для каждого фрейма
        for f in (self.frame_catalog, self.frame_orders, self.frame_payment):
            f.grid_rowconfigure(0, weight=1)
            f.grid_columnconfigure(0, weight=3)
            f.grid_columnconfigure(1, weight=2)

        # Для профиля - только одна колонка
        self.frame_profile.grid_rowconfigure(0, weight=1)
        self.frame_profile.grid_columnconfigure(0, weight=1)

        # Построение содержимого во фреймах
        self._build_catalog()
        self._build_orders()
        self._build_payment()
        self._build_profile()

        # Показать экран по умолчанию
        self._show_view(self.frame_catalog, "🛍️ Каталог товаров")
        self.current_view = "catalog"

    # ---------- СЛУЖЕБНОЕ: ПЕРЕКЛЮЧЕНИЕ ЭКРАНОВ ----------

    def _show_view(self, frame, title: str):
        """Показать один из четырёх фреймов и скрыть остальные."""
        for f in (self.frame_catalog, self.frame_orders, self.frame_payment, self.frame_profile):
            f.grid_forget()

        frame.grid(row=1, column=0, sticky="nsew")
        self.view_title.configure(text=title)

    def show_catalog(self):
        self.current_view = "catalog"
        self._show_view(self.frame_catalog, "🛍️ Каталог товаров")
        self._load_products()

    def show_orders(self):
        self.current_view = "orders"
        self._show_view(self.frame_orders, "📦 Мои заказы")
        self._load_orders()

    def show_payment(self):
        self.current_view = "payment"
        self._show_view(self.frame_payment, "💳 Платёжные данные")
        self._load_payment_data()

    def show_profile(self):
        self.current_view = "profile"
        self._show_view(self.frame_profile, "👤 Профиль клиента")
        self._load_profile()
        # Скрываем правую панель при переходе в профиль
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

    def refresh_current_view(self):
        """Обновить данные в зависимости от активного экрана."""
        if self.current_view == "catalog":
            self._load_products()
        elif self.current_view == "orders":
            self._load_orders()
        elif self.current_view == "payment":
            self._load_payment_data()
        elif self.current_view == "profile":
            self._load_profile()

    # ---------- КАТАЛОГ ----------

    def _build_catalog(self):
        # Настраиваем сетку для правой панели
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=2)

        # Левая часть - таблица товаров
        left_frame = ctk.CTkFrame(
            self.frame_catalog,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Правая часть - информация о товаре
        self.right_frame_catalog = ctk.CTkFrame(
            self.frame_catalog,
            width=420,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        self.right_frame_catalog.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.right_frame_catalog.grid_rowconfigure(1, weight=1)
        self.right_frame_catalog.grid_columnconfigure(0, weight=1)

        # Заголовок правой панели
        ctk.CTkLabel(
            self.right_frame_catalog,
            text="🔍 Информация о товаре",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_DARK
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Фрейм для изображения
        self.image_frame = ctk.CTkFrame(self.right_frame_catalog, height=200, fg_color="#f9f9f9", corner_radius=8)
        self.image_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.image_frame.pack_propagate(False)

        self.label_image = tk.Label(self.image_frame, bg="#f9f9f9")
        self.label_image.pack(expand=True, padx=10, pady=10)
        self.current_photo = None

        # Информация о товаре
        info_frame = ctk.CTkFrame(self.right_frame_catalog, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.label_name = ctk.CTkLabel(
            info_frame,
            text="Выберите товар",
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=370,
            justify="left",
            text_color=TEXT_DARK
        )
        self.label_name.pack(anchor="w", pady=(0, 8))

        self.label_price = ctk.CTkLabel(
            info_frame,
            text="💰 Цена: -",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_LIGHT
        )
        self.label_price.pack(anchor="w", pady=2)

        self.label_qty = ctk.CTkLabel(
            info_frame,
            text="📦 В наличии: -",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_LIGHT
        )
        self.label_qty.pack(anchor="w", pady=2)

        # Выбор количества
        qty_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        qty_frame.pack(anchor="w", pady=(15, 0))

        ctk.CTkLabel(qty_frame, text="Количество:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 12))

        # Используем tk.Spinbox
        self.spin_qty = tk.Spinbox(
            qty_frame,
            from_=1,
            to=1,
            width=10,
            font=("Segoe UI", 11),
            justify="center",
            background="white",
            foreground=TEXT_DARK
        )
        self.spin_qty.pack(side="left")

        # Кнопка добавления в корзину
        self.btn_add_to_cart = ctk.CTkButton(
            self.right_frame_catalog,
            text="🛒 Добавить в корзину",
            command=self._add_selected_to_cart,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="white",
            corner_radius=10,
            state="disabled"
        )
        self.btn_add_to_cart.pack(padx=20, pady=10, fill="x")

        # Кнопка оформления заказа
        self.btn_checkout = ctk.CTkButton(
            self.right_frame_catalog,
            text="💳 Оформить заказ",
            command=self._checkout,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=SUCCESS,
            hover_color="#45a049",
            text_color="white",
            corner_radius=10
        )
        self.btn_checkout.pack(padx=20, pady=(0, 20), fill="x")

        # Внутренний tk.Frame для корректной работы ttk.Treeview
        table_frame = tk.Frame(left_frame, bg=BG_CARD)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Создаем Treeview
        from tkinter import ttk
        self.tree_products = ttk.Treeview(
            table_frame,
            columns=("id", "name", "price", "qty"),
            show="headings",
            style="Custom.Treeview"
        )

        # Стилизация Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background=BG_CARD,
                        fieldbackground=BG_CARD,
                        font=("Segoe UI", 10),
                        rowheight=30)
        style.configure("Custom.Treeview.Heading",
                        background=ACCENT_LIGHT,
                        font=("Segoe UI", 11, "bold"))

        # Настройка колонок
        columns_config = [
            ("id", "ID", 70),
            ("name", "Наименование", 300),
            ("price", "Цена", 120),
            ("qty", "Количество", 100),
        ]

        for col, text, width in columns_config:
            self.tree_products.heading(col, text=text)
            self.tree_products.column(col, width=width,
                                      anchor="center" if col in ["id", "qty"] else "w")

        self.tree_products.grid(row=0, column=0, sticky="nsew")

        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_products.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_products.xview)
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.tree_products.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        # Привязка события выбора
        self.tree_products.bind('<<TreeviewSelect>>', self._on_product_select)

        # Нижняя панель кнопок
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15), padx=15)

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Обновить каталог",
            command=self._load_products,
            height=38,
            fg_color=ACCENT_LIGHT,
            hover_color=HOVER_LIGHT,
            text_color=ACCENT_DARK,
            font=("Segoe UI", 12),
            corner_radius=8
        )
        refresh_btn.pack(side="left", padx=5)

        view_cart_btn = ctk.CTkButton(
            btn_frame,
            text="🛒 Просмотр корзины",
            command=self._view_cart,
            height=38,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            corner_radius=8
        )
        view_cart_btn.pack(side="left", padx=5)

        self._load_products()

    def _load_products(self):
        for row in self.tree_products.get_children():
            self.tree_products.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT Номер_товара, Название, Цена, Количество, Изображение
                       FROM Товар
                       WHERE Количество > 0
                       """)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            formatted_row = (
                row[0],
                row[1],
                f"{float(row[2]):.2f} ₽",
                row[3]
            )
            self.tree_products.insert("", "end", values=formatted_row)

        # Сбрасываем информацию о товаре
        self._reset_product_info()

    def _reset_product_info(self):
        """Сброс информации о товаре в правой панели"""
        self.label_image.configure(image="", text="Выберите товар")
        self.label_name.configure(text="Выберите товар")
        self.label_price.configure(text="💰 Цена: -")
        self.label_qty.configure(text="📦 В наличии: -")
        self.spin_qty.configure(from_=1, to=1)
        self.spin_qty.delete(0, "end")
        self.spin_qty.insert(0, "1")
        self.btn_add_to_cart.configure(state="disabled")
        self.selected_product_id = None

        # Очищаем фото
        if self.current_photo:
            self.current_photo = None

    def _on_product_select(self, event=None):
        """Обработка выбора товара в таблице"""
        selection = self.tree_products.selection()
        if not selection:
            self.btn_add_to_cart.configure(state="disabled")
            return

        item_id = selection[0]
        values = self.tree_products.item(item_id, "values")
        if not values:
            return

        try:
            prod_id = int(values[0])
        except (ValueError, TypeError):
            return

        # Загружаем информацию о товаре
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT Название, Цена, Количество, Изображение
                       FROM Товар
                       WHERE Номер_товара = ?
                       """, (prod_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        name, price, qty, image_data = row

        # Обновляем информацию
        self.label_name.configure(text=name)
        self.label_price.configure(text=f"💰 Цена: {float(price):.2f} ₽")
        self.label_qty.configure(text=f"📦 В наличии: {qty}")
        self.spin_qty.configure(to=qty)
        self.spin_qty.delete(0, "end")
        self.spin_qty.insert(0, "1")
        self.btn_add_to_cart.configure(state="normal")
        self.selected_product_id = prod_id

        # Отображаем изображение
        if image_data:
            try:
                img_bytes = bytes(image_data)
                image = Image.open(io.BytesIO(img_bytes))
                image.thumbnail((280, 280))

                # Конвертируем для tkinter
                photo = ImageTk.PhotoImage(image, master=self)

                # Сохраняем ссылку и обновляем изображение
                self.current_photo = photo
                self.label_image.configure(image=photo, text="")
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")
                self.label_image.configure(image="", text="Нет изображения")
                self.current_photo = None
        else:
            self.label_image.configure(image="", text="Нет изображения")
            self.current_photo = None

    def _add_selected_to_cart(self):
        if not self.selected_product_id:
            messagebox.showwarning("Товар не выбран", "Выберите товар из списка")
            return

        try:
            qty = int(self.spin_qty.get())
            if qty < 1:
                messagebox.showwarning("Количество", "Количество должно быть не менее 1")
                return

            # Проверяем доступное количество
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Количество, Название FROM Товар WHERE Номер_товара = ?",
                (self.selected_product_id,)
            )
            result = cursor.fetchone()
            conn.close()

            if not result:
                messagebox.showwarning("Ошибка", "Товар не найден")
                return

            available_qty, prod_name = result[0], result[1]
            if available_qty < qty:
                messagebox.showwarning(
                    "Количество",
                    f"Товара '{prod_name}' недостаточно в наличии.\n"
                    f"Заказано: {qty}, в наличии: {available_qty}"
                )
                return

            # Проверяем, не добавлен ли уже этот товар
            for i, (existing_id, existing_qty) in enumerate(self.cart):
                if existing_id == self.selected_product_id:
                    self.cart[i] = (self.selected_product_id, existing_qty + qty)
                    break
            else:
                self.cart.append((self.selected_product_id, qty))

            # Обновляем счетчик корзины в сайдбаре
            for widget in self.sidebar_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton) and "Корзина" in str(widget.cget("text")):
                    widget.configure(text=f"🛒 Корзина ({len(self.cart)})")

            messagebox.showinfo("Корзина", "Товар добавлен в корзину")
        except ValueError:
            messagebox.showwarning("Количество", "Некорректное количество")

    def _view_cart(self):
        if not self.cart:
            messagebox.showinfo("Корзина", "Корзина пуста")
            return

        conn = get_connection()
        cursor = conn.cursor()

        cart_details = []
        total = 0

        for prod_id, qty in self.cart:
            cursor.execute(
                "SELECT Название, Цена FROM Товар WHERE Номер_товара = ?",
                (prod_id,)
            )
            product = cursor.fetchone()
            if product:
                name, price = product
                item_total = float(price) * qty
                total += item_total
                cart_details.append(f"• {name}: {qty} × {price:.2f} ₽ = {item_total:.2f} ₽")

        conn.close()

        cart_text = "🛒 Товары в корзине:\n\n" + "\n".join(cart_details)
        cart_text += f"\n\n💰 Итого: {total:.2f} ₽"

        messagebox.showinfo("Корзина", cart_text)

    def _checkout(self):
        if not self.cart:
            messagebox.showwarning("Корзина пуста", "Сначала добавьте товары в корзину")
            return

        # Получаем список платежных данных
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT ID_данных, Номер_карты, CONVERT(varchar (10), Срок_действия, 120)
                       FROM Платежные_данные
                       WHERE ID_Клиента = ?
                       ORDER BY ID_данных
                       """, (self.client_id,))
        payment_methods = cursor.fetchall()
        conn.close()

        if not payment_methods:
            messagebox.showwarning(
                "Нет платежных данных",
                "Добавьте платежную карту в разделе 'Платежные данные'"
            )
            return

        # Создаем окно выбора платежного метода
        payment_window = ctk.CTkToplevel(self)
        payment_window.title("Выбор платежного метода")
        payment_window.geometry("500x400")
        payment_window.configure(fg_color=BG_MAIN)

        # Центрируем окно
        payment_window.update_idletasks()
        width = payment_window.winfo_width()
        height = payment_window.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        payment_window.geometry(f'{width}x{height}+{x}+{y}')

        payment_window.transient(self)
        payment_window.grab_set()

        ctk.CTkLabel(
            payment_window,
            text="💳 Выберите платежную карту:",
            font=("Segoe UI", 16, "bold"),
            text_color=ACCENT_DARK
        ).pack(pady=20)

        # Фрейм для радиокнопок
        radio_frame = ctk.CTkFrame(payment_window, fg_color=BG_CARD, corner_radius=10)
        radio_frame.pack(fill="both", expand=True, padx=30, pady=10)

        selected_payment = ctk.IntVar(value=payment_methods[0][0])

        for payment_id, card, exp in payment_methods:
            radio = ctk.CTkRadioButton(
                radio_frame,
                text=f"{self._mask_card(card)} (действ. до {exp})",
                variable=selected_payment,
                value=payment_id,
                font=("Segoe UI", 12),
                fg_color=ACCENT,
                hover_color=ACCENT_DARK,
                text_color=TEXT_DARK
            )
            radio.pack(anchor="w", pady=8, padx=15)

        def process_order():
            payment_id = selected_payment.get()
            payment_window.destroy()
            self._create_order(payment_id)

        ctk.CTkButton(
            payment_window,
            text="✅ Оформить заказ",
            command=process_order,
            height=45,
            font=("Segoe UI", 14, "bold"),
            fg_color=SUCCESS,
            hover_color="#45a049",
            text_color="white",
            corner_radius=10
        ).pack(pady=20)

    def _create_order(self, payment_id):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Проверяем наличие товаров
            for prod_id, qty in self.cart:
                cursor.execute(
                    "SELECT Количество, Название FROM Товар WHERE Номер_товара = ?",
                    (prod_id,)
                )
                result = cursor.fetchone()
                if not result:
                    messagebox.showerror(
                        "Ошибка",
                        f"Товар с ID {prod_id} не найден"
                    )
                    conn.close()
                    return

                available_qty, prod_name = result[0], result[1]
                if available_qty < qty:
                    messagebox.showerror(
                        "Ошибка",
                        f"Товара '{prod_name}' недостаточно в наличии.\n"
                        f"Заказано: {qty}, в наличии: {available_qty}"
                    )
                    conn.close()
                    return

            # Получаем текущую дату
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Создаем заказы для каждого товара
            order_ids = []
            product_names = []

            # Получаем названия товаров
            for prod_id, qty in self.cart:
                cursor.execute(
                    "SELECT Название FROM Товар WHERE Номер_товара = ?",
                    (prod_id,)
                )
                result = cursor.fetchone()
                if result:
                    product_names.append(result[0])
                else:
                    product_names.append(f"Товар ID:{prod_id}")

            # Создаем заказы с датой
            for (prod_id, qty), prod_name in zip(self.cart, product_names):
                cursor.execute("""
                               INSERT INTO Заказ (ID_данные, Номер_товара,
                                                  Количество_заказанного_товара, Статус, Дата_заказа)
                               VALUES (?, ?, ?, N'создан', ?)
                               """, (payment_id, prod_id, qty, current_date))

                # Получаем ID созданного заказа
                order_id = self._get_last_insert_id(cursor)
                if order_id:
                    order_ids.append(order_id)
                else:
                    order_ids.append("?")

                # Обновляем количество товара
                cursor.execute("""
                               UPDATE Товар
                               SET Количество = Количество - ?
                               WHERE Номер_товара = ?
                               """, (qty, prod_id))

            conn.commit()

            # Формируем сообщение
            if len(order_ids) == 1 and order_ids[0] != "?":
                message = f"✅ Заказ №{order_ids[0]} успешно создан!\n"
                message += f"Товар: {product_names[0]}\n"
                message += f"📅 Дата заказа: {current_date}"
            else:
                message = f"✅ Создано заказов: {len(self.cart)}\n"
                message += f"📅 Дата заказа: {current_date}\n\n"
                for i, (order_num, prod_name) in enumerate(zip(order_ids, product_names), 1):
                    message += f"{i}. {prod_name}"
                    if order_num != "?":
                        message += f" - заказ №{order_num}"
                    message += "\n"

                total_items = sum(item[1] for item in self.cart)
                message += f"\n📦 Всего товаров: {total_items}"

            messagebox.showinfo("Успешно", message)

            # Очищаем корзину и обновляем интерфейс
            self.cart = []
            self._load_products()
            self._load_orders()

            # Обновляем счетчик корзины в сайдбаре
            for widget in self.sidebar_frame.winfo_children():
                if isinstance(widget, ctk.CTkButton) and "Корзина" in str(widget.cget("text")):
                    widget.configure(text=f"🛒 Корзина (0)")

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось оформить заказ: {str(e)}")
            print(f"Error creating order: {e}")
        finally:
            conn.close()

    def _mask_card(self, full: str) -> str:
        digits = full.replace(" ", "")
        if len(digits) < 4:
            return "*" * len(digits)
        return "**** **** **** " + digits[-4:]

    def _get_last_insert_id(self, cursor):
        """Получение ID последней вставленной записи"""
        cursor.execute("SELECT SCOPE_IDENTITY()")
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else None

    # ---------- ЗАКАЗЫ ----------

    def _build_orders(self):
        # Настраиваем сетку для правой панели
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=2)

        # Левая часть - таблица заказов
        left_frame = ctk.CTkFrame(
            self.frame_orders,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Правая часть - детали заказа
        self.right_frame_orders = ctk.CTkFrame(
            self.frame_orders,
            width=420,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        self.right_frame_orders.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.right_frame_orders.grid_rowconfigure(1, weight=1)
        self.right_frame_orders.grid_columnconfigure(0, weight=1)

        # Заголовок правой панели
        ctk.CTkLabel(
            self.right_frame_orders,
            text="🔍 Детали заказа",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_DARK
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Текстовое поле для деталей
        self.details_text_orders = ctk.CTkTextbox(
            self.right_frame_orders,
            font=ctk.CTkFont(size=13),
            fg_color="#f9f9f9",
            border_width=1,
            border_color=BORDER,
            corner_radius=8
        )
        self.details_text_orders.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.details_text_orders.configure(state="disabled")

        # Внутренний tk.Frame для таблицы
        table_frame = tk.Frame(left_frame, bg=BG_CARD)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Создаем Treeview для заказов
        from tkinter import ttk
        self.tree_orders = ttk.Treeview(
            table_frame,
            columns=("id", "date", "status", "product", "qty", "total"),
            show="headings",
            style="Custom.Treeview"
        )

        # Стилизация Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background=BG_CARD,
                        fieldbackground=BG_CARD,
                        font=("Segoe UI", 10),
                        rowheight=30)
        style.configure("Custom.Treeview.Heading",
                        background=ACCENT_LIGHT,
                        font=("Segoe UI", 11, "bold"))

        # Настройка колонок
        columns_config = [
            ("id", "ID заказа", 90),
            ("date", "Дата заказа", 110),
            ("status", "Статус", 130),
            ("product", "Товар", 260),
            ("qty", "Кол-во", 80),
            ("total", "Сумма", 110),
        ]

        for col, text, width in columns_config:
            self.tree_orders.heading(col, text=text)
            self.tree_orders.column(col, width=width,
                                    anchor="center" if col in ["id", "qty", "total"] else "w")

        self.tree_orders.grid(row=0, column=0, sticky="nsew")

        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_orders.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_orders.xview)
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.tree_orders.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        # Привязка события выбора
        self.tree_orders.bind('<<TreeviewSelect>>', self._on_order_select)

        # Нижняя панель кнопок
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15), padx=15)

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Обновить",
            command=self._load_orders,
            height=38,
            fg_color=ACCENT_LIGHT,
            hover_color=HOVER_LIGHT,
            text_color=ACCENT_DARK,
            font=("Segoe UI", 12),
            corner_radius=8
        )
        refresh_btn.pack(side="left", padx=5)

        details_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Подробнее",
            command=self._show_order_details_dialog,
            height=38,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            corner_radius=8
        )
        details_btn.pack(side="left", padx=5)

        self._load_orders()

    def _load_orders(self):
        for row in self.tree_orders.get_children():
            self.tree_orders.delete(row)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           SELECT Z.ID_заказа,
                                  CONVERT(varchar (10), Z.Дата_заказа, 120),
                                  Z.Статус,
                                  T.Название,
                                  Z.Количество_заказанного_товара,
                                  T.Цена,
                                  (Z.Количество_заказанного_товара * T.Цена) as Сумма
                           FROM Заказ Z
                                    JOIN Платежные_данные P ON Z.ID_данные = P.ID_данных
                                    JOIN Товар T ON Z.Номер_товара = T.Номер_товара
                           WHERE P.ID_Клиента = ?
                           ORDER BY Z.Дата_заказа DESC, Z.ID_заказа DESC
                           """, (self.client_id,))

            rows = cursor.fetchall()

            for row in rows:
                formatted_row = (
                    row[0],  # ID заказа
                    row[1],  # Дата заказа
                    row[2],  # Статус
                    row[3],  # Название товара
                    row[4],  # Количество
                    f"{float(row[6]):.2f} ₽" if row[6] else "0.00 ₽"  # Сумма
                )
                self.tree_orders.insert("", "end", values=formatted_row)

        except Exception as e:
            print(f"Error loading orders: {e}")
        finally:
            conn.close()

        # Сбрасываем детали
        self.details_text_orders.configure(state="normal")
        self.details_text_orders.delete("1.0", "end")
        self.details_text_orders.insert("1.0", "Выберите заказ для просмотра деталей")
        self.details_text_orders.configure(state="disabled")

    def _on_order_select(self, event):
        """Обработка выбора заказа в таблице"""
        selection = self.tree_orders.selection()
        if not selection:
            return

        values = self.tree_orders.item(selection[0], "values")
        if not values or len(values) < 6:
            return

        order_id = values[0]
        self._load_order_details(order_id, self.details_text_orders)

    def _load_order_details(self, order_id, details_widget):
        """Загрузка деталей заказа"""
        try:
            order_id_int = int(order_id)
        except ValueError:
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           SELECT Z.ID_заказа,
                                  Z.Статус,
                                  T.Название,
                                  Z.Количество_заказанного_товара,
                                  T.Цена,
                                  CONVERT(varchar (10), Z.Дата_заказа, 120),
                                  C.Фамилия,
                                  C.Имя,
                                  C.Отчество,
                                  C.Город,
                                  C.Улица,
                                  C.Дом,
                                  C.Квартира,
                                  P.Номер_карты,
                                  CONVERT(varchar (10), P.Срок_действия, 120)
                           FROM Заказ Z
                                    JOIN Платежные_данные P ON Z.ID_данные = P.ID_данных
                                    JOIN Клиент C ON P.ID_Клиента = C.ID_Клиент
                                    JOIN Товар T ON Z.Номер_товара = T.Номер_товара
                           WHERE Z.ID_заказа = ?
                           """, (order_id_int,))

            row = cursor.fetchone()

            if not row:
                details_widget.configure(state="normal")
                details_widget.delete("1.0", "end")
                details_widget.insert("1.0", "⚠️ Информация о заказе не найдена")
                details_widget.configure(state="disabled")
                return

            (oid, status, prod_name, qty, price, order_date,
             fam, im, otch, city, street, house, flat,
             card_number, card_exp) = row

            try:
                total = float(price) * float(qty)
            except (ValueError, TypeError):
                total = 0

            # Форматируем адрес
            address_parts = []
            if city:
                address_parts.append(f"г. {city}")
            if street:
                address_parts.append(f"ул. {street}")
            if house:
                address_parts.append(f"д. {house}")
            if flat:
                address_parts.append(f"кв. {flat}")
            address = ", ".join(address_parts)

            # Маскируем номер карты
            masked_card = self._mask_card(card_number) if card_number else "**** **** **** ****"

            # Формируем текст с деталями
            details_text = f"""📦 ЗАКАЗ №{oid}
{'=' * 45}

📋 ОСНОВНАЯ ИНФОРМАЦИЯ:
• 🏷️ Статус: {status}
• 📅 Дата заказа: {order_date}

🛒 ТОВАР:
• 📝 Название: {prod_name}
• 🔢 Количество: {qty} шт.
• 💰 Цена за единицу: {float(price):.2f} ₽
• 💵 Итого: {total:.2f} ₽

👤 ПОЛУЧАТЕЛЬ:
• 👤 ФИО: {fam} {im} {otch}
• 📍 Адрес доставки: {address}

💳 ОПЛАТА:
• 💳 Карта: {masked_card}
• 📅 Срок действия: {card_exp if card_exp else 'Не указан'}

{'=' * 45}
📝 Статус заказа можно отслеживать в этом разделе.
"""

            details_widget.configure(state="normal")
            details_widget.delete("1.0", "end")
            details_widget.insert("1.0", details_text)
            details_widget.configure(state="disabled")

        except Exception as e:
            print(f"Database error: {e}")
            details_widget.configure(state="normal")
            details_widget.delete("1.0", "end")
            details_widget.insert("1.0", f"❌ Ошибка загрузки деталей: {str(e)}")
            details_widget.configure(state="disabled")
        finally:
            conn.close()

    def _show_order_details_dialog(self):
        """Показать детали заказа в отдельном окне"""
        sel = self.tree_orders.selection()
        if not sel:
            messagebox.showwarning("Выбор", "Выберите заказ")
            return

        values = self.tree_orders.item(sel[0], "values")
        if not values or len(values) < 6:
            messagebox.showwarning("Ошибка", "Некорректные данные заказа")
            return

        order_id = values[0]

        try:
            order_id_int = int(order_id)
        except ValueError:
            messagebox.showerror("Ошибка", f"Некорректный ID заказа: {order_id}")
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                           SELECT Z.ID_заказа,
                                  Z.Статус,
                                  T.Название,
                                  Z.Количество_заказанного_товара,
                                  T.Цена,
                                  CONVERT(varchar (10), Z.Дата_заказа, 120),
                                  C.Фамилия,
                                  C.Имя,
                                  C.Отчество,
                                  C.Город,
                                  C.Улица,
                                  C.Дом,
                                  C.Квартира,
                                  P.Номер_карты,
                                  CONVERT(varchar (10), P.Срок_действия, 120)
                           FROM Заказ Z
                                    JOIN Платежные_данные P ON Z.ID_данные = P.ID_данных
                                    JOIN Клиент C ON P.ID_Клиента = C.ID_Клиент
                                    JOIN Товар T ON Z.Номер_товара = T.Номер_товара
                           WHERE Z.ID_заказа = ?
                           """, (order_id_int,))

            row = cursor.fetchone()

            if not row:
                messagebox.showwarning("Заказ", "Данные заказа не найдены")
                return

            (oid, status, prod_name, qty, price, order_date,
             fam, im, otch, city, street, house, flat,
             card_number, card_exp) = row

            try:
                total = float(price) * float(qty)
            except (ValueError, TypeError):
                total = 0

            # Формируем адрес
            address_parts = []
            if city:
                address_parts.append(f"г. {city}")
            if street:
                address_parts.append(f"ул. {street}")
            if house:
                address_parts.append(f"д. {house}")
            if flat:
                address_parts.append(f"кв. {flat}")
            address = ", ".join(address_parts)

            # Маскируем номер карты
            masked_card = self._mask_card(card_number) if card_number else "**** **** **** ****"

            # Создаем диалоговое окно с детальной информацией
            details_window = ctk.CTkToplevel(self)
            details_window.title(f"Информация о заказе №{oid}")
            details_window.geometry("600x500")
            details_window.configure(fg_color=BG_MAIN)

            # Центрируем окно
            details_window.update_idletasks()
            width = details_window.winfo_width()
            height = details_window.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            details_window.geometry(f'{width}x{height}+{x}+{y}')

            details_window.transient(self)
            details_window.grab_set()

            # Основной контент
            content_frame = ctk.CTkFrame(details_window, fg_color=BG_CARD, corner_radius=10)
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Заголовок
            ctk.CTkLabel(
                content_frame,
                text=f"📦 Заказ №{oid}",
                font=("Segoe UI", 22, "bold"),
                text_color=ACCENT_DARK
            ).pack(anchor="w", pady=(20, 10), padx=25)

            # Разделитель
            ctk.CTkFrame(content_frame, height=2, fg_color=BORDER).pack(fill="x", pady=5, padx=25)

            # Информация о заказе
            info_text = f"""
📅 Дата заказа: {order_date}
📊 Статус: {status}

🛒 Товар: {prod_name}
🔢 Количество: {qty}
💰 Цена за единицу: {float(price):.2f} ₽
💵 Итого: {total:.2f} ₽

👤 Получатель: {fam} {im} {otch}
📍 Адрес доставки: {address}

💳 Карта оплаты: {masked_card}
📅 Срок действия карты: {card_exp if card_exp else 'Не указан'}
"""

            info_label = ctk.CTkLabel(
                content_frame,
                text=info_text,
                font=("Segoe UI", 12),
                justify="left",
                text_color=TEXT_DARK
            )
            info_label.pack(anchor="w", pady=20, padx=25)

            # Кнопка закрытия
            ctk.CTkButton(
                content_frame,
                text="Закрыть",
                command=details_window.destroy,
                height=40,
                width=120,
                fg_color=ACCENT,
                hover_color=ACCENT_DARK,
                text_color="white",
                corner_radius=10
            ).pack(pady=20)

        except Exception as e:
            print(f"Database error: {e}")
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {e}")
        finally:
            conn.close()

    # ---------- ПЛАТЁЖНЫЕ ДАННЫЕ ----------

    def _build_payment(self):
        # Настраиваем сетку для правой панели
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=2)

        # Левая часть - таблица карт
        left_frame = ctk.CTkFrame(
            self.frame_payment,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Правая часть - редактирование
        self.right_frame_payment = ctk.CTkFrame(
            self.frame_payment,
            width=420,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        self.right_frame_payment.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.right_frame_payment.grid_rowconfigure(1, weight=1)
        self.right_frame_payment.grid_columnconfigure(0, weight=1)

        # Заголовок правой панели
        ctk.CTkLabel(
            self.right_frame_payment,
            text="✏️ Редактирование карты",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_DARK
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Форма редактирования
        form_frame = ctk.CTkFrame(self.right_frame_payment, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Номер карты
        ctk.CTkLabel(form_frame, text="Номер карты:", font=ctk.CTkFont(size=13),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 5))
        self.entry_card = ctk.CTkEntry(
            form_frame,
            placeholder_text="0000 0000 0000 0000",
            height=38,
            font=ctk.CTkFont(size=12),
            fg_color=ENTRY_BG,
            border_color=ENTRY_BORDER,
            text_color=ENTRY_TEXT,
            placeholder_text_color=ENTRY_PLACEHOLDER
        )
        self.entry_card.pack(fill="x", pady=(0, 12))

        # Срок действия
        ctk.CTkLabel(form_frame, text="Срок действия (ГГГГ-ММ-ДД):",
                     font=ctk.CTkFont(size=13), text_color=TEXT_DARK).pack(anchor="w", pady=(0, 5))
        self.entry_exp = ctk.CTkEntry(
            form_frame,
            placeholder_text="2025-12-31",
            height=38,
            font=ctk.CTkFont(size=12),
            fg_color=ENTRY_BG,
            border_color=ENTRY_BORDER,
            text_color=ENTRY_TEXT,
            placeholder_text_color=ENTRY_PLACEHOLDER
        )
        self.entry_exp.pack(fill="x", pady=(0, 12))

        # CVV
        ctk.CTkLabel(form_frame, text="CVV код:", font=ctk.CTkFont(size=13),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 5))
        cvv_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        cvv_frame.pack(fill="x", pady=(0, 20))

        self.entry_cvv = ctk.CTkEntry(
            cvv_frame,
            placeholder_text="123",
            width=100,
            height=38,
            font=ctk.CTkFont(size=12),
            show="●",
            fg_color=ENTRY_BG,
            border_color=ENTRY_BORDER,
            text_color=ENTRY_TEXT,
            placeholder_text_color=ENTRY_PLACEHOLDER
        )
        self.entry_cvv.pack(side="left")

        self.show_cvv_var = ctk.BooleanVar(value=False)
        show_cvv_check = ctk.CTkCheckBox(
            cvv_frame,
            text="Показать",
            variable=self.show_cvv_var,
            command=self._toggle_cvv_visibility,
            font=ctk.CTkFont(size=11),
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color=TEXT_DARK
        )
        show_cvv_check.pack(side="left", padx=20)

        # Кнопки действий
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        add_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Добавить",
            command=self._add_payment,
            height=38,
            fg_color=SUCCESS,
            hover_color="#45a049",
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            corner_radius=8
        )
        add_btn.grid(row=0, column=0, padx=2, sticky="ew")

        edit_btn = ctk.CTkButton(
            buttons_frame,
            text="✏️ Изменить",
            command=self._edit_payment,
            height=38,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="white",
            font=("Segoe UI", 12),
            corner_radius=8
        )
        edit_btn.grid(row=0, column=1, padx=2, sticky="ew")

        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Удалить",
            command=self._delete_payment,
            height=38,
            fg_color=ERROR,
            hover_color="#d32f2f",
            text_color="white",
            font=("Segoe UI", 12),
            corner_radius=8
        )
        delete_btn.grid(row=0, column=2, padx=2, sticky="ew")

        show_cvv_btn = ctk.CTkButton(
            buttons_frame,
            text="👁️ Показать CVV",
            command=self._show_cvv,
            height=38,
            fg_color=ACCENT_LIGHT,
            hover_color=HOVER_LIGHT,
            text_color=ACCENT_DARK,
            font=("Segoe UI", 12),
            corner_radius=8
        )
        show_cvv_btn.grid(row=1, column=0, columnspan=3, pady=(10, 0), sticky="ew")

        # Настройка равномерного распределения кнопок
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)

        # Внутренний tk.Frame для таблицы
        table_frame = tk.Frame(left_frame, bg=BG_CARD)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Создаем Treeview для платежных данных
        from tkinter import ttk
        self.tree_pay = ttk.Treeview(
            table_frame,
            columns=("id", "number", "exp"),
            show="headings",
            style="Custom.Treeview"
        )

        # Стилизация Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background=BG_CARD,
                        fieldbackground=BG_CARD,
                        font=("Segoe UI", 10),
                        rowheight=30)
        style.configure("Custom.Treeview.Heading",
                        background=ACCENT_LIGHT,
                        font=("Segoe UI", 11, "bold"))

        # Настройка колонок
        columns_config = [
            ("id", "ID", 70),
            ("number", "Номер карты", 220),
            ("exp", "Срок действия", 130),
        ]

        for col, text, width in columns_config:
            self.tree_pay.heading(col, text=text)
            self.tree_pay.column(col, width=width,
                                 anchor="center" if col in ["id", "exp"] else "w")

        self.tree_pay.grid(row=0, column=0, sticky="nsew")

        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_pay.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_pay.xview)
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.tree_pay.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        # Привязка события выбора
        self.tree_pay.bind('<<TreeviewSelect>>', self._on_pay_select)

        # Нижняя панель кнопок
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15), padx=15)

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Обновить",
            command=self._load_payment_data,
            height=38,
            fg_color=ACCENT_LIGHT,
            hover_color=HOVER_LIGHT,
            text_color=ACCENT_DARK,
            font=("Segoe UI", 12),
            corner_radius=8
        )
        refresh_btn.pack(side="left", padx=5)

        self.payment_map = {}
        self._load_payment_data()

    def _toggle_cvv_visibility(self):
        if self.show_cvv_var.get():
            self.entry_cvv.configure(show="")
        else:
            self.entry_cvv.configure(show="●")

    def _load_payment_data(self):
        for row in self.tree_pay.get_children():
            self.tree_pay.delete(row)
        self.payment_map.clear()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT ID_данных, Номер_карты, CONVERT(varchar (10), Срок_действия, 120)
                       FROM Платежные_данные
                       WHERE ID_Клиента = ?
                       """, (self.client_id,))
        rows = cursor.fetchall()
        conn.close()

        for pid, card, exp in rows:
            self.payment_map[pid] = (card, exp)
            self.tree_pay.insert(
                "", "end",
                values=(pid, self._mask_card(card), exp)
            )

    def _on_pay_select(self, event):
        sel = self.tree_pay.selection()
        if not sel:
            return
        pid = self.tree_pay.item(sel[0], "values")[0]
        try:
            pid = int(pid)
        except Exception:
            return
        card, exp = self.payment_map.get(pid, ("", ""))
        self.entry_card.delete(0, "end")
        self.entry_card.insert(0, card)
        self.entry_exp.delete(0, "end")
        self.entry_exp.insert(0, exp)
        self.entry_cvv.delete(0, "end")
        self.show_cvv_var.set(False)
        self.entry_cvv.configure(show="●")
        self.selected_payment_id = pid

    def _add_payment(self):
        card = self.entry_card.get().strip()
        exp = self.entry_exp.get().strip()
        cvv = self.entry_cvv.get().strip()

        if not card or not exp or not cvv:
            messagebox.showwarning("Проверка данных", "Заполните все поля карты")
            return

        # Проверяем формат срока действия
        try:
            datetime.strptime(exp, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Проверка данных", "Некорректный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           INSERT INTO Платежные_данные (ID_Клиента, Номер_карты, Срок_действия, CVV_код)
                           VALUES (?, ?, ?, ?)
                           """, (self.client_id, card, exp, cvv))
            conn.commit()
            messagebox.showinfo("Карты", "✅ Карта успешно добавлена")
            self._load_payment_data()

            # Очищаем поля
            self.entry_card.delete(0, "end")
            self.entry_exp.delete(0, "end")
            self.entry_cvv.delete(0, "end")
            self.selected_payment_id = None
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            conn.close()

    def _edit_payment(self):
        if not self.selected_payment_id:
            messagebox.showwarning("Выбор", "Выберите запись карты для редактирования")
            return

        card = self.entry_card.get().strip()
        exp = self.entry_exp.get().strip()
        cvv = self.entry_cvv.get().strip()

        if not card or not exp or not cvv:
            messagebox.showwarning("Проверка данных", "Заполните все поля карты")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           UPDATE Платежные_данные
                           SET Номер_карты   = ?,
                               Срок_действия = ?,
                               CVV_код       = ?
                           WHERE ID_данных = ?
                             AND ID_Клиента = ?
                           """, (card, exp, cvv, self.selected_payment_id, self.client_id))
            conn.commit()
            messagebox.showinfo("Карты", "✅ Данные карты обновлены")
            self._load_payment_data()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            conn.close()

    def _delete_payment(self):
        if not self.selected_payment_id:
            messagebox.showwarning("Выбор", "Выберите запись карты для удаления")
            return

        if messagebox.askyesno("Удаление", "Удалить выбранную карту?"):
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                               DELETE
                               FROM Платежные_данные
                               WHERE ID_данных = ?
                                 AND ID_Клиента = ?
                               """, (self.selected_payment_id, self.client_id))
                conn.commit()
                messagebox.showinfo("Карты", "✅ Карта удалена")
                self._load_payment_data()

                # Очищаем поля
                self.entry_card.delete(0, "end")
                self.entry_exp.delete(0, "end")
                self.entry_cvv.delete(0, "end")
                self.selected_payment_id = None
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Ошибка", str(e))
            finally:
                conn.close()

    def _show_cvv(self):
        if not self.selected_payment_id:
            messagebox.showwarning("Выбор", "Выберите запись карты")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT CVV_код
                       FROM Платежные_данные
                       WHERE ID_данных = ?
                         AND ID_Клиента = ?
                       """, (self.selected_payment_id, self.client_id))
        row = cursor.fetchone()
        conn.close()

        if row:
            messagebox.showinfo("CVV", f"🔐 CVV код: {row[0]}")
        else:
            messagebox.showwarning("CVV", "Запись не найдена")

    # ---------- ПРОФИЛЬ ----------

    def _build_profile(self):
        frame = ctk.CTkFrame(
            self.frame_profile,
            fg_color=BG_CARD,
            corner_radius=15,
            border_width=1,
            border_color=BORDER
        )
        frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(
            frame,
            text="👤 Профиль клиента",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=ACCENT_DARK
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 25), padx=30)

        # Форма с полями
        self.profile_entries = {}
        labels = [
            ("Фамилия", "fam", 1),
            ("Имя", "name", 2),
            ("Отчество", "patr", 3),
            ("Серия паспорта", "ser", 4),
            ("Номер паспорта", "num", 5),
            ("Город", "city", 6),
            ("Улица", "street", 7),
            ("Дом", "house", 8),
            ("Квартира", "flat", 9),
        ]

        for text, key, row in labels:
            # Метка
            label = ctk.CTkLabel(
                frame,
                text=text + ":",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=TEXT_DARK
            )
            label.grid(row=row, column=0, sticky="e", padx=(0, 15), pady=10)

            # Поле ввода
            entry = ctk.CTkEntry(
                frame,
                width=320,
                height=38,
                font=ctk.CTkFont(size=12),
                placeholder_text=f"Введите {text.lower()}",
                fg_color=ENTRY_BG,
                border_color=ENTRY_BORDER,
                text_color=ENTRY_TEXT,
                placeholder_text_color=ENTRY_PLACEHOLDER
            )
            entry.grid(row=row, column=1, sticky="w", pady=10)
            self.profile_entries[key] = entry

        # Разделитель
        separator = ctk.CTkFrame(frame, height=2, fg_color=BORDER)
        separator.grid(row=10, column=0, columnspan=2, sticky="ew", pady=25, padx=30)

        # Кнопка сохранения
        save_btn = ctk.CTkButton(
            frame,
            text="💾 Сохранить изменения",
            command=self._save_profile,
            height=45,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10
        )
        save_btn.grid(row=11, column=0, columnspan=2, pady=(0, 10))

        self._load_profile()

    def _load_profile(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT Фамилия,
                              Имя,
                              Отчество,
                              Серия_паcпорта,
                              Номер_паcпорта,
                              Город,
                              Улица,
                              Дом,
                              Квартира
                       FROM Клиент
                       WHERE ID_Клиент = ?
                       """, (self.client_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        # Теперь 9 полей вместо 8
        keys = ["fam", "name", "patr", "ser", "num", "city", "street", "house", "flat"]
        for key, value in zip(keys, row):
            self.profile_entries[key].delete(0, "end")
            if value is not None:
                self.profile_entries[key].insert(0, str(value))

    def _save_profile(self):
        vals = {k: e.get().strip() for k, e in self.profile_entries.items()}

        # Обязательные поля (без отчества и квартиры)
        mandatory = ["fam", "name", "ser", "num", "city", "street", "house"]
        for key in mandatory:
            if not vals[key]:
                messagebox.showwarning("Проверка данных", f"Заполните поле: {key}")
                return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           UPDATE Клиент
                           SET Фамилия        = ?,
                               Имя            = ?,
                               Отчество       = ?,
                               Серия_паcпорта = ?,
                               Номер_паcпорта = ?,
                               Город          = ?,
                               Улица          = ?,
                               Дом            = ?,
                               Квартира       = ?
                           WHERE ID_Клиент = ?
                           """, (
                               vals["fam"], vals["name"], vals["patr"],
                               vals["ser"], vals["num"], vals["city"],
                               vals["street"], vals["house"], vals["flat"],
                               self.client_id
                           ))
            conn.commit()
            messagebox.showinfo("Профиль", "✅ Данные успешно сохранены")

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            conn.close()