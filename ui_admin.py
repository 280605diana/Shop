# ui_admin.py
import customtkinter as ctk
from tkinter import messagebox
from db import get_connection
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
from datetime import datetime

# Импортируем розовую цветовую схему
from theme import *

ctk.set_appearance_mode("light")

class AdminApp(ctk.CTkToplevel):
    def __init__(self, master, user_id: int):
        super().__init__(master)
        self.user_id = user_id
        self.title("Электронный магазин – Административная панель")
        self.geometry("1400x750")

        self.configure(fg_color=BG_MAIN)

        # Центрирование окна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # Текущая таблица и данные
        self.current_table = None
        self.table_data = []
        self.selected_row_id = None
        self.current_photo = None  # Для хранения ссылки на изображение

        # Создание интерфейса
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        self.configure(fg_color=BG_MAIN)

        # Основная сетка
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Панель навигации слева
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=ACCENT_DARK)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # Логотип/заголовок
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Админ-панель",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Кнопки навигации
        nav_buttons = [
            ("👥 Пользователи", self.load_users),
            ("👤 Клиенты", self.load_clients),
            ("🚴 Курьеры", self.load_couriers),
            ("📦 Товары", self.load_products),
            ("📋 Заказы", self.load_orders),
            ("💳 Платежные данные", self.load_payments),
        ]

        for i, (text, command) in enumerate(nav_buttons, start=1):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=command,
                font=ctk.CTkFont(size=14),
                height=40,
                fg_color="transparent",
                text_color="white",
                hover_color=HOVER_DARK,
                anchor="w",
                corner_radius=5
            )
            btn.grid(row=i, column=0, padx=15, pady=5, sticky="ew")

        # Кнопки управления (только для редактируемых таблиц)
        self.refresh_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🔄 Обновить",
            command=self.refresh_table,
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color=BTN_SECONDARY,
            text_color=BTN_SECONDARY_TEXT,
            hover_color=BTN_SECONDARY_HOVER
        )
        self.refresh_btn.grid(row=len(nav_buttons) + 1, column=0, padx=15, pady=(20, 5), sticky="ew")

        self.add_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="➕ Добавить",
            command=self.add_record,
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color="#28a745",  # Зеленый для добавления
            text_color="white",
            hover_color="#218838"
        )
        self.add_btn.grid(row=len(nav_buttons) + 2, column=0, padx=15, pady=5, sticky="ew")

        self.edit_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="✏️ Редактировать",
            command=self.edit_record,
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color=BTN_SECONDARY,
            text_color=BTN_SECONDARY_TEXT,
            hover_color=BTN_SECONDARY_HOVER
        )
        self.edit_btn.grid(row=len(nav_buttons) + 3, column=0, padx=15, pady=5, sticky="ew")

        self.delete_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🗑️ Удалить",
            command=self.delete_record,
            font=ctk.CTkFont(size=14),
            height=35,
            fg_color="#dc3545",  # Красный для удаления
            hover_color="#c82333",
            text_color="white"
        )
        self.delete_btn.grid(row=len(nav_buttons) + 4, column=0, padx=15, pady=5, sticky="ew")

        # Основная область с таблицей и деталями
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=BG_CARD)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        # Заголовок таблицы
        self.table_title = ctk.CTkLabel(
            self.main_frame,
            text="Выберите таблицу",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=HEADER_PRIMARY
        )
        self.table_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Левая панель - таблица
        left_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Фрейм для таблицы с прокруткой
        self.table_container = ctk.CTkFrame(left_frame, corner_radius=8, fg_color=ACCENT_LIGHT)
        self.table_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.table_container.grid_rowconfigure(0, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)

        # Создаем Treeview в отдельном tk.Frame
        self.tk_table_frame = tk.Frame(self.table_container, bg=ACCENT_LIGHT)
        self.tk_table_frame.grid(row=0, column=0, sticky="nsew")
        self.tk_table_frame.grid_rowconfigure(0, weight=1)
        self.tk_table_frame.grid_columnconfigure(0, weight=1)

        # Вертикальная прокрутка
        self.scrollbar_y = tk.Scrollbar(self.tk_table_frame, orient="vertical")
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")

        # Горизонтальная прокрутка
        self.scrollbar_x = tk.Scrollbar(self.tk_table_frame, orient="horizontal")
        self.scrollbar_x.grid(row=1, column=0, sticky="ew", columnspan=2)

        # Treeview для отображения данных
        self.tree = ttk.Treeview(
            self.tk_table_frame,
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set,
            selectmode="browse",
            style="Custom.Treeview"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar_y.config(command=self.tree.yview)
        self.scrollbar_x.config(command=self.tree.xview)

        # Стиль для Treeview с розовой темой
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=BG_CARD,
                        foreground=TEXT_DARK,
                        rowheight=30,
                        fieldbackground=BG_CARD,
                        borderwidth=0,
                        font=('Segoe UI', 10))
        style.configure("Custom.Treeview.Heading",
                        background=ACCENT,
                        foreground="white",
                        font=('Segoe UI', 11, 'bold'),
                        relief="flat")
        style.map('Custom.Treeview',
                  background=[('selected', ACCENT)],
                  foreground=[('selected', 'white')])

        # Правая панель - детали/изображение
        self.right_frame = ctk.CTkFrame(self.main_frame, width=350, corner_radius=8, fg_color=ACCENT_LIGHT)
        self.right_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Заголовок правой панели
        self.details_title = ctk.CTkLabel(
            self.right_frame,
            text="Детали записи",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=HEADER_PRIMARY
        )
        self.details_title.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        # Фрейм для изображения (вверху)
        self.image_frame = ctk.CTkFrame(self.right_frame, height=200, fg_color=BG_CARD, corner_radius=8)
        self.image_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        self.image_frame.grid_propagate(False)
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)

        # Label для изображения в отдельном Frame для правильного позиционирования
        self.image_label_frame = tk.Frame(self.image_frame, bg=BG_CARD)
        self.image_label_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.image_label = tk.Label(self.image_label_frame, bg=BG_CARD)
        self.image_label.pack()

        # Поле для отображения деталей
        self.details_text = ctk.CTkTextbox(self.right_frame, height=200, font=ctk.CTkFont(size=12))
        self.details_text.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))

        # Привязка события выбора строки
        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)

    def on_row_select(self, event):
        """Обработка выбора строки в таблице"""
        selection = self.tree.selection()
        if not selection:
            return
        selected_item = selection[0]
        values = self.tree.item(selected_item, 'values')
        self.selected_row_id = values[0] if values else None
        # Показываем детали в правой панели
        self.show_details(values)
        # Если выбрана таблица товаров, показываем изображение
        if self.current_table == "Товар" and values:
            self.load_product_image(values[0])
        else:
            # Для других таблиц или если нет данных - просто очищаем
            self.clear_image_display()

    def clear_image_display(self):
        """Очистка отображения изображения"""
        if self.image_label:
            self.image_label.configure(image="", bg=BG_CARD)
        if hasattr(self, 'current_photo'):
            self.current_photo = None

    def show_details(self, values):
        """Отображение деталей выбранной записи"""
        self.details_text.delete("1.0", "end")

        if not values:
            self.details_text.insert("1.0", "Нет данных")
            return

        # Получаем заголовки колонок
        columns = self.tree["columns"]

        # Формируем текст с деталями
        details = ""
        for i, (col, val) in enumerate(zip(columns, values)):
            details += f"• {col}: {val}\n"

        self.details_text.insert("1.0", details)

    def load_product_image(self, product_id):
        """Загрузка и отображение изображения товара"""
        try:
            # Очищаем предыдущее изображение
            self.clear_image_display()

            # Если нет ID товара
            if not product_id:
                self.image_label.configure(text="Нет изображения", font=("Segoe UI", 10))
                return

            try:
                pid = int(str(product_id).strip().strip("(), "))
            except ValueError:
                self.image_label.configure(text="Некорректный ID", font=("Segoe UI", 10))
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Изображение FROM Товар WHERE Номер_товара = ?",
                (pid,)
            )
            row = cursor.fetchone()
            conn.close()

            if row and row[0]:
                img_bytes = bytes(row[0])  # memoryview → bytes
                try:
                    # Загружаем изображение через PIL
                    image = Image.open(io.BytesIO(img_bytes))
                    image.thumbnail((280, 280), Image.Resampling.LANCZOS)

                    # Конвертируем в PhotoImage для tkinter
                    photo = ImageTk.PhotoImage(image, master=self)

                    # Сохраняем ссылку и обновляем отображение
                    self.current_photo = photo
                    self.image_label.configure(image=photo, text="", bg=BG_CARD)

                except Exception as e:
                    print(f"Ошибка обработки изображения: {e}")
                    self.image_label.configure(text="Ошибка изображения", font=("Segoe UI", 10), bg=BG_CARD)
            else:
                self.image_label.configure(text="Нет изображения", font=("Segoe UI", 10), bg=BG_CARD)

        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")
            self.image_label.configure(text="Ошибка загрузки", font=("Segoe UI", 10), bg=BG_CARD)

    def load_table(self, table_name, title, query=None):
        self.current_table = table_name
        self.table_title.configure(text=title)
        self.selected_row_id = None

        # Очищаем детали и изображение
        self.details_text.delete("1.0", "end")
        self.clear_image_display()

        # Очищаем таблицу
        self.tree.delete(*self.tree.get_children())

        # Удаляем старые колонки
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
            self.tree.column(col, width=0)

        # Получаем данные из БД
        conn = get_connection()
        cursor = conn.cursor()

        try:
            if query:
                cursor.execute(query)
            else:
                cursor.execute(f"SELECT * FROM {table_name}")

            # Получаем заголовки колонок
            columns = [desc[0] for desc in cursor.description]

            # Настраиваем колонки Treeview
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col, anchor="w")
                self.tree.column(col, width=120, minwidth=80, stretch=True)

            # Заполняем данными
            rows = cursor.fetchall()
            self.table_data = []

            for row in rows:
                # Преобразуем типы для отображения
                formatted_row = []
                for value in row:
                    if value is None:
                        formatted_row.append("")
                    elif isinstance(value, bytes):
                        formatted_row.append("[BINARY DATA]")
                    elif isinstance(value, bool):
                        formatted_row.append("Да" if value else "Нет")
                    elif isinstance(value, datetime):
                        formatted_row.append(value.strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        formatted_row.append(str(value))

                self.table_data.append(formatted_row)
                self.tree.insert("", "end", values=formatted_row)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
        finally:
            conn.close()

    def load_users(self):
        self.load_table(
            "Пользователь",
            "👥 Пользователи",
            """
            SELECT ID_пользователя,
                   Логин,
                   ISNULL(Email, '')                              as Email,
                   Роль,
                   CONVERT(varchar (19), Дата_регистрации, 120)   as Дата_регистрации,
                   CASE WHEN Активен = 1 THEN 'Да' ELSE 'Нет' END as Активен
            FROM Пользователь
            ORDER BY ID_пользователя
            """
        )

    def load_clients(self):
        self.load_table(
            "Клиент",
            "👤 Клиенты",
            """
            SELECT c.ID_Клиент,
                   c.Фамилия,
                   c.Имя,
                   c.Отчество,
                   c.Серия_паcпорта,
                   c.Номер_паcпорта,
                   c.Город,
                   c.Улица,
                   ISNULL(c.Дом, '')      as Дом,
                   ISNULL(c.Квартира, '') as Квартира,
                   u.Логин
            FROM Клиент c
                     JOIN Пользователь u ON c.ID_пользователя = u.ID_пользователя
            ORDER BY c.ID_Клиент
            """
        )

    def load_couriers(self):
        self.load_table(
            "Курьер",
            "🚴 Курьеры",
            """
            SELECT k.ID_курьера,
                   k.Фамилия,
                   k.Имя,
                   k.Отчество,
                   k.Номер_телефона,
                   u.Логин,
                   ISNULL(u.Email, '') as Email
            FROM Курьер k
                     JOIN Пользователь u ON k.ID_пользователя = u.ID_пользователя
            ORDER BY k.ID_курьера
            """
        )

    def load_products(self):
        self.load_table(
            "Товар",
            "📦 Товары",
            """
            SELECT Номер_товара,
                   Название,
                   CONVERT(varchar (20), Цена) as Цена,
                   Количество,
                   CASE
                       WHEN Изображение IS NULL THEN 'Нет'
                       ELSE 'Есть'
                       END                     as Изображение
            FROM Товар
            ORDER BY Номер_товара
            """
        )

    def load_orders(self):
        self.load_table(
            "Заказ",
            "📋 Заказы",
            """
            SELECT z.ID_заказа,
                   CONVERT(varchar (10), z.Дата_заказа, 120)                                               as Дата_заказа,
                   t.Название                                                                              as Товар,
                   z.Количество_заказанного_товара                                                         as Количество,
                   CONCAT(c.Фамилия, ' ', c.Имя)                                                           as Клиент,
                   ISNULL(CONCAT(k.Фамилия, ' ', k.Имя), 'Не назначен')                                    as Курьер,
                   z.Статус,
                   CONVERT(varchar (10), t.Цена)                                                           as Цена_за_единицу,
                   CONVERT(varchar (20), CAST(t.Цена * z.Количество_заказанного_товара AS DECIMAL(10, 2))) as Сумма
            FROM Заказ z
                     JOIN Товар t ON z.Номер_товара = t.Номер_товара
                     JOIN Платежные_данные p ON z.ID_данные = p.ID_данных
                     JOIN Клиент c ON p.ID_Клиента = c.ID_Клиент
                     LEFT JOIN Курьер k ON z.ID_курьера = k.ID_курьера
            ORDER BY z.Дата_заказа DESC, z.ID_заказа DESC
            """
        )

    def load_payments(self):
        self.load_table(
            "Платежные_данные",
            "💳 Платежные данные",
            """
            SELECT p.ID_данных,
                   CONCAT(c.Фамилия, ' ', c.Имя, ' ', ISNULL(c.Отчество, '')) as Клиент,
                   CONCAT('**** **** **** ', RIGHT(p.Номер_карты, 4))         as Номер_карты,
                   CONVERT(varchar (10), p.Срок_действия, 120)                as Срок_действия,
                   '***'                                                      as CVV
            FROM Платежные_данные p
                     JOIN Клиент c ON p.ID_Клиента = c.ID_Клиент
            ORDER BY p.ID_данных
            """
        )

    def refresh_table(self):
        if self.current_table:
            tables = {
                "Пользователь": self.load_users,
                "Клиент": self.load_clients,
                "Курьер": self.load_couriers,
                "Товар": self.load_products,
                "Заказ": self.load_orders,
                "Платежные_данные": self.load_payments,
            }

            for table_name, func in tables.items():
                if table_name.lower() in self.current_table.lower():
                    func()
                    break

    def add_record(self):
        if not self.current_table:
            messagebox.showinfo("Информация", "Сначала выберите таблицу")
            return

        # Только для редактируемых таблиц
        editable_tables = ["Пользователь", "Товар"]

        if self.current_table not in editable_tables:
            messagebox.showinfo("Информация",
                                f"Добавление записей в таблицу '{self.current_table}' не предусмотрено.\n\n"
                                f"Доступно добавление только для: Пользователи, Товары")
            return

        # Создаем диалоговое окно в зависимости от таблицы
        if self.current_table == "Пользователь":
            dialog = AddUserDialog(self, self.refresh_table)
            dialog.grab_set()
        elif self.current_table == "Товар":
            dialog = AddProductDialog(self, self.refresh_table)
            dialog.grab_set()

    def edit_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выбор", "Выберите запись для редактирования")
            return

        if not self.current_table:
            return

        # Получаем данные выбранной строки
        item = self.tree.item(selected[0])
        values = item["values"]

        # Только для редактируемых таблиц
        editable_tables = {
            "Пользователь": EditUserDialog,
            "Товар": EditProductDialog,
            "Заказ": EditOrderDialog
        }

        if self.current_table not in editable_tables:
            messagebox.showinfo("Информация",
                                f"Редактирование записей в таблицу '{self.current_table}' не предусмотрено.\n\n"
                                f"Доступно редактирование только для: Пользователи, Товары, Заказы")
            return

        # Создаем диалоговое окно
        dialog_class = editable_tables[self.current_table]
        dialog = dialog_class(self, values, self.refresh_table)
        dialog.grab_set()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выбор", "Выберите запись для удаления")
            return

        if not self.current_table:
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        # Определяем, какие таблицы можно удалять
        deletable_tables = ["Пользователь", "Товар", "Заказ"]

        if self.current_table not in deletable_tables:
            messagebox.showinfo("Информация",
                                f"Удаление записей из таблицы '{self.current_table}' не предусмотрено.\n\n"
                                f"Доступно удаление только для: Пользователи, Товары, Заказы")
            return

        # Подтверждение удаления
        response = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить выбранную запись?\nID: {values[0] if values else 'N/A'}"
        )

        if response:
            try:
                conn = get_connection()
                cursor = conn.cursor()

                # Определяем имя ID колонки и таблицы
                table_id_map = {
                    "Пользователь": ("Пользователь", "ID_пользователя"),
                    "Клиент": ("Клиент", "ID_Клиент"),
                    "Курьер": ("Курьер", "ID_курьера"),
                    "Товар": ("Товар", "Номер_товара"),
                    "Заказ": ("Заказ", "ID_заказа"),
                    "Платежные_данные": ("Платежные_данные", "ID_данных")
                }

                table_name, id_column = table_id_map.get(self.current_table, (None, None))

                if table_name and id_column:
                    record_id = values[0]
                    cursor.execute(f"DELETE FROM {table_name} WHERE {id_column} = ?", (record_id,))
                    conn.commit()

                    messagebox.showinfo("Успех", "Запись успешно удалена")
                    self.refresh_table()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить запись: {str(e)}")
            finally:
                conn.close()


# Диалоговые окна для добавления/редактирования записей

class AddUserDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback

        self.title("Добавить пользователя")
        self.geometry("500x450")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)

        # Центрирование окна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = (parent.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.setup_ui()

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        ctk.CTkLabel(main_frame, text="Добавить пользователя",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=HEADER_PRIMARY).pack(pady=(0, 20))

        # Поля ввода
        fields_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        fields_frame.pack(fill="x", pady=10)

        # Логин
        ctk.CTkLabel(fields_frame, text="Логин:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_login = ctk.CTkEntry(fields_frame, width=250, height=35,
                                        fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                        text_color=ENTRY_TEXT)
        self.entry_login.grid(row=0, column=1, padx=5, pady=5)

        # Пароль
        ctk.CTkLabel(fields_frame, text="Пароль:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_password = ctk.CTkEntry(fields_frame, width=250, height=35, show="*",
                                           fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                           text_color=ENTRY_TEXT)
        self.entry_password.grid(row=1, column=1, padx=5, pady=5)

        # Email
        ctk.CTkLabel(fields_frame, text="Email:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_email = ctk.CTkEntry(fields_frame, width=250, height=35,
                                        fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                        text_color=ENTRY_TEXT)
        self.entry_email.grid(row=2, column=1, padx=5, pady=5)

        # Роль
        ctk.CTkLabel(fields_frame, text="Роль:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.combo_role = ctk.CTkComboBox(fields_frame,
                                          values=["Администратор", "Клиент", "Курьер"],
                                          width=250, height=35,
                                          fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                          text_color=ENTRY_TEXT,
                                          button_color=ACCENT, button_hover_color=ACCENT_DARK)
        self.combo_role.grid(row=3, column=1, padx=5, pady=5)
        self.combo_role.set("Клиент")

        # Активен
        ctk.CTkLabel(fields_frame, text="Активен:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.combo_active = ctk.CTkComboBox(fields_frame,
                                            values=["Да", "Нет"],
                                            width=250, height=35,
                                            fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                            text_color=ENTRY_TEXT,
                                            button_color=ACCENT, button_hover_color=ACCENT_DARK)
        self.combo_active.grid(row=4, column=1, padx=5, pady=5)
        self.combo_active.set("Да")

        # Кнопки
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(btn_frame, text="Сохранить", command=self.save,
                      height=40, fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=BTN_TEXT).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=self.destroy,
                      height=40, fg_color=BTN_SECONDARY, hover_color=BTN_SECONDARY_HOVER,
                      text_color=BTN_SECONDARY_TEXT).pack(side="right", padx=5)

    def save(self):
        # Получаем данные
        login = self.entry_login.get().strip()
        password = self.entry_password.get()
        email = self.entry_email.get().strip() or None
        role = self.combo_role.get()
        active = 1 if self.combo_active.get() == "Да" else 0

        if not login or not password:
            messagebox.showwarning("Ошибка", "Логин и пароль обязательны")
            return

        try:
            from security import hash_password
            hashed_password = hash_password(password)

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO Пользователь (Логин, Хеш_пароля, Email, Роль, Активен, Дата_регистрации)
                           VALUES (?, ?, ?, ?, ?, GETDATE())
                           """, (login, hashed_password, email, role, active))

            conn.commit()
            messagebox.showinfo("Успех", "Пользователь добавлен")
            self.callback()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {str(e)}")
        finally:
            conn.close()


class EditUserDialog(AddUserDialog):
    def __init__(self, parent, values, callback):
        self.user_id = values[0] if values else None
        super().__init__(parent, callback)
        self.title("Редактировать пользователя")

        # Заполняем поля значениями
        if values and len(values) >= 6:
            self.entry_login.insert(0, values[1])
            self.entry_login.configure(state="disabled")  # Логин нельзя менять
            self.entry_password.delete(0, "end")
            self.entry_password.insert(0, "********")  # Заглушка для пароля
            self.entry_password.configure(show="")

            if values[2]:  # Email
                self.entry_email.insert(0, values[2])

            self.combo_role.set(values[3])
            self.combo_active.set(values[5])

    def save(self):
        # Получаем данные
        email = self.entry_email.get().strip() or None
        role = self.combo_role.get()
        active = 1 if self.combo_active.get() == "Да" else 0

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Проверяем, нужно ли обновлять пароль
            password = self.entry_password.get()
            if password and password != "********":
                from security import hash_password
                hashed_password = hash_password(password)
                cursor.execute("""
                               UPDATE Пользователь
                               SET Email      = ?,
                                   Роль       = ?,
                                   Активен    = ?,
                                   Хеш_пароля = ?
                               WHERE ID_пользователя = ?
                               """, (email, role, active, hashed_password, self.user_id))
            else:
                cursor.execute("""
                               UPDATE Пользователь
                               SET Email   = ?,
                                   Роль    = ?,
                                   Активен = ?
                               WHERE ID_пользователя = ?
                               """, (email, role, active, self.user_id))

            conn.commit()
            messagebox.showinfo("Успех", "Пользователь обновлен")
            self.callback()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить пользователя: {str(e)}")
        finally:
            conn.close()


class AddProductDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.configure(fg_color=BG_MAIN)

        # байты картинки из файла / БД
        self.image_bytes: bytes | None = None
        # PhotoImage для превью (держим ссылку, чтобы не отгрузилась)
        self.preview_photo: ImageTk.PhotoImage | None = None

        self.title("Добавить товар")
        self.geometry("500x550")
        self.resizable(False, False)

        # Центрирование окна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = (parent.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self._setup_ui()

    def _setup_ui(self):
        main_frame = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="Добавить товар",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=HEADER_PRIMARY
        ).pack(pady=(0, 20))

        # фрейм с полями
        self.fields_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.fields_frame.pack(fill="x", pady=10)

        # Название
        ctk.CTkLabel(self.fields_frame, text="Название:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_name = ctk.CTkEntry(self.fields_frame, width=250, height=35,
                                       fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                       text_color=ENTRY_TEXT)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        # Цена
        ctk.CTkLabel(self.fields_frame, text="Цена:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_price = ctk.CTkEntry(self.fields_frame, width=250, height=35,
                                        fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                        text_color=ENTRY_TEXT)
        self.entry_price.grid(row=1, column=1, padx=5, pady=5)

        # Количество
        ctk.CTkLabel(self.fields_frame, text="Количество:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_qty = ctk.CTkEntry(self.fields_frame, width=250, height=35,
                                      fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                      text_color=ENTRY_TEXT)
        self.entry_qty.grid(row=2, column=1, padx=5, pady=5)

        # Изображение
        ctk.CTkLabel(self.fields_frame, text="Изображение:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.btn_image = ctk.CTkButton(
            self.fields_frame,
            text="Выбрать файл",
            command=self.select_image,
            width=250, height=35,
            fg_color=BTN_SECONDARY, hover_color=BTN_SECONDARY_HOVER,
            text_color=BTN_SECONDARY_TEXT
        )
        self.btn_image.grid(row=3, column=1, padx=5, pady=5)

        self.lbl_image_status = ctk.CTkLabel(
            self.fields_frame, text="Файл не выбран",
            text_color=TEXT_LIGHT
        )
        self.lbl_image_status.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Фрейм для превью изображения
        self.preview_frame = tk.Frame(self.fields_frame, bg=ACCENT_LIGHT, height=120)
        self.preview_frame.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.preview_frame.grid_propagate(False)

        self.preview_label = tk.Label(self.preview_frame, bg=ACCENT_LIGHT)
        self.preview_label.pack(expand=True)

        # Кнопки
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(
            btn_frame, text="Сохранить", command=self.save,
            height=40, fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
            text_color=BTN_TEXT
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self._on_cancel,
            height=40,
            fg_color=BTN_SECONDARY, hover_color=BTN_SECONDARY_HOVER,
            text_color=BTN_SECONDARY_TEXT,
        ).pack(side="right", padx=5)

    def select_image(self):
        from tkinter import filedialog
        import os

        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                ("Все файлы", "*.*"),
            ],
        )

        if not file_path:
            return

        try:
            # читаем байты для записи в БД
            with open(file_path, "rb") as f:
                self.image_bytes = f.read()

            self.lbl_image_status.configure(
                text=f"Выбран: {os.path.basename(file_path)}"
            )

            # создаём превью через PIL + PhotoImage
            try:
                img = Image.open(file_path)
                img.thumbnail((120, 120), Image.Resampling.LANCZOS)

                self.preview_photo = ImageTk.PhotoImage(img, master=self)
                self.preview_label.configure(image=self.preview_photo, text="")

            except Exception as e:
                print(f"Ошибка создания превью: {e}")
                self.preview_label.configure(text="Ошибка превью", image=None)

        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Не удалось загрузить изображение: {e}"
            )

    def save(self):
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        qty_str = self.entry_qty.get().strip()

        if not name:
            messagebox.showwarning("Ошибка", "Название обязательно")
            return

        try:
            price = float(price_str.replace(",", "."))
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Некорректная цена")
            return

        try:
            qty = int(qty_str)
            if qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Некорректное количество")
            return

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Товар (Название, Цена, Количество, Изображение)
                VALUES (?, ?, ?, ?)
                """,
                (name, price, qty, self.image_bytes),
            )
            conn.commit()
            messagebox.showinfo("Успех", "Товар добавлен")
            if self.callback:
                self.callback()
            self.destroy()
        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить товар: {e}")
        finally:
            if conn:
                conn.close()

    def _on_cancel(self):
        # безопасно отвяжем картинку
        if self.preview_label is not None:
            self.preview_label.configure(image=None)
        self.preview_photo = None
        self.destroy()


class EditProductDialog(AddProductDialog):
    def __init__(self, parent, values, callback):
        # сначала инициализируем базовый диалог (создаём форму и превью-лейбл)
        super().__init__(parent, callback)
        self.product_id = int(values[0]) if values and values[0] else None
        self.title("Редактировать товар")

        # заполняем поля из таблицы
        if values and len(values) >= 5:
            # values: (id, name, price, qty, "Есть"/"—" или др.)
            self.entry_name.delete(0, "end")
            self.entry_name.insert(0, values[1])

            self.entry_price.delete(0, "end")
            self.entry_price.insert(0, str(values[2]))

            self.entry_qty.delete(0, "end")
            self.entry_qty.insert(0, str(values[3]))

            has_image_flag = values[4]

            if has_image_flag in ("Есть", "Да", "1", True):
                # подгружаем изображение из БД
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT Изображение FROM Товар WHERE Номер_товара = ?",
                        (self.product_id,),
                    )
                    row = cursor.fetchone()
                    conn.close()

                    if row and row[0]:
                        self.image_bytes = row[0]

                        try:
                            img = Image.open(
                                io.BytesIO(self.image_bytes)
                            )
                            img.thumbnail(
                                (120, 120), Image.Resampling.LANCZOS
                            )

                            self.preview_photo = ImageTk.PhotoImage(img, master=self)
                            self.preview_label.configure(
                                image=self.preview_photo, text=""
                            )
                            self.lbl_image_status.configure(
                                text="Изображение загружено из БД"
                            )
                        except Exception as e:
                            print(f"Ошибка создания превью: {e}")
                            self.preview_label.configure(
                                image=None,
                                text="Изображение загружено (ошибка превью)",
                            )
                    else:
                        self.lbl_image_status.configure(
                            text="Изображение в БД отсутствует"
                        )

                except Exception as e:
                    print(f"Ошибка загрузки изображения из БД: {e}")
                    self.lbl_image_status.configure(
                        text="Ошибка загрузки изображения"
                    )

    def save(self):
        if not self.product_id:
            messagebox.showerror("Ошибка", "Не выбран товар для редактирования")
            return

        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        qty_str = self.entry_qty.get().strip()

        if not name:
            messagebox.showwarning("Ошибка", "Название обязательно")
            return

        try:
            price = float(price_str.replace(",", "."))
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Некорректная цена")
            return

        try:
            qty = int(qty_str)
            if qty < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка", "Некорректное количество")
            return

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.image_bytes is not None:
                cursor.execute(
                    """
                    UPDATE Товар
                    SET Название    = ?,
                        Цена        = ?,
                        Количество  = ?,
                        Изображение = ?
                    WHERE Номер_товара = ?
                    """,
                    (name, price, qty, self.image_bytes, self.product_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE Товар
                    SET Название   = ?,
                        Цена       = ?,
                        Количество = ?
                    WHERE Номер_товара = ?
                    """,
                    (name, price, qty, self.product_id),
                )

            conn.commit()
            messagebox.showinfo("Успех", "Товар обновлён")
            if self.callback:
                self.callback()
            self._on_cancel()
        except Exception as e:
            if conn:
                conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось обновить товар: {e}")
        finally:
            if conn:
                conn.close()


class EditOrderDialog(ctk.CTkToplevel):
    def __init__(self, parent, values, callback):
        super().__init__(parent)
        self.order_id = values[0] if values else None
        self.callback = callback
        self.configure(fg_color=BG_MAIN)

        self.title("Редактировать заказ")
        self.geometry("500x450")
        self.resizable(False, False)

        # Центрирование окна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = (parent.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.setup_ui(values)

    def setup_ui(self, values):
        main_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_frame, text=f"Редактирование заказа #{self.order_id}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=HEADER_PRIMARY).pack(pady=(0, 20))

        # Статус
        ctk.CTkLabel(main_frame, text="Статус:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=5)
        self.combo_status = ctk.CTkComboBox(main_frame,
                                            values=["создан", "в обработке", "у курьера", "доставлен", "отменен"],
                                            height=35,
                                            fg_color=ENTRY_BG, border_color=ENTRY_BORDER,
                                            text_color=ENTRY_TEXT,
                                            button_color=ACCENT, button_hover_color=ACCENT_DARK)
        if values and len(values) >= 7:
            self.combo_status.set(values[6])  # Статус теперь на 6-й позиции (после добавления даты)
        else:
            self.combo_status.set("создан")
        self.combo_status.pack(fill="x", pady=5)

        # Информация о заказе
        if values and len(values) >= 9:
            info_text = f"""
            📅 Дата заказа: {values[1]}
            🛒 Товар: {values[2]}
            🔢 Количество: {values[3]}
            👤 Клиент: {values[4]}
            🚴 Курьер: {values[5]}
            💰 Цена за единицу: {values[7]}
            💵 Сумма: {values[8]}
            """
            ctk.CTkLabel(main_frame, text="Информация о заказе:",
                         font=ctk.CTkFont(weight="bold"),
                         text_color=TEXT_DARK).pack(anchor="w", pady=(10, 5))
            ctk.CTkLabel(main_frame, text=info_text, justify="left",
                         text_color=TEXT_LIGHT).pack(anchor="w", pady=5)

        # Кнопки
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        ctk.CTkButton(btn_frame, text="Сохранить", command=self.save,
                      height=40, fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=BTN_TEXT).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", command=self.destroy,
                      height=40, fg_color=BTN_SECONDARY, hover_color=BTN_SECONDARY_HOVER,
                      text_color=BTN_SECONDARY_TEXT).pack(side="right", padx=5)

    def save(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                           UPDATE Заказ
                           SET Статус = ?
                           WHERE ID_заказа = ?
                           """, (self.combo_status.get(), self.order_id))

            conn.commit()
            messagebox.showinfo("Успех", "Статус заказа обновлен")
            self.callback()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить заказ: {str(e)}")
        finally:
            conn.close()