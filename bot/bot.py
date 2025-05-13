import os
import asyncio
import logging
import sqlite3
import requests
import matplotlib.pyplot as plt

from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

from werkzeug.security import check_password_hash


TOKEN = "7755232438:AAHCm49ljNW8XEFw_JiMJugnV3TPZ-zQTcU"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
dp = Dispatcher()


# Главная функция
async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

# Класс для сценариев
class User(StatesGroup):
    user_email = State()
    user_password = State()
    logged = State()
    profile = State()
    edit_profile = State()
    edit_goal = State()
    edit_height = State()
    edit_weight = State()
    edit_age = State()
    edit_lifestyle = State()
    statistics = State()
    add_meal = State()
    article = State()


# Обработчик команды старт
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if not data.get("user_password"):

        await state.set_state(User.user_email)
        await message.reply("Добро пожаловать в Vital Stats!👋\n"
                            "Войдите в свой аккаунт, если же его нет, "
                            "то зарегистируйтесь на сайте Vital Stats. Введите почту:",
                            reply_markup=ReplyKeyboardRemove())
    else:
        await message.reply("Вы уже вошли в аккаунт!")


# Обработчик статуса user_email
@dp.message(User.user_email)
async def input_email(message: types.Message, state: FSMContext):
    data = requests.get("http://127.0.0.1:5000/api/user")
    data = data.json()
    if "@" in message.text:
        if message.text.lower() in [i["email"] for i in data["users"]]:
            await state.update_data(user_email=message.text.lower())
            await state.set_state(User.user_password)
            await message.reply(f"Введите пароль к аккаунту {message.text}\n"
                                f"Или же если вы хотите войти в другой аккаунт введите команду `/back`")
        else:
            await message.reply(f"аккаунта {message.text} не существует❗️\n"
                                f"Проверьте правильность написания почты и попробуйте еще раз❗️")
    else:
        await message.reply("Неверный формат ввода почты❗")


# Обработчик команды back
@dp.message(Command("back"))
async def command_back(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("user_password"):
        await state.set_state(User.user_email)
        await message.reply("Войдите в свой аккаунт, если же его нет,\n"
                            "то зарегистрируйтесь на сайте Vital Stats. Введите почту:")
    else:
        await message.reply("Вы уже вошли в аккаунт!")


# Обработчик статуса user_password
@dp.message(User.user_password)
async def input_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")

    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()
    check_password = cur.execute(f"""SELECT hashed_password FROM user
    WHERE email LIKE '{email}'""").fetchone()[0]
    name = cur.execute(f"""SELECT name FROM user WHERE email LIKE '{email}'""").fetchone()[0]

    if check_password_hash(check_password, message.text):
        await state.update_data(user_password=message.text)
        await state.set_state(User.logged)

        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("menu"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply(f"Успешный вход в аккаунт🎉\n"
                            f"Здравствуйте {name}👋", reply_markup=kb)
    else:
        await message.reply(f"НЕВЕРНЫЙ ПАРОЛЬ❗\n"
                            f"Попробуйте еще раз или можете войти в другой аккаунт: `/back`")
    con.close()


# Функция со всеми Кейбордами
def make_keyboard(mode):
    if mode == "menu":
        return [[KeyboardButton(text="Профиль👤")],
                [KeyboardButton(text="Статистика📊")],
                [KeyboardButton(text="Добавить приём пищи🍔")],
                [KeyboardButton(text="Статьи📃")],
                [KeyboardButton(text="Выйти⛔")]]
    elif mode == "profile":
        return [[KeyboardButton(text="Назад🔙")],
                [KeyboardButton(text="Редактировать✍️")]]
    elif mode == "edit_profile":
        return [[KeyboardButton(text="Цель🎯")],
                [KeyboardButton(text="Рост📏")],
                [KeyboardButton(text="Вес⚖️")],
                [KeyboardButton(text="Возраст🔢")],
                [KeyboardButton(text="Образ жизни🏃‍♂️")],
                [KeyboardButton(text="Назад🔙")]]
    elif mode == "edit_goal":
        return [[KeyboardButton(text="Сбросить вес")],
                [KeyboardButton(text="Поддерживать вес")],
                [KeyboardButton(text="Набрать вес")],
                [KeyboardButton(text="Назад🔙")]]
    elif mode == "only_back":
        return [[KeyboardButton(text="Назад🔙")]]
    elif mode == "edit_lifestyle":
        return [[KeyboardButton(text="Сидячий образ жизни")],
                [KeyboardButton(text="Низкая активность")],
                [KeyboardButton(text="Умеренная активность")],
                [KeyboardButton(text="Высокая активность")],
                [KeyboardButton(text="Очень высокая активность")],
                [KeyboardButton(text="Назад🔙")]]


# Функция для перехода в профиль пользователя
async def go_to_profile(state, message, email):
    text = check_profile(email)
    kb = ReplyKeyboardMarkup(keyboard=make_keyboard("profile"), resize_keyboard=True, one_time_keyboard=False)
    await message.reply(text, reply_markup=kb)
    await state.set_state(User.profile)


# Вывод информации о пользователе
def check_profile(email):
    data = requests.get("http://127.0.0.1:5000/api/user")
    data = data.json()

    stats = [i for i in data["users"] if i["email"] == email][0]
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    name = stats["name"]
    surname = stats["surname"]
    email = stats["email"]
    age = stats["age"]
    gender = cur.execute(f"""SELECT gender FROM gender WHERE id == {stats['gender']}""").fetchone()[0]
    goal = cur.execute(f"""SELECT goal FROM goal WHERE id == {stats['goal']}""").fetchone()[0]
    height = stats["height"]
    weight = stats["weight"]
    is_admin = "Да" if stats["is_admin"] else "Нет"

    con.close()

    return f"""
    -------------------------
👤 Имя: {name} {surname}
📧 Email: {email}
🔢 Возраст: {age} лет
🚻 Пол: {gender}
🎯 Цель: {goal}
📏 Рост: {height} см
⚖️ Вес: {weight} кг
⚙️ Администратор: {is_admin}
-------------------------
"""


# Вывод Статистики пользователя за последний день
async def make_stats(message, state):
    data = await state.get_data()
    email = data.get("user_email")
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    today_stat = cur.execute(f"""SELECT * FROM statistics 
    WHERE user == (SELECT id FROM user 
    WHERE email = '{email}') AND date = '{datetime.today().strftime('%Y-%m-%d')}'""").fetchone()
    if today_stat:
        calories = today_stat[3]
        proteins = today_stat[4]
        fats = today_stat[5]
        carbohydrates = today_stat[6]
    else:
        calories = 0
        proteins = 0
        fats = 0
        carbohydrates = 0
    text = f"""
-------------------------
Калории: {round(calories, 1)} г
Белки: {round(proteins, 1)} г
Жиры: {round(fats, 1)} г
Углеводы: {round(carbohydrates, 1)} г
-------------------------"""

    plt.figure(figsize=(4, 4))
    plt.pie([calories, proteins, fats, carbohydrates],
            labels=["Калории", "Белки", "Жиры", "Углеводы"],
            autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.savefig("img.png")
    plt.close()

    kb = ReplyKeyboardMarkup(keyboard=make_keyboard("only_back"), resize_keyboard=True, one_time_keyboard=False)
    media = MediaGroupBuilder()
    media.add_photo(FSInputFile('img.png'))
    await message.reply_media_group(media=media.build())
    await message.reply(f"📊 Ваша статистика:{text}", reply_markup=kb)
    os.remove("img.png")
    con.close()


# Обработчик статуса logged
@dp.message(User.logged)
async def user_logged(message: types.Message, state: FSMContext):
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()
    data = await state.get_data()
    email = data.get("user_email")

    if message.text == "Профиль👤":
        await go_to_profile(state, message, email)
    elif message.text == "Статистика📊":
        await state.set_state(User.statistics)
        await make_stats(message, state)
    elif message.text == "Добавить приём пищи🍔":
        await state.set_state(User.add_meal)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("only_back"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("Введите название продукта в формате `<название> <вес(г)>`🍕:", reply_markup=kb)
    elif message.text == "Статьи📃":
        await state.set_state(User.article)
        reply_kb = [[KeyboardButton(text="Назад🔙")]]
        for i in cur.execute("""SELECT * FROM article""").fetchall():
            reply_kb.append([KeyboardButton(text=i[1])])
        kb = ReplyKeyboardMarkup(keyboard=reply_kb, resize_keyboard=True, one_time_keyboard=False)
        await message.reply("Приветствуем в разделе статей!\n"
                            "Возможно здесь будет то, что вас заинтересует😉", reply_markup=kb)
    elif message.text == "Выйти⛔":
        await state.clear()
        await message.reply("🔓 Вы вышли из своего профиля.\n"
                            "Для продолжения войдите снова. Введите почту📧:",
                            reply_markup=ReplyKeyboardRemove())
        await state.set_state(User.user_email)
    con.close()


# Обработчик статуса profile
@dp.message(User.profile)
async def profile(message: types.Message, state: FSMContext):
    if message.text == "Назад🔙":
        await state.set_state(User.logged)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("menu"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("Вы вернулись в главное меню🏠", reply_markup=kb)
    elif message.text == "Редактировать✍️":
        await state.set_state(User.edit_profile)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("edit_profile"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("⚙️ Вы перешли в режим редактирования профиля.\n"
                            "Выберите поле, которое хотите обновить.",
                            reply_markup=kb)
    else:
        await message.reply("Я не знаю такой команды😔.\nВыберите из предложенных вариантов")


# Обработчик статуса statistics
@dp.message(User.statistics)
async def statistics(message: types.Message, state: FSMContext):
    if message.text == "Назад🔙":
        await state.set_state(User.logged)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("menu"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("Вы вернулись в главное меню🏠", reply_markup=kb)
    else:
        await message.reply("Я не знаю такой команды😔.\nВыберите из предложенных вариантов")


# Обработчик статуса add_meal
@dp.message(User.add_meal)
async def add_meal(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    if message.text == "Назад🔙":
        await state.set_state(User.logged)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("menu"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("Вы вернулись в главное меню🏠", reply_markup=kb)
    else:
        if len(message.text.split()) == 2 and message.text.split()[1].isdigit():
            if not cur.execute(f"""SELECT * FROM statistics 
            WHERE user = (SELECT id FROM user
            WHERE email = '{email}') AND date = '{datetime.today().strftime('%Y-%m-%d')}'""").fetchone():
                user = cur.execute(f"""SELECT id FROM user WHERE email = '{email}'""").fetchone()[0]
                cur.execute(f"""INSERT INTO statistics(id, user, date, calories, proteins, fats, carbohydrates) VALUES(42, {user}, '{datetime.today().strftime('%Y-%m-%d')}', 0, 0, 0, 0)""")
                con.commit()
            result = cur.execute(f"""SELECT * FROM product
            WHERE name = '{message.text.split()[0]}'""").fetchone()
            if result:
                weight = int(message.text.split()[1]) / 100
                cur.execute(f"""UPDATE statistics 
                SET calories = calories + {weight * result[2]},
                    proteins = proteins + {weight * result[3]},
                    fats = fats + {weight * result[4]},
                    carbohydrates = carbohydrates + {weight * result[5]}
                WHERE user = (SELECT id FROM user
                WHERE email = '{email}') AND date = '{datetime.today().strftime('%Y-%m-%d')}'""")
                con.commit()
                await message.reply("Приём пищи успешно добавлен🎉\n"
                                    "Можете добавить еще или вернуться назад")
            else:
                await message.reply("Такой продукт не найден, проверьте правильность написания "
                                    "\nили добавьте новый продукт на сайте🍎")
        else:
            await message.reply("НЕКОРРЕКТНЫЙ ВВОД ДАННЫХ❗️")
    con.close()


# Обработчик статуса article
@dp.message(User.article)
async def article(message: types.Message, state: FSMContext):
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    if message.text == "Назад🔙":
        await state.set_state(User.logged)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("menu"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("Вы вернулись в главное меню🏠", reply_markup=kb)
    else:
        result = cur.execute(f"""SELECT * FROM article WHERE title == '{message.text}'""").fetchone()
        if result:
            await message.reply(f"{result[1]}\n\n{result[2]}")
        else:
            await message.reply("НЕКОРРЕКТНЫЙ ВВОД! Выберите вариант из предложенных📃")
    con.close()


# Обработчик статуса edit_profile
@dp.message(User.edit_profile)
async def profile(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")

    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    if message.text == "Назад🔙":
        await state.set_state(User.profile)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("profile"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply(check_profile(email), reply_markup=kb)
    elif message.text == "Цель🎯":
        await state.set_state(User.edit_goal)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("edit_goal"), resize_keyboard=True, one_time_keyboard=False)
        goal = cur.execute(f"""SELECT goal FROM goal 
        WHERE id == (SELECT goal FROM user 
        WHERE email == '{email}')""").fetchone()[0]
        await message.reply(f"🔄 Изменение цели диеты. Ваша текущая цель - {goal}. \n"
                            "Какую новую цель вы хотите установить?", reply_markup=kb)
    elif message.text == "Рост📏":
        await state.set_state(User.edit_height)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("only_back"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply(f"Введите свой рост📏:", reply_markup=kb)
    elif message.text == "Вес⚖️":
        await state.set_state(User.edit_weight)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("only_back"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply(f"Введите свой вес:⚖️", reply_markup=kb)
    elif message.text == "Возраст🔢":
        await state.set_state(User.edit_age)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("only_back"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply(f"Введите свой Возраст🔢:", reply_markup=kb)
    elif message.text == "Образ жизни🏃‍♂️":
        await state.set_state(User.edit_lifestyle)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("edit_lifestyle"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply(f"🚶‍♂️ Вы выбрали изменение образа жизни. "
                            f"Выберите из предложенного нужный вариант", reply_markup=kb)
    else:
        await message.reply("Я не знаю такой команды😔.\nВыберите из предложенных вариантов")

    con.close()


# Обработчик статуса edit_goal
@dp.message(User.edit_goal)
async def edit_goal(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    if message.text == "Назад🔙":
        await state.set_state(User.edit_profile)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("edit_profile"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("⚙️ Вы вернулись в режим редактирования профиля.\n"
                            "Выберите поле, которое хотите обновить.", reply_markup=kb)
    elif message.text == "Сбросить вес":
        cur.execute(f"""UPDATE user SET goal = 1 WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    elif message.text == "Поддерживать вес":
        cur.execute(f"""UPDATE user SET goal = 2 WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    elif message.text == "Набрать вес":
        cur.execute(f"""UPDATE user SET goal = 3 WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    else:
        await message.reply("Я не знаю такой команды😔.\nВыберите из предложенных вариантов")
    con.close()


# Обработчик статуса edit_height
@dp.message(User.edit_height)
async def edit_height(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    if message.text == "Назад🔙":
        await state.set_state(User.edit_profile)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("edit_profile"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("⚙️ Вы вернулись в режим редактирования профиля.\n"
                            "Выберите поле, которое хотите обновить.", reply_markup=kb)
    elif message.text.isdigit() and  50 <= int(message.text)<= 300:
        cur.execute(f"""UPDATE user SET height = {int(message.text)} WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    else:
        await message.reply("Значение роста должно находится от 50 до 300❗️")
    con.close()


# Обработчик статуса edit_weight
@dp.message(User.edit_weight)
async def edit_weight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    if message.text == "Назад🔙":
        await state.set_state(User.edit_profile)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("edit_profile"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("⚙️ Вы вернулись в режим редактирования профиля.\n"
                            "Выберите поле, которое хотите обновить.", reply_markup=kb)
    elif message.text.isdigit() and 10 <= int(message.text) <= 600:
        cur.execute(f"""UPDATE user SET weight = {int(message.text)} WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    else:
        await message.reply("Значение веса должно находится от 10 до 600❗️")
    con.close()


# Обработчик статуса edit_age
@dp.message(User.edit_age)
async def edit_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    if message.text == "Назад🔙":
        await state.set_state(User.edit_profile)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("edit_profile"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("⚙️ Вы вернулись в режим редактирования профиля.\n"
                            "Выберите поле, которое хотите обновить.", reply_markup=kb)
    elif message.text.isdigit() and 5 <= int(message.text) <= 200:
        cur.execute(f"""UPDATE user SET age = {int(message.text)} WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    else:
        await message.reply("Возраст должен быть от 5 до 200 лет❗ ️")
    con.close()


# Обработчик статуса edit_lifestyle
@dp.message(User.edit_lifestyle)
async def edit_lifestyle(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("user_email")
    con = sqlite3.connect("../db/calorie_tracker.db")
    cur = con.cursor()

    if message.text == "Назад🔙":
        await state.set_state(User.edit_profile)
        kb = ReplyKeyboardMarkup(keyboard=make_keyboard("edit_profile"), resize_keyboard=True, one_time_keyboard=False)
        await message.reply("⚙️ Вы вернулись в режим редактирования профиля.\n"
                            "Выберите поле, которое хотите обновить.", reply_markup=kb)
    elif message.text == "Сидячий образ жизни":
        cur.execute(f"""UPDATE user SET lifestyle = 1 WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    elif message.text == "Низкая активность":
        cur.execute(f"""UPDATE user SET lifestyle = 2 WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    elif message.text == "Умеренная активность":
        cur.execute(f"""UPDATE user SET lifestyle = 3 WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    elif message.text == "Высокая активность":
        cur.execute(f"""UPDATE user SET lifestyle = 4 WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    elif message.text == "Очень высокая активность":
        cur.execute(f"""UPDATE user SET lifestyle = 5 WHERE email == '{email}'""")
        con.commit()
        await go_to_profile(state, message, email)
    else:
        await message.reply("Я не знаю такой команды😔.\nВыберите из предложенных вариантов")
    con.close()


if __name__ == '__main__':
    asyncio.run(main())


