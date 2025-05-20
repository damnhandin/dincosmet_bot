import logging
from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from environs import Env
from fastapi import FastAPI

from app.routes import register_routes

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Загрузка переменных окружения
    load_dotenv()
    env = Env()
    env.read_env(".env")

    # Настройка логики ошибок
    # setup_exception_handlers(app)

    bot_token = env.str("BOT_TOKEN")

    # Конфигурация переменных
    manager_ids = env.list("MANAGER_IDS", subcast=int)
    app.state.manager_ids = manager_ids
    app.state.bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app.state.dincosmet_bot_url = f"http://{env.str('DINCOSMET_BOT_URL')}:{env.int('DINCOSMET_BOT_PORT')}"

    register_routes(app)

    logger.info("Lifespan init completed")
    yield
    logger.info("Lifespan shutdown started")


async def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    return app
