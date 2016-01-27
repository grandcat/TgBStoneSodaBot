#!/usr/bin/python3

import pigpio
from telebot import types


class IceTime:

    PIN_FAULT = 24       # 5
    PIN_EMPTY_ICE = 23   # 6

    TEXT_YES = "Ich machs"
    TEXT_NO = "Keine Zeit"

    def __init__(self, telebot):
        self.bot = telebot
        self.registered_chats = []
        self.looking_for_icemen = False

        # Setup GPIO ISRs
        self.gpio = pigpio.pi()
        # Empty ice ISR
        self.gpio.set_mode(self.PIN_EMPTY_ICE, pigpio.INPUT)
        self.gpio.set_glitch_filter(self.PIN_EMPTY_ICE, 300000)
        self.gpio.set_pull_up_down(self.PIN_EMPTY_ICE, pigpio.PUD_UP)
        self.gpio.callback(self.PIN_EMPTY_ICE, pigpio.EITHER_EDGE, self.handle_ice_status_changed)
        # Fault condition ISR
        self.gpio.set_mode(self.PIN_FAULT, pigpio.INPUT)
        self.gpio.set_glitch_filter(self.PIN_FAULT, 300000)
        self.gpio.set_pull_up_down(self.PIN_FAULT, pigpio.PUD_UP)
        self.gpio.callback(self.PIN_FAULT, pigpio.EITHER_EDGE, self.handle_icemaker_fault)

    def __send_text_to_listeners(self, text, markup=None):
        for chat_id in self.registered_chats:
              self.bot.send_message(chat_id, text, reply_markup=markup)

    def register_listener(self, chat_id):
        if chat_id not in self.registered_chats:
            self.registered_chats.append(chat_id)
            print("Registering chat " + str(chat_id) + " for ice messages.")

    def remove_listener(self, chat_id):
        if chat_id in self.registered_chats:
            self.registered_chats.remove(chat_id)

    @staticmethod
    def check_reply(message_text, any_reply=False):
        if IceTime.TEXT_YES in message_text:
            return True
        elif (IceTime.TEXT_NO in message_text) and any_reply:
            return True
        else:
            return False

    def empty_ice(self, icemen_name):
        if self.looking_for_icemen:
            self.looking_for_icemen = False
            self.__send_text_to_listeners("👍 Vielen Dank, {0}!".format(icemen_name))

    def handle_ice_status_changed(self, gpio, level, tick):
       if level == 1:
          print("Rising edge detected at", tick)
          self.looking_for_icemen = False

          self.__send_text_to_listeners("✅ Eisfach ok", markup=types.ReplyKeyboardHide())

       else:
          print("Falling edge detected at", tick)
          self.looking_for_icemen = True

          keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
          keyboard.row(self.TEXT_YES)
          keyboard.row(self.TEXT_NO)
          self.__send_text_to_listeners("❄️❄️❄️❄️ Eisfach voll \nKann es jemand kurz leeren?", markup=keyboard)

    def handle_icemaker_fault(self, gpio, level, tick):
        if level == 0:
            print("Icemaker fault (falling edge)")
            self.__send_text_to_listeners("❌ Fehler an der Eismaschine erkannt (FAULT)")

        else:
            print("Icemaker running (rising edge)")
            self.__send_text_to_listeners("✅ Eismaschine sollte laufen (NO FAULT)")

    def get_status_all(self):
        res = {}

        PINS = {'Eisbox': self.PIN_EMPTY_ICE, 'Fehlerzustand': self.PIN_FAULT}
        for name, pin_ID in PINS.items():
            pinState = not self.gpio.read(pin_ID)
            res[name] = pinState

        return res