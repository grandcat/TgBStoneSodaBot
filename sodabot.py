#!/usr/bin/python3
from gpiopins import GPIOSoda
import logging
import telebot

with open('api_key.txt') as key_file:
    API_KEY = key_file.readline().strip()

print('API Key: ', API_KEY)

# Bot setup
bot = telebot.TeleBot(API_KEY)
telebot.logger.setLevel(logging.DEBUG)

# Startup GPIO pins
gpio = GPIOSoda()

logging.basicConfig(format='[%(levelname)s:%(threadName)s:%(name)s:%(funcName)s] %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

commands = { # Command description in help text
    'getsodastatus': 'zeigt den Füllzustand meiner Fächer',
    'gettemp': 'zeigt die Temperatur im Inneren'
}

@bot.message_handler(commands=['help', 'start'])
def handle_help(message):
    name = message.chat.first_name or "zusammen"
    msg = "Hi " + name + ",\n" \
          "ich bin der BStone Getränkeautomat aus Haus 4.\n" \
          "Wenn du wissen willst, wie es mir gerade geht, probier doch mal folgendes:\n\n"
    # Add all commands with description
    for cmd, desc in commands.items():
        msg += "/"+cmd + " - " + desc + "\n"

    bot.reply_to(message, msg)

@bot.message_handler(commands=['getsodastatus'])
def handle_soda_status(message):
    msg = "Füllstand der Getränkefächer:\n"

    for tray, status in gpio.get_status_all().items():
        if status == 0:
            msg += "✅ "
        else:
            msg += "⚠ "

        msg += tray + "\n"

    bot.reply_to(message, msg)

@bot.message_handler(commands=['gettemp'])
def handle_temp_status(message):
    msg = "Ups, das weiß ich gerade auch nicht so genau. Mir fehlt noch ein passender Sensor. ".encode() \
          + b'\xF0\x9F\x98\x88'

    bot.reply_to(message, msg)


@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    """
    Handle all unknown commands or mentions with stupid answers :)
    """
    if message.text:
        if "dumm" in message.text.lower():
            bot.reply_to(message, "Nein, keinenfalls!")
        else:
            log.debug('Chat ID: %d, User: %s', message.chat.id, message.chat.username)
            bot.reply_to(message, "Awesome!")

# Start polling loop
bot.polling(timeout=30)