# ui_courier.py
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from theme import *

ctk.set_appearance_mode("light")


def setup_style(root):
    """Стиль для ttk-элементов (Treeview и т.п.)."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=BG_MAIN)
    style.configure("TLabel", background=BG_MAIN)
    style.configure("TNotebook", background=BG_MAIN)
    style.configure("TNotebook.Tab", padding=(10, 4))
    style.configure("Treeview", background=BG_CARD, fieldbackground=BG_CARD)
    style.configure("Treeview.Heading", background=ACCENT_LIGHT, font=("Segoe UI", 10, "bold"))

    style.configure("Accent.TButton", foreground="white")
    style.map(
        "Accent.TButton",
        background=[("!disabled", ACCENT), ("pressed", ACCENT_DARK), ("active", ACCENT_DARK)],
    )


class CourierApp(ctk.CTkToplevel):
    """
    Окно курьера с правой панелью деталей заказа:
    - слева: боковая панель навигации + таблица заказов
    - справа: детальная информация о выбранном заказе (кроме профиля)
    """

    def __init__(self, master, user_id: int, courier_id: int):
        super().__init__(master)
        self.user_id = user_id
        self.courier_id = courier_id

        self.title("Электронный магазин – Курьер")
        self.geometry("1400x750")
        self.configure(fg_color=BG_MAIN)

        # Центрирование окна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # Текущий режим просмотра: 'available' / 'my_orders' / 'profile'
        self.current_view = "available"
        self.selected_order_id = None

        # Глобальный стиль для ttk
        setup_style(self)

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
            text="🚴 Панель курьера",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        )
        self.logo_label.grid(row=0, column=0, padx=25, pady=(25, 15), sticky="w")

        # Кнопки навигации
        nav_buttons = [
            ("📦 Доступные заказы", self.show_available),
            ("📋 Мои заказы", self.show_my_orders),
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

        # Кнопка "Обновить"
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
        self.refresh_btn.grid(row=len(nav_buttons) + 2, column=0, padx=20, pady=10, sticky="ew")

        # ---------- ОСНОВНАЯ ОБЛАСТЬ ----------
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=BG_MAIN, border_width=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Динамически настраиваем колонки в зависимости от вкладки
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Заголовок текущего раздела
        self.view_title = ctk.CTkLabel(
            self.main_frame,
            text="📦 Доступные заказы",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=ACCENT_DARK
        )
        self.view_title.grid(row=0, column=0, padx=15, pady=(0, 20), sticky="w")

        # Три "экрана" (фреймы)
        self.frame_available = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_my_orders = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_profile = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        # Внутренняя сетка для каждого фрейма
        for f in (self.frame_available, self.frame_my_orders):
            f.grid_rowconfigure(0, weight=1)
            f.grid_columnconfigure(0, weight=3)
            f.grid_columnconfigure(1, weight=2)

        # Для профиля - только одна колонка
        self.frame_profile.grid_rowconfigure(0, weight=1)
        self.frame_profile.grid_columnconfigure(0, weight=1)

        # Построение содержимого во фреймах
        self._build_available()
        self._build_my_orders()
        self._build_profile()

        # Показать экран по умолчанию
        self._show_view(self.frame_available, "📦 Доступные заказы")
        self.current_view = "available"

    # ---------- СЛУЖЕБНОЕ: ПЕРЕКЛЮЧЕНИЕ ЭКРАНОВ ----------

    def _show_view(self, frame, title: str):
        """Показать один из трёх фреймов и скрыть остальные."""
        for f in (self.frame_available, self.frame_my_orders, self.frame_profile):
            f.grid_forget()

        frame.grid(row=1, column=0, sticky="nsew")
        self.view_title.configure(text=title)

    def show_available(self):
        self.current_view = "available"
        self._show_view(self.frame_available, "📦 Доступные заказы")
        self._load_available()

    def show_my_orders(self):
        self.current_view = "my_orders"
        self._show_view(self.frame_my_orders, "📋 Мои заказы")
        self._load_my_orders()

    def show_profile(self):
        self.current_view = "profile"
        self._show_view(self.frame_profile, "👤 Профиль курьера")
        self._load_profile()
        # Скрываем правую панель при переходе в профиль
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)
        if hasattr(self, 'right_frame'):
            self.right_frame.grid_forget()

    def refresh_current_view(self):
        """Обновить данные в зависимости от активного экрана."""
        if self.current_view == "available":
            self._load_available()
        elif self.current_view == "my_orders":
            self._load_my_orders()
        elif self.current_view == "profile":
            self._load_profile()

    # ---------- Доступные заказы ----------

    def _build_available(self):
        # Настраиваем сетку для правой панели
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=2)

        # Левая часть - таблица заказов
        left_frame = ctk.CTkFrame(
            self.frame_available,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Правая часть - детали заказа
        self.right_frame = ctk.CTkFrame(
            self.frame_available,
            width=420,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Заголовок правой панели
        self.details_title = ctk.CTkLabel(
            self.right_frame,
            text="🔍 Детали заказа",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_DARK
        )
        self.details_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Поле для отображения деталей
        self.details_text = ctk.CTkTextbox(
            self.right_frame,
            font=ctk.CTkFont(size=13),
            fg_color="#f9f9f9",
            border_width=1,
            border_color=BORDER,
            corner_radius=8
        )
        self.details_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.details_text.configure(state="disabled")

        # Внутренний tk.Frame для корректной работы ttk.Treeview
        table_frame = tk.Frame(left_frame, bg=BG_CARD)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree_av = ttk.Treeview(
            table_frame,
            columns=("id", "date", "status", "client", "product", "qty", "sum"),
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
            ("date", "Дата", 130),
            ("status", "Статус", 120),
            ("client", "Клиент", 170),
            ("product", "Товар", 200),
            ("qty", "Кол-во", 80),
            ("sum", "Сумма", 120),
        ]

        for col, text, width in columns_config:
            self.tree_av.heading(col, text=text)
            self.tree_av.column(col, width=width, anchor="center" if col in ["id", "qty", "sum"] else "w")

        self.tree_av.grid(row=0, column=0, sticky="nsew")

        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_av.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_av.xview)
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.tree_av.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        # Привязка события выбора
        self.tree_av.bind('<<TreeviewSelect>>', self._on_available_select)

        # Нижняя панель кнопок
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15), padx=15)

        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Обновить",
            command=self._load_available,
            height=38,
            fg_color=ACCENT_LIGHT,
            hover_color=HOVER_LIGHT,
            text_color=ACCENT_DARK,
            font=("Segoe UI", 12),
            corner_radius=8
        )
        refresh_btn.pack(side="left", padx=5)

        self.btn_take = ctk.CTkButton(
            btn_frame,
            text="✅ Взять в работу",
            command=self._take_order,
            height=38,
            fg_color=SUCCESS,
            hover_color="#45a049",
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            corner_radius=8,
            state="disabled"
        )
        self.btn_take.pack(side="left", padx=5)

        self._load_available()

    def _load_available(self):
        for row in self.tree_av.get_children():
            self.tree_av.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT Z.ID_заказа,
                       CONVERT(varchar (10), Z.Дата_заказа, 104)                                               as Дата,
                       Z.Статус,
                       C.Фамилия + ' ' + C.Имя                                                                 as Клиент,
                       T.Название                                                                              as Товар,
                       Z.Количество_заказанного_товара                                                         as Количество,
                       CONVERT(varchar (20), CAST(T.Цена * Z.Количество_заказанного_товара AS DECIMAL(10, 2))) as Сумма
                FROM Заказ Z
                         JOIN Платежные_данные P ON Z.ID_данные = P.ID_данных
                         JOIN Клиент C ON P.ID_Клиента = C.ID_Клиент
                         JOIN Товар T ON Z.Номер_товара = T.Номер_товара
                WHERE Z.ID_курьера IS NULL
                  AND Z.Статус IN (N'создан', N'в обработке')
                ORDER BY Z.Дата_заказа ASC
                """
            )

            for row in cursor.fetchall():
                formatted_row = (
                    str(row[0]),
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    str(row[5]),
                    f"{row[6]} ₽"
                )
                self.tree_av.insert("", "end", values=formatted_row)

        except Exception as e:
            print(f"Error loading available orders: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить доступные заказы: {e}")
        finally:
            conn.close()

    def _on_available_select(self, event):
        """Обработка выбора заказа в таблице доступных заказов."""
        selection = self.tree_av.selection()
        if not selection:
            self.btn_take.configure(state="disabled")
            return

        item = selection[0]
        values = self.tree_av.item(item, "values")
        if values:
            self.selected_order_id = values[0]
            self.btn_take.configure(state="normal")
            self._load_order_details(self.selected_order_id)

    def _take_order(self):
        if not self.selected_order_id:
            messagebox.showwarning("Выбор", "Выберите заказ")
            return

        order_id = self.selected_order_id
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Проверяем, свободен ли заказ
            cursor.execute(
                """
                SELECT Статус, ID_курьера
                FROM Заказ
                WHERE ID_заказа = ?
                """,
                (order_id,),
            )

            order_info = cursor.fetchone()
            if not order_info:
                messagebox.showerror("Ошибка", f"Заказ №{order_id} не найден")
                return

            status, current_courier = order_info
            if current_courier is not None:
                messagebox.showwarning("Ошибка", "Этот заказ уже взят другим курьером")
                self._load_available()
                return

            if status not in ("создан", "в обработке"):
                messagebox.showwarning(
                    "Ошибка", f"Заказ имеет статус '{status}', взять нельзя"
                )
                return

            # Берём заказ в работу
            cursor.execute(
                """
                UPDATE Заказ
                SET ID_курьера = ?,
                    Статус     = N'у курьера'
                WHERE ID_заказа = ?
                """,
                (self.courier_id, order_id),
            )

            conn.commit()
            messagebox.showinfo("✅ Успешно", f"Заказ №{order_id} взят в работу")

            self._load_available()
            self._load_my_orders()
            self.selected_order_id = None
            self.btn_take.configure(state="disabled")
            self.details_text.configure(state="normal")
            self.details_text.delete("1.0", "end")
            self.details_text.insert("1.0", "Выберите заказ для просмотра деталей")
            self.details_text.configure(state="disabled")

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось взять заказ: {str(e)}")
            print(f"Error taking order: {e}")
        finally:
            conn.close()

    # ---------- Мои заказы ----------

    def _build_my_orders(self):
        # Настраиваем сетку для правой панели
        self.main_frame.grid_columnconfigure(0, weight=3)
        self.main_frame.grid_columnconfigure(1, weight=2)

        # Левая часть - таблица заказов
        left_frame = ctk.CTkFrame(
            self.frame_my_orders,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Правая часть - детали заказа
        self.right_frame_my = ctk.CTkFrame(
            self.frame_my_orders,
            width=420,
            fg_color=BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        self.right_frame_my.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.right_frame_my.grid_rowconfigure(1, weight=1)
        self.right_frame_my.grid_columnconfigure(0, weight=1)

        # Заголовок правой панели
        details_title_my = ctk.CTkLabel(
            self.right_frame_my,
            text="🔍 Детали заказа",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_DARK
        )
        details_title_my.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Поле для отображения деталей
        self.details_text_my = ctk.CTkTextbox(
            self.right_frame_my,
            font=ctk.CTkFont(size=13),
            fg_color="#f9f9f9",
            border_width=1,
            border_color=BORDER,
            corner_radius=8
        )
        self.details_text_my.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.details_text_my.configure(state="disabled")

        # Внутренний tk.Frame для корректной работы ttk.Treeview
        table_frame = tk.Frame(left_frame, bg=BG_CARD)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree_my = ttk.Treeview(
            table_frame,
            columns=("id", "date", "status", "client", "product", "qty", "sum"),
            show="headings",
            style="Custom.Treeview"
        )

        # Настройка колонок
        columns_config = [
            ("id", "ID", 70),
            ("date", "Дата", 130),
            ("status", "Статус", 120),
            ("client", "Клиент", 170),
            ("product", "Товар", 200),
            ("qty", "Кол-во", 80),
            ("sum", "Сумма", 120),
        ]

        for col, text, width in columns_config:
            self.tree_my.heading(col, text=text)
            self.tree_my.column(col, width=width, anchor="center" if col in ["id", "qty", "sum"] else "w")

        self.tree_my.grid(row=0, column=0, sticky="nsew")

        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_my.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_my.xview)
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.tree_my.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        # Привязка события выбора
        self.tree_my.bind('<<TreeviewSelect>>', self._on_my_order_select)

        # Нижняя панель кнопок
        bottom = ctk.CTkFrame(left_frame, fg_color="transparent")
        bottom.pack(fill="x", pady=(0, 15), padx=15)

        refresh_btn = ctk.CTkButton(
            bottom,
            text="🔄 Обновить",
            command=self._load_my_orders,
            height=38,
            fg_color=ACCENT_LIGHT,
            hover_color=HOVER_LIGHT,
            text_color=ACCENT_DARK,
            font=("Segoe UI", 12),
            corner_radius=8
        )
        refresh_btn.pack(side="left", padx=5)

        self.combo_status = ctk.CTkComboBox(
            bottom,
            values=["у курьера", "доставлен"],
            width=200,
            height=38,
            fg_color="white",
            border_color=BORDER,
            button_color=ACCENT,
            button_hover_color=ACCENT_DARK,
            font=("Segoe UI", 12),
            dropdown_font=("Segoe UI", 12),
            corner_radius=8
        )
        self.combo_status.pack(side="left", padx=5)
        self.combo_status.set("у курьера")

        self.btn_change_status = ctk.CTkButton(
            bottom,
            text="✏️ Изменить статус",
            command=self._change_status,
            height=38,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            corner_radius=8,
            state="disabled"
        )
        self.btn_change_status.pack(side="left", padx=5)

        self._load_my_orders()

    def _load_my_orders(self):
        for row in self.tree_my.get_children():
            self.tree_my.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT Z.ID_заказа,
                       CONVERT(varchar (10), Z.Дата_заказа, 104)                                               as Дата,
                       Z.Статус,
                       C.Фамилия + ' ' + C.Имя                                                                 as Клиент,
                       T.Название                                                                              as Товар,
                       Z.Количество_заказанного_товара                                                         as Количество,
                       CONVERT(varchar (20), CAST(T.Цена * Z.Количество_заказанного_товара AS DECIMAL(10, 2))) as Сумма
                FROM Заказ Z
                         JOIN Платежные_данные P ON Z.ID_данные = P.ID_данных
                         JOIN Клиент C ON P.ID_Клиента = C.ID_Клиент
                         JOIN Товар T ON Z.Номер_товара = T.Номер_товара
                WHERE Z.ID_курьера = ?
                ORDER BY Z.Дата_заказа DESC
                """,
                (self.courier_id,),
            )

            for row in cursor.fetchall():
                formatted_row = (
                    str(row[0]),
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    str(row[5]),
                    f"{row[6]} ₽"
                )
                self.tree_my.insert("", "end", values=formatted_row)

        except Exception as e:
            print(f"Error loading my orders: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить ваши заказы: {e}")
        finally:
            conn.close()

    def _on_my_order_select(self, event):
        """Обработка выбора заказа в таблице моих заказов."""
        selection = self.tree_my.selection()
        if not selection:
            self.btn_change_status.configure(state="disabled")
            return

        item = selection[0]
        values = self.tree_my.item(item, "values")
        if values:
            self.selected_order_id = values[0]
            self.btn_change_status.configure(state="normal")
            self._load_order_details_my(self.selected_order_id)

    def _load_order_details_my(self, order_id):
        """Загрузка деталей для моих заказов."""
        self._load_order_details(order_id, self.details_text_my)

    def _change_status(self):
        if not self.selected_order_id:
            messagebox.showwarning("Выбор", "Выберите заказ")
            return

        new_status = self.combo_status.get()
        if not new_status:
            messagebox.showwarning("Статус", "Выберите статус")
            return

        order_id = self.selected_order_id
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Проверяем, принадлежит ли заказ этому курьеру
            cursor.execute(
                """
                SELECT Статус
                FROM Заказ
                WHERE ID_заказа = ?
                  AND ID_курьера = ?
                """,
                (order_id, self.courier_id),
            )

            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Ошибка", "Заказ не найден или не принадлежит вам")
                self._load_my_orders()
                return

            current_status = result[0]

            # Валидация смены статуса
            if current_status == "доставлен" and new_status != "доставлен":
                messagebox.showwarning("Ошибка", "Доставленный заказ нельзя изменить")
                return

            cursor.execute(
                """
                UPDATE Заказ
                SET Статус = ?
                WHERE ID_заказа = ?
                  AND ID_курьера = ?
                """,
                (new_status, order_id, self.courier_id),
            )

            conn.commit()
            messagebox.showinfo(
                "✅ Успешно", f"Статус заказа №{order_id} изменён на '{new_status}'"
            )
            self._load_my_orders()
            self.selected_order_id = None
            self.btn_change_status.configure(state="disabled")
            self.details_text_my.configure(state="normal")
            self.details_text_my.delete("1.0", "end")
            self.details_text_my.insert("1.0", "Выберите заказ для просмотра деталей")
            self.details_text_my.configure(state="disabled")

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            conn.close()

    # ---------- Загрузка деталей заказа ----------

    def _load_order_details(self, order_id, details_widget=None):
        """Загрузка и отображение детальной информации о заказе."""
        if details_widget is None:
            details_widget = self.details_text

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT Z.ID_заказа,
                       Z.Статус,
                       Z.Количество_заказанного_товара,
                       CONVERT(varchar (19), Z.Дата_заказа, 120)                                 as Дата_заказа,

                       -- Информация о клиенте
                       C.Фамилия + ' ' + C.Имя + ' ' + ISNULL(C.Отчество, '')                    as Клиент_ФИО,
                       C.Город + ', ' + C.Улица + N', д. ' + C.Дом
                       + N', кв. ' + C.Квартира                                                   as Адрес,

                       -- Информация о товаре
                       T.Название                                                                as Товар,
                       CONVERT(varchar (20), T.Цена)                                             as Цена_за_единицу,

                       -- Расчет суммы
                       CONVERT(varchar (20),
                               CAST(T.Цена * Z.Количество_заказанного_товара AS DECIMAL(10, 2))) as Общая_сумма,

                       -- Курьер (если есть)
                       ISNULL(K.Фамилия + ' ' + K.Имя, 'Не назначен')                            as Курьер,
                       ISNULL(K.Номер_телефона, '')                                              as Телефон_курьера

                FROM Заказ Z
                         JOIN Платежные_данные P ON Z.ID_данные = P.ID_данных
                         JOIN Клиент C ON P.ID_Клиента = C.ID_Клиент
                         JOIN Товар T ON Z.Номер_товара = T.Номер_товара
                         LEFT JOIN Курьер K ON Z.ID_курьера = K.ID_курьера
                WHERE Z.ID_заказа = ?
                """,
                (order_id,),
            )

            result = cursor.fetchone()
            if result:
                # Форматирование с эмодзи и цветовым оформлением
                details_text = f"""📦 ЗАКАЗ №{result[0]}
{'=' * 45}

📋 ОСНОВНАЯ ИНФОРМАЦИЯ:
• 🏷️ Статус: {result[1]}
• 📦 Количество: {result[2]} шт.
• 📅 Дата заказа: {result[3]}

👤 КЛИЕНТ:
• 👤 ФИО: {result[4]}
• 📍 Адрес доставки: {result[5]}

🛒 ТОВАР:
• 📝 Название: {result[6]}
• 💰 Цена за единицу: {result[7]} ₽
• 💵 Общая сумма: {result[8]} ₽

🚴 КУРЬЕР:
• 👤 ФИО: {result[9]}
• 📞 Телефон: {result[10] if result[10] else 'Не указан'}

{'=' * 45}
📝 Примечание: Для связи с клиентом используйте контактные данные из системы.
"""

                details_widget.configure(state="normal")
                details_widget.delete("1.0", "end")
                details_widget.insert("1.0", details_text)
                details_widget.configure(state="disabled")
            else:
                details_widget.configure(state="normal")
                details_widget.delete("1.0", "end")
                details_widget.insert("1.0", "⚠️ Информация о заказе не найдена")
                details_widget.configure(state="disabled")

        except Exception as e:
            print(f"Error loading order details: {e}")
            details_widget.configure(state="normal")
            details_widget.delete("1.0", "end")
            details_widget.insert("1.0", f"❌ Ошибка загрузки деталей: {str(e)}")
            details_widget.configure(state="disabled")
        finally:
            conn.close()

    # ---------- Профиль курьера ----------

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
            text="👤 Профиль курьера",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=ACCENT_DARK
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 25), padx=30)

        labels = [
            ("Фамилия", "fam"),
            ("Имя", "name"),
            ("Отчество", "patr"),
            ("Телефон", "phone"),
        ]
        self.profile_entries = {}
        for i, (text, key) in enumerate(labels, start=1):
            ctk.CTkLabel(
                frame,
                text=text + ":",
                font=("Segoe UI", 13, "bold"),
                text_color=TEXT_DARK
            ).grid(row=i, column=0, sticky="e", padx=(0, 15), pady=10)

            entry = ctk.CTkEntry(
                frame,
                width=320,
                height=40,
                font=("Segoe UI", 12),
                fg_color=ENTRY_BG,
                border_color=ENTRY_BORDER,
                text_color=ENTRY_TEXT,
                placeholder_text_color=ENTRY_PLACEHOLDER
            )
            entry.grid(row=i, column=1, sticky="w", pady=10)
            self.profile_entries[key] = entry

        # Логин (только чтение)
        ctk.CTkLabel(
            frame,
            text="Логин:",
            font=("Segoe UI", 13, "bold"),
            text_color=TEXT_DARK
        ).grid(row=len(labels) + 1, column=0, sticky="e", padx=(0, 15), pady=10)

        self.entry_login = ctk.CTkEntry(
            frame,
            width=320,
            height=40,
            font=("Segoe UI", 12),
            fg_color="#f5f5f5",
            border_color=DISABLED,
            text_color=TEXT_LIGHT
        )
        self.entry_login.grid(row=len(labels) + 1, column=1, sticky="w", pady=10)
        self.entry_login.configure(state="disabled")

        # E-mail
        ctk.CTkLabel(
            frame,
            text="E-mail:",
            font=("Segoe UI", 13, "bold"),
            text_color=TEXT_DARK
        ).grid(row=len(labels) + 2, column=0, sticky="e", padx=(0, 15), pady=10)

        self.entry_email = ctk.CTkEntry(
            frame,
            width=320,
            height=40,
            font=("Segoe UI", 12),
            fg_color=ENTRY_BG,
            border_color=ENTRY_BORDER,
            text_color=ENTRY_TEXT,
            placeholder_text_color=ENTRY_PLACEHOLDER
        )
        self.entry_email.grid(row=len(labels) + 2, column=1, sticky="w", pady=10)

        # Разделитель
        separator = ctk.CTkFrame(frame, height=2, fg_color=BORDER)
        separator.grid(row=len(labels) + 3, column=0, columnspan=2, sticky="ew", pady=25, padx=30)

        # Кнопка "Сохранить"
        save_btn = ctk.CTkButton(
            frame,
            text="💾 Сохранить изменения",
            command=self._save_profile,
            height=45,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            text_color="white",
            font=("Segoe UI", 14, "bold"),
            corner_radius=10
        )
        save_btn.grid(row=len(labels) + 4, column=0, columnspan=2, pady=(0, 10))

        self._load_profile()

    def _load_profile(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT K.Фамилия,
                   K.Имя,
                   K.Отчество,
                   K.Номер_телефона,
                   U.Логин,
                   U.Email
            FROM Курьер K
                     JOIN Пользователь U ON K.ID_пользователя = U.ID_пользователя
            WHERE K.ID_курьера = ?
            """,
            (self.courier_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        fam, name, patr, phone, login, email = row
        vals = {
            "fam": fam,
            "name": name,
            "patr": patr,
            "phone": phone,
        }
        for key, val in vals.items():
            entry = self.profile_entries[key]
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, "" if val is None else str(val))

        self.entry_login.configure(state="normal")
        self.entry_login.delete(0, "end")
        self.entry_login.insert(0, "" if login is None else str(login))
        self.entry_login.configure(state="disabled")

        self.entry_email.delete(0, "end")
        self.entry_email.insert(0, "" if email is None else str(email))

    def _save_profile(self):
        vals = {k: e.get().strip() for k, e in self.profile_entries.items()}
        if not all(vals.values()):
            messagebox.showwarning("Проверка данных", "Заполните все поля профиля")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Обновляем Курьер
            cursor.execute(
                """
                UPDATE Курьер
                SET Фамилия        = ?,
                    Имя            = ?,
                    Отчество       = ?,
                    Номер_телефона = ?
                WHERE ID_курьера = ?
                """,
                (vals["fam"], vals["name"], vals["patr"], vals["phone"], self.courier_id),
            )

            # Обновляем Email пользователя по user_id
            email = self.entry_email.get().strip()
            cursor.execute(
                """
                UPDATE Пользователь
                SET Email = ?
                WHERE ID_пользователя = ?
                """,
                (email, self.user_id),
            )

            conn.commit()
            messagebox.showinfo("✅ Профиль", "Данные успешно сохранены")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка", str(e))
        finally:
            conn.close()