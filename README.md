# PythonProg
Выполнил Сисенов Марат М8О-310Б-22

## Подготовка к запуску
Если вы использовали PostgreSQL и RabbitMQ со стандартными настройками, то ничего настраивать не придется.\
Если нет, то перед началом настройте файл .env со следующим содержимым:
```
# .env
DATABASE_URL=your_database_url
BROKER_URL=your_broker_url

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

YANDEX_CLIENT_ID=your_yandex_client_id
YANDEX_CLIENT_SECRET=your_yandex_client_secret
YANDEX_REDIRECT_URL=https://oauth.yandex.ru/verification_code

VK_CLIENT_ID=your_vk_client_id
VK_CLIENT_SECRET=your_vk_client_secret
VK_SERVICE_SECRET=your_vk_service_secret
VK_REDIRECT_URL=https://oauth.vk.com/blank.html

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```
Если вы использовали PostgreSQL и RabbitMQ со стандартными настройками, то ничего настраивать не придется.

### Установите зависимости
```
pip install -r requirements.txt
```

### Запустите базу данных и брокер
Я использовал PostgreSQL и RabbitMQ.\
RabbitMQ использовался для Celery одновременно как брокер и как бэкенд.

## Запустите приложение
В разных консолях
```
celery -A app.tasks worker --loglevel=info --pool=solo #для Windows
celery -A app.tasks worker --loglevel=info #для Linux
uvicorn app.main:app --reload
```

## Телеграм бот
Телеграм боты не могут писать сообщения первыми. Вам нужно запустить бот самому, чтобы он мог отправлять сообщения.\
Сам бот - @PythonAuthBot.\
Для использования ручек понадобится id вашего телеграм аккаунта. Узнать его можно через этого бота - @getmyid_bot.

## Авторизация через сервисы: Yandex, VK
Из-за того, что используется локальный сервер, авторизация работает через 2 ручки для каждого сервиса.\
Yandex - /auth/yandex/, Здесь вы получаете код, который вписываете в поле в ручку /auth/yandex/callback/.\
VK - /auth/vk/, Код находится в ссылке, его вы вписываете в поле в ручку /auth/vk/callback/.