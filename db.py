# db.py
import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=Электронный магазин;"
    "UID=sa;"
    "PWD=Gtynfujy243@;"
    "TrustServerCertificate=yes;"
)


def get_connection():
    return pyodbc.connect(CONN_STR)


def get_user_by_login(login: str):
    """
    Возвращает:
    ID_пользователя, Логин, Хеш_пароля, Роль,
    ID_Клиент (или None), ID_курьера (или None)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT U.ID_пользователя,
               U.Логин,
               U.Хеш_пароля,
               U.Роль,
               C.ID_Клиент,
               K.ID_курьера
        FROM Пользователь AS U
        LEFT JOIN Клиент AS C
               ON C.ID_пользователя = U.ID_пользователя
        LEFT JOIN Курьер AS K
               ON K.ID_пользователя = U.ID_пользователя
        WHERE U.Логин = ?
        """,
        (login,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def create_default_admin():
    return
