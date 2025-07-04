import telebot
import os
from dotenv import load_dotenv
from telebot import types
import random
import time

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

# Словарь для хранения игровых сессий пользователей
user_games = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🎮 Играть"))
    markup.add(types.KeyboardButton("📊 Статистика"), types.KeyboardButton("ℹ️ Помощь"))
    
    bot.send_message(
        message.chat.id, 
        f"🎮 Добро пожаловать в NoFan Game Bot!\n\n"
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Я игровой бот с крутыми мини-играми.\n\n"
        f"Выберите действие из меню ниже:",
        reply_markup=markup
    )

@bot.message_handler(commands=['game'])
def start_game(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎯 Быстрая игра", callback_data="quick_game"))
    markup.add(types.InlineKeyboardButton("🎲 Игра на удачу", callback_data="luck_game"))
    markup.add(types.InlineKeyboardButton("⚡ Тест реакции", callback_data="reaction_test"))
    markup.add(types.InlineKeyboardButton("🏆 Лидерборд", callback_data="leaderboard"))
    
    bot.send_message(
        message.chat.id,
        "🎯 NoFan Game - Выберите игру!\n\n"
        "🎮 Доступные игры:\n"
        "• 🎯 Быстрая игра - случайные очки\n"
        "• 🎲 Игра на удачу - угадай число\n"
        "• ⚡ Тест реакции - кликай быстро\n\n"
        "Готовы начать?",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = """
🎮 NoFan Game Bot - Помощь

📋 Доступные команды:
/start - Главное меню
/game - Запустить игру
/stats - Ваша статистика
/help - Эта справка

🎯 Доступные игры:
• 🎯 Быстрая игра - получите случайные очки
• 🎲 Игра на удачу - угадайте число от 1 до 10
• ⚡ Тест реакции - нажимайте кнопки быстро

💡 Советы:
• Играйте регулярно для улучшения результатов
• Приглашайте друзей для большего веселья
• Следите за своим прогрессом в статистике
    """
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.from_user.id
    if user_id in user_games:
        games_played = len(user_games[user_id])
        total_score = sum(user_games[user_id])
        best_score = max(user_games[user_id]) if user_games[user_id] else 0
        avg_score = total_score // games_played if games_played > 0 else 0
    else:
        games_played = 0
        total_score = 0
        best_score = 0
        avg_score = 0
    
    stats_text = f"""
📊 Статистика игрока {message.from_user.first_name}

🏆 Лучший результат: {best_score} очков
🎯 Всего игр: {games_played}
⚡ Средний результат: {avg_score} очков
🎮 Общий счет: {total_score} очков

{"Отличная статистика! 🌟" if games_played > 10 else "Начните играть, чтобы улучшить статистику!"}
    """
    bot.send_message(message.chat.id, stats_text)

@bot.message_handler(func=lambda message: message.text == "🎮 Играть")
def play_button(message):
    start_game(message)

@bot.message_handler(func=lambda message: message.text == "📊 Статистика")
def stats_button(message):
    show_stats(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def help_button(message):
    help_message(message)

@bot.callback_query_handler(func=lambda call: call.data == "quick_game")
def quick_game(call):
    user_id = call.from_user.id
    score = random.randint(50, 300)
    
    # Сохраняем результат
    if user_id not in user_games:
        user_games[user_id] = []
    user_games[user_id].append(score)
    
    bot.answer_callback_query(call.id, "🎉 Игра завершена!")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Играть еще", callback_data="quick_game"))
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="show_stats"))
    
    bot.send_message(
        call.message.chat.id,
        f"🎉 Быстрая игра завершена!\n\n"
        f"🏆 Ваш результат: {score} очков\n"
        f"⚡ {'Отличный результат!' if score > 200 else 'Хороший результат!' if score > 150 else 'Попробуйте еще раз!'}",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "luck_game")
def luck_game(call):
    bot.answer_callback_query(call.id)
    
    markup = types.InlineKeyboardMarkup()
    for i in range(1, 11):
        markup.add(types.InlineKeyboardButton(f"{i}", callback_data=f"guess_{i}"))
    
    bot.send_message(
        call.message.chat.id,
        "🎲 Игра на удачу!\n\n"
        "🎯 Угадайте число от 1 до 10\n"
        "🏆 Угадали = 100 очков\n"
        "⚡ Не угадали = 10 очков за попытку\n\n"
        "Выберите число:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("guess_"))
def handle_guess(call):
    user_id = call.from_user.id
    user_guess = int(call.data.split("_")[1])
    winning_number = random.randint(1, 10)
    
    if user_guess == winning_number:
        score = 100
        result_text = f"🎉 ПОЗДРАВЛЯЕМ!\n\n🎯 Вы угадали число {winning_number}!\n🏆 Получено: {score} очков"
    else:
        score = 10
        result_text = f"😔 Не угадали!\n\n🎯 Было число: {winning_number}\n🎲 Ваше число: {user_guess}\n🏆 Получено: {score} очков за попытку"
    
    # Сохраняем результат
    if user_id not in user_games:
        user_games[user_id] = []
    user_games[user_id].append(score)
    
    bot.answer_callback_query(call.id, "🎲 Результат готов!")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Играть еще", callback_data="luck_game"))
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="show_stats"))
    
    bot.send_message(call.message.chat.id, result_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "reaction_test")
def reaction_test(call):
    bot.answer_callback_query(call.id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 СТАРТ", callback_data="start_reaction"))
    
    bot.send_message(
        call.message.chat.id,
        "⚡ Тест реакции!\n\n"
        "🎯 Правила:\n"
        "• Нажмите СТАРТ\n"
        "• Дождитесь кнопки КЛИК\n"
        "• Нажмите как можно быстрее!\n"
        "• Чем быстрее - тем больше очков\n\n"
        "Готовы?",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "start_reaction")
def start_reaction_test(call):
    bot.answer_callback_query(call.id, "⏳ Приготовьтесь...")
    
    # Случайная задержка от 2 до 5 секунд
    delay = random.randint(2, 5)
    
    bot.send_message(
        call.message.chat.id,
        f"⏳ Приготовьтесь...\n\n"
        f"🎯 Кнопка появится через {delay} секунд\n"
        f"⚡ Будьте готовы нажать быстро!"
    )
    
    # Сохраняем время начала
    start_time = time.time() + delay
    
    # Отправляем кнопку через delay секунд
    time.sleep(delay)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔥 КЛИК!", callback_data=f"reaction_click_{start_time}"))
    
    bot.send_message(
        call.message.chat.id,
        "🔥 СЕЙЧАС! НАЖИМАЙТЕ!",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("reaction_click_"))
def handle_reaction_click(call):
    user_id = call.from_user.id
    start_time = float(call.data.split("_")[2])
    reaction_time = time.time() - start_time
    
    # Рассчитываем очки на основе времени реакции
    if reaction_time < 0.5:
        score = 200
        rating = "🏆 МОЛНИЕНОСНО!"
    elif reaction_time < 1.0:
        score = 150
        rating = "⚡ ОТЛИЧНО!"
    elif reaction_time < 1.5:
        score = 100
        rating = "👍 ХОРОШО!"
    elif reaction_time < 2.0:
        score = 50
        rating = "😐 НОРМАЛЬНО"
    else:
        score = 25
        rating = "🐌 МЕДЛЕННО"
    
    # Сохраняем результат
    if user_id not in user_games:
        user_games[user_id] = []
    user_games[user_id].append(score)
    
    bot.answer_callback_query(call.id, f"{rating}")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Играть еще", callback_data="reaction_test"))
    markup.add(types.InlineKeyboardButton("📊 Статистика", callback_data="show_stats"))
    
    bot.send_message(
        call.message.chat.id,
        f"⚡ Тест реакции завершен!\n\n"
        f"⏱️ Время реакции: {reaction_time:.2f} сек\n"
        f"🏆 Результат: {score} очков\n"
        f"🎯 Оценка: {rating}",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "show_stats")
def show_stats_callback(call):
    user_id = call.from_user.id
    if user_id in user_games:
        games_played = len(user_games[user_id])
        total_score = sum(user_games[user_id])
        best_score = max(user_games[user_id]) if user_games[user_id] else 0
        avg_score = total_score // games_played if games_played > 0 else 0
    else:
        games_played = 0
        total_score = 0
        best_score = 0
        avg_score = 0
    
    bot.answer_callback_query(call.id)
    
    stats_text = f"""
📊 Статистика игрока {call.from_user.first_name}

🏆 Лучший результат: {best_score} очков
🎯 Всего игр: {games_played}
⚡ Средний результат: {avg_score} очков
🎮 Общий счет: {total_score} очков

{"Отличная статистика! 🌟" if games_played > 10 else "Продолжайте играть!"}
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎮 Играть еще", callback_data="back_to_games"))
    
    bot.send_message(call.message.chat.id, stats_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_games")
def back_to_games(call):
    bot.answer_callback_query(call.id)
    start_game(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "leaderboard")
def show_leaderboard(call):
    # Создаем фейковый лидерборд для демонстрации
    leaderboard_text = """
🏆 Топ игроков NoFan Game

1. 👑 Игрок1 - 1500 очков
2. 🥈 Игрок2 - 1200 очков  
3. 🥉 Игрок3 - 1000 очков
4. 🏅 Игрок4 - 800 очков
5. 🏅 Игрок5 - 600 очков

Играйте больше, чтобы попасть в топ!
    """
    bot.answer_callback_query(call.id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎮 Играть", callback_data="back_to_games"))
    
    bot.send_message(call.message.chat.id, leaderboard_text, reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    # Обработка данных из игры (пока не используется)
    import json
    try:
        data = json.loads(message.web_app_data.data)
        score = data.get('score', 0)
        
        bot.send_message(
            message.chat.id,
            f"🎉 Отличная игра!\n\n"
            f"🏆 Ваш результат: {score} очков\n"
            f"⚡ Продолжайте играть для улучшения результата!"
        )
    except:
        bot.send_message(message.chat.id, "❌ Ошибка при обработке результата игры")

if __name__ == "__main__":
    print("🚀 NoFan Game Bot запущен!")
    bot.polling(none_stop=True)
