import sqlite3 as sq


def create_db() -> None:
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS commands (
        chat_id INTEGER,
        time TEXT,
        command TEXT,
        location TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS hotels (
        chat_id INTEGER,
        time TEXT,
        name_hotel TEXT,
        address TEXT,
        price TEXT,
        url_hotel TEXT
        )""")


def add_in_commands(chat_id: int, time: str, command: str, location: str) -> None:
    """
    Добавление данных в таблицу БД commands.
    :param chat_id: ID чата с пользователем
    :param time: время запроса
    :param command: команда, которую ввел пользователь
    :param location: место поиска
    """
    insert = "INSERT INTO commands VALUES(?, ?, ?, ?)"
    args = (chat_id, time, command, location)
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute(insert, args)


def add_in_hotels(chat_id: int,
                  time: str,
                  name_hotel: str,
                  address: str,
                  url_hotel: str,
                  price: str) -> None:
    """
    Добавление данных в таблицу БД hotels.
    :param chat_id: ID чата с пользователем
    :param time: время запроса
    :param name_hotel: название отеля
    :param address: адрес отеля
    :param url_hotel: ссылка на отель
    :param price: цены проживания за сутки
    """
    insert = "INSERT INTO hotels VALUES(?, ?, ?, ?, ?, ?)"
    args = (chat_id, time, name_hotel, address, price, url_hotel)
    with sq.connect('database.db') as db:
        cur = db.cursor()
        cur.execute(insert, args)


def data_request(chat_id: int) -> dict:
    """
    SQL-запрос в таблицы БД для вывода истории поиска.
    :param chat_id: ID чата с пользователем
    :return: словарь с ключом: список команд(команда, время, место поиска).
    Значение: список отелей(название, адрес, цена, ссылка)
    """
    res_dict = {}

    req_command = "SELECT time, command, location FROM commands WHERE chat_id=(?) ORDER BY rowid DESC"
    req_hotels = "SELECT name_hotel, address, price, url_hotel FROM hotels WHERE chat_id=(?) AND time=(?)"

    with sq.connect('database.db') as db:
        arg = (chat_id,)
        cur = db.cursor()
        cur.execute(req_command, arg)
        list_commands = cur.fetchmany(5)

        for command in list_commands:
            args = (chat_id, command[0], )
            cur.execute(req_hotels, args)
            res_dict[command] = cur.fetchall()
    return res_dict
