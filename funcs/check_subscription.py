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


async def is_administrator(user_id):
    try:
        chat_admins = await bot.get_chat_administrators(chat_id='@shamemedia')
        chat_admin_ids = [admin.user.id for admin in chat_admins]
        return user_id in chat_admin_ids

    except Exception as ex:
        pass
        # Запись ошибки в лог-файл
        with open('error.log', 'a') as f:
            f.write(str(ex) + '\n')
