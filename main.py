# main.py
import customtkinter as ctk
from db import get_user_by_login, get_connection
from security import verify_password
from ui_admin import AdminApp
from ui_client import ClientApp
from ui_courier import CourierApp
from ui_login import RegistrationWindow, AdminManagerWindow
from theme import *  # Импортируем все цвета из темы

# Настройка CustomTkinter
ctk.set_appearance_mode("light")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Электронный магазин – вход")
        self.geometry("400x350")
        self.resizable(False, False)

        # Применяем тему к окну
        self.configure(fg_color=BG_MAIN)

        self.setup_ui()

        # Скрытая комбинация для окна админов: Ctrl+Shift+A
        self.bind("<Control-Shift-A>", self.open_admin_manager)

    def setup_ui(self):
        # Основная рамка
        container = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=15,
            border_width=2,
            border_color=BORDER
        )
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Заголовок
        title = ctk.CTkLabel(
            container,
            text="Вход в систему",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=ACCENT_DARK
        )
        title.pack(pady=(0, 20))

        # Логин
        ctk.CTkLabel(
            container,
            text="Логин:",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_DARK
        ).pack(anchor="w", padx=20, pady=(5, 0))

        self.entry_login = ctk.CTkEntry(
            container,
            width=250,
            fg_color=ENTRY_BG,
            border_color=ENTRY_BORDER,
            text_color=ENTRY_TEXT,
            placeholder_text_color=ENTRY_PLACEHOLDER,
            placeholder_text="Введите логин"
        )
        self.entry_login.pack(padx=20, pady=(0, 10))

        # Пароль
        ctk.CTkLabel(
            container,
            text="Пароль:",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_DARK
        ).pack(anchor="w", padx=20, pady=(5, 0))

        self.entry_password = ctk.CTkEntry(
            container,
            width=250,
            show="*",
            fg_color=ENTRY_BG,
            border_color=ENTRY_BORDER,
            text_color=ENTRY_TEXT,
            placeholder_text_color=ENTRY_PLACEHOLDER,
            placeholder_text="Введите пароль"
        )
        self.entry_password.pack(padx=20, pady=(0, 20))

        # Кнопки
        btn_frame = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )
        btn_frame.pack(pady=10)

        # Основная кнопка
        ctk.CTkButton(
            btn_frame,
            text="Войти",
            command=self.on_login,
            width=100,
            height=35,
            fg_color=BTN_PRIMARY,
            hover_color=BTN_PRIMARY_HOVER,
            text_color=BTN_TEXT,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10
        ).pack(side="left", padx=5)

        # Вторичная кнопка
        ctk.CTkButton(
            btn_frame,
            text="Регистрация",
            command=self.open_register,
            width=100,
            height=35,
            fg_color=BTN_SECONDARY,
            hover_color=BTN_SECONDARY_HOVER,
            text_color=BTN_SECONDARY_TEXT,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        ).pack(side="left", padx=5)

        # Статус
        self.label_status = ctk.CTkLabel(
            container,
            text="",
            text_color=ACCENT,  # Ярко-розовый для статуса
            font=ctk.CTkFont(size=12)
        )
        self.label_status.pack(pady=(10, 0))

    def on_login(self):
        login = self.entry_login.get().strip()
        password = self.entry_password.get()

        if not login or not password:
            self.label_status.configure(text="Введите логин и пароль")
            return

        row = get_user_by_login(login)
        if row is None:
            self.label_status.configure(text="Пользователь не найден")
            return

        user_id, login_db, hashed_pwd, role, id_client, id_courier = row

        if not verify_password(password, hashed_pwd):
            self.label_status.configure(text="Неверный пароль")
            return

        # Скрываем окно входа
        self.withdraw()

        # Открываем интерфейс по роли
        if role == "Администратор":
            app = AdminApp(self, user_id)
        elif role == "Клиент":
            app = ClientApp(self, user_id, id_client)
        elif role == "Курьер":
            app = CourierApp(self, user_id, id_courier)
        else:
            # запасной вариант — простое окно
            app = ctk.CTkToplevel(self)
            app.title("Неизвестная роль")

        # когда дочернее окно закрывается — показываем логин обратно
        app.protocol("WM_DELETE_WINDOW", lambda w=app: self.on_window_close(w))
        app.focus_set()

    def on_window_close(self, window):
        window.destroy()
        self.deiconify()  # Показываем окно входа снова

    def open_register(self, event=None):
        RegistrationWindow(self)

    def open_admin_manager(self, event=None):
        AdminManagerWindow(self)


def create_default_admin():
    """Создает администратора по умолчанию, если его нет"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Проверяем, есть ли администраторы
        cursor.execute("SELECT COUNT(*) FROM Пользователь WHERE Роль = N'Администратор'")
        admin_count = cursor.fetchone()[0]

        if admin_count == 0:
            from security import hash_password
            default_pass = hash_password("admin123")

            cursor.execute("""
                           INSERT INTO Пользователь
                               (Логин, Хеш_пароля, Email, Роль, Дата_регистрации, Активен)
                           VALUES (?, ?, ?, N'Администратор', SYSDATETIME(), 1)
                           """, ("admin", default_pass, "admin@example.com"))

            conn.commit()
            print("Создан администратор по умолчанию: admin/admin123")
    except Exception as e:
        print(f"Ошибка при создании администратора по умолчанию: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_default_admin()
    app = LoginWindow()
    app.mainloop()