# ui_login.py
import customtkinter as ctk
from tkinter import messagebox
from db import get_connection
from security import hash_password
from datetime import datetime
from theme import *
# Настройка темы CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class RegistrationWindow(ctk.CTkToplevel):
    """
    Регистрация пользователя.
    Внутри выбираем роль: Клиент или Курьер.
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("Регистрация пользователя")
        self.geometry("750x600")
        self.minsize(750, 600)
        self.transient(master)
        self.grab_set()

        # Центрирование окна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (master.winfo_screenwidth() // 2) - (width // 2)
        y = (master.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.configure(fg_color=BG_MAIN)

        # Основной контейнер
        outer = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        ctk.CTkLabel(
            outer,
            text="🌸 Регистрация пользователя",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT
        ).pack(anchor="w", pady=(0, 15))

        # Вкладки
        self.tabview = ctk.CTkTabview(outer,
                                      fg_color=BG_CARD,
                                      border_width=1,
                                      border_color=ACCENT_LIGHT,
                                      segmented_button_selected_color=ACCENT,
                                      segmented_button_selected_hover_color=ACCENT_DARK,
                                      segmented_button_unselected_color=BG_CARD,
                                      segmented_button_unselected_hover_color=ACCENT_LIGHT)
        self.tabview.pack(fill="both", expand=True, pady=(0, 10))

        # Создаем вкладки
        self.tab_account = self.tabview.add("👤 Учётная запись")
        self.tab_profile = self.tabview.add("📋 Профиль")

        # ---------------- Вкладка учётной записи ----------------
        acc_frame = ctk.CTkFrame(self.tab_account, fg_color="transparent")
        acc_frame.pack(fill="both", expand=True, padx=20, pady=20)

        row = 0
        # Логин
        ctk.CTkLabel(acc_frame,
                     text="Логин:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=row, column=0, sticky="e", pady=10, padx=(0, 10)
        )
        self.entry_login = ctk.CTkEntry(acc_frame,
                                        width=300,
                                        height=35,
                                        font=ctk.CTkFont(size=14))
        self.entry_login.grid(row=row, column=1, sticky="w", pady=10)

        row += 1
        # Пароль
        ctk.CTkLabel(acc_frame,
                     text="Пароль:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=row, column=0, sticky="e", pady=10, padx=(0, 10)
        )
        self.entry_password = ctk.CTkEntry(acc_frame,
                                           show="*",
                                           width=300,
                                           height=35,
                                           font=ctk.CTkFont(size=14))
        self.entry_password.grid(row=row, column=1, sticky="w", pady=10)

        row += 1
        # Email
        ctk.CTkLabel(acc_frame,
                     text="E-mail:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=row, column=0, sticky="e", pady=10, padx=(0, 10)
        )
        self.entry_email = ctk.CTkEntry(acc_frame,
                                        width=300,
                                        height=35,
                                        font=ctk.CTkFont(size=14))
        self.entry_email.grid(row=row, column=1, sticky="w", pady=10)

        row += 1
        # Роль
        ctk.CTkLabel(acc_frame,
                     text="Роль:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=row, column=0, sticky="e", pady=10, padx=(0, 10)
        )
        self.combo_role = ctk.CTkComboBox(
            acc_frame,
            values=["Клиент", "Курьер"],
            width=300,
            height=35,
            font=ctk.CTkFont(size=14),
            button_color=ACCENT,
            dropdown_hover_color=ACCENT_LIGHT
        )
        self.combo_role.grid(row=row, column=1, sticky="w", pady=10)
        self.combo_role.set("Клиент")
        self.combo_role.configure(command=self.on_role_change)

        # Настройка сетки
        acc_frame.grid_columnconfigure(0, weight=0, minsize=100)
        acc_frame.grid_columnconfigure(1, weight=1)

        # ---------------- Вкладка профиля ----------------
        profile_frame = ctk.CTkScrollableFrame(self.tab_profile,
                                               fg_color="transparent",
                                               height=400)
        profile_frame.pack(fill="both", expand=True, padx=20, pady=20)

        r = 0
        # Фамилия
        ctk.CTkLabel(profile_frame,
                     text="Фамилия:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_lastname = ctk.CTkEntry(profile_frame,
                                           width=300,
                                           height=35,
                                           font=ctk.CTkFont(size=14))
        self.entry_lastname.grid(row=r, column=1, sticky="w", pady=8)

        r += 1
        # Имя
        ctk.CTkLabel(profile_frame,
                     text="Имя:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_firstname = ctk.CTkEntry(profile_frame,
                                            width=300,
                                            height=35,
                                            font=ctk.CTkFont(size=14))
        self.entry_firstname.grid(row=r, column=1, sticky="w", pady=8)

        r += 1
        # Отчество
        ctk.CTkLabel(profile_frame,
                     text="Отчество:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_middlename = ctk.CTkEntry(profile_frame,
                                             width=300,
                                             height=35,
                                             font=ctk.CTkFont(size=14))
        self.entry_middlename.grid(row=r, column=1, sticky="w", pady=8)

        # Для клиента нужны паспорт + адрес
        r += 1
        ctk.CTkLabel(profile_frame,
                     text="Серия паспорта:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_pass_series = ctk.CTkEntry(profile_frame,
                                              width=150,
                                              height=35,
                                              font=ctk.CTkFont(size=14))
        self.entry_pass_series.grid(row=r, column=1, sticky="w", pady=8)

        r += 1
        ctk.CTkLabel(profile_frame,
                     text="Номер паспорта:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_pass_number = ctk.CTkEntry(profile_frame,
                                              width=150,
                                              height=35,
                                              font=ctk.CTkFont(size=14))
        self.entry_pass_number.grid(row=r, column=1, sticky="w", pady=8)

        r += 1
        ctk.CTkLabel(profile_frame,
                     text="Город:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_city = ctk.CTkEntry(profile_frame,
                                       width=300,
                                       height=35,
                                       font=ctk.CTkFont(size=14))
        self.entry_city.grid(row=r, column=1, sticky="w", pady=8)

        r += 1
        ctk.CTkLabel(profile_frame,
                     text="Улица:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_street = ctk.CTkEntry(profile_frame,
                                         width=300,
                                         height=35,
                                         font=ctk.CTkFont(size=14))
        self.entry_street.grid(row=r, column=1, sticky="w", pady=8)

        r += 1
        ctk.CTkLabel(profile_frame,
                     text="Дом:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_house = ctk.CTkEntry(profile_frame,
                                        width=100,
                                        height=35,
                                        font=ctk.CTkFont(size=14))
        self.entry_house.grid(row=r, column=1, sticky="w", pady=8)

        r += 1
        ctk.CTkLabel(profile_frame,
                     text="Квартира:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=r, column=0, sticky="e", pady=8, padx=(0, 10)
        )
        self.entry_flat = ctk.CTkEntry(profile_frame,
                                       width=100,
                                       height=35,
                                       font=ctk.CTkFont(size=14))
        self.entry_flat.grid(row=r, column=1, sticky="w", pady=8)

        # Телефон только для курьера
        r += 1
        self.lbl_phone = ctk.CTkLabel(profile_frame,
                                      text="Телефон:",
                                      font=ctk.CTkFont(weight="bold"),
                                      text_color=TEXT_DARK)
        self.lbl_phone.grid(row=r, column=0, sticky="e", pady=8, padx=(0, 10))

        self.entry_phone = ctk.CTkEntry(profile_frame,
                                        width=200,
                                        height=35,
                                        font=ctk.CTkFont(size=14))
        self.entry_phone.grid(row=r, column=1, sticky="w", pady=8)

        # Скрываем телефон по умолчанию (для клиента)
        self.lbl_phone.grid_remove()
        self.entry_phone.grid_remove()

        # Настройка сетки
        profile_frame.grid_columnconfigure(0, weight=0, minsize=150)
        profile_frame.grid_columnconfigure(1, weight=1)

        # ---------------- Кнопки ----------------
        btn_frame = ctk.CTkFrame(outer, fg_color="transparent")
        btn_frame.pack(pady=(10, 0))

        ctk.CTkButton(
            btn_frame,
            text="🌸 Зарегистрировать",
            command=self.on_register,
            height=45,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            corner_radius=8
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self.destroy,
            height=45,
            width=120,
            font=ctk.CTkFont(size=14),
            fg_color="#9e9e9e",
            hover_color="#757575",
            corner_radius=8
        ).pack(side="left", padx=10)

        # Инициализация видимости полей
        self.on_role_change(None)

    def on_role_change(self, choice):
        """Изменение видимости полей в зависимости от роли"""
        role = self.combo_role.get()

        if role == "Курьер":
            # Для курьера показываем телефон, скрываем часть полей
            self.lbl_phone.grid()
            self.entry_phone.grid()
            # Поля паспорта и адреса не обязательны для курьера
            required_text_color = TEXT_DARK
        else:  # Клиент
            # Для клиента скрываем телефон, показываем все поля
            self.lbl_phone.grid_remove()
            self.entry_phone.grid_remove()
            # Все поля обязательны для клиента
            required_text_color = TEXT_DARK

        # Обновляем цвет текста для обязательных полей
        widgets = [
            (self.entry_lastname, "Фамилия"),
            (self.entry_firstname, "Имя"),
            (self.entry_middlename, "Отчество"),
        ]

        if role == "Клиент":
            widgets.extend([
                (self.entry_pass_series, "Серия паспорта"),
                (self.entry_pass_number, "Номер паспорта"),
                (self.entry_city, "Город"),
                (self.entry_street, "Улица"),
                (self.entry_house, "Дом"),
            ])

        if role == "Курьер":
            widgets.append((self.entry_phone, "Телефон"))

    def validate_required_fields(self, role):
        """Валидация обязательных полей"""
        errors = []

        # Общие поля для всех ролей
        if not self.entry_login.get().strip():
            errors.append("Логин")
        if not self.entry_password.get():
            errors.append("Пароль")
        if not self.entry_lastname.get().strip():
            errors.append("Фамилия")
        if not self.entry_firstname.get().strip():
            errors.append("Имя")
        if not self.entry_middlename.get().strip():
            errors.append("Отчество")

        if role == "Клиент":
            # Все поля обязательны для клиента
            if not self.entry_pass_series.get().strip():
                errors.append("Серия паспорта")
            if not self.entry_pass_number.get().strip():
                errors.append("Номер паспорта")
            if not self.entry_city.get().strip():
                errors.append("Город")
            if not self.entry_street.get().strip():
                errors.append("Улица")
            if not self.entry_house.get().strip():
                errors.append("Дом")
            # Квартира не обязательна

        elif role == "Курьер":
            # Телефон обязателен для курьера
            if not self.entry_phone.get().strip():
                errors.append("Телефон")

        return errors

    def on_register(self):
        login = self.entry_login.get().strip()
        password = self.entry_password.get()
        email = self.entry_email.get().strip() or None
        role = self.combo_role.get()

        # Валидация обязательных полей
        missing_fields = self.validate_required_fields(role)
        if missing_fields:
            messagebox.showwarning("⚠️ Обязательные поля",
                                   f"Заполните следующие обязательные поля:\n• " +
                                   "\n• ".join(missing_fields))
            return

        lastname = self.entry_lastname.get().strip()
        firstname = self.entry_firstname.get().strip()
        middlename = self.entry_middlename.get().strip()

        conn = get_connection()
        cur = conn.cursor()

        try:
            hashed = hash_password(password)

            # 1) создаём пользователя и сразу получаем его ID
            cur.execute(
                """
                INSERT INTO Пользователь
                    (Логин, Хеш_пароля, Email, Роль, Дата_регистрации, Активен)
                    OUTPUT INSERTED.ID_пользователя
                VALUES (?, ?, ?, ?, GETDATE(), 1)
                """,
                (login, hashed, email, role)
            )
            row = cur.fetchone()
            if not row or row[0] is None:
                raise RuntimeError("Не удалось получить ID нового пользователя")
            user_id = int(row[0])

            # 2) в зависимости от роли создаём профиль
            if role == "Клиент":
                series = self.entry_pass_series.get().strip()
                number = self.entry_pass_number.get().strip()
                city = self.entry_city.get().strip()
                street = self.entry_street.get().strip()
                house = self.entry_house.get().strip()
                flat = self.entry_flat.get().strip() or None

                cur.execute(
                    """
                    INSERT INTO Клиент
                    (ID_пользователя, Фамилия, Имя, Отчество,
                     Серия_паcпорта, Номер_паcпорта,
                     Город, Улица, Дом, Квартира)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id, lastname, firstname, middlename,
                        series, number, city, street, house, flat
                    )
                )

            elif role == "Курьер":
                phone = self.entry_phone.get().strip()

                cur.execute(
                    """
                    INSERT INTO Курьер
                        (ID_пользователя, Фамилия, Имя, Отчество, Номер_телефона)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, lastname, firstname, middlename, phone)
                )

            conn.commit()
            messagebox.showinfo("🌸 Успех", "Пользователь успешно зарегистрирован!")
            self.destroy()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("❌ Ошибка", f"Не удалось зарегистрировать: {str(e)}")
        finally:
            conn.close()


class AdminManagerWindow(ctk.CTkToplevel):
    """
    Служебное окно:
    - показывает список администраторов (таблица Пользователь, Роль = 'Администратор')
    - позволяет добавить нового админа.
    Открывается из LoginWindow по Ctrl+Shift+A.
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("🌸 Управление администраторами (служебное окно)")
        self.geometry("700x500")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)

        # Центрирование окна
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (master.winfo_screenwidth() // 2) - (width // 2)
        y = (master.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        # Основной контейнер
        outer = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        outer.pack(expand=True, fill="both", padx=20, pady=20)

        # Заголовок
        ctk.CTkLabel(
            outer,
            text="🌸 Управление администраторами",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT
        ).pack(pady=(0, 15))

        # Список админов
        list_frame = ctk.CTkFrame(outer,
                                  fg_color=BG_CARD,
                                  corner_radius=8,
                                  border_width=1,
                                  border_color=ACCENT_LIGHT)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            list_frame,
            text="Существующие администраторы",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_DARK
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Фрейм для Treeview
        tree_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Импортируем tkinter для Treeview
        import tkinter as tk
        from tkinter import ttk

        # Создаем Treeview в отдельном фрейме
        tk_tree_frame = tk.Frame(tree_frame)
        tk_tree_frame.pack(fill="both", expand=True)

        columns = ("id", "login", "email", "reg", "active")
        self.tree = ttk.Treeview(tk_tree_frame, columns=columns, show="headings", height=8)

        # Настраиваем заголовки
        self.tree.heading("id", text="ID")
        self.tree.heading("login", text="Логин")
        self.tree.heading("email", text="Email")
        self.tree.heading("reg", text="Дата регистрации")
        self.tree.heading("active", text="Активен")

        # Настраиваем колонки
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("login", width=120)
        self.tree.column("email", width=150)
        self.tree.column("reg", width=150)
        self.tree.column("active", width=70, anchor="center")

        # Стиль для Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground=TEXT_DARK,
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=('Segoe UI', 10))
        style.configure("Treeview.Heading",
                        background=ACCENT,
                        foreground="white",
                        font=('Segoe UI', 11, 'bold'),
                        relief="flat")
        style.map('Treeview',
                  background=[('selected', ACCENT)],
                  foreground=[('selected', 'white')])

        self.tree.pack(side="left", fill="both", expand=True)

        # Скроллбар
        scrollbar = ttk.Scrollbar(tk_tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Форма добавления админа
        form = ctk.CTkFrame(outer,
                            fg_color=BG_CARD,
                            corner_radius=8,
                            border_width=1,
                            border_color=ACCENT_LIGHT)
        form.pack(fill="x", padx=5, pady=(10, 0))

        ctk.CTkLabel(
            form,
            text="Добавить администратора",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_DARK
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Поля формы
        fields_frame = ctk.CTkFrame(form, fg_color="transparent")
        fields_frame.pack(fill="x", padx=15, pady=(0, 10))

        # Логин
        ctk.CTkLabel(fields_frame,
                     text="Логин:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.entry_login = ctk.CTkEntry(fields_frame,
                                        width=250,
                                        height=35,
                                        font=ctk.CTkFont(size=14))
        self.entry_login.grid(row=0, column=1, sticky="w", pady=5, padx=(10, 0))

        # Пароль
        ctk.CTkLabel(fields_frame,
                     text="Пароль:",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.entry_password = ctk.CTkEntry(fields_frame,
                                           show="*",
                                           width=250,
                                           height=35,
                                           font=ctk.CTkFont(size=14))
        self.entry_password.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))

        # Email
        ctk.CTkLabel(fields_frame,
                     text="Email (опционально):",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_DARK).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.entry_email = ctk.CTkEntry(fields_frame,
                                        width=250,
                                        height=35,
                                        font=ctk.CTkFont(size=14))
        self.entry_email.grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))

        # Кнопка добавления
        ctk.CTkButton(
            form,
            text="➕ Добавить администратора",
            command=self.add_admin,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            corner_radius=8
        ).pack(pady=(0, 10))

        # Загружаем список администраторов
        self.load_admins()

    def load_admins(self):
        """Загрузка списка администраторов"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           SELECT ID_пользователя, Логин, Email, Дата_регистрации, Активен
                           FROM Пользователь
                           WHERE Роль = N'Администратор'
                           ORDER BY ID_пользователя
                           """)
            for row in cursor.fetchall():
                user_id, login, email, reg, active = row
                self.tree.insert(
                    "", "end",
                    values=(
                        user_id,
                        login,
                        email or "",
                        reg.strftime("%Y-%m-%d %H:%M:%S") if reg else "",
                        "✅ Да" if active else "❌ Нет"
                    )
                )
        finally:
            conn.close()

    def add_admin(self):
        """Добавление нового администратора"""
        login = self.entry_login.get().strip()
        password = self.entry_password.get()
        email = self.entry_email.get().strip() or None

        if not login or not password:
            messagebox.showwarning("⚠️ Внимание", "Логин и пароль обязательны")
            return

        hashed = hash_password(password)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           INSERT INTO Пользователь
                               (Логин, Хеш_пароля, Email, Роль, Дата_регистрации, Активен)
                           VALUES (?, ?, ?, N'Администратор', GETDATE(), 1)
                           """, (login, hashed, email))
            conn.commit()
            messagebox.showinfo("🌸 Успех", "Администратор успешно добавлен!")

            # Очищаем поля
            self.entry_login.delete(0, "end")
            self.entry_password.delete(0, "end")
            self.entry_email.delete(0, "end")

            # Обновляем список
            self.load_admins()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("❌ Ошибка", f"Не удалось добавить администратора: {str(e)}")
        finally:
            conn.close()