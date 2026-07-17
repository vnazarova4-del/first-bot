import telebot
import datetime
import json
import os
import random
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает!"

# ===== ТОКЕН ПЕРВОГО БОТА =====
TOKEN = "8776336680:AAFyM8_rtWnNyI61TZ5IjQl8bJ-vGpla6DQ"
# =================================

bot = telebot.TeleBot(TOKEN)

# ===== ФАЙЛ ДЛЯ ХРАНЕНИЯ ДАННЫХ =====
DATA_FILE = "user_data.json"

# =============================================
# РАБОТА С ДАННЫМИ
# =============================================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(user_id):
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "daily_goal": {"kcal": 2000, "protein": 150, "fat": 70, "carbs": 200},
            "today_food": [],
            "pending_recipe": None,
            "pending_weight": False,
            "difficulty": "простой",
            "last_category": None
        }
        save_data(data)
    return data[user_id]

def save_user_data(user_id, user_data):
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

def get_user_stats(user_id):
    user_data = get_user_data(user_id)
    food_list = user_data.get("today_food", [])
    
    total_kcal = sum(f["kcal"] for f in food_list)
    total_protein = sum(f["protein"] for f in food_list)
    total_fat = sum(f["fat"] for f in food_list)
    total_carbs = sum(f["carbs"] for f in food_list)
    
    goal = user_data.get("daily_goal", {"kcal": 2000, "protein": 150, "fat": 70, "carbs": 200})
    
    return {
        "total_kcal": total_kcal,
        "total_protein": total_protein,
        "total_fat": total_fat,
        "total_carbs": total_carbs,
        "goal_kcal": goal.get("kcal", 2000),
        "goal_protein": goal.get("protein", 150),
        "goal_fat": goal.get("fat", 70),
        "goal_carbs": goal.get("carbs", 200),
        "remaining_kcal": max(0, goal.get("kcal", 2000) - total_kcal),
        "remaining_protein": max(0, goal.get("protein", 150) - total_protein),
        "remaining_fat": max(0, goal.get("fat", 70) - total_fat),
        "remaining_carbs": max(0, goal.get("carbs", 200) - total_carbs),
        "food_count": len(food_list)
    }

# =============================================
# ПОЛНАЯ БАЗА РЕЦЕПТОВ
# =============================================
RECIPES = {
    # ========================================
    # ЗАВТРАКИ (СТАРЫЕ)
    # ========================================
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
    "омлет с сыром и зеленью": {
        "ингредиенты": "🥚 Яйца (3 шт), 🧀 Сыр (50 г), 🥛 Молоко (30 мл), 🌿 Зелень, 🧂 Соль, 🧈 Масло сливочное (10 г)",
        "инструкция": "1. Яйца взбить с молоком и солью.\n2. Вылить на сковороду с маслом.\n3. Жарить 2 минуты, посыпать сыром и зеленью.\n4. Сложить пополам и жарить ещё 1 минуту.",
        "время": "10 минут",
        "kcal_100": 212,
        "protein_100": 15.6,
        "fat_100": 16.2,
        "carbs_100": 3.4,
        "категория": "завтрак",
        "сложность": "простой"
    },
    "каша рисовая с яблоком": {
        "ингредиенты": "🍚 Рис (1 стакан), 🥛 Молоко (2 стакана), 🍎 Яблоко (1 шт), 🍬 Сахар (2 ст.л), 🧈 Масло (10 г), 🍬 Корица",
        "инструкция": "1. Рис промыть, варить в воде 10 минут.\n2. Влить молоко, добавить сахар, варить 15 минут.\n3. Добавить нарезанное яблоко, масло и корицу.",
        "время": "30 минут",
        "kcal_100": 158,
        "protein_100": 4.5,
        "fat_100": 4.2,
        "carbs_100": 27.8,
        "категория": "завтрак",
        "сложность": "средний"
    },
    "скрэмбл с авокадо": {
        "ингредиенты": "🥚 Яйца (3 шт), 🥑 Авокадо (1 шт), 🧈 Масло (10 г), 🧂 Соль, перец, 🌿 Зелень",
        "инструкция": "1. Яйца взбить с солью и перцем.\n2. Вылить на сковороду с маслом.\n3. Жарить, помешивая, 3-4 минуты.\n4. Добавить нарезанный авокадо, посыпать зеленью.",
        "время": "8 минут",
        "kcal_100": 198,
        "protein_100": 11.8,
        "fat_100": 16.5,
        "carbs_100": 4.2,
        "категория": "завтрак",
        "сложность": "простой"
    },

    # ========================================
    # ОБЕДЫ (СТАРЫЕ)
    # ========================================
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

    # ========================================
    # УЖИНЫ (СТАРЫЕ)
    # ========================================
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
    },

    # ========================================
    # НОВЫЕ ПП-УЖИНЫ (10 шт)
    # ========================================
    "куриная грудка с гречкой и морковью": {
        "ингредиенты": "🍗 Куриная грудка (200 г), 🌾 Гречка (100 г), 🥕 Морковь (1 шт), 🧅 Лук (1/2 шт), 🫒 Оливковое масло (1 ч.л), 🧂 Соль, 🌿 Перец, 🌿 Зелень",
        "инструкция": "1. Куриную грудку нарезать кубиками, посолить, поперчить.\n2. Морковь натереть на тёрке, лук мелко нарезать.\n3. Гречку промыть и сварить до готовности (15-20 минут).\n4. Курицу обжарить на масле 5-7 минут до золотистой корочки.\n5. Добавить морковь и лук, обжаривать ещё 3-4 минуты.\n6. Смешать с гречкой, прогреть 1-2 минуты.\n7. Подавать, посыпав зеленью.",
        "время": "30 минут",
        "kcal_100": 145,
        "protein_100": 17,
        "fat_100": 3.5,
        "carbs_100": 13,
        "категория": "ужин",
        "сложность": "простой"
    },
    "запечённая рыба с овощами": {
        "ингредиенты": "🐟 Филе белой рыбы (200 г), 🥦 Брокколи (150 г), 🥕 Морковь (1 шт), 🧅 Лук (1/2 шт), 🫒 Оливковое масло (1 ст.л), 🍋 Лимон (2 кружочка), 🧂 Соль, 🌿 Перец, 🌿 Сушёные травы",
        "инструкция": "1. Рыбу посолить, поперчить, сбрызнуть маслом и лимоном.\n2. Оставить мариноваться 10-15 минут.\n3. Брокколи разобрать на соцветия, морковь нарезать кружочками.\n4. Противень застелить пергаментом, выложить рыбу и овощи.\n5. Запекать 20-25 минут при 180°C.\n6. Подавать с зеленью.",
        "время": "30 минут",
        "kcal_100": 95,
        "protein_100": 15,
        "fat_100": 3,
        "carbs_100": 4,
        "категория": "ужин",
        "сложность": "простой"
    },
    "омлет с овощами": {
        "ингредиенты": "🥚 Яйца (3 шт), 🥛 Молоко (50 мл), 🍅 Помидор (1 шт), 🫑 Перец болгарский (1/2 шт), 🌿 Зелень, 🧂 Соль, 🌿 Перец, 🫒 Оливковое масло (1 ч.л)",
        "инструкция": "1. Помидор нарезать кубиками, перец — мелкими кубиками, зелень порубить.\n2. Яйца взбить с молоком, солью и перцем.\n3. Разогреть сковороду с маслом.\n4. Вылить яичную смесь, сверху распределить овощи.\n5. Накрыть крышкой и жарить 5-7 минут.\n6. Подавать, посыпав зеленью.",
        "время": "10 минут",
        "kcal_100": 130,
        "protein_100": 12,
        "fat_100": 8,
        "carbs_100": 3,
        "категория": "ужин",
        "сложность": "простой"
    },
    "тушёная курица с кабачками": {
        "ингредиенты": "🍗 Куриное филе (250 г), 🥒 Кабачок (1 шт), 🧅 Лук (1 шт), 🥕 Морковь (1/2 шт), 🫒 Оливковое масло (1 ст.л), 🧂 Соль, 🌿 Перец, 🌿 Зелень, 🧄 Чеснок (1 зубчик)",
        "инструкция": "1. Курицу нарезать кубиками, кабачок — кружочками, лук — полукольцами, морковь — соломкой.\n2. Обжарить курицу 5-7 минут до золотистой корочки.\n3. Добавить лук и морковь, обжаривать 3-4 минуты.\n4. Добавить кабачок, чеснок, соль, перец, влить 50 мл воды.\n5. Тушить под крышкой 10-12 минут.\n6. Подавать с зеленью.",
        "время": "25 минут",
        "kcal_100": 110,
        "protein_100": 16,
        "fat_100": 4,
        "carbs_100": 5,
        "категория": "ужин",
        "сложность": "простой"
    },
    "рыбные котлеты с рисом": {
        "ингредиенты": "🐟 Филе рыбы (300 г), 🥚 Яйцо (1 шт), 🧅 Лук (1 шт), 🌾 Рис (100 г), 🧂 Соль, 🌿 Перец, 🌿 Зелень, 🫒 Оливковое масло (1 ч.л)",
        "инструкция": "1. Рис промыть и сварить до готовности (15-20 минут).\n2. Рыбу и лук пропустить через мясорубку.\n3. Добавить яйцо, соль, перец, перемешать.\n4. Сформировать котлеты, обжарить на масле по 3-4 минуты с каждой стороны.\n5. Подавать с рисом и зеленью.",
        "время": "30 минут",
        "kcal_100": 150,
        "protein_100": 16,
        "fat_100": 5,
        "carbs_100": 12,
        "категория": "ужин",
        "сложность": "простой"
    },
    "овощное рагу с нутом": {
        "ингредиенты": "🥫 Нут консервированный (200 г), 🥕 Морковь (1 шт), 🧅 Лук (1 шт), 🫑 Перец болгарский (1/2 шт), 🍅 Томатная паста (2 ст.л), 🫒 Оливковое масло (1 ст.л), 🧂 Соль, 🌿 Перец, 🌿 Орегано, 🧄 Чеснок (1 зубчик)",
        "инструкция": "1. Морковь нарезать кружочками, лук — полукольцами, перец — полосками.\n2. Обжарить лук и морковь 3-4 минуты.\n3. Добавить перец, обжаривать 2 минуты.\n4. Добавить томатную пасту, прогреть 1 минуту.\n5. Влить 300 мл воды, добавить нут, соль, перец, орегано, чеснок.\n6. Тушить под крышкой 15-20 минут.\n7. Подавать с зеленью.",
        "время": "35 минут",
        "kcal_100": 120,
        "protein_100": 7,
        "fat_100": 3,
        "carbs_100": 16,
        "категория": "ужин",
        "сложность": "простой"
    },
    "салат с курицей и авокадо": {
        "ингредиенты": "🍗 Куриное филе (150 г), 🥑 Авокадо (1 шт), 🥬 Листья салата (100 г), 🍅 Помидоры черри (5-6 шт), 🫒 Оливковое масло (1 ст.л), 🍋 Лимонный сок (1 ч.л), 🧂 Соль, 🌿 Перец",
        "инструкция": "1. Курицу отварить до готовности, нарезать кубиками.\n2. Авокадо нарезать кубиками, сбрызнуть лимонным соком.\n3. Помидоры разрезать пополам, салат порвать руками.\n4. Смешать все ингредиенты, заправить маслом и лимонным соком.\n5. Посолить, поперчить по вкусу.",
        "время": "20 минут",
        "kcal_100": 135,
        "protein_100": 12,
        "fat_100": 9,
        "carbs_100": 4,
        "категория": "ужин",
        "сложность": "простой"
    },
    "кабачки с фаршем": {
        "ингредиенты": "🥒 Кабачок (2 шт), 🥩 Фарш (300 г), 🧅 Лук (1 шт), 🧀 Сыр (30 г), 🥚 Яйцо (1 шт), 🧂 Соль, 🌿 Перец, 🌿 Сушёный чеснок, 🫒 Оливковое масло (1 ч.л)",
        "инструкция": "1. Кабачки нарезать кружочками (1.5-2 см).\n2. Смешать фарш с луком, яйцом, солью, перцем, чесноком.\n3. Противень застелить пергаментом, смазать маслом.\n4. Выложить кабачки, сверху — фарш.\n5. Посыпать тёртым сыром.\n6. Запекать 20-25 минут при 200°C.",
        "время": "35 минут",
        "kcal_100": 125,
        "protein_100": 14,
        "fat_100": 6,
        "carbs_100": 5,
        "категория": "ужин",
        "сложность": "простой"
    },
    "греческий салат с сыром фета": {
        "ингредиенты": "🍅 Помидоры (2 шт), 🥒 Огурец (1 шт), 🫑 Перец болгарский (1 шт), 🧅 Лук красный (1/2 шт), 🫒 Маслины (50 г), 🧀 Сыр фета (100 г), 🫒 Оливковое масло (2 ст.л), 🍋 Лимонный сок (1 ст.л), 🌿 Орегано, 🧂 Соль",
        "инструкция": "1. Помидоры нарезать дольками, огурец — кружочками, перец — полосками, лук — полукольцами.\n2. Смешать овощи с маслинами.\n3. Заправить маслом, лимонным соком, орегано и солью.\n4. Сыр фета нарезать кубиками и выложить сверху.\n5. Подавать сразу.",
        "время": "15 минут",
        "kcal_100": 120,
        "protein_100": 5,
        "fat_100": 9,
        "carbs_100": 5,
        "категория": "ужин",
        "сложность": "простой"
    },
    "запечённый тунец с зеленью": {
        "ингредиенты": "🐟 Филе тунца (200 г), 🍋 Лимон, 🌿 Укроп, 🧂 Соль, 🌿 Перец, 🫒 Оливковое масло (1 ч.л), 🧄 Чеснок (по желанию)",
        "инструкция": "1. Филе тунца разморозить, промыть, обсушить.\n2. Натереть солью, перцем, сбрызнуть маслом и лимонным соком.\n3. Чеснок и укроп мелко порубить, натереть рыбу.\n4. Оставить мариноваться на 10 минут.\n5. Завернуть в фольгу с кружочками лимона.\n6. Запекать 12-15 минут при 190°C.\n7. Подавать с зеленью и лимоном.",
        "время": "25 минут",
        "kcal_100": 130,
        "protein_100": 26,
        "fat_100": 3,
        "carbs_100": 0,
        "категория": "ужин",
        "сложность": "простой"
    }
}

# =============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================

def get_habits_by_category(category):
    result = {}
    for name, data in RECIPES.items():
        if data.get("категория") == category:
            result[name] = data
    return result

def get_habits_by_difficulty(difficulty):
    result = {}
    for name, data in RECIPES.items():
        if data.get("сложность") == difficulty:
            result[name] = data
    return result

def format_recipe_list(recipes, category_name, difficulty):
    if not recipes:
        return f"😅 В категории '{category_name}' с уровнем '{difficulty}' нет рецептов."
    
    text = f"🍽 *{category_name.capitalize()} (уровень: {difficulty}):*\n\n"
    for i, (name, data) in enumerate(recipes.items(), 1):
        text += f"{i}. {name.capitalize()} — {data['время']} — {data['kcal_100']} ккал/100г\n"
    text += "\n✏️ Напиши номер (например, 5), чтобы получить рецепт!"
    return text

def send_recipe(chat_id, name, recipe, show_add_button=True):
    reply = (
        f"🍽 *{name.capitalize()}*\n"
        f"{'='*30}\n\n"
        f"📋 *Ингредиенты:*\n{recipe['ингредиенты']}\n\n"
        f"👨‍🍳 *Инструкция:*\n{recipe['инструкция']}\n\n"
        f"⏱️ *Время:* {recipe['время']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *КБЖУ на 100 г:*\n"
        f"🔥 {recipe['kcal_100']} ккал\n"
        f"💪 {recipe['protein_100']} г белков\n"
        f"🧈 {recipe['fat_100']} г жиров\n"
        f"🍚 {recipe['carbs_100']} г углеводов\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ *Категория:* {recipe['категория'].capitalize()}\n"
        f"🏷️ *Сложность:* {recipe['сложность'].capitalize()}"
    )
    
    if show_add_button:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(
            "📝 Добавить в дневник",
            callback_data=f"add_{name}"
        ))
        bot.send_message(chat_id, reply, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(chat_id, reply, parse_mode='Markdown')

def show_stats(chat_id):
    user_id = chat_id
    stats = get_user_stats(user_id)
    
    if stats["food_count"] == 0:
        bot.send_message(chat_id, "📭 Ты ещё ничего не добавил в дневник сегодня.")
        return
    
    progress_kcal = min(100, int((stats["total_kcal"] / stats["goal_kcal"]) * 100))
    bar_kcal = "█" * (progress_kcal // 5) + "░" * (20 - (progress_kcal // 5))
    
    progress_protein = min(100, int((stats["total_protein"] / stats["goal_protein"]) * 100))
    bar_protein = "█" * (progress_protein // 5) + "░" * (20 - (progress_protein // 5))
    
    progress_fat = min(100, int((stats["total_fat"] / stats["goal_fat"]) * 100))
    bar_fat = "█" * (progress_fat // 5) + "░" * (20 - (progress_fat // 5))
    
    progress_carbs = min(100, int((stats["total_carbs"] / stats["goal_carbs"]) * 100))
    bar_carbs = "█" * (progress_carbs // 5) + "░" * (20 - (progress_carbs // 5))
    
    reply = (
        f"📊 *Твоя статистика сегодня:*\n\n"
        f"🥗 Съедено блюд: {stats['food_count']}\n\n"
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
        f"`{bar_carbs}` {progress_carbs}%"
    )
    bot.send_message(chat_id, reply, parse_mode='Markdown')

# =============================================
# ОБРАБОТЧИКИ КОМАНД
# =============================================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("🍳 Завтрак"),
        telebot.types.KeyboardButton("🍲 Обед"),
        telebot.types.KeyboardButton("🍝 Ужин"),
        telebot.types.KeyboardButton("⚙️ Настройки"),
        telebot.types.KeyboardButton("📊 Статистика"),
        telebot.types.KeyboardButton("📋 Чеклист"),
        telebot.types.KeyboardButton("🎲 Случайный рецепт")
    ]
    markup.add(*buttons)
    
    difficulty = user_data.get("difficulty", "простой")
    
    bot.send_message(
        message.chat.id,
        f"👋 *Привет! Я бот-шеф-повар!*\n\n"
        f"🔹 Настрой свой профиль через ⚙️ Настройки\n"
        f"🔹 Выбирай категорию: Завтрак, Обед или Ужин\n"
        f"🔹 Напиши номер — получи рецепт!\n"
        f"🔹 Нажми 'Добавить в дневник' и укажи вес порции\n\n"
        f"📊 *Текущий уровень сложности:* {difficulty.capitalize()}",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: m.text == "⚙️ Настройки")
def settings_menu(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "🍽 Норма КБЖУ",
        "📊 Уровень сложности",
        "🗑 Сбросить дневник",
        "🔙 Назад"
    )
    
    goal = user_data.get("daily_goal", {"kcal": 2000, "protein": 150, "fat": 70, "carbs": 200})
    
    bot.send_message(
        message.chat.id,
        f"⚙️ *Настройки:*\n\n"
        f"🔥 Норма калорий: {goal['kcal']} ккал\n"
        f"💪 Белки: {goal['protein']} г\n"
        f"🧈 Жиры: {goal['fat']} г\n"
        f"🍚 Углеводы: {goal['carbs']} г\n\n"
        f"📊 Уровень сложности: {user_data.get('difficulty', 'простой').capitalize()}",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: m.text == "🍽 Норма КБЖУ")
def set_goal_menu(message):
    msg = bot.send_message(
        message.chat.id,
        "🍽 *Установим дневную норму КБЖУ*\n\n"
        "Напиши в формате:\n"
        "`калории, белки, жиры, углеводы`\n\n"
        "Например: `2000, 150, 70, 200`\n\n"
        "Или просто число (только калории): `1800`",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, save_goal)

def save_goal(message):
    try:
        text = message.text.strip()
        user_id = message.chat.id
        user_data = get_user_data(user_id)
        
        if "," in text:
            parts = [p.strip() for p in text.split(",")]
            if len(parts) == 4:
                user_data["daily_goal"] = {
                    "kcal": int(parts[0]),
                    "protein": int(parts[1]),
                    "fat": int(parts[2]),
                    "carbs": int(parts[3])
                }
                save_user_data(user_id, user_data)
                bot.send_message(
                    user_id,
                    f"✅ Норма установлена:\n"
                    f"🔥 {parts[0]} ккал\n"
                    f"💪 {parts[1]} г белков\n"
                    f"🧈 {parts[2]} г жиров\n"
                    f"🍚 {parts[3]} г углеводов"
                )
                return
        
        goal = int(text)
        user_data["daily_goal"] = {
            "kcal": goal,
            "protein": 150,
            "fat": 70,
            "carbs": 200
        }
        save_user_data(user_id, user_data)
        bot.send_message(
            user_id,
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
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    user_data["difficulty"] = diff_map[message.text]
    save_user_data(user_id, user_data)
    bot.send_message(user_id, f"✅ Уровень сложности: {message.text}")

@bot.message_handler(func=lambda m: m.text == "🗑 Сбросить дневник")
def reset_diary(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    user_data["today_food"] = []
    save_user_data(user_id, user_data)
    bot.send_message(user_id, "🗑 Дневник питания очищен!")

@bot.message_handler(func=lambda m: m.text == "📊 Статистика")
def stats_command(message):
    show_stats(message.chat.id)

@bot.message_handler(func=lambda m: m.text == "🔙 Назад")
def back_to_main(message):
    start(message)

@bot.message_handler(func=lambda m: m.text == "🍳 Завтрак")
def show_breakfast(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    difficulty = user_data.get("difficulty", "простой")
    
    recipes = get_habits_by_category("завтрак")
    filtered = {}
    for name, data in recipes.items():
        if data.get("сложность") == difficulty:
            filtered[name] = data
    
    if not filtered:
        filtered = recipes
    
    user_data["last_category"] = "завтрак"
    user_data["last_recipes"] = filtered
    save_user_data(user_id, user_data)
    
    reply = format_recipe_list(filtered, "завтрак", difficulty)
    bot.send_message(user_id, reply, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🍲 Обед")
def show_lunch(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    difficulty = user_data.get("difficulty", "простой")
    
    recipes = get_habits_by_category("обед")
    filtered = {}
    for name, data in recipes.items():
        if data.get("сложность") == difficulty:
            filtered[name] = data
    
    if not filtered:
        filtered = recipes
    
    user_data["last_category"] = "обед"
    user_data["last_recipes"] = filtered
    save_user_data(user_id, user_data)
    
    reply = format_recipe_list(filtered, "обед", difficulty)
    bot.send_message(user_id, reply, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🍝 Ужин")
def show_dinner(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    difficulty = user_data.get("difficulty", "простой")
    
    recipes = get_habits_by_category("ужин")
    filtered = {}
    for name, data in recipes.items():
        if data.get("сложность") == difficulty:
            filtered[name] = data
    
    if not filtered:
        filtered = recipes
    
    user_data["last_category"] = "ужин"
    user_data["last_recipes"] = filtered
    save_user_data(user_id, user_data)
    
    reply = format_recipe_list(filtered, "ужин", difficulty)
    bot.send_message(user_id, reply, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "📋 Чеклист")
def manual_checklist(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    
    if not user_data.get("last_recipes"):
        bot.send_message(user_id, "❌ Сначала выбери категорию: Завтрак, Обед или Ужин!")
        return
    
    reply = format_recipe_list(
        user_data["last_recipes"],
        user_data.get("last_category", "блюд"),
        user_data.get("difficulty", "простой")
    )
    bot.send_message(user_id, reply, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🎲 Случайный рецепт")
def random_recipe(message):
    user_id = message.chat.id
    name = random.choice(list(RECIPES.keys()))
    recipe = RECIPES[name]
    send_recipe(user_id, name, recipe, show_add_button=True)

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) <= 2)
def handle_number(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    num = int(message.text.strip()) - 1
    
    recipes = user_data.get("last_recipes")
    if not recipes:
        bot.send_message(user_id, "❌ Сначала выбери категорию: Завтрак, Обед или Ужин!")
        return
    
    recipe_names = list(recipes.keys())
    if 0 <= num < len(recipe_names):
        name = recipe_names[num]
        recipe = recipes[name]
        send_recipe(user_id, name, recipe, show_add_button=True)
    else:
        bot.send_message(user_id, f"❌ Нет рецепта под номером {num + 1}. Попробуй от 1 до {len(recipe_names)}.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def ask_weight(call):
    user_id = call.message.chat.id
    recipe_name = call.data.replace("add_", "")
    
    user_data = get_user_data(user_id)
    user_data["pending_recipe"] = recipe_name
    user_data["pending_weight"] = True
    save_user_data(user_id, user_data)
    
    bot.send_message(
        user_id,
        f"📝 *{recipe_name.capitalize()}*\n\n"
        f"✏️ Напиши вес в граммах (например, 150):",
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text.isdigit() and m.chat.id in [int(uid) for uid in load_data().keys()])
def save_food_with_weight(message):
    user_id = message.chat.id
    user_data = get_user_data(user_id)
    
    if not user_data.get("pending_weight") or not user_data.get("pending_recipe"):
        return
    
    try:
        weight = float(message.text.strip())
        name = user_data["pending_recipe"]
        recipe = RECIPES[name]
        
        kcal = round(recipe["kcal_100"] * weight / 100, 1)
        protein = round(recipe["protein_100"] * weight / 100, 1)
        fat = round(recipe["fat_100"] * weight / 100, 1)
        carbs = round(recipe["carbs_100"] * weight / 100, 1)
        
        user_data["today_food"].append({
            "name": name,
            "weight": weight,
            "kcal": kcal,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        })
        
        user_data["pending_weight"] = False
        user_data["pending_recipe"] = None
        save_user_data(user_id, user_data)
        
        bot.send_message(
            user_id,
            f"✅ *{name.capitalize()}* — {weight} г добавлен в дневник!\n\n"
            f"📊 КБЖУ:\n"
            f"🔥 {kcal} ккал\n"
            f"💪 {protein} г белков\n"
            f"🧈 {fat} г жиров\n"
            f"🍚 {carbs} г углеводов",
            parse_mode='Markdown'
        )
    except:
        bot.reply_to(message, "❌ Напиши число, например 150")

@bot.message_handler(func=lambda m: True)
def handle_unknown(message):
    text = message.text.lower().strip()
    user_id = message.chat.id
    
    # Игнорируем кнопки и команды
    if text in ["🍳 завтрак", "🍲 обед", "🍝 ужин", "⚙️ настройки", "📊 статистика", "📋 чеклист", "🎲 случайный рецепт"]:
        return
    
    # Поиск по названию
    for name, recipe in RECIPES.items():
        if text in name.lower() or name.lower() in text:
            send_recipe(user_id, name, recipe, show_add_button=True)
            return
    
    bot.send_message(
        user_id,
        "😅 Я не нашёл такого рецепта.\n\n"
        "📋 Попробуй:\n"
        "• выбрать категорию (Завтрак/Обед/Ужин)\n"
        "• написать название блюда\n"
        "• нажать '🎲 Случайный рецепт'"
    )

# =============================================
# ЗАПУСК БОТА
# =============================================

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
