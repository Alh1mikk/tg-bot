
import json
import os
from datetime import datetime

# Путь к файлу с рейтингами
RATINGS_FILE = "ratings.json"

# Инициализация файла рейтингов, если он не существует
def init_ratings():
    if not os.path.exists(RATINGS_FILE):
        with open(RATINGS_FILE, "w") as f:
            json.dump({}, f)

# Загрузка рейтингов из файла
def load_ratings():
    init_ratings()
    with open(RATINGS_FILE, "r") as f:
        return json.load(f)

# Сохранение рейтингов в файл
def save_ratings(ratings):
    with open(RATINGS_FILE, "w") as f:
        json.dump(ratings, f)

# Добавление или обновление рейтинга игрока
def update_player_rating(user_id, username, game, score):
    ratings = load_ratings()
    user_id_str = str(user_id)

    # Если игрока нет в рейтингах, создаем запись
    if user_id_str not in ratings:
        ratings[user_id_str] = {
            "username": username,
            "games": {},
            "total_score": 0,
            "last_updated": datetime.now().isoformat()
        }

    # Обновляем данные для конкретной игры
    if game not in ratings[user_id_str]["games"]:
        ratings[user_id_str]["games"][game] = {"best_score": 0, "plays": 0}

    # Обновляем лучший результат, если текущий лучше
    if score > ratings[user_id_str]["games"][game]["best_score"]:
        ratings[user_id_str]["games"][game]["best_score"] = score

    # Увеличиваем количество игр
    ratings[user_id_str]["games"][game]["plays"] += 1

    # Обновляем общий счет
    ratings[user_id_str]["total_score"] += score
    ratings[user_id_str]["last_updated"] = datetime.now().isoformat()

    save_ratings(ratings)
    return True

# Получение топ-игроков
def get_top_players(limit=10, game=None):
    ratings = load_ratings()
    players = []

    for user_id, data in ratings.items():
        if game:
            # Если указана игра, учитываем только результат в этой игре
            if game in data["games"] and data["games"][game]["best_score"] > 0:
                players.append({
                    "user_id": user_id,
                    "username": data["username"],
                    "score": data["games"][game]["best_score"],
                    "game": game
                })
        else:
            # Иначе учитываем общий счет
            if data["total_score"] > 0:
                players.append({
                    "user_id": user_id,
                    "username": data["username"],
                    "score": data["total_score"],
                    "game": "общий"
                })

    # Сортируем по убыванию счета
    players.sort(key=lambda x: x["score"], reverse=True)
    return players[:limit]

# Получение рейтинга конкретного игрока
def get_player_rating(user_id):
    ratings = load_ratings()
    user_id_str = str(user_id)

    if user_id_str not in ratings:
        return None

    return ratings[user_id_str]
