
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from config import token
from data import add_rating, get_average_rating, add_review, get_reviews, record_game_play, get_game_stats

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = token

# База игр с Web App URL
GAMES = {
    "wordle": {
        "name": "🔠 Вордли (Wordle)",
        "available": True,
        "web_app_url": "https://Alh1mikk.github.io/tg-game/wordle",
        "description": "Угадайте слово за 6 попыток!",
        "emoji": "🔠"
    },
    "tic-tac-toe": {
        "name": "❌ Крестики-нолики",
        "available": True,
        "web_app_url": "https://Alh1mikk.github.io/tg-game/tic-tac-toe",
        "description": "Классическая игра 3x3",
        "emoji": "❌"
    },
    "snake": {
        "name": "🐍 Змейка",
        "available": True,
        "web_app_url": "https://Alh1mikk.github.io/tg-game/snake",
        "description": "Классическая змейка с яблоками",
        "emoji": "🐍"
    },
    "memory": {
        "name": "🎴 Игра памяти",
        "available": True,
        "web_app_url": "https://Alh1mikk.github.io/tg-game/memory",
        "description": "Найдите все парные карточки",
        "emoji": "🎴"
    },
    "quiz": {
        "name": "🧠 Викторина",
        "available": True,
        "web_app_url": "https://Alh1mikk.github.io/tg-game/quiz",
        "description": "Проверьте свои знания",
        "emoji": "🧠"
    },
    "puzzle": {
        "name": "🧩 Пазл-15",
        "available": True,
        "web_app_url": "https://Alh1mikk.github.io/tg-game/puzzle",
        "description": "Соберите головоломку из 15 элементов",
        "emoji": "🧩"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    keyboard = [
        [InlineKeyboardButton("🎮 Выбрать игру", callback_data="hub")],
        [InlineKeyboardButton("🏆 Топ игр", callback_data="top_games")],
        [InlineKeyboardButton("⭐ Оценить игры", callback_data="rate_games")],
        [InlineKeyboardButton("💬 Отзывы", callback_data="reviews")],
        [InlineKeyboardButton("💰 Поддержать автора", callback_data="support")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = """
🎮 **Добро пожаловать в Хаб Игр!**

✨ **Наши игры:**
• 🔠 Вордли - угадайте слово
• ❌ Крестики-нолики - классика
• 🐍 Змейка - ностальгия
• 🎴 Память - тренируем мозг
• 🧠 Викторина - проверка знаний
• 🧩 Пазл-15 - головоломка

🚀 **Запускаются в один клик!**

⭐ **Оценивайте игры и оставляйте отзывы!**
💰 **Поддержите развитие проекта!**
"""

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_game_hub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать хаб игр"""
    query = update.callback_query
    await query.answer()

    # Создаем кнопки игр в два столбца
    keyboard = []
    row = []
    for i, (game_key, game_info) in enumerate(GAMES.items()):
        status = "✅" if game_info["available"] else "🚧"
        rating = get_average_rating(game_key)
        stars = "⭐" * int(rating) if rating > 0 else "☆"
        button_text = f"{game_info['emoji']} {game_info['name'].split()[-1]} {stars}"
        callback_data = f"game_{game_key}" if game_info["available"] else "dev"

        row.append(InlineKeyboardButton(button_text, callback_data=callback_data))

        # Каждые 2 кнопки - новая строка
        if len(row) == 2 or i == len(GAMES) - 1:
            keyboard.append(row)
            row = []

    # Дополнительные кнопки
    keyboard.extend([
        [InlineKeyboardButton("🏆 Рекомендуемые", callback_data="top_games")],
        [InlineKeyboardButton("⭐ Оценить игры", callback_data="rate_games")],
        [InlineKeyboardButton("💬 Отзывы", callback_data="reviews")],
        [InlineKeyboardButton("🔄 Обновить", callback_data="hub"), InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    hub_text = """
🎯 **Хаб Игр**

Выберите игру для запуска:

🔠 Вордли - угадайте слово
❌ Крест-нол - классика
🐍 Змейка - ретро игра
🎴 Память - тренировка
🧠 Викторина - знания
🧩 Пазл-15 - головоломка

✅ Все игры работают в Telegram!
⭐ Оцените игры и оставьте отзывы!
"""

    await query.edit_message_text(
        hub_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_top_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать рекомендуемые игры"""
    query = update.callback_query
    await query.answer()

    # Получаем статистику игр и сортируем по популярности
    games_stats = []
    for game_key in GAMES:
        if GAMES[game_key]["available"]:
            stats = get_game_stats(game_key)
            rating = get_average_rating(game_key)
            games_stats.append({
                "key": game_key,
                "plays": stats.get("plays", 0),
                "rating": rating
            })

    # Сортируем по количеству игр и рейтингу
    games_stats.sort(key=lambda x: (x["plays"], x["rating"]), reverse=True)
    top_games = [game["key"] for game in games_stats[:3]]

    keyboard = []
    for game_key in top_games:
        if game_key in GAMES and GAMES[game_key]["available"]:
            game_info = GAMES[game_key]
            rating = get_average_rating(game_key)
            stars = "⭐" * int(rating) if rating > 0 else "☆"
            keyboard.append([
                InlineKeyboardButton(
                    f"{stars} {game_info['name']}",
                    callback_data=f"game_{game_key}"
                )
            ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="hub"),
        InlineKeyboardButton("🎮 Все игры", callback_data="hub")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    top_text = """
🏆 **Рекомендуемые игры**

⭐ **Топ-3 для начала:**

🔠 **Вордли** - Захватывающая игра в слова
❌ **Крестики-нолики** - Быстрая классика
🐍 **Змейка** - Ностальгический хит

Выберите игру для старта!
"""

    await query.edit_message_text(
        top_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_game_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора игры"""
    query = update.callback_query
    await query.answer()

    game_key = query.data.replace("game_", "")

    if game_key in GAMES:
        game_info = GAMES[game_key]

        if game_info["available"]:
            # Записываем статистику игры
            record_game_play(game_key)

            # Получаем рейтинг и отзывы
            rating = get_average_rating(game_key)
            stars = "⭐" * int(rating) if rating > 0 else "☆"
            reviews = get_reviews(game_key, limit=2)
            reviews_text = ""
            if reviews:
                reviews_text = "\n\n💬 **Последние отзывы:**\n"
                for review in reviews:
                    reviews_text += f"• {review['text']}\n"

            # Создаем кнопки
            keyboard = [
                [InlineKeyboardButton(
                    "🎮 Играть сейчас",
                    web_app=WebAppInfo(url=game_info["web_app_url"])
                )],
                [InlineKeyboardButton("📋 Как играть?", callback_data=f"desc_{game_key}")],
                [InlineKeyboardButton("⭐ Оценить игру", callback_data=f"rate_{game_key}")],
                [InlineKeyboardButton("💬 Оставить отзыв", callback_data=f"review_{game_key}")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="hub")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"{game_info['emoji']} **{game_info['name']}** {stars}\n\n{game_info['description']}{reviews_text}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await show_development_message(update, context)

async def show_game_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать описание игры"""
    query = update.callback_query
    await query.answer()

    game_key = query.data.replace("desc_", "")
    game_info = GAMES[game_key]

    # Описания правил для каждой игры
    rules = {
        "wordle": """
🔠 **Как играть в Вордли:**

🎯 **Цель:** Угадать слово из 5 букв за 6 попыток

📝 **Правила:**
• Вводите слова из 5 букв
• 🟩 Зеленая - буква на своем месте
• 🟨 Желтая - буква есть в слове, но в другом месте
• ⬜ Серая - буквы нет в слове

💡 **Советы:**
• Начинайте с частых букв
• Используйте подсказки цвета
"""
        ,
        "tic-tac-toe": """
❌ **Как играть в Крестики-нолики:**

🎯 **Цель:** Поставить 3 своих знака в ряд

📝 **Правила:**
• Игроки ходят по очереди
• ❌ - крестики, ⭕ - нолики
• Победа: горизонталь, вертикаль или диагональ
• Ничья при заполненном поле
"""
        ,
        "snake": """
🐍 **Как играть в Змейку:**

🎯 **Цель:** Вырастить змейку как можно длиннее

📝 **Управление:**
• ⬆️ Вверх - влево от сообщения
• ⬇️ Вниз - вправо от сообщения
• ➡️ Вправо - вниз от сообщения
• ⬅️ Влево - вверх от сообщения

🍎 **Собирайте яблоки** для роста
⚠️ **Избегайте** стен и своего хвоста
"""
        ,
        "memory": """
🎴 **Как играть в Память:**

🎯 **Цель:** Найти все парные карточки

📝 **Правила:**
• Открывайте по 2 карточки за ход
• Если совпали - остаются открытыми
• Если нет - переворачиваются обратно
• Запоминайте расположение карточек

🧠 **Тренируйте память** и внимание!
"""
        ,
        "quiz": """
🧠 **Как играть в Викторину:**

🎯 **Цель:** Ответить на максимальное число вопросов

📝 **Правила:**
• Выбирайте из 4 вариантов ответа
• За правильный ответ - +1 балл
• Вопросы из разных категорий
• Уровень сложности растет

📚 **Проверьте** свои знания!
"""
        ,
        "puzzle": """
🧩 **Как играть в Пазл-15:**

🎯 **Цель:** Расставить числа по порядку

📝 **Правила:**
• Перемещайте костяшки кликом
• Используйте пустую клетку
• Соберите числа от 1 до 15
• Чем меньше ходов - тем лучше!

🎲 **Развивайте** логическое мышление
"""
    }

    rule_text = rules.get(game_key, "Правила скоро будут добавлены...")

    keyboard = [
        [InlineKeyboardButton(
            "🎮 Играть сейчас",
            web_app=WebAppInfo(url=game_info["web_app_url"])
        )],
        [InlineKeyboardButton("⭐ Оценить игру", callback_data=f"rate_{game_key}")],
        [InlineKeyboardButton("💬 Оставить отзыв", callback_data=f"review_{game_key}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data=f"game_{game_key}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    description_text = f"""
{game_info['emoji']} **{game_info['name']}**

{rule_text}
"""

    await query.edit_message_text(
        description_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_development_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать сообщение о разработке"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад в хаб", callback_data="hub")],
        [InlineKeyboardButton("🏆 Популярные игры", callback_data="top_games")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    dev_text = """
🚧 **В разработке**

Эта игра скоро появится! Наша команда усердно трудится над ее созданием.

📅 **Следите за обновлениями:**
• Новые игры добавляются регулярно
• Обещаем, что будет интересно!

А пока попробуйте другие наши игры! 🎮
"""

    await query.edit_message_text(
        dev_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать справку"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🎮 В хаб игр", callback_data="hub")],
        [InlineKeyboardButton("🏆 Топ игр", callback_data="top_games")],
        [InlineKeyboardButton("⬅️ Главная", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    help_text = """
❓ **Помощь по играм**

🎮 **Как начать играть:**
1. Нажмите "🎮 Выбрать игру"
2. Выберите понравившуюся игру
3. Нажмите "🎮 Играть сейчас"
4. Игра запустится прямо в Telegram!

📱 **Поддерживаемые платформы:**
• Telegram для Android
• Telegram для iOS
• Telegram Desktop
• Telegram Web

🛠 **Если игра не работает:**
• Обновите приложение Telegram
• Проверьте интернет-соединение
• Перезапустите игру

💾 **Особенности:**
• Все игры бесплатные
• Работают оффлайн
• Автосохранение прогресса
• Оптимизированы для мобильных

⭐ **Рейтинги и отзывы:**
• Оценивайте игры звездами
• Оставляйте отзывы
• Помогайте улучшать проект

💰 **Поддержка проекта:**
• Поддержите автора донатом
• Помогите развивать проект
• Добавлять новые игры

📧 **Поддержка:**
По вопросам пишите: @developer_username
"""

    await query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_rate_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню оценки игр"""
    query = update.callback_query
    await query.answer()

    keyboard = []
    for game_key, game_info in GAMES.items():
        if game_info["available"]:
            rating = get_average_rating(game_key)
            stars = "⭐" * int(rating) if rating > 0 else "☆"
            keyboard.append([
                InlineKeyboardButton(
                    f"{game_info['emoji']} {game_info['name'].split()[-1]} {stars}",
                    callback_data=f"rate_{game_key}"
                )
            ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="hub")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    rate_text = """
⭐ **Оцените игры!**

Ваше мнение очень важно для нас!
Выберите игру, которую хотите оценить:

⭐⭐⭐⭐⭐ - Отлично!
⭐⭐⭐⭐ - Хорошо
⭐⭐⭐ - Нормально
⭐⭐ - Так себе
⭐ - Плохо

После оценки вы сможете оставить отзыв!
"""

    await query.edit_message_text(
        rate_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_game_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню оценки конкретной игры"""
    query = update.callback_query
    await query.answer()

    game_key = query.data.replace("rate_", "")
    game_info = GAMES[game_key]
    current_rating = get_average_rating(game_key)
    stars = "⭐" * int(current_rating) if current_rating > 0 else "☆"

    keyboard = [
        [
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data=f"set_rating_{game_key}_5"),
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data=f"set_rating_{game_key}_4")
        ],
        [
            InlineKeyboardButton("⭐⭐⭐", callback_data=f"set_rating_{game_key}_3"),
            InlineKeyboardButton("⭐⭐", callback_data=f"set_rating_{game_key}_2")
        ],
        [
            InlineKeyboardButton("⭐", callback_data=f"set_rating_{game_key}_1")
        ],
        [
            InlineKeyboardButton("💬 Оставить отзыв", callback_data=f"review_{game_key}")
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="rate_games")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    rating_text = f"""
⭐ **Оцените игру: {game_info['name']}**

Текущий рейтинг: {stars} ({current_rating:.1f}/5)

Пожалуйста, оцените игру:
"""

    await query.edit_message_text(
        rating_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def set_game_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка рейтинга игры"""
    query = update.callback_query
    await query.answer()

    data_parts = query.data.split("_")
    game_key = data_parts[2]
    rating = int(data_parts[3])
    user_id = update.effective_user.id

    # Устанавливаем рейтинг
    new_rating = add_rating(game_key, user_id, rating)
    game_info = GAMES[game_key]
    stars = "⭐" * rating

    keyboard = [
        [InlineKeyboardButton("💬 Оставить отзыв", callback_data=f"review_{game_key}")],
        [InlineKeyboardButton("🎮 Играть", callback_data=f"game_{game_key}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="rate_games")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    thanks_text = f"""
⭐ **Спасибо за вашу оценку!**

Вы поставили игре {game_info['name']} {stars} ({rating}/5)

Новый средний рейтинг: {new_rating:.1f}/5

Хотите оставить отзыв?
"""

    await query.edit_message_text(
        thanks_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать отзывы"""
    query = update.callback_query
    await query.answer()

    keyboard = []
    for game_key, game_info in GAMES.items():
        if game_info["available"]:
            reviews = get_reviews(game_key, limit=1)
            review_count = len(get_reviews(game_key, limit=100))
            keyboard.append([
                InlineKeyboardButton(
                    f"{game_info['emoji']} {game_info['name'].split()[-1]} ({review_count} отзывов)",
                    callback_data=f"game_reviews_{game_key}"
                )
            ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="hub")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    reviews_text = """
💬 **Отзывы игроков**

Читайте и оставляйте отзывы на игры!
Ваше мнение помогает улучшать проект.

Выберите игру для просмотра отзывов:
"""

    await query.edit_message_text(
        reviews_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_game_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать отзывы для конкретной игры"""
    query = update.callback_query
    await query.answer()

    game_key = query.data.replace("game_reviews_", "")
    game_info = GAMES[game_key]
    reviews = get_reviews(game_key, limit=5)
    rating = get_average_rating(game_key)
    stars = "⭐" * int(rating) if rating > 0 else "☆"

    keyboard = [
        [InlineKeyboardButton("💬 Оставить отзыв", callback_data=f"review_{game_key}")],
        [InlineKeyboardButton("⭐ Оценить игру", callback_data=f"rate_{game_key}")],
        [InlineKeyboardButton("🎮 Играть", callback_data=f"game_{game_key}")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="reviews")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if reviews:
        reviews_text = "\n\n💬 **Последние отзывы:**\n"
        for review in reviews:
            reviews_text += f"• {review['text']}\n"
    else:
        reviews_text = "\n\n📝 Отзывов пока нет. Будьте первым!"

    game_reviews_text = f"""
💬 **Отзывы на игру: {game_info['name']}**

Рейтинг: {stars} ({rating:.1f}/5)
{reviews_text}
"""

    await query.edit_message_text(
        game_reviews_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def request_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос отзыва от пользователя"""
    query = update.callback_query
    await query.answer()

    game_key = query.data.replace("review_", "")
    game_info = GAMES[game_key]

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data=f"game_{game_key}")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    review_text = f"""
💬 **Оставьте отзыв на игру {game_info['name']}**

Пожалуйста, напишите ваш отзыв в ответном сообщении.
Ваше мнение очень важно для нас!

Поделитесь впечатлениями, предложениями
или найденными ошибками.
"""

    await query.edit_message_text(
        review_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    # Сохраняем информацию о том, что пользователь оставляет отзыв
    context.user_data['reviewing_game'] = game_key

async def handle_review_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста отзыва"""
    if 'reviewing_game' in context.user_data:
        game_key = context.user_data['reviewing_game']
        game_info = GAMES[game_key]
        user_id = update.effective_user.id
        review_text = update.message.text

        # Добавляем отзыв
        add_review(game_key, user_id, review_text)

        # Очищаем состояние
        del context.user_data['reviewing_game']

        keyboard = [
            [InlineKeyboardButton("🎮 Играть", callback_data=f"game_{game_key}")],
            [InlineKeyboardButton("⭐ Оценить игру", callback_data=f"rate_{game_key}")],
            [InlineKeyboardButton("⬅️ В хаб", callback_data="hub")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        thanks_text = f"""
💬 **Спасибо за ваш отзыв!**

Ваш отзыв на игру {game_info['name']} сохранен.

Мы ценим ваше мнение и учтем его
при дальнейших обновлениях!

Хотите сыграть еще?
"""

        await update.message.reply_text(
            thanks_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать информацию о поддержке проекта"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💳 Поддержать проект", url="https://www.tinkoff.ru/cf/1M8h6M6jJ9o")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="hub")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    support_text = """
💰 **Поддержите проект!**

Разработка и поддержка игр требует времени и ресурсов.
Ваша поддержка поможет:

🎮 Добавлять новые игры
🐛 Исправлять ошибки
✨ Улучшать интерфейс
📱 Адаптировать под разные устройства

Любая сумма важна для нас!
Спасибо за вашу поддержку! ❤️

💳 **Поддержать проект:**
• Тинькофф: ссылка выше
• BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
• ETH: 0x89205A3A3b2A69De6Dbf7F01ED13B2108B2c43e7
"""

    await query.edit_message_text(
        support_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    data = query.data

    if data == "hub":
        await show_game_hub(update, context)
    elif data == "top_games":
        await show_top_games(update, context)
    elif data == "rate_games":
        await show_rate_games(update, context)
    elif data == "reviews":
        await show_reviews(update, context)
    elif data == "support":
        await show_support(update, context)
    elif data == "dev":
        await show_development_message(update, context)
    elif data == "help":
        await show_help(update, context)
    elif data == "start":
        await start(update, context)
    elif data.startswith("game_"):
        await handle_game_selection(update, context)
    elif data.startswith("desc_"):
        await show_game_description(update, context)
    elif data.startswith("rate_") and not data.startswith("set_rating_"):
        await show_game_rating(update, context)
    elif data.startswith("set_rating_"):
        await set_game_rating(update, context)
    elif data.startswith("review_"):
        await request_review(update, context)
    elif data.startswith("game_reviews_"):
        await show_game_reviews(update, context)

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_review_text))

    # Запускаем бота
    print("🎮 Бот 'Хаб Игр' запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
