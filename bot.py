from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Первый бот работает!"
import telebot
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== ТОКЕН (ЗАМЕНИТЕ НА СВОЙ) =====
TOKEN = "8776336680:AAFyM8_rtWnNyI61TZ5IjQl8bJ-vGpla6DQ"
# =====================================

bot = telebot.TeleBot(TOKEN)

# ===== ХРАНЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ =====
user_data = {}
user_last_category = {}
awaiting_weight = {}
awaiting_product = {}

# =============================================
# РЕЦЕПТЫ (КБЖУ НА 100 Г)
# =============================================
RECIPES = {
    "омлет классический": {
        "ингредиенты": "🥚 Яйца (3 шт), 🥛 Молоко (50 мл), 🧂 Соль, 🧈 Масло сливочное (10 г), 🌿 Зелень",
        "инструкция": "1. Взбить яйца с молоком и солью.\n2. Разогреть сковороду с маслом.\n3. Вылить смесь и жарить 3-4 минуты.\n4. Сложить пополам и посыпать зеленью.",
        "время": "10 минут",
        "kcal_100": 184,
        "protein_100": 12.3,
        "fat_100": 13.5,
        "carbs_100": 2.1,
        "категория": "завтрак",
        "сложность": "простой"
    },
    "блины тонкие": {
        "ингредиенты": "🥛 Молоко (500 мл), 🌾 Мука (300 г), 🥚 Яйца (2 шт), 🍬 Сахар (2 ст.л), 🧂 Соль, 🧈 Масло растительное (2 ст.л)",
        "инструкция": "1. Смешать яйца, сахар, соль.\n2. Добавить молоко и муку, размешать до однородности.\n3. Влить масло.\n4. Жарить на раскаленной сковороде с двух сторон.",
        "время": "30 минут",
        "kcal_100": 189,
        "protein_100": 6.8,
        "fat_100": 7.2,
        "carbs_100": 25.4,
        "категория": "завтрак",
        "сложность": "средний"
    },
    "овсянка с яблоком и корицей": {
        "ингредиенты": "🥣 Овсяные хлопья (1 стакан), 🥛 Молоко (2 стакана), 🍎 Яблоко (1 шт), 🍯 Мёд (1 ст.л), 🧈 Масло сливочное (10 г), 🍬 Корица (1 ч.л)",
        "инструкция": "1. Яблоко натереть на тёрке.\n2. Смешать овсянку, молоко и яблоко.\n3. Варить 5-7 минут.\n4. Добавить мёд, масло, посыпать корицей.",
        "время": "10 минут",
        "kcal_100": 112,
        "protein_100": 4.2,
        "fat_100": 3.5,
        "carbs_100": 16.8,
        "категория": "завтрак",
        "сложность": "простой"
    },
    "сырники классические": {
        "ингредиенты": "🧀 Творог (500 г), 🥚 Яйца (2 шт), 🌾 Мука (100 г), 🍬 Сахар (3 ст.л), 🧂 Соль, 🧈 Масло для жарки",
        "инструкция": "1. Творог растереть с яйцами, мукой и сахаром.\n2. Сформировать сырники.\n3. Обжарить до золотистой корочки с двух сторон.",
        "время": "25 минут",
        "kcal_100": 198,
        "protein_100": 14.2,
        "fat_100": 9.8,
        "carbs_100": 14.5,
        "категория": "завтрак",
        "сложность": "средний"
    },
    "тосты с авокадо": {
        "ингредиенты": "🍞 Хлеб (2 куска), 🥑 Авокадо (1 шт), 🍋 Сок лимона (1 ч.л), 🧂 Соль, перец, 🌿 Зелень",
        "инструкция": "1. Хлеб поджарить.\n2. Авокадо размять вилкой с лимонным соком, солью и перцем.\n3. Намазать на тосты, посыпать зеленью.",
        "время": "10 минут",
        "kcal_100": 178,
        "protein_100": 4.2,
        "fat_100": 14.5,
        "carbs_100": 9.8,
        "категория": "завтрак",
        "сложность": "простой"
    },
    "борщ классический": {
        "ингредиенты": "🥩 Говядина (500 г), 🥬 Капуста (300 г), 🥕 Морковь (1 шт), 🧅 Лук (1 шт), 🥔 Картошка (3 шт), 🍅 Томатная паста (2 ст.л), 🌿 Свекла (1 шт), 🌿 Зелень",
        "инструкция": "1. Сварить мясной бульон (1.5 часа).\n2. Добавить нарезанный картофель.\n3. Отдельно потушить свеклу, морковь и лук с пастой.\n4. Добавить зажарку и капусту в бульон.\n5. Варить 15 минут, посолить, добавить зелень.",
        "время": "2 часа",
        "kcal_100": 62,
        "protein_100": 4.2,
        "fat_100": 2.8,
        "carbs_100": 5.6,
        "категория": "обед",
        "сложность": "сложный"
    },
    "гречка с мясом": {
        "ингредиенты": "🥩 Свинина (400 г), 🌾 Гречка (1.5 ст.), 🧅 Лук (1 шт), 🥕 Морковь (1 шт), 🌿 Зелень",
        "инструкция": "1. Мясо обжарить с луком и морковью.\n2. Засыпать гречку, залить водой (3 ст.).\n3. Варить под крышкой 20 минут.\n4. Настоять 10 минут, посыпать зеленью.",
        "время": "45 минут",
        "kcal_100": 158,
        "protein_100": 11.2,
        "fat_100": 6.8,
        "carbs_100": 14.5,
        "категория": "обед",
        "сложность": "средний"
    },
    "паста карбонара": {
        "ингредиенты": "🍝 Спагетти (400 г), 🥓 Бекон (150 г), 🥚 Яйца (3 шт), 🧀 Пармезан (50 г), 🧄 Чеснок, 🧂 Соль, перец",
        "инструкция": "1. Спагетти отварить до аль денте.\n2. Бекон обжарить с чесноком.\n3. Яйца взбить с пармезаном.\n4. Смешать спагетти с беконом, снять с огня.\n5. Добавить яичную смесь и быстро перемешать.",
        "время": "20 минут",
        "kcal_100": 168,
        "protein_100": 7.5,
        "fat_100": 8.3,
        "carbs_100": 16.2,
        "категория": "ужин",
        "сложность": "средний"
    },
    "запечённая курица с овощами": {
        "ингредиенты": "🍗 Курица (1 шт), 🥕 Морковь (2 шт), 🧅 Лук (2 шт), 🥔 Картошка (4 шт), 🫒 Масло, 🌿 Специи",
        "инструкция": "1. Курицу натереть специями и солью.\n2. Овощи нарезать крупными кусками.\n3. Выложить на противень, полить маслом.\n4. Запекать 1 час при 190°C.",
        "время": "1 час 10 минут",
        "kcal_100": 185,
        "protein_100": 16.5,
        "fat_100": 9.5,
        "carbs_100": 12.5,
        "категория": "ужин",
        "сложность": "сложный"
    },
    "стейк с картофелем": {
        "ингредиенты": "🥩 Говяжий стейк (400 г), 🥔 Картошка (4 шт), 🫒 Масло оливковое, 🌿 Розмарин, 🧂 Соль, перец",
        "инструкция": "1. Стейк посолить, поперчить, обжарить 4-5 минут с каждой стороны.\n2. Картошку нарезать дольками, запечь в духовке до золотистого цвета.\n3. Подавать с розмарином и овощами.",
        "время": "30 минут",
        "kcal_100": 265,
        "protein_100": 22.5,
        "fat_100": 15.8,
        "carbs_100": 10.5,
        "категория": "ужин",
        "сложность": "сложный"
    }
}

def get_user_stats(uid):
    user = user_data.get(uid, {})
    food_list = user.get("today_food", [])
    
    total_kcal = sum(f["kcal"] for f in food_list)
    total_protein = sum(f["protein"] for f in food_list)
    total_fat = sum(f["fat"] for f in food_list)
    total_carbs = sum(f["carbs"] for f in food_list)
    
    daily_goal = user.get("daily_goal", {})
    goal_kcal = daily_goal.get("kcal", 2000)
    goal_protein = daily_goal.get("protein", 150)
    goal_fat = daily_goal.get("fat", 70)
    goal_carbs = daily_goal.get("carbs", 200)
    
    return {
        "total_kcal": total_kcal,
        "total_protein": total_protein,
        "total_fat": total_fat,
        "total_carbs": total_carbs,
        "goal_kcal": goal_kcal,
        "goal_protein": goal_protein,
        "goal_fat": goal_fat,
        "goal_carbs": goal_carbs,
        "remaining_kcal": max(0, goal_kcal - total_kcal),
        "remaining_protein": max(0, goal_protein - total_protein),
        "remaining_fat": max(0, goal_fat - total_fat),
        "remaining_carbs": max(0, goal_carbs - total_carbs),
        "food_count": len(food_list)
    }

def send_recipe(uid, name, data):
    reply = (
        f"🍽 *{name.capitalize()}*\n"
        f"{'='*30}\n\n"
        f"📋 *Ингредиенты:*\n{data['ингредиенты']}\n\n"
        f"👨‍🍳 *Инструкция:*\n{data['инструкция']}\n\n"
        f"⏱️ *Время:* {data['время']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *КБЖУ на 100 г:*\n"
        f"🔥 {data['kcal_100']} ккал\n"
        f"💪 {data['protein_100']} г белков\n"
        f"🧈 {data['fat_100']} г жиров\n"
        f"🍚 {data['carbs_100']} г углеводов\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ *Сложность:* {data.get('сложность', 'не указана').capitalize()}"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Добавить в дневник", callback_data=f"add_{name}"))
    bot.send_message(uid, reply, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("🍳 Завтрак"),
        telebot.types.KeyboardButton("🍲 Обед"),
        telebot.types.KeyboardButton("🍝 Ужин"),
        telebot.types.KeyboardButton("➕ Свой продукт"),
        telebot.types.KeyboardButton("⚙️ Настройки")
    ]
    markup.add(*buttons)
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я бот-шеф-повар!\n\n"
        "🔹 Настрой свой профиль через ⚙️ Настройки\n"
        "🔹 Выбирай категорию: Завтрак, Обед или Ужин\n"
        "🔹 Напиши номер — получи рецепт!\n"
        "🔹 Нажми '➕ Свой продукт' — добавь любой продукт в дневник",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "⚙️ Настройки")
def settings_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "🍽 Норма калорий",
        "📊 Уровень сложности",
        "📊 Моя статистика",
        "🗑 Сбросить дневник",
        "🔙 Назад"
    )
    bot.send_message(message.chat.id, "⚙️ *Настройки:*\n\nВыбери, что хочешь изменить:", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🍽 Норма калорий")
def set_goal_menu(message):
    bot.send_message(
        message.chat.id,
        "🍽 *Установим дневную норму КБЖУ*\n\n"
        "Напиши в формате:\n"
        "`калории, белки, жиры, углеводы`\n\n"
        "Например: `2000, 150, 70, 200`\n\n"
        "Или просто число (только калории): `1800`",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, save_goal)

def save_goal(message):
    try:
        text = message.text.strip()
        uid = message.chat.id
        
        if uid not in user_data:
            user_data[uid] = {}
        
        if "," in text:
            parts = [p.strip() for p in text.split(",")]
            if len(parts) == 4:
                user_data[uid]["daily_goal"] = {
                    "kcal": int(parts[0]),
                    "protein": int(parts[1]),
                    "fat": int(parts[2]),
                    "carbs": int(parts[3])
                }
                bot.send_message(
                    uid,
                    f"✅ Норма установлена:\n"
                    f"🔥 {parts[0]} ккал\n"
                    f"💪 {parts[1]} г белков\n"
                    f"🧈 {parts[2]} г жиров\n"
                    f"🍚 {parts[3]} г углеводов"
                )
                return
        
        goal = int(text)
        user_data[uid]["daily_goal"] = {
            "kcal": goal,
            "protein": 150,
            "fat": 70,
            "carbs": 200
        }
        bot.send_message(
            uid,
            f"✅ Норма установлена:\n"
            f"🔥 {goal} ккал\n"
            f"💪 150 г белков (по умолчанию)\n"
            f"🧈 70 г жиров (по умолчанию)\n"
            f"🍚 200 г углеводов (по умолчанию)"
        )
    except:
        bot.reply_to(message, "❌ Неправильный формат. Напиши: `2000, 150, 70, 200`", parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "📊 Уровень сложности")
def set_difficulty_menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🟢 Простой", "🟡 Средний", "🔴 Сложный", "🔙 Назад")
    bot.send_message(
        message.chat.id,
        "📊 *Выбери уровень сложности:*\n\n"
        "🟢 Простой — до 10 минут, 3-5 ингредиентов\n"
        "🟡 Средний — до 30 минут, классические рецепты\n"
        "🔴 Сложный — от 30 минут, интересная техника",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: m.text in ["🟢 Простой", "🟡 Средний", "🔴 Сложный"])
def save_difficulty(message):
    diff_map = {
        "🟢 Простой": "простой",
        "🟡 Средний": "средний",
        "🔴 Сложный": "сложный"
    }
    uid = message.chat.id
    if uid not in user_data:
        user_data[uid] = {}
    user_data[uid]["difficulty"] = diff_map[message.text]
    if "today_food" not in user_data[uid]:
        user_data[uid]["today_food"] = []
    bot.send_message(uid, f"✅ Уровень сложности: {message.text}")

@bot.message_handler(func=lambda m: m.text == "📊 Моя статистика")
def show_stats(message):
    uid = message.chat.id
    stats = get_user_stats(uid)
    
    if stats["food_count"] == 0:
        bot.send_message(uid, "📭 Ты ещё ничего не добавил в дневник сегодня.")
        return
    
    progress_kcal = min(100, int((stats["total_kcal"] / stats["goal_kcal"]) * 100))
    bar_kcal = "█" * (progress_kcal // 5) + "░" * (20 - (progress_kcal // 5))
    
    progress_protein = min(100, int((stats["total_protein"] / stats["goal_protein"]) * 100))
    bar_protein = "█" * (progress_protein // 5) + "░" * (20 - (progress_protein // 5))
    
    progress_fat = min(100, int((stats["total_fat"] / stats["goal_fat"]) * 100))
    bar_fat = "█" * (progress_fat // 5) + "░" * (20 - (progress_fat // 5))
    
    progress_carbs = min(100, int((stats["total_carbs"] / stats["goal_carbs"]) * 100))
    bar_carbs = "█" * (progress_carbs // 5) + "░" * (20 - (progress_carbs // 5))
    
    bot.send_message(
        uid,
        f"📊 *Твоя статистика сегодня:*\n\n"
        f"🥗 Съедено блюд/продуктов: {stats['food_count']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 *Калории:* {stats['total_kcal']:.0f} / {stats['goal_kcal']} ккал\n"
        f"⚡️ Осталось: {stats['remaining_kcal']:.0f} ккал\n"
        f"`{bar_kcal}` {progress_kcal}%\n\n"
        f"💪 *Белки:* {stats['total_protein']:.0f} / {stats['goal_protein']} г\n"
        f"⚡️ Осталось: {stats['remaining_protein']:.0f} г\n"
        f"`{bar_protein}` {progress_protein}%\n\n"
        f"🧈 *Жиры:* {stats['total_fat']:.0f} / {stats['goal_fat']} г\n"
        f"⚡️ Осталось: {stats['remaining_fat']:.0f} г\n"
        f"`{bar_fat}` {progress_fat}%\n\n"
        f"🍚 *Углеводы:* {stats['total_carbs']:.0f} / {stats['goal_carbs']} г\n"
        f"⚡️ Осталось: {stats['remaining_carbs']:.0f} г\n"
        f"`{bar_carbs}` {progress_carbs}%",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: m.text == "🗑 Сбросить дневник")
def reset_diary(message):
    uid = message.chat.id
    if uid in user_data:
        user_data[uid]["today_food"] = []
    bot.send_message(uid, "🗑 Дневник питания очищен!")

@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def back_to_main(message):
    start(message)

@bot.message_handler(func=lambda m: m.text in ["🍳 Завтрак", "🍲 Обед", "🍝 Ужин"])
def show_category(message):
    cat_map = {"🍳 Завтрак": "завтрак", "🍲 Обед": "обед", "🍝 Ужин": "ужин"}
    category = cat_map[message.text]
    uid = message.chat.id
    
    user = user_data.get(uid, {})
    difficulty = user.get("difficulty", "простой")
    
    recipes = []
    for name, data in RECIPES.items():
        if data["категория"] == category and data["сложность"] == difficulty:
            recipes.append((name, data))
    
    if not recipes:
        for name, data in RECIPES.items():
            if data["категория"] == category:
                recipes.append((name, data))
    
    user_last_category[uid] = recipes
    
    reply = f"🍽 *{category.capitalize()} (уровень: {difficulty}):*\n\n"
    for i, (name, data) in enumerate(recipes, 1):
        reply += f"{i}. {name.capitalize()} — {data['время']} — {data['kcal_100']} ккал/100г\n"
    reply += "\n✏️ Напиши номер (например, 5), чтобы получить рецепт!"
    
    bot.send_message(uid, reply, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text.isdigit())
def handle_number(message):
    uid = message.chat.id
    num = int(message.text.strip())
    
    if uid in awaiting_weight and awaiting_weight[uid]:
        save_food_with_weight(message)
        return
    
    recipe_index = num - 1
    
    if uid in user_last_category and user_last_category[uid]:
        recipes = user_last_category[uid]
        if 0 <= recipe_index < len(recipes):
            name, data = recipes[recipe_index]
            send_recipe(uid, name, data)
            return
        else:
            bot.reply_to(message, f"❌ Нет рецепта под номером {num}.")
            return
    
    all_names = list(RECIPES.keys())
    if 0 <= recipe_index < len(all_names):
        name = all_names[recipe_index]
        data = RECIPES[name]
        send_recipe(uid, name, data)
    else:
        bot.reply_to(message, "❌ Сначала выбери категорию!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def ask_weight(call):
    uid = call.message.chat.id
    name = call.data.replace("add_", "")
    data = RECIPES[name]
    
    if uid not in user_data:
        user_data[uid] = {}
    user_data[uid]["pending_recipe"] = name
    awaiting_weight[uid] = True
    
    bot.send_message(
        uid,
        f"📝 *{name.capitalize()}*\n"
        f"КБЖУ на 100 г:\n"
        f"🔥 {data['kcal_100']} ккал\n"
        f"💪 {data['protein_100']} г белков\n"
        f"🧈 {data['fat_100']} г жиров\n"
        f"🍚 {data['carbs_100']} г углеводов\n\n"
        f"✏️ Напиши вес в граммах (например, 150):",
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

def save_food_with_weight(message):
    uid = message.chat.id
    weight = float(message.text.strip())
    name = user_data[uid]["pending_recipe"]
    data = RECIPES[name]
    
    kcal = round(data["kcal_100"] * weight / 100, 1)
    protein = round(data["protein_100"] * weight / 100, 1)
    fat = round(data["fat_100"] * weight / 100, 1)
    carbs = round(data["carbs_100"] * weight / 100, 1)
    
    if "today_food" not in user_data[uid]:
        user_data[uid]["today_food"] = []
    
    user_data[uid]["today_food"].append({
        "name": name,
        "weight": weight,
        "kcal": kcal,
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    })
    
    del user_data[uid]["pending_recipe"]
    awaiting_weight[uid] = False
    
    bot.send_message(
        uid,
        f"✅ *{name.capitalize()}* — {weight} г добавлен в дневник!\n\n"
        f"📊 КБЖУ:\n"
        f"🔥 {kcal} ккал\n"
        f"💪 {protein} г белков\n"
        f"🧈 {fat} г жиров\n"
        f"🍚 {carbs} г углеводов",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: m.text == "➕ Свой продукт")
def add_own_product_start(message):
    uid = message.chat.id
    awaiting_product[uid] = True
    
    bot.send_message(
        uid,
        "✏️ *Добавим свой продукт в дневник*\n\n"
        "Напиши в формате:\n"
        "`Название, вес (г), калории на 100г, белки, жиры, углеводы`\n\n"
        "Например: `Яблоко, 150, 52, 0.3, 0.2, 13.8`\n\n"
        "Или просто: `Яблоко, 150` (тогда калории и БЖУ будут по умолчанию)",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: True)
def main_handler(message):
    uid = message.chat.id
    
    # Если пользователь в режиме добавления продукта
    if uid in awaiting_product and awaiting_product[uid]:
        text = message.text.strip()
        
        try:
            parts = text.split(",")
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 2:
                name = parts[0]
                weight = float(parts[1])
                
                if len(parts) >= 6:
                    kcal_100 = float(parts[2])
                    protein_100 = float(parts[3])
                    fat_100 = float(parts[4])
                    carbs_100 = float(parts[5])
                else:
                    kcal_100 = 100
                    protein_100 = 5
                    fat_100 = 5
                    carbs_100 = 10
                
                kcal = round(kcal_100 * weight / 100, 1)
                protein = round(protein_100 * weight / 100, 1)
                fat = round(fat_100 * weight / 100, 1)
                carbs = round(carbs_100 * weight / 100, 1)
                
                if "today_food" not in user_data[uid]:
                    user_data[uid] = {"today_food": []}
                if "today_food" not in user_data[uid]:
                    user_data[uid]["today_food"] = []
                
                user_data[uid]["today_food"].append({
                    "name": name,
                    "weight": weight,
                    "kcal": kcal,
                    "protein": protein,
                    "fat": fat,
                    "carbs": carbs
                })
                
                awaiting_product[uid] = False
                
                bot.send_message(
                    uid,
                    f"✅ *{name}* — {weight} г добавлен в дневник!\n\n"
                    f"📊 КБЖУ:\n"
                    f"🔥 {kcal} ккал\n"
                    f"💪 {protein} г белков\n"
                    f"🧈 {fat} г жиров\n"
                    f"🍚 {carbs} г углеводов\n\n"
                    f"📌 Чтобы добавить ещё продукт, снова нажми '➕ Свой продукт'",
                    parse_mode='Markdown'
                )
                return
            
            bot.reply_to(message, "❌ Неправильный формат. Напиши: `Название, вес, калории, белки, жиры, углеводы`", parse_mode='Markdown')
        
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка: {str(e)}\n\nНапиши в формате:\n`Название, вес, калории, белки, жиры, углеводы`", parse_mode='Markdown')
        return
    
    # Обычная обработка
    text = message.text.lower().strip()
    
    if "настройки" in text or "настрой" in text:
        settings_menu(message)
        return
    if "норм" in text or "калорий" in text:
        set_goal_menu(message)
        return
    if "сложность" in text or "уровень" in text:
        set_difficulty_menu(message)
        return
    if "статистик" in text:
        show_stats(message)
        return
    if "сброс" in text or "очист" in text:
        reset_diary(message)
        return
    
    for name, data in RECIPES.items():
        if text in data["ингредиенты"].lower() and len(text) > 2:
            send_recipe(uid, name, data)
            return
        if text == name.lower():
            send_recipe(uid, name, data)
            return
    
    bot.reply_to(message, "😅 Не нашёл такого. Попробуй нажать кнопку или написать 'настройки'.")

# Запускаем бота в отдельном потоке
def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

# Запускаем Flask для Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
