
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from config import token
from data import add_rating, get_average_rating, add_review, get_reviews, record_game_play, get_game_stats
from ratings import update_player_rating, get_top_players, get_player_rating

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
        [InlineKeyboardButton("🥇 Рейтинг игроков", callback_data="ratings")],
        [InlineKeyboardButton("📊 Мой рейтинг", callback_data="my_rating")],
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
            
            # Получаем информацию о пользователе
            user_id = update.effective_user.id
            username = update.effective_user.username or update.effective_user.first_name or "Аноним"
            
            # Сохраняем информацию о текущей игре для обновления рейтинга
            context.user_data["current_game"] = game_key
            context.user_data["game_start_time"] = datetime.now().isoformat()

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

async def show_ratings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать рейтинг игроков"""
    query = update.callback_query
    await query.answer()
    
    # Получаем топ-10 игроков по общему счету
    top_players = get_top_players(limit=10)
    
    if not top_players:
        ratings_text = "🏆 **Рейтинг игроков**\n\nПока нет игроков в рейтинге. Станьте первым!"
    else:
        ratings_text = "🏆 **Топ-10 игроков**\n\n"
        
        for i, player in enumerate(top_players, 1):
            # Добавляем медаль для первых трех мест
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "
            
            ratings_text += f"{medal}{i}. {player['username']} - {player['score']} очков\n"
    
    keyboard = [
        [InlineKeyboardButton("🎮 Игры", callback_data="hub")],
        [InlineKeyboardButton("🏆 Рейтинг по играм", callback_data="ratings_by_games")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        ratings_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_ratings_by_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать рейтинг игроков по конкретным играм"""
    query = update.callback_query
    await query.answer()
    
    # Создаем клавиатуру с выбором игр
    keyboard = []
    for game_key, game_info in GAMES.items():
        keyboard.append([InlineKeyboardButton(
            f"{game_info['emoji']} {game_info['name'].split()[-1]}",
            callback_data=f"rating_{game_key}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="ratings")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    ratings_text = """
🏆 **Рейтинг по играм**

Выберите игру, чтобы посмотреть рейтинг игроков:
"""
    
    await query.edit_message_text(
        ratings_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_game_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать рейтинг для конкретной игры"""
    query = update.callback_query
    await query.answer()
    
    game_key = query.data.replace("rating_", "")
    game_info = GAMES[game_key]
    
    # Получаем топ-10 игроков для этой игры
    top_players = get_top_players(limit=10, game=game_key)
    
    if not top_players:
        ratings_text = f"🏆 **Рейтинг: {game_info['name']}**\n\nПока нет игроков в рейтинге. Станьте первым!"
    else:
        ratings_text = f"🏆 **Топ-10 игроков: {game_info['name']}**\n\n"
        
        for i, player in enumerate(top_players, 1):
            # Добавляем медаль для первых трех мест
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "
            
            ratings_text += f"{medal}{i}. {player['username']} - {player['score']} очков\n"
    
    keyboard = [
        [InlineKeyboardButton("🎮 Играть", callback_data=f"game_{game_key}")],
        [InlineKeyboardButton("⬅️ Назад к списку игр", callback_data="ratings_by_games")],
        [InlineKeyboardButton("🏆 Общий рейтинг", callback_data="ratings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        ratings_text,
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
    elif data == "ratings":
        await show_ratings(update, context)
    elif data == "my_rating":
        await show_my_rating(update, context)
    elif data == "ratings_by_games":
        await show_ratings_by_games(update, context)
    elif data.startswith("rating_"):
        await show_game_rating(update, context)
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

async def show_my_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать личный рейтинг игрока"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name or "Аноним"
    
    # Получаем рейтинг игрока
    player_rating = get_player_rating(user_id)
    
    if not player_rating:
        await update.message.reply_text(
            "🏆 **Ваш рейтинг**\n\nВы еще не играли. Начните игру, чтобы попасть в рейтинг!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 Выбрать игру", callback_data="hub")]
            ]),
            parse_mode='Markdown'
        )
        return
    
    # Формируем текст с информацией о рейтинге
    rating_text = f"🏆 **Ваш рейтинг**\n\n👤 Игрок: {username}\n📊 Общий счет: {player_rating['total_score']} очков\n\n🎮 **Результаты по играм:**\n"
    
    # Добавляем информацию по каждой игре
    for game_key, game_data in player_rating["games"].items():
        if game_key in GAMES:
            game_name = GAMES[game_key]["name"]
            best_score = game_data["best_score"]
            plays = game_data["plays"]
            rating_text += f"• {game_name}: лучший результат - {best_score} очков ({plays} игр)\n"
    
    # Добавляем дату последнего обновления
    if "last_updated" in player_rating:
        from datetime import datetime
        last_updated = datetime.fromisoformat(player_rating["last_updated"])
        rating_text += f"\n📅 Последняя игра: {last_updated.strftime('%d.%m.%Y %H:%M')}"
    
    # Создаем клавиатуру
    keyboard = [
        [InlineKeyboardButton("🏆 Общий рейтинг", callback_data="ratings")],
        [InlineKeyboardButton("🎮 Играть", callback_data="hub")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        rating_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_game_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик результатов игры"""
    # Проверяем, что это текстовое сообщение и у пользователя есть активная игра
    if not update.message or not update.message.text:
        return
    
    if "current_game" not in context.user_data:
        return
    
    try:
        # Пытаемся извлечь счет из сообщения
        message_text = update.message.text.lower()
        score = 0
        
        # Ищем различные форматы счетов в сообщении
        if "счёт" in message_text or "счет" in message_text or "очко" in message_text or "очки" in message_text:
            # Извлекаем числа из сообщения
            import re
            numbers = re.findall(r'\d+', message_text)
            if numbers:
                score = int(numbers[0])
        
        # Если счет не найден, но есть слова "игра окончена" или "проигрыш"
        if score == 0 and ("игра окончена" in message_text or "проигрыш" in message_text):
            score = 0  # Проигрыш
        
        # Если счет не найден, но есть слова "победа" или "выигрыш"
        if score == 0 and ("победа" in message_text or "выигрыш" in message_text):
            score = 100  # Стандартное значение для победы
        
        # Обновляем рейтинг игрока
        if score > 0 or "игра окончена" in message_text:
            user_id = update.effective_user.id
            username = update.effective_user.username or update.effective_user.first_name or "Аноним"
            game_key = context.user_data["current_game"]
            
            update_player_rating(user_id, username, game_key, score)
            
            # Отправляем подтверждение
            await update.message.reply_text(
                f"✅ Ваш результат в игре {GAMES[game_key]['name']} учтен! "
                f"Счет: {score} очков. Посмотреть рейтинг: /ratings",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏆 Рейтинг", callback_data="ratings")],
                    [InlineKeyboardButton("🎮 Играть снова", callback_data=f"game_{game_key}")]
                ])
            )
        
        # Очищаем информацию о текущей игре
        context.user_data.pop("current_game", None)
        context.user_data.pop("game_start_time", None)
        
    except Exception as e:
        logging.error(f"Ошибка при обработке результата игры: {e}")

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ratings", lambda u, c: show_ratings(u, c)))
    application.add_handler(CommandHandler("myrating", show_my_rating))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_review_text))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_game_result))

    # Запускаем бота
    print("🎮 Бот 'Хаб Игр' запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
