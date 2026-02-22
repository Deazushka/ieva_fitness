# Telegram Fitness Tracker Bot

Бот для отслеживания тренировок в Telegram.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте токен бота:

```
TELEGRAM_BOT_TOKEN=your_token_here
```

## Локальный запуск (polling)

```bash
source venv/bin/activate
python src/bot_local.py
```

## Деплой на Render (webhook)

1. Залей репозиторий на GitHub
2. Создай **Web Service** на Render
3. Подключи репозиторий
4. Добавь переменные окружения:
   - `TELEGRAM_BOT_TOKEN` — токен бота
   - `RENDER_EXTERNAL_URL` — URL сервиса (например, `https://your-app.onrender.com`)
5. Deploy

## Функции

- 🏋️ Начать тренировку
- 📊 История тренировок
- ⚙️ Настройки
- ❓ Помощь
# ieva_fitness
