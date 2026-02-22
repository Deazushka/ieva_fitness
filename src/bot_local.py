import logging
import os
import sys
import asyncio
from dotenv import load_dotenv

from telegram.ext import Application

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from handlers import create_conv_handler

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def run_bot():
    # Получение токена
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        return

    # Создание приложения
    application = Application.builder().token(token).build()

    # Добавление обработчика разговора
    conv_handler = create_conv_handler()
    application.add_handler(conv_handler)

    # Запуск бота (polling для локальной разработки)
    logger.info("Бот запущен в режиме polling...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=["message", "callback_query"])

    # Держим бота запущенным
    while True:
        await asyncio.sleep(1)


def main():
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
