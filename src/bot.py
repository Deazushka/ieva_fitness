import logging
import os
import sys
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler

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


def main():
    # Получение токена
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        return

    # Получение URL из переменных окружения (Render)
    base_url = os.getenv("RENDER_EXTERNAL_URL")
    if not base_url:
        logger.error("RENDER_EXTERNAL_URL не найден. Убедитесь, что сервис запущен на Render.")
        return

    # Создание приложения
    application = Application.builder().token(token).build()

    # Добавление обработчика разговора
    conv_handler = create_conv_handler()
    application.add_handler(conv_handler)

    # Настройка webhook
    webhook_url = f"{base_url}/webhook/{token.split(':')[0]}"
    
    async def post_init(app):
        await app.bot.set_webhook(webhook_url)
        logger.info(f"Webhook установлен: {webhook_url}")

    async def post_shutdown(app):
        await app.bot.delete_webhook()
        logger.info("Webhook удалён")

    application.post_init = post_init
    application.post_shutdown = post_shutdown

    # Запуск веб-сервера
    logger.info("Бот запущен в режиме webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        webhook_url=webhook_url,
    )


if __name__ == "__main__":
    main()
