
import json
import os

# Путь к файлу с данными
DATA_FILE = "game_data.json"

# Инициализация данных, если файл не существует
def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({
                "ratings": {},
                "reviews": {},
                "stats": {}
            }, f)

# Загрузка данных из файла
def load_data():
    init_data()
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Сохранение данных в файл
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Добавление рейтинга игре
def add_rating(game_id, user_id, rating):
    data = load_data()
    if game_id not in data["ratings"]:
        data["ratings"][game_id] = {}
    data["ratings"][game_id][str(user_id)] = rating
    save_data(data)
    return get_average_rating(game_id)

# Получение среднего рейтинга игры
def get_average_rating(game_id):
    data = load_data()
    if game_id not in data["ratings"] or not data["ratings"][game_id]:
        return 0
    ratings = list(data["ratings"][game_id].values())
    return sum(ratings) / len(ratings)

# Добавление отзыва
def add_review(game_id, user_id, review_text):
    data = load_data()
    if game_id not in data["reviews"]:
        data["reviews"][game_id] = []
    data["reviews"][game_id].append({
        "user_id": str(user_id),
        "text": review_text
    })
    save_data(data)
    return True

# Получение отзывов для игры
def get_reviews(game_id, limit=5):
    data = load_data()
    if game_id not in data["reviews"]:
        return []
    return data["reviews"][game_id][-limit:]

# Запись статистики игры
def record_game_play(game_id):
    data = load_data()
    if game_id not in data["stats"]:
        data["stats"][game_id] = {"plays": 0}
    data["stats"][game_id]["plays"] += 1
    save_data(data)

# Получение статистики игры
def get_game_stats(game_id):
    data = load_data()
    if game_id not in data["stats"]:
        return {"plays": 0}
    return data["stats"][game_id]
