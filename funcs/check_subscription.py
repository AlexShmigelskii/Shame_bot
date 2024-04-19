from essentials import bot


async def is_subscribed(user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id='@shamemedia', user_id=user_id)
        status = chat_member.status
        return status == 'member'

    except Exception as ex:
        pass
        # Запись ошибки в лог-файл
        with open('error.log', 'a') as f:
            f.write(str(ex) + '\n')
