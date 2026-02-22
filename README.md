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

## Запуск

```bash
source venv/bin/activate
python src/bot.py
```

## Использование

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен
3. Добавьте токен в `.env`
4. Запустите бота
5. Отправьте `/start` в Telegram

## Функции

- 🏋️ Начать тренировку
- 📊 История тренировок
- ⚙️ Настройки
- ❓ Помощь
# ieva_fitness
