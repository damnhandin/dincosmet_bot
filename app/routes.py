import logging

from fastapi import FastAPI, HTTPException
from fastapi import Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from bot.bot import send_to_managers

logger = logging.getLogger(__name__)


class Lead(BaseModel):
    name: str
    phone: str


# Функция получения IP из заголовка или request.client
def get_real_ip(request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.client.host


def register_routes(app: FastAPI):
    limiter = Limiter(key_func=get_real_ip)

    app.state.limiter = limiter

    app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
        status_code=429,
        content={"error": "Слишком много заявок. Попробуйте позже."}
    ))

    bot = app.state.bot
    manager_ids = app.state.manager_ids

    @app.post("/submit")
    @limiter.limit("3/5minutes")
    async def submit_lead(lead: Lead, request: Request):
        client_ip = get_real_ip(request)
        for id in manager_ids:
            await bot.send_message(chat_id=id, text=f"{len(lead.phone)}")
        # 🔐 Базовая ручная проверка на случай обхода валидации
        if not lead.name.strip() or len(lead.phone) <= 12:
            logger.warning(f"[{client_ip}] ❌ Некорректные данные: name='{lead.name}' phone='{lead.phone}'")
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid data"
            )

        logger.info(f"[{client_ip}] 📩 Заявка: {lead.name} / {lead.phone}")

        try:
            await send_to_managers(lead.name, lead.phone, bot=bot, manager_ids=manager_ids)
        except Exception as e:
            logger.error(f"[{client_ip}] ❗ Ошибка при отправке заявки: {e}")
            raise HTTPException(status_code=500, detail="Failed to process request")

        return {"status": "ok"}