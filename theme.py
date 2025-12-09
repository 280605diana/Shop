# theme.py
"""
Розовая цветовая схема для приложения "Электронный магазин"
"""

# Основные цвета
BG_MAIN = "#f9f0f5"  # Нежно-розовый фон
BG_CARD = "#ffffff"  # Белый для карточек
ACCENT = "#e91e63"  # Ярко-розовый акцентный
ACCENT_DARK = "#c2185b"  # Темно-розовый
ACCENT_LIGHT = "#fce4ec"  # Светло-розовый
TEXT_DARK = "#5d4037"  # Темный шоколадный для текста
TEXT_LIGHT = "#8d6e63"  # Светлый шоколадный
BORDER = "#f8bbd0"  # Розовая рамка

# Дополнительные цвета для состояний
HOVER_LIGHT = "#f8bbd0"  # Розовый при наведении (светлый)
HOVER_DARK = "#ad1457"  # Розовый при наведении (темный)
ERROR = "#f44336"  # Красный для ошибок
SUCCESS = "#4caf50"  # Зеленый для успеха
WARNING = "#ff9800"  # Оранжевый для предупреждений
DISABLED = "#e0e0e0"  # Серый для неактивных элементов

# Цвета для кнопок
BTN_PRIMARY = ACCENT
BTN_PRIMARY_HOVER = ACCENT_DARK
BTN_SECONDARY = ACCENT_LIGHT
BTN_SECONDARY_HOVER = HOVER_LIGHT
BTN_TEXT = "white"  # Текст на кнопках
BTN_SECONDARY_TEXT = ACCENT_DARK  # Текст на вторичных кнопках

# Цвета для полей ввода
ENTRY_BG = "#ffffff"  # Белый фон
ENTRY_BORDER = BORDER
ENTRY_TEXT = TEXT_DARK
ENTRY_PLACEHOLDER = "#bdbdbd"  # Серый для подсказок

# Цвета для заголовков
HEADER_PRIMARY = ACCENT_DARK
HEADER_SECONDARY = TEXT_LIGHT

# Цвета для таблиц
TABLE_HEADER = ACCENT_LIGHT
TABLE_ROW_EVEN = "#fafafa"
TABLE_ROW_ODD = "#ffffff"
TABLE_BORDER = "#e0e0e0"


def apply_theme_to_window(window):
    """Применяет розовую тему к окну"""
    window.configure(fg_color=BG_MAIN)

    # Обновляем цветовую тему CTk
    ctk.set_default_color_theme({
        "CTk": {
            "fg_color": BG_MAIN,
            "text_color": TEXT_DARK,
        },
        "CTkButton": {
            "fg_color": BTN_PRIMARY,
            "hover_color": BTN_PRIMARY_HOVER,
            "text_color": BTN_TEXT,
            "border_color": ACCENT_DARK,
        },
        "CTkEntry": {
            "fg_color": ENTRY_BG,
            "border_color": ENTRY_BORDER,
            "text_color": ENTRY_TEXT,
            "placeholder_text_color": ENTRY_PLACEHOLDER,
        },
        "CTkLabel": {
            "text_color": TEXT_DARK,
        }
    })