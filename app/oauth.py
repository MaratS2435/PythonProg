import httpx
import requests
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlmodel import select
import logging
from urllib.parse import quote
from app.auth import create_tokens
from app.config import SECRET_KEY, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET, YANDEX_REDIRECT_URL, VK_CLIENT_ID, \
    VK_REDIRECT_URL, VK_CLIENT_SECRET
from app.database import Session, get_session
from app.models import Users, LoginHistory
from .tasks import send_telegram_message

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_yandex_auth_url():
    return (
        "https://oauth.yandex.ru/authorize?"
        "response_type=code&"
        f"client_id={YANDEX_CLIENT_ID}&"
        f"redirect_uri={YANDEX_REDIRECT_URL}"
    )

@router.get("/yandex/")
async def auth_yandex():
    return RedirectResponse(get_yandex_auth_url())

@router.get("/yandex/callback")
async def auth_yandex_callback(code: str, telegram_id: int, resp: Response = None, session: Session = Depends(get_session)):
    # Получение токена
    token_url = "https://oauth.yandex.ru/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": YANDEX_CLIENT_ID,
        "client_secret": YANDEX_CLIENT_SECRET
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
    access_token = response.json()["access_token"]

    # Получение информации о пользователе
    async with httpx.AsyncClient() as client:
        response = await client.get(token_url, params={"format": "json", "oauth_token": access_token})
    user_info = response.json()

    logger.info(user_info)

    query = select(Users).where(Users.email == user_info["default_email"])
    result = await session.execute(query)
    user = result.scalars().first()

    if not user:
        new_user = Users(email=user_info["default_email"], role='user')
        session.add(new_user)
        new_history = LoginHistory(user_id=new_user.id)
        session.add(new_history)
        await session.commit()
        await session.refresh(new_user, new_history)
        role = new_user.role
    else:
        new_history = LoginHistory(user_id=user.id)
        session.add(new_history)
        await session.commit()
        await session.refresh(new_history)
        role = user.role

    send_telegram_message.delay(telegram_id, "Welcome to the app!")

    # Создание JWT
    access_token, refresh_token = create_tokens(user_info["default_email"], role)

    # Установка Refresh Token в httpOnly cookie
    resp.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Только для сервера, недоступен из JavaScript
        secure=False,
        samesite="lax"  # Защита от CSRF
    )

    # Возврат Access Token в теле ответа
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def get_vk_auth_url():
    return (
        "https://oauth.vk.com/authorize?"
        "response_type=code&"
        f"client_id={VK_CLIENT_ID}&"       # Идентификатор вашего приложения VK
        f"redirect_uri={VK_REDIRECT_URL}&"    # URL, куда VK перенаправит пользователя после авторизации
        "display=page&"                      # Вид отображения страницы авторизации
        "scope=email&"        # Перечень прав доступа (настраивайте по необходимости)
    )

@router.get("/vk/")
async def auth_vk():
    return RedirectResponse(get_vk_auth_url())


@router.get("/vk/callback/")
async def vk_callback(code: str, telegram_id: int, resp: Response = None, session: Session = Depends(get_session)):
    token_url = "https://oauth.vk.com/access_token"
    params = {
        "client_id": VK_CLIENT_ID,
        "client_secret": VK_CLIENT_SECRET,
        "redirect_uri": VK_REDIRECT_URL,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(token_url, params=params)
    user_info = response.json()


    query = select(Users).where(Users.email == user_info["email"])
    result = await session.execute(query)
    user = result.scalars().first()

    if not user:
        new_user = Users(email=user_info["default_email"], role='user')
        session.add(new_user)
        new_history = LoginHistory(user_id=new_user.id)
        session.add(new_history)
        await session.commit()
        await session.refresh(new_user, new_history)
        role = new_user.role
    else:
        new_history = LoginHistory(user_id=user.id)
        session.add(new_history)
        await session.commit()
        await session.refresh(new_history)
        role = user.role

    send_telegram_message.delay(telegram_id, "Welcome to the app!")

    access_token, refresh_token = create_tokens(user_info["email"], role)

    # Установка Refresh Token в httpOnly cookie
    resp.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Только для сервера, недоступен из JavaScript
        secure=False,
        samesite="lax"  # Защита от CSRF
    )

    # Возврат Access Token в теле ответа
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
