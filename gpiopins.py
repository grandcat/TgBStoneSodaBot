import logging
import wiringpi2


class GPIOSoda:
    GPIO_INPUT = 0
    GPIO_PUD_DOWN = 1

    # BCM port mapping
    PINS = {'MATE': 17, 'ADEL': 18, 'SPEZI': 21, 'RADLER': 22, 'TEGERN': 23, 'GUSTL': 24}  # 'EIS': 25

    def __init__(self):
        self.log = logging.getLogger(__name__)
        # Setup GPIO pins
        # This routine uses /sys/class/gpio for non-root access.
        # Attention: export all pins beforehand (done by launcher.sh at the moment)
        wiringpi2.wiringPiSetupSys()
        # Inputs
        for key, value in self.PINS.items():
            self.log.debug('Setting up pin %d for "%s"', value, key)
            # Set input mode
            wiringpi2.pinMode(value, self.GPIO_INPUT)
            # Pull pin down to ground
            wiringpi2.pullUpDnControl(value, self.GPIO_PUD_DOWN)

    def get_status(self, port_name):
        pin = self.PINS[port_name]
        if pin is None:
            self.log.error('Provided port "%s" not found.', port_name)
            return -1

        return wiringpi2.digitalRead(pin)

    def get_status_all(self):
        res = {}

        for name, pin_ID in self.PINS.items():
            pinState = wiringpi2.digitalRead(pin_ID)
            res[name] = pinState

        return res

# TEST
# logging.basicConfig(format='[%(levelname)s:%(threadName)s:%(name)s:%(funcName)s] %(message)s', level=logging.DEBUG)
#
# gpio = GPIOSoda()
# while True:
#     # print("Mate Pin: ", gpio.get_status('MATE'))
#     print(gpio.get_status_all())
#     time.sleep(2)