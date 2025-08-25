import telebot
from telebot import types
import sqlite3
import config
from datetime import datetime
from flask import Flask
import threading


bot = telebot.TeleBot(config.TOKEN)
now = datetime.now()

app = Flask(__name__)


def db_connect():
    conn = sqlite3.connect('bot_database')

    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sites (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, size INTEGER, admin_panel 
    INTEGER DEFAULT 0, funcs TEXT DEFAULT 'NONE', order_link TEXT DEFAULT 'NONE', garant INTEGER DEFAULT 1, is_ready 
    INTEGER DEFAULT 0, garant_date TEXT DEFAULT 'None', price INTEGER DEFAULT 0)
        """)

    cursor.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, full_nam"
                   "e TEXT, message TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, name TEXT"
                   ", rang TEXT)")
    if cursor.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
        cursor.execute("INSERT INTO admins (chat_id, name, rang) VALUES (?, ?, ?)",
                       [config.ADMIN_ID, config.MY_RANG, config.MY_ADMIN_RANG])
    conn.commit()


init_db()


@app.route('/')
def index():
    return "Bot is working!"


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("О Программисте", callback_data='about_programmer')
    btn2 = types.InlineKeyboardButton("Связатся с тех. поддержкой", callback_data='support')
    btn3 = types.InlineKeyboardButton("Купить сайт", callback_data='buy_products')
    btn4 = types.InlineKeyboardButton("Мои заказы", callback_data='my_order')
    btn5 = types.InlineKeyboardButton("Сообщения в Тех. Поддердку", callback_data='reports')
    btn6 = types.InlineKeyboardButton("Простомреть заказы", callback_data='projects')
    if message.chat.id == config.ADMIN_ID:
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    elif message.chat.id != config.ADMIN_ID:
        markup.add(btn1, btn2, btn3, btn4)
    text = f"Здравствуйте {message.from_user.first_name}! Я бот - продавец компании ALS Progs(Official)."
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('about_programmer'))
def about_programmer(call):
    text = (f"О главном программисте {config.MY_RANG}\n\nОпыт работы: 2года\nИспользуемые технологии и языки программир"
            f"ования: Node.js, Express, PostgreSQL, HTML5/EJS, CSS3, JavaScript\n\nРезюме: {config.MY_SITE}\n\nWhatsApp"
            f": https://wa.me/+77078704110")
    bot.send_message(call.message.chat.id, text)


@bot.callback_query_handler(func=lambda call: call.data.startswith('support'))
def support(call):
    text = "Введите сообщение которое хотите отправить в тех.поддержку."
    bot.send_message(call.message.chat.id, text)

    bot.register_next_step_handler(call.message, save_support_message)


def save_support_message(message):
    text = message.text
    bot.send_message(message.chat.id, f"Ваше сообщение успешно отправленно! Текст сообщения:\n{text}\n\nМы объязат"
                                      f"ельно просмотрим ваше сообщение и ответим.")
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reports (chat_id, full_name, message) VALUES(?, ?, ?)
    """, [message.chat.id, f"{message.from_user.first_name} {message.from_user.last_name}", text])
    conn.commit()
    conn.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_product'))
def buy_product(call):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton("Маленький сайт", callback_data='small')
    btn2 = types.InlineKeyboardButton("Средний сайт", callback_data='medium')
    btn3 = types.InlineKeyboardButton("Большой сайт", callback_data='large')
    markup.add(btn1, btn2, btn3)
    text = "Выберите размер сайта:"
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('small'))
def small_size(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("С Админ Панелью", callback_data='with_panel')
    btn2 = types.InlineKeyboardButton("Без Админ Панели", callback_data='no_panel')
    markup.add(btn1, btn2)
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sites (chat_id, size) VALUES (?, ?)", [call.message.chat.id, 1])
    conn.commit()
    text = ("Нужна ли вам админ панель в вашем сайте? Админ панель - панель для управления сайтом и его контентом. Без "
            "неё надо будет доплачивать определённую сумму за каждую правку в сайте.")
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('medium'))
def medium_size(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("С Админ Панелью", callback_data='with_panel')
    btn2 = types.InlineKeyboardButton("Без Админ Панели", callback_data='no_panel')
    markup.add(btn1, btn2)
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sites (chat_id, size) VALUES (?, ?)", [call.message.chat.id, 2])
    conn.commit()
    text = ("Нужна ли вам админ панель в вашем сайте? Админ панель - панель для управления сайтом и его контентом. Без "
            "неё надо будет доплачивать определённую сумму за каждую правку в сайте.")
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('large'))
def large_size(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("С Админ Панелью", callback_data='with_panel')
    btn2 = types.InlineKeyboardButton("Без Админ Панели", callback_data='no_panel')
    markup.add(btn1, btn2)
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sites (chat_id, size) VALUES (?, ?)", [call.message.chat.id, 3])
    conn.commit()
    text = ("Нужна ли вам админ панель в вашем сайте? Админ панель - панель для управления сайтом и его контентом. Без "
            "неё надо будет доплачивать определённую сумму за каждую правку в сайте.")
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('with_panel'))
def with_panel(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("С дополнительными функциями", callback_data='with_funcs')
    btn2 = types.InlineKeyboardButton("Без дополнительных функции", callback_data='no_funcs')
    markup.add(btn1, btn2)
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
    site_id = cursor.fetchone()
    cursor.execute("UPDATE sites SET admin_panel=? WHERE id=?", [int(1), site_id["id"]])
    conn.commit()
    text = "Нужны ли вам дополнительный функции?"
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('no_panel'))
def no_panel(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("С дополнительными функциями", callback_data='with_funcs')
    btn2 = types.InlineKeyboardButton("Без дополнительных функции", callback_data='no_funcs')
    markup.add(btn1, btn2)
    text = "Нужны ли вам дополнительный функции?"
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('no_funcs'))
def no_funcs(call):
    text = ("Теперь отправьте сюда ссылку на макет сайта, если же у вас фотография, загрузите её в облако и отправьте с"
            "юда")
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, save_link)


@bot.callback_query_handler(func=lambda call: call.data.startswith('with_funcs'))
def with_funcs(call):
    text = "Какие функции вы бы хотели добавить в сайт?"
    bot.send_message(call.message.chat.id, text)

    bot.register_next_step_handler(call.message, adding_funcs)


def adding_funcs(message):
    text = message.text

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [message.chat.id])
    id = cursor.fetchone()
    cursor.execute("UPDATE sites SET funcs=? WHERE id=?", [text, id["id"]])
    conn.commit()
    bot.send_message(message.chat.id, f"Функции успешно добавлены в заказ!\nФункции:\n\n{text}\n\nДалее отправьте "
                                      f"ссылку на макет, если у вас фотография загрузите в облако и отправьте ссылку.")
    bot.register_next_step_handler(message, save_link)


def save_link(message):
    text = message.text

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Верно', callback_data='correct_link')
    btn2 = types.InlineKeyboardButton('Нет, ссылка не верна', callback_data='incorrect_link')
    markup.row(btn1, btn2)

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [message.chat.id])
    id = cursor.fetchone()
    cursor.execute("UPDATE sites SET order_link=? WHERE id=?", [text, id["id"]])
    conn.commit()
    bot.send_message(message.chat.id, f"Ссылка на макет: {text} Верно?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('correct_link'))
def correct_link(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("1год гарантии", callback_data='one_year')
    btn2 = types.InlineKeyboardButton("2года гарантии", callback_data='two_year')
    markup.add(btn1, btn2)
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
    order = cursor.fetchall()
    for o in order:
        if o["size"] == 1:
            size = "Маленький"
        elif o["size"] == 2:
            size = "Средний"
        elif o["size"] == 3:
            size = "Большой"
        if o["admin_panel"] == True:
            admin_panel = "Есть"
        elif o["admin_panel"] == False:
            admin_panel = "Нету"
        if o["funcs"] == 'None' or o["funcs"] == None:
            funcs = "Нету"
        else:
            funcs = o["funcs"]
    if now.month in (5, 7, 10):
        if 5 <= now.day <= 25:
            text = (f'Отлично! Сейчас действует сезонная скидка 10%\nВаш сайт:\nРазмер сайта: {size}\nАдмин панель в са'
                    f'йте: {admin_panel}\nДополнительные фукнкции:\n{funcs}\nНа сколько времени вы хотели бы гарантию? '
                    f'\nДоступны варианты такие как: 1год и 2года.')
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
    elif now.month == 12:
        if 10 <= now.day <= 25:
            text = (f"Отлично! Сейчас действует сезонная скидка 25%\nТакже у нас имеются новогодние скидки и если во вр"
                    f"емя нового года использовать купон, вы сэкономите в два раза больше чем в другое время.\nНовогодн"
                    f"яя скидки действуют от 25 декабря до 5 января.\nВаш сайт:\nРазмер сайта: {size}\nАдмин панель в с"
                    f"айте: {admin_panel}\nДополнительные фукнкции:\n{funcs}\nНа сколько времени вы хотели бы гарантию?"
                    f"\nДоступны варианты такие как: 1год и 2года.")
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
    else:
        text = (f"Отлично! \nВаш сайт:\nРазмер сайта: {size}\nАдмин панель в сайте: {admin_panel}\nДополнительные фукнк"
                f"ции:\n{funcs}\nНа сколько времени вы хотели бы гарантию?\nДоступны варианты такие как: 1год и 2года.")
        bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('incorrect_link'))
def incorrect_link(call):
    text = "Тогда отправьте правильную ссылку! Это очень важно для создания сайта!"
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, save_link)


@bot.callback_query_handler(func=lambda call: call.data.startswith('one_year'))
def one_year(call):
    date = f"{now.day}.{now.month}.{now.year}"
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
    cursor.execute("UPDATE sites SET garant_date=? WHERE chat_id=?", [date, call.message.chat.id])
    conn.commit()
    price = cursor.fetchone()
    text = (f'У каждого сайта изначально имеется 1 год гарантии!\nОжидайте ответа '
            f'модерации на ваш заказ. Как только модрация заметит ваш заказ будет на статусе обрабатывается и вам прид'
            f'ёт сообщение!')
    bot.send_message(call.message.chat.id, text)


@bot.callback_query_handler(func=lambda call: call.data.startswith('two_year'))
def two_year(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('Да, я согласен(-на)', callback_data='accept')
    btn2 = types.InlineKeyboardButton('Нет, я не согласен(-на)', callback_data='decline')
    markup.add(btn1, btn2)
    text = ("За дополнительный год гарантии к цене сайта добавляется 10.000тенге, вы согласны? Если нет, у вас будет од"
            "ин год гарантии!")
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('accept'))
def accept(call):
    conn = db_connect()
    cursor = conn.cursor()
    date = f"{now.day}.{now.month}.{now.year}"
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
    id = cursor.fetchone()
    cursor.execute("UPDATE sites SET garant=? WHERE id=?", [2, id["id"]])
    conn.commit()
    cursor.execute("UPDATE sites SET garant_date=? WHERE chat_id=?", [date, call.message.chat.id])
    conn.commit()
    text = (f"У вас теперь гарантия на 2 года! К цене сайта добавилось 10.000тенге.\nЦена вашего сайта: \nДалее ожидай"
            f"те ответа модерации на ваш заказ. Как только модерция заметит у вашего з"
            f"аказа будет статус <b>обрабатывается</b> и вам придёт сообщение об этом.")
    bot.send_message(call.message.chat.id, text)


@bot.callback_query_handler(func=lambda call: call.data.startswith('decline'))
def decline(call):
    conn = db_connect()
    cursor = conn.cursor()
    date = f"{now.day}.{now.month}.{now.year}"
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
    cursor.execute("UPDATE sites SET garant_date=? WHERE chat_id=?", [date, call.message.chat.id])
    conn.commit()
    text = (f"У вас теперь гарантия на 1 год!\n Далее ожидайте ответа модерации на ваш"
            f" заказ. Как только модерция заметит у вашего заказа будет статус <b>обрабатывается</b> и вам придёт сооб"
            f"щение об этом.")
    bot.send_message(call.message.chat.id, text)


def site_price(message):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [message.chat.id])
    order = cursor.fetchall()
    price = 0
    for o in order:
        if o["size"] == 1:
            price += 40000
        elif o["size"] == 2:
            price += 70000
        elif o["size"] == 3:
            price += 130000
        if o["admin_panel"] == True:
            price += 70000
        elif o["admin_panel"] == False:
            price += 0
        if o["garant"] == 1:
            price += 0
        elif o["garant"] == 2:
            price += 10000
        if o["funcs"] == 'None' or o["funcs"] == None:
            price += 0
        if now.month in (5, 7, 10):
            if 5 <= now.day <= 25:
                price100 = price / 100
                price = price100 * 90
        elif now.month == 12:
            if 10 <= now.day <= 25:
                price100 = price / 100
                price = price100 * 75
        else:
            price100 = price / 100
            price = price100 * 100
        cursor.execute("UPDATE sites SET price=? WHERE id=?", [price, o["id"]])
        conn.commit()


@bot.callback_query_handler(func=lambda call: call.data.startswith('projects'))
def projects(call):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
    order = cursor.fetchall()
    for o in order:
        price = 0
        if o["size"] == 1:
            price += 40000
        elif o["size"] == 2:
            price += 70000
        elif o["size"] == 3:
            price += 130000
        if o["admin_panel"] == True:
            price += 70000
        elif o["admin_panel"] == False:
            price += 0
        if o["garant"] == 1:
            price += 0
        elif o["garant"] == 2:
            price += 10000
        if o["funcs"] == 'None' or o["funcs"] == None:
            price += 0
        if now.month in (5, 7, 10):
            if 5 <= now.day <= 25:
                price100 = price / 100
                price = price100 * 90
        elif now.month == 12:
            if 10 <= now.day <= 25:
                price100 = price / 100
                price = price100 * 75
        else:
            price100 = price / 100
            price = price100 * 100
        cursor.execute("UPDATE sites SET price=? WHERE id=?", [price, o["id"]])
        conn.commit()
    text = f"Заказы:"
    bot.send_message(call.message.chat.id, text)
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
    order = cursor.fetchall()
    for o in order:
        id = o["id"]
        chat_id = o["chat_id"]
        price = o["price"]
        garant_date = o["garant_date"]
        if o["size"] == 1:
            size = "Маленький"
        elif o["size"] == 2:
            size = "Средний"
        elif o["size"] == 3:
            size = "Большой"
        if o["admin_panel"] == True:
            admin_panel = "Есть"
        elif o["admin_panel"] == False:
            admin_panel = "Нету"
        if o["garant"] == 1:
            garant = "Гарантия на 1год"
        elif o["garant"] == 2:
            garant = "Гарантия на 2года"
        if o["is_ready"] == 0:
            is_ready = "Ожидает ответа"
            btn_text = "Принять заказ"
            callback_request = f'get_order_{id}'
        elif o["is_ready"] == 1:
            is_ready = "В обработке"
            btn_text = "Окончить заказ"
            callback_request = f'finish_order_{id}'
        elif o["is_ready"] == 2:
            is_ready = "Ожидает оплаты"
            btn_text = "Сдать заказ"
            callback_request = f'pay_order_{id}'
        elif o["is_ready"] == 3:
            is_ready = "Сдан клиенту"
            btn_text = "Получить отзыв"
            callback_request = f'send_congratulations_{id}'
        if o["funcs"] == 'None' or o["funcs"] == None:
            funcs = "Нету"
        else:
            funcs = o["funcs"]
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(btn_text, callback_data=callback_request)
        btn2 = types.InlineKeyboardButton('Оказаться от заказа', callback_data=f"clear_order{id}")
        markup.add(btn1, btn2)
        text = (f"Размер сайта: {size}\nАдмин панель: {admin_panel}\nДополнительные функции:\n{funcs}\n{garant}\nЦена:"
                f" {price}\n\nСтатус: {is_ready}\nChat ID: {chat_id}\nOrder ID: {o["id"]}\nДата покупки: {garant_date}\n\n")
        bot.send_message(call.message.chat.id, text, reply_markup=markup)


conn = db_connect()
cursor = conn.cursor()
cursor.execute("SELECT * FROM sites")
my_orders = cursor.fetchall()
for o in my_orders:
    id = o["id"]
    bot.send_message(config.ADMIN_ID, id)


@bot.callback_query_handler(func=lambda call: call.data.startswith(f'get_order_{id}'))
def get_order(call):
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sites WHERE id=?", [id])
        order_chat = cursor.fetchall()
        for cid in order_chat:
            chat_id = cid["chat_id"]
        text = 'Статус сайта изменён на "В обработке"'
        bot.send_message(call.message.chat.id, text)
        bot.send_message(chat_id, "Ваш заказ был принят разработчиками и он сейчас в работе!")
        cursor.execute("UPDATE sites SET is_ready=? WHERE id=?", [1, id])
        conn.commit()
    except:
        bot.send_message(call.message.chat.id, "Error")


@bot.callback_query_handler(func=lambda call: call.data.startswith(f'finish_order_{id}'))
def finish_order(call):
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sites WHERE id=?", [id])
        order_chat = cursor.fetchall()
        for cid in order_chat:
            chat_id = cid["chat_id"]
        text = 'Статус сайта изменён на "Ожидает оплаты"'
        bot.send_message(call.message.chat.id, text)
        bot.send_message(chat_id, "Ваш заказ готов! Далее ожидается оплата проекта. Обратитесь в тех. поддержку дл"
                                  "я оплаты и получения заказа.")
        cursor.execute("UPDATE sites SET is_ready=? WHERE id=?", [2, id])
        conn.commit()
    except:
        bot.send_message(call.message.chat.id, "Error")


@bot.callback_query_handler(func=lambda call: call.data.startswith(f'pay_order_{id}'))
def pay_order(call):
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sites WHERE id=?", [id])
        order_chat = cursor.fetchall()
        for cid in order_chat:
            chat_id = cid["chat_id"]
        text = 'Статус сайта изменён на "Сдан клиенту"'
        bot.send_message(call.message.chat.id, text)
        bot.send_message(chat_id, f"Ваш сайт был оплачен! Чтобы получить его отправьте это в тех. поддержку: Получ"
                                  f"ение сайта с ID: {id}")
        cursor.execute("UPDATE sites SET is_ready=? WHERE id=?", [3, id])
        conn.commit()
    except:
        bot.send_message(call.message.chat.id, "Error")


@bot.callback_query_handler(func=lambda call: call.data.startswith(f'clear_order{id}'))
def clear_order(call):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sites WHERE id=?", [id])
    conn.commit()
    bot.send_message(call.message.chat.id, "Данный заказ был удалён! Если же это ошибка, обратитесь к клиенту!")
    cursor.execute("INSERT INTO reports (chat_id, message) VALUES (?, ?)", [call.message.chat.id,
                                                                            f"Заказ с ID: {id} был удалён"])


@bot.callback_query_handler(func=lambda call: call.data.startswith('my_order'))
def my_orders(call):
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
        order = cursor.fetchall()
        price = 0
        for o in order:
            if o["size"] == 1:
                price += 40000
            elif o["size"] == 2:
                price += 70000
            elif o["size"] == 3:
                price += 130000
            if o["admin_panel"] == True:
                price += 70000
            elif o["admin_panel"] == False:
                price += 0
            if o["garant"] == 1:
                price += 0
            elif o["garant"] == 2:
                price += 10000
            if o["funcs"] == 'None' or o["funcs"] == None:
                price += 0
            if now.month in (5, 7, 10):
                if 5 <= now.day <= 25:
                    price100 = price / 100
                    price = price100 * 90
            elif now.month == 12:
                if 10 <= now.day <= 25:
                    price100 = price / 100
                    price = price100 * 75
            else:
                price100 = price / 100
                price = price100 * 100
            cursor.execute("UPDATE sites SET price=? WHERE id=?", [price, o["id"]])
            conn.commit()
        cursor.execute("SELECT * FROM sites WHERE chat_id=?", [call.message.chat.id])
        my_orders = cursor.fetchall()
        text = "Ваши заказы:"
        bot.send_message(call.message.chat.id, text)
        if not my_orders:
            bot.send_message(call.message.chat.id, "У вас нету заказов!")
        for s in my_orders:
            garant_date = s["garant_date"]
            id = s["id"]
            price = s["price"]
            if s["size"] == 1:
                size = "Маленький"
            elif s["size"] == 2:
                size = "Средний"
            elif s["size"] == 3:
                size = "Большой"
            if s["admin_panel"] == True:
                admin_panel = "Есть"
            elif s["admin_panel"] == False:
                admin_panel = "Нету"
            if s["garant"] == 1:
                garant = "Гарантия на 1год"
            elif s["garant"] == 2:
                garant = "Гарантия на 2года"
            if s["is_ready"] == 0:
                is_ready = "Ожидает ответа"
            elif s["is_ready"] == 1:
                is_ready = "В обработке"
            elif s["is_ready"] == 2:
                is_ready = "Ожидает оплаты"
            if s["funcs"] == 'None':
                funcs = "Нету"
            else:
                funcs = s["funcs"]
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton(f"Гарантия", callback_data=f'check_{id}')
            btn2 = types.InlineKeyboardButton(f"Отменить", callback_data=f'delete_{id}')
            markup.add(btn1, btn2)
            text = (f"Размер сайта: {size}\nАдмин панель: {admin_panel}\nДополнительные функции:\n{funcs}\n{garant}\nЦена:"
                    f" {price}\n\nСтатус: {is_ready}\nКод заказа: {id}\n\nДата покупки: {garant_date}\n\nДля получения ваше"
                    f"го заказа или же его оплаты отправьте это в тех. поддержку: Оплата/Получение сайта OrderID: {id}")
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Error: {e}")

conn = db_connect()
cursor = conn.cursor()
cursor.execute("SELECT * FROM sites")
my_orders = cursor.fetchall()
for o in my_orders:
    id = o["id"]
    chat_id = o["chat_id"]


@bot.callback_query_handler(func=lambda call: call.data.startswith(f'check_{id}'))
def garant_check_order(call):
    text = "Введите что вы хотите сделать с вашим сайтом, мы обьязательно ответим вам!"
    bot.send_message(call.message.chat.id, text)
    bot.register_next_step_handler(call.message, get_garant_check)


def get_garant_check(message):
    text = f"Сообщение в связи с гарантиеи:\n\n{message.text}\n\n"
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reports (chat_id, message) VALUES (?, ?)", [message.chat.id, text])
    conn.commit()
    bot.send_message(message.chat.id, "Модерация получила ваше сообщение, как только модерация начнёт работать по "
                                      "вашему запросу мы напишем вам!")


@bot.callback_query_handler(func=lambda call: call.data.startswith(f'delete_{id}'))
def delete_order(call):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sites WHERE id=?", [id])
    conn.commit()
    bot.send_message(call.message.chat.id, "Ваш заказ был удалён! Если же это ошибка, обратитесь в тех. "
                                           "поддержку!")
    cursor.execute("INSERT INTO reports (chat_id, message) VALUES (?, ?)", [call.message.chat.id,
                                                                            f"Заказ с ID: {id} был удалён"])


@bot.callback_query_handler(func=lambda call: call.data.startswith('reports'))
def reports(call):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports")
    report = cursor.fetchall()
    text = f'Сообщения полученные пользователями:\n\n'
    if not report:
        bot.send_message(call.message.chat.id, text)
        bot.send_message(call.message.chat.id, "В базе данных нету сообщении!")
        return
    for r in report:
        id = r["id"]
        full_name = r["full_name"]
        message = r["message"]
        chat_id = r["chat_id"]
        text += (f'Сообщение от пользователя {full_name}:\n\n{message}\n\nID чата: {chat_id}\nReport ID: {id}\n\n/suppo'
                 f'rt_message {id} {chat_id}\nСкопируйте и вставьте, далее в конце введит'
                 f'е ваше сообщение\n\n')
    bot.send_message(call.message.chat.id, text)


@bot.message_handler(func=lambda message: '/support_message' in message.text)
def support_func(message):
    if message.chat.id == config.ADMIN_ID:
        args = message.text.split(maxsplit=3)

        if len(args) < 4:
            bot.reply_to(message, "Использование: /support_message <report_id> <user_id> <text>")
            return
        try:
            id = int(args[1])
            user_id = int(args[2])
            reply_text = args[3]
            bot.send_message(user_id, f'Сообщение от администрации:\n\n{reply_text}')
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reports WHERE id=?", [id])
            conn.commit()
            bot.reply_to(message, f"Сообщение успешно отправленно пользователю с ID: {user_id}\nReport ID: {id}")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")
    elif message.chat.id != config.ADMIN_ID:
        bot.send_message(message.chat.id, "Вы не администратор!")


def run_bot():
    print("Бот запущен!")
    bot.infinty_polling()


def run_site():
    print("Server is working!")

    if __name__ == "__main__":
        app.run(host='0.0.0.0', port=8080)

def run_all():
    threading.Thread(target=run_bot).start()
    threading.Thread(target=run_site).start()


threading.Thread(target=run_all).start()
