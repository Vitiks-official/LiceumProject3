from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests
import asyncio

BOT_TOKEN = "7323990577:AAE7w19-4uVw7wynwPuElE1FNd70LPNHT2A"
ADMIN_GROUP_ID = -4780888054

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def send_product_request_to_admin(api_url):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Принять", callback_data=f"accept>{api_url}")
    keyboard.button(text="❌ Отклонить", callback_data=f"reject")

    product_data = requests.get(api_url).json()["product"]

    message_text = f"Новая заявка на добавление продукта:\n\n"
    message_text += f"Название: {product_data['name']}\n"
    message_text += f"Калории: {product_data.get('calories', '-')}\n"
    message_text += f"Белки: {product_data.get('proteins', '-')}\n"
    message_text += f"Жиры: {product_data.get('fats', '-')}\n"
    message_text += f"Углеводы: {product_data.get('carbohydrates', '-')}"

    await bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=message_text,
        reply_markup=keyboard.as_markup()
    )


@dp.callback_query(lambda c: c.data.startswith("accept"))
async def process_accept(callback_query: types.CallbackQuery):
    api_url = callback_query.data[7:]
    if not api_url:
        print(callback_query.data)
        return

    requests.post(api_url)

    await bot.answer_callback_query(callback_query.id, text=f"Заявка принята!")
    await bot.edit_message_text(
        chat_id=ADMIN_GROUP_ID,
        message_id=callback_query.message.message_id,
        text=f"✅ Заявка принята!\n\n{callback_query.message.text}"
    )


@dp.callback_query(lambda c: c.data.startswith("reject"))
async def process_reject(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, text=f"Заявка отклонена!")
    await bot.edit_message_text(
        chat_id=ADMIN_GROUP_ID,
        message_id=callback_query.message.message_id,
        text=f"❌ Заявка отклонена!\n\n{callback_query.message.text}"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
