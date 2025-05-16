from fastapi import FastAPI
from pydantic import BaseModel

from bot.bot import send_to_managers


class Lead(BaseModel):
    name: str
    phone: str

def register_routes(app: FastAPI):
    bot = app.state.bot

    @app.post("/submit")
    async def submit_lead(lead: Lead):
        await send_to_managers(lead.name, lead.phone, bot=bot)
        return {"status": "ok"}

