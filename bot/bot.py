from typing import List

from aiogram import Bot


async def send_to_managers(name: str, phone: str, bot: Bot):
    if not hasattr(bot, "manager_ids"):
        return
    text = f"📥 <b>Новая заявка</b>\n👤 Имя: {name}\n📞 Телефон: {phone}"
    for manager_id in bot.manager_ids:
        try:
            await bot.send_message(manager_id, text)
        except Exception as e:
            print(f"❌ Ошибка отправки менеджеру {manager_id}: {e}")
