import telebot
import sqlite3
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from calories import *
from mealplannnn import *


API_KEY = "7954917621:AAEUxDwyimCq8jntMbeKeMC-jgQXyCae_WQ"
bot = telebot.TeleBot(API_KEY)
user_data = {}


@bot.message_handler(commands=['start', 'begin'])
def start_conversation(message):
    user_id = message.chat.id
    user_data[user_id] = {} 
    bot.send_photo(user_id, photo=open('Image.webp', 'rb'))
    bot.send_message(user_id, "Welcome! Let's get started 🍄 What's your Telegram username?")
    bot.register_next_step_handler(message, check_username)

def check_username(message):
    user_id = message.chat.id
    username = message.text
    user_data[user_id]['name'] = username 
    
    db = sqlite3.connect("HealthShroom.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ShroomDB WHERE Username=?", (username,))
    existing_user = cursor.fetchone()
    db.close()

    if existing_user:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Yes ✅", callback_data="update_yes"),
            InlineKeyboardButton("No ❌", callback_data="update_no")
        )
        bot.send_message(
            user_id, 
            f"Username {username} already exists. Would you like to update your information?", 
            reply_markup=keyboard
        )
    else:
        ask_gender(message)

def ask_gender(message):
    user_id = message.chat.id

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Female 👩", callback_data="gender_F"),
        InlineKeyboardButton("Male 👨", callback_data="gender_M")
    )

    bot.send_message(
        user_id,
        "Please select your gender:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("gender_"))
def handle_gender_response(call):
        user_id = call.message.chat.id
        gender = call.data.split("_")[1]

        try:
            user_data[user_id]['gender'] = gender

            gender_display = "Female 👩" if gender == "F" else "Male 👨"

            bot.send_message(
                chat_id=user_id,
                text=f"Thank you! Your gender has been set to {gender_display}"
            )

            bot.delete_message(
                    chat_id=user_id,
                    message_id=call.message.message_id
                )

            bot.send_message(user_id, "How old are you?")
            bot.register_next_step_handler(call.message, ask_age)

        except Exception as e:
            bot.send_message(user_id, "Sorry, there was an error saving your information. Please try again.")
            print(f"Error in handle_gender_response: {str(e)}")
            return ask_gender(call.message)

@bot.callback_query_handler(func=lambda call: call.data in ["update_yes", "update_no"])
def handle_update_response(call):
    user_id = call.message.chat.id

    if call.data == "update_yes":
        username = user_data[user_id]['name']
        db = sqlite3.connect("HealthShroom.db")
        cursor = db.cursor()
        cursor.execute("DELETE FROM ShroomDB WHERE Username=?", (username,))
        db.commit()
        db.close()

        ask_gender(call.message)

    elif call.data == "update_no":
        bot.send_message(user_id, "Okay, we won't update your information. You can contact support if you change your mind.")
        recommend_food(user_id)

    bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=None)

def ask_age(message):
    try:
        user_id = message.chat.id
        age = int(message.text)
        if 0 <= age <= 120:  
            user_data[user_id]['age'] = age
            bot.send_message(message.chat.id, "What's your current weight in kilograms?")
            bot.register_next_step_handler(message, ask_current_weight)
        else:
            bot.send_message(message.chat.id, "Please enter a valid age between 0 and 120.")
            bot.register_next_step_handler(message, ask_age)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number for your age.")
        bot.register_next_step_handler(message, ask_age)

def ask_current_weight(message):
    try:
        user_id = message.chat.id
        weight = float(message.text)
        if 20 <= weight <= 300: 
            user_data[user_id]['current_weight'] = weight
            bot.send_message(message.chat.id, "What's your goal weight in kilograms?")
            bot.register_next_step_handler(message, ask_goal_weight)
        else:
            bot.send_message(message.chat.id, "Please enter a valid weight between 20 and 300 kg.")
            bot.register_next_step_handler(message, ask_current_weight)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number for your weight.")
        bot.register_next_step_handler(message, ask_current_weight)

def ask_goal_weight(message):
    try:
        user_id = message.chat.id
        goal_weight = float(message.text)
        if 20 <= goal_weight <= 300:  
            user_data[user_id]['goal_weight'] = goal_weight
            bot.send_message(message.chat.id, "In how many months would you like to achieve this goal?")
            bot.register_next_step_handler(message, ask_time_period)
        else:
            bot.send_message(message.chat.id, "Please enter a valid weight between 20 and 300 kg.")
            bot.register_next_step_handler(message, ask_goal_weight)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number for your goal weight.")
        bot.register_next_step_handler(message, ask_goal_weight)

def ask_time_period(message):
    try:
        user_id = message.chat.id
        time_period = float(message.text)
        if 1 <= time_period <= 36:  
            user_data[user_id]['time'] = time_period
            bot.send_message(message.chat.id, "What is your height in centimeters?")
            bot.register_next_step_handler(message, summary)
        else:
            bot.send_message(message.chat.id, "Please enter a valid time period between 1 and 36 months.")
            bot.register_next_step_handler(message, ask_time_period)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number for the time period.")
        bot.register_next_step_handler(message, ask_time_period)

def summary(message):
    try:
        user_id = message.chat.id
        height = float(message.text)
        if 100 <= height <= 250:  
            user_data[user_id]['Height'] = height

            user_info = user_data[user_id]
            summary_text = (
                f"📋 Here is your profile:\n\n"
                f"👤 Username: {user_info['name']}\n"
                f"⚧ Gender: {'Female 👩' if user_info['gender'] == 'F' else 'Male 👨'}\n"
                f"🎂 Age: {user_info['age']}\n"
                f"⚖️ Current Weight: {user_info['current_weight']} kg\n"
                f"🎯 Goal Weight: {user_info['goal_weight']} kg\n"
                f"⏳ Time Period: {user_info['time']} months\n"
                f"📏 Height: {user_info['Height']} cm\n"
            )
            bot.send_message(user_id, summary_text)

            db = sqlite3.connect("HealthShroom.db")
            cursor = db.cursor()

            cursor.execute('''
            INSERT INTO "ShroomDB" (Username, Gender, Age, "Current Weight", "Goal Weight", "Time Period (Months)", Height)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_info['name'], user_info['gender'], user_info['age'], 
                user_info['current_weight'], user_info['goal_weight'], 
                user_info['time'], user_info['Height']))

            db.commit()
            db.close()

            send_confirmation_message(bot, user_id)
        else:
            bot.send_message(message.chat.id, "Please enter a valid height between 100 and 250 cm.")
            bot.register_next_step_handler(message, summary)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number for your height.")
        bot.register_next_step_handler(message, summary)

def send_confirmation_message(bot, user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Yes ✅", callback_data="confirm_yes"),
        InlineKeyboardButton("No ❌", callback_data="confirm_no")
    )

    bot.send_message(
        chat_id=user_id,
        text="Is this information correct?",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data in ["confirm_yes", "confirm_no"])
def handle_confirmation(call):
    user_id = call.message.chat.id

    if call.data == "confirm_yes":
        bot.send_message(user_id, "Great! Let's move on to recommend some food options. 🍽️")
        recommend_food(user_id)
    elif call.data == "confirm_no":
        bot.send_message(user_id, "Okay, let's restart. Please type /start to begin again.")

    bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=None)

def recommend_food(user_id):
    db = sqlite3.connect("HealthShroom.db")
    cursor = db.cursor()
    cursor.execute('''
    SELECT Age, "Current Weight", Height, Gender, "Goal Weight", "Time Period (Months)"
    FROM ShroomDB
    WHERE Username = ?''', (user_data[user_id]['name'],))

    user_info = cursor.fetchone()
    db.close()

    if user_info:
        age, weight, height, gender, gweight, time = user_info

        calorie_plan = calculate_calories_per_meal(age, weight, height, gender, gweight, time)  
        plan = generate_meal_plan("Food.csv", calorie_plan["Breakfast"], calorie_plan["Lunch"], calorie_plan["Dinner"])

        meal_plan_message = (
            "🍳 Here are your recommended food options:\n\n"
            f"🌅 Breakfast - {plan['Breakfast']}\n\n"
            f"☀️ Lunch - {plan['Lunch']}\n\n"
            f"🌙 Dinner - {plan['Dinner']}\n\n"
            f"📊 Total Calories: {plan['Total Calories']}"
        )

        bot.send_message(user_id, meal_plan_message)
    else:
        bot.send_message(user_id, "Sorry, I couldn't find your information. Please try registering again with /start")


bot.polling()