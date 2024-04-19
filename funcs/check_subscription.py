from essentials import bot
import logging

# Настройка конфигурации логгера
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


async def is_subscribed(user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id='@shamemedia', user_id=user_id)
        status = chat_member.status
        return status == 'member'

    except Exception as ex:
        # Запись ошибки в лог-файл
        logging.error(f'Ошибка при выполнении функции is_subscribed: {ex}')
