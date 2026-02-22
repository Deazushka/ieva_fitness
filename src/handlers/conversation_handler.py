from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import sys
sys.path.insert(0, "/Users/aliaksandr/IdeaProjects/MyTraningProjectAqa/myfavoritestask/new_version_tg_bot/src")

from database import (
    init_db,
    get_categories,
    get_exercises_for_category,
    get_or_create_category,
    get_or_create_exercise,
    delete_category,
    delete_exercise,
    create_workout,
    get_active_workout,
    add_workout_exercise,
    get_workout_exercises,
    finish_workout,
    cancel_workout,
    get_user_workouts,
    get_workout_by_id,
)
from keyboards import (
    MAIN_MENU_KEYBOARD,
    category_keyboard,
    exercise_keyboard,
    EXERCISE_DETAIL_KEYBOARD,
    history_keyboard,
    SETTINGS_KEYBOARD,
    delete_category_keyboard,
    delete_exercise_keyboard,
)

# States
(
    MAIN_MENU,
    CATEGORY_SELECT,
    EXERCISE_SELECT,
    EXERCISE_DETAIL,
    ADD_CATEGORY,
    DELETE_CATEGORY,
    ADD_EXERCISE,
    DELETE_EXERCISE,
    HISTORY_MENU,
    HISTORY_DETAIL,
    SETTINGS_MENU,
    HELP,
) = range(12)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🏋️ Добро пожаловать, {user.first_name}!\nВыберите действие:",
        reply_markup=MAIN_MENU_KEYBOARD,
    )
    return MAIN_MENU


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🏋️ Начать тренировку":
        # Проверяем активную тренировку
        user_id = update.effective_user.id
        active = get_active_workout(user_id)
        if active:
            await update.message.reply_text(
                "⚠️ У вас уже есть активная тренировка!\nЗавершите или отмените её.",
                reply_markup=exercise_keyboard(
                    get_exercises_for_category(active["category_name"]),
                    active["category_name"],
                ),
            )
            context.user_data["active_workout"] = active
            return EXERCISE_SELECT
        else:
            categories = get_categories()
            if not categories:
                await update.message.reply_text(
                    "📋 Категорий пока нет.\nСначала добавьте категорию.",
                    reply_markup=category_keyboard([]),
                )
                return ADD_CATEGORY
            await update.message.reply_text(
                "📋 Выберите категорию тренировки:",
                reply_markup=category_keyboard(categories),
            )
            return CATEGORY_SELECT

    elif text == "📊 История":
        user_id = update.effective_user.id
        workouts = get_user_workouts(user_id)
        if not workouts:
            await update.message.reply_text(
                "📊 История пуста.\nНачните свою первую тренировку!",
                reply_markup=MAIN_MENU_KEYBOARD,
            )
            return MAIN_MENU
        await update.message.reply_text(
            "📊 История тренировок:",
            reply_markup=history_keyboard(workouts),
        )
        return HISTORY_MENU

    elif text == "⚙️ Настройки":
        await update.message.reply_text(
            "⚙️ Настройки",
            reply_markup=SETTINGS_KEYBOARD,
        )
        return SETTINGS_MENU

    elif text == "❓ Помощь":
        await update.message.reply_text(
            "❓ Помощь\n\n"
            "1. Нажмите 'Начать тренировку'\n"
            "2. Выберите категорию (день ног, день рук и т.д.)\n"
            "3. Выберите упражнение\n"
            "4. Введите подходы в формате: 3 12 или 4 10 50\n"
            "   (подходы повторения [вес])\n"
            "5. Добавьте несколько упражнений\n"
            "6. Нажмите 'Завершить тренировку'\n\n"
            "Кнопка '🔙 Назад' возвращает на предыдущий экран.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    return MAIN_MENU


async def category_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🔙 Назад":
        await update.message.reply_text(
            "🏋️ Добро пожаловать!\nВыберите действие:",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    elif text == "➕ Добавить категорию":
        await update.message.reply_text(
            "Введите название новой категории:",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return ADD_CATEGORY

    elif text == "🗑️ Удалить категорию":
        categories = get_categories()
        if not categories:
            await update.message.reply_text(
                "Нет категорий для удаления.",
                reply_markup=category_keyboard([]),
            )
            return CATEGORY_SELECT
        await update.message.reply_text(
            "Выберите категорию для удаления:",
            reply_markup=delete_category_keyboard(categories),
        )
        return DELETE_CATEGORY

    else:
        # Выбор категории
        categories = get_categories()
        if text in categories:
            # Создаём новую тренировку
            workout = create_workout(user_id, text)
            context.user_data["active_workout"] = {"id": workout, "category_name": text}
            exercises = get_exercises_for_category(text)
            await update.message.reply_text(
                f"💪 Категория: {text}\nВыберите упражнение:",
                reply_markup=exercise_keyboard(exercises, text),
            )
            return EXERCISE_SELECT
        else:
            await update.message.reply_text(
                "📋 Выберите категорию тренировки:",
                reply_markup=category_keyboard(get_categories()),
            )
            return CATEGORY_SELECT


async def add_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    get_or_create_category(name)
    await update.message.reply_text(
        f"✅ Категория '{name}' добавлена!",
        reply_markup=category_keyboard(get_categories()),
    )
    return CATEGORY_SELECT


async def delete_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    delete_category(name)
    await update.message.reply_text(
        f"🗑️ Категория '{name}' удалена!",
        reply_markup=category_keyboard(get_categories()),
    )
    return CATEGORY_SELECT


async def exercise_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    active_workout = context.user_data.get("active_workout")

    if not active_workout:
        await update.message.reply_text(
            "⚠️ Активная тренировка не найдена.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    if text == "🔙 Назад":
        categories = get_categories()
        await update.message.reply_text(
            "📋 Выберите категорию тренировки:",
            reply_markup=category_keyboard(categories),
        )
        return CATEGORY_SELECT

    elif text == "➕ Добавить упражнение":
        await update.message.reply_text(
            "Введите название нового упражнения:",
            reply_markup=exercise_keyboard(
                get_exercises_for_category(active_workout["category_name"]),
                active_workout["category_name"],
            ),
        )
        return ADD_EXERCISE

    elif text == "🗑️ Удалить упражнение":
        exercises = get_exercises_for_category(active_workout["category_name"])
        if not exercises:
            await update.message.reply_text(
                "Нет упражнений для удаления.",
                reply_markup=exercise_keyboard(exercises, active_workout["category_name"]),
            )
            return EXERCISE_SELECT
        await update.message.reply_text(
            "Выберите упражнение для удаления:",
            reply_markup=delete_exercise_keyboard(exercises),
        )
        return DELETE_EXERCISE

    elif text == "✅ Завершить тренировку":
        workout_id = active_workout["id"]
        exercises = get_workout_exercises(workout_id)

        summary = "✅ Тренировка завершена\n\n"
        summary += f"Категория: {active_workout['category_name']}\n"
        summary += f"Упражнений: {len(exercises)}\n\n"

        if exercises:
            for ex in exercises:
                weight_str = f" ({ex['weight']} кг)" if ex['weight'] else ""
                summary += f"• {ex['exercise_name']} — {ex['sets']}x{ex['reps']}{weight_str}\n"
        else:
            summary += "Нет выполненных упражнений."

        finish_workout(workout_id)
        context.user_data.pop("active_workout", None)

        await update.message.reply_text(
            summary,
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    elif text == "❌ Отменить тренировку":
        workout_id = active_workout["id"]
        cancel_workout(workout_id)
        context.user_data.pop("active_workout", None)

        await update.message.reply_text(
            "❌ Тренировка отменена.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    else:
        # Выбор упражнения
        exercises = get_exercises_for_category(active_workout["category_name"])
        if text in exercises or text in ["3 x 12", "4 x 10", "5 x 5"]:
            context.user_data["selected_exercise"] = text
            await update.message.reply_text(
                f"💪 {text}\n\nВведите подходы:\n\n"
                "Формат: подходы повторения [вес]\n\n"
                "Примеры:\n3 12\n4 10 50",
                reply_markup=EXERCISE_DETAIL_KEYBOARD,
            )
            return EXERCISE_DETAIL
        else:
            await update.message.reply_text(
                f"💪 Категория: {active_workout['category_name']}\nВыберите упражнение:",
                reply_markup=exercise_keyboard(
                    get_exercises_for_category(active_workout["category_name"]),
                    active_workout["category_name"],
                ),
            )
            return EXERCISE_SELECT


async def add_exercise_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    active_workout = context.user_data.get("active_workout")

    if not active_workout:
        await update.message.reply_text(
            "⚠️ Активная тренировка не найдена.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    get_or_create_exercise(name, active_workout["category_name"])
    exercises = get_exercises_for_category(active_workout["category_name"])

    await update.message.reply_text(
        f"✅ Упражнение '{name}' добавлено!",
        reply_markup=exercise_keyboard(exercises, active_workout["category_name"]),
    )
    return EXERCISE_SELECT


async def delete_exercise_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    active_workout = context.user_data.get("active_workout")

    if not active_workout:
        await update.message.reply_text(
            "⚠️ Активная тренировка не найдена.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    delete_exercise(name, active_workout["category_name"])
    exercises = get_exercises_for_category(active_workout["category_name"])

    await update.message.reply_text(
        f"🗑️ Упражнение '{name}' удалено!",
        reply_markup=exercise_keyboard(exercises, active_workout["category_name"]),
    )
    return EXERCISE_SELECT


async def exercise_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    active_workout = context.user_data.get("active_workout")

    if not active_workout:
        await update.message.reply_text(
            "⚠️ Активная тренировка не найдена.",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    if text == "🔙 Назад":
        exercises = get_exercises_for_category(active_workout["category_name"])
        await update.message.reply_text(
            f"💪 Категория: {active_workout['category_name']}\nВыберите упражнение:",
            reply_markup=exercise_keyboard(exercises, active_workout["category_name"]),
        )
        return EXERCISE_SELECT

    # Обработка пресетов
    if text in ["3 x 12", "4 x 10", "5 x 5"]:
        parts = text.split(" x ")
        sets = int(parts[0])
        reps = int(parts[1])
        exercise_name = context.user_data.get("selected_exercise", "Неизвестное")

        add_workout_exercise(active_workout["id"], exercise_name, sets, reps, None)

        exercises = get_exercises_for_category(active_workout["category_name"])
        await update.message.reply_text(
            f"✅ Добавлено: {exercise_name} — {sets}x{reps}",
            reply_markup=exercise_keyboard(exercises, active_workout["category_name"]),
        )
        return EXERCISE_SELECT

    # Обработка ввода пользователя
    parts = text.strip().split()
    if len(parts) >= 2:
        try:
            sets = int(parts[0])
            reps = int(parts[1])
            weight = float(parts[2]) if len(parts) > 2 else None
            exercise_name = context.user_data.get("selected_exercise", "Неизвестное")

            add_workout_exercise(active_workout["id"], exercise_name, sets, reps, weight)

            exercises = get_exercises_for_category(active_workout["category_name"])
            weight_str = f" ({weight} кг)" if weight else ""
            await update.message.reply_text(
                f"✅ Добавлено: {exercise_name} — {sets}x{reps}{weight_str}",
                reply_markup=exercise_keyboard(exercises, active_workout["category_name"]),
            )
            return EXERCISE_SELECT
        except ValueError:
            await update.message.reply_text(
                "❌ Неверный формат.\nПример: 3 12 или 4 10 50",
                reply_markup=EXERCISE_DETAIL_KEYBOARD,
            )
            return EXERCISE_DETAIL
    else:
        await update.message.reply_text(
            "❌ Неверный формат.\nПример: 3 12 или 4 10 50",
            reply_markup=EXERCISE_DETAIL_KEYBOARD,
        )
        return EXERCISE_DETAIL


async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🔙 Назад":
        await update.message.reply_text(
            "🏋️ Добро пожаловать!\nВыберите действие:",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    # Выбор тренировки из истории
    workouts = get_user_workouts(user_id)
    for workout in workouts:
        date = workout["started_at"][:10]
        label = f"{date} - {workout['category_name']}"
        if text == label:
            exercises = get_workout_exercises(workout["id"])
            summary = f"📋 Тренировка {date}\n"
            summary += f"Категория: {workout['category_name']}\n\n"

            if exercises:
                for ex in exercises:
                    weight_str = f" ({ex['weight']} кг)" if ex['weight'] else ""
                    summary += f"• {ex['exercise_name']} — {ex['sets']}x{ex['reps']}{weight_str}\n"
            else:
                summary += "Нет упражнений."

            await update.message.reply_text(
                summary,
                reply_markup=history_keyboard(workouts),
            )
            return HISTORY_MENU

    return HISTORY_MENU


async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔙 Назад":
        await update.message.reply_text(
            "🏋️ Добро пожаловать!\nВыберите действие:",
            reply_markup=MAIN_MENU_KEYBOARD,
        )
        return MAIN_MENU

    elif text in ["🇷🇺 Русский", "🇬🇧 English", "⚖️ Кг", "⚖️ Фунты"]:
        await update.message.reply_text(
            f"✅ {text} выбрано.\n(Функция в разработке)",
            reply_markup=SETTINGS_KEYBOARD,
        )
        return SETTINGS_MENU

    return SETTINGS_MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("active_workout", None)
    await update.message.reply_text(
        "🏋️ Добро пожаловать!\nВыберите действие:",
        reply_markup=MAIN_MENU_KEYBOARD,
    )
    return MAIN_MENU


def create_conv_handler() -> ConversationHandler:
    init_db()

    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler),
            ],
            CATEGORY_SELECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, category_select_handler),
            ],
            EXERCISE_SELECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, exercise_select_handler),
            ],
            EXERCISE_DETAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, exercise_detail_handler),
            ],
            ADD_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_handler),
            ],
            DELETE_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_category_handler),
            ],
            ADD_EXERCISE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_exercise_handler),
            ],
            DELETE_EXERCISE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_exercise_handler),
            ],
            HISTORY_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, history_handler),
            ],
            SETTINGS_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, settings_handler),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
