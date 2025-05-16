import logging
from contextlib import asynccontextmanager

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

    # Конфигурация переменных
    manager_ids = env.list("MANAGER_IDS", subcast=int)
    app.state.manager_ids = manager_ids

    app.state.dincosmet_bot_url = f"http://{env.str('DINCOSMET_BOT_URL')}:{env.int('DINCOSMET_BOT_PORT')}"


async def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    register_routes(app)
    return app
