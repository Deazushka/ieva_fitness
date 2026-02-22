from telegram import ReplyKeyboardMarkup

# Главное меню
MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🏋️ Начать тренировку"],
        ["📊 История"],
        ["⚙️ Настройки"],
        ["❓ Помощь"],
    ],
    resize_keyboard=True,
)

# Выбор категории
def category_keyboard(categories: list) -> ReplyKeyboardMarkup:
    rows = [categories[i:i+2] for i in range(0, len(categories), 2)]
    keyboard = rows if rows else []
    keyboard.append(["➕ Добавить категорию", "🗑️ Удалить категорию"])
    keyboard.append(["🔙 Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Выбор упражнения
def exercise_keyboard(exercises: list, category_name: str) -> ReplyKeyboardMarkup:
    rows = [exercises[i:i+2] for i in range(0, len(exercises), 2)]
    keyboard = rows if rows else []
    keyboard.append(["➕ Добавить упражнение", "🗑️ Удалить упражнение"])
    keyboard.append(["✅ Завершить тренировку", "❌ Отменить тренировку"])
    keyboard.append(["🔙 Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Детали упражнения
EXERCISE_DETAIL_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["3 x 12", "4 x 10", "5 x 5"],
        ["🔙 Назад"],
    ],
    resize_keyboard=True,
)

# История
def history_keyboard(workouts: list) -> ReplyKeyboardMarkup:
    keyboard = []
    for workout in workouts:
        date = workout["started_at"][:10]
        category = workout["category_name"]
        keyboard.append([f"{date} - {category}"])
    keyboard.append(["🔙 Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Настройки
SETTINGS_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🇷🇺 Русский", "🇬🇧 English"],
        ["⚖️ Кг", "⚖️ Фунты"],
        ["🔙 Назад"],
    ],
    resize_keyboard=True,
)

# Меню удаления категории
def delete_category_keyboard(categories: list) -> ReplyKeyboardMarkup:
    keyboard = [[cat] for cat in categories]
    keyboard.append(["🔙 Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Меню удаления упражнения
def delete_exercise_keyboard(exercises: list) -> ReplyKeyboardMarkup:
    keyboard = [[ex] for ex in exercises]
    keyboard.append(["🔙 Назад"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
