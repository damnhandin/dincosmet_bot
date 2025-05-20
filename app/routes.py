import logging

from fastapi import FastAPI
from fastapi import Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from bot.bot import send_to_managers

logger = logging.getLogger(__name__)


class Lead(BaseModel):
    name: str
    phone: str


# Функция получения IP из заголовка или request.client
def get_real_ip(request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        logger.info(x_forwarded_for)
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

    @limiter.limit("3/5minutes")
    @app.post("/submit")
    async def submit_lead(lead: Lead, request: Request):
        client_ip = get_real_ip(request)
        logger.info(f"Заявка от {client_ip}: {lead.name} / {lead.phone}")
        await send_to_managers(lead.name, lead.phone, bot=bot, manager_ids=manager_ids)
        return {"status": "ok"}