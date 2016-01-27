#!/usr/bin/python3
from gpiopins import GPIOSoda
from icecheck import IceTime
import w1
import logging
import telebot
import datetime

with open('api_key.txt') as key_file:
    API_KEY = key_file.readline().strip()

# Bot setup
bot = telebot.TeleBot(API_KEY)
telebot.logger.setLevel(logging.DEBUG)

# Startup GPIO pins
gpio = GPIOSoda()
ice_manager = IceTime(bot)

logging.basicConfig(format='[%(levelname)s:%(threadName)s:%(name)s:%(funcName)s] %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

commands = { # Command description in help text
    'getsodastatus': 'zeigt den Füllzustand meiner Fächer',
    'geticestatus': 'prüft die Eismaschine',
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

def __format_pin_states(pin_results):
    msg = ""
    for tray, status in pin_results.items():
        if status == 0:
            msg += "✅ "
        else:
            msg += "⚠ "

        msg += tray + "\n"
    return msg


@bot.message_handler(commands=['getsodastatus'])
def handle_soda_status(message):
    msg = "Füllstand der Getränkefächer:\n" + __format_pin_states(gpio.get_status_all())
    bot.reply_to(message, msg)


@bot.message_handler(commands=['geticestatus'])
def handle_ice_status(message):
    msg = "Eismaschine:\n" + __format_pin_states(ice_manager.get_status_all())
    bot.reply_to(message, msg)


@bot.message_handler(commands=['icemen'])
def notify_ice_change(message):
    if "stop" in message.text.lower():
        msg = "Ice-men für diesen Chat deaktiviert.\n"
        ice_manager.remove_listener(message.chat.id)
    else:
        msg = "Registrierung als Ice-men erfolgreich!\n\n"
        msg += "Wenn keine weiteren Benachrichtigungen mehr gewünscht sind, so einfach\n"
        msg += "  /icemen stop\n"
        msg += "senden."
        ice_manager.register_listener(message.chat.id)

    bot.reply_to(message, msg)


@bot.message_handler(func=lambda m: IceTime.check_reply(m.text, any_reply=True))
def empty_ice(message):
    # Only credit positive answers
    if IceTime.check_reply(message.text):
        print(message)
        ice_manager.empty_ice(message.from_user.first_name)


@bot.message_handler(commands=['gettemp'])
def handle_temp_status(message):
    msg = ''
    try:
        temp = w1.read_therm_sensor()
        msg = "Im Innenraum hat es gerade " + str(temp) + "°C."

    except IOError as e:
        log.error("W1 sensor not connected properly. Please check.")
        msg = "Ups, das weiß ich gerade auch nicht so genau. Mein Sensor ist offline. ".encode() \
          + b'\xF0\x9F\x98\x88'

    bot.reply_to(message, msg)


def handle_bier(message):
    msg = ""
    time = datetime.datetime.now()
    if time.hour > 7 and time.hour < 16:
        msg += "Kein Bier vor vier!!!\n"
        msg += "Bei mir ists jetzt " + time.strftime("%H:%M") + " Uhr."
    else:
        msg += "Prost 🍻 !"

    return msg


@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    """
    Handle all unknown commands or mentions with stupid answers :)
    """
    if message.text:
        if "dumm" in message.text.lower():
            bot.reply_to(message, "Nein, keinenfalls!")
        elif "bier" in message.text.lower():
            bot.reply_to(message, handle_bier(message))
        else:
            log.debug('Chat ID: %d, User: %s', message.chat.id, message.chat.username)
            bot.reply_to(message, "Awesome!")


# Start polling loop
bot.polling(timeout=30)
