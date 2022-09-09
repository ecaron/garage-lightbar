"""Main Application"""
import os
import configparser
import json
import datetime
from multiprocessing import Process, Value, Lock, Array
from threading import Timer
from flask import Flask, render_template, request, redirect, send_from_directory

if not os.getenv("SKIP_LIGHTS"):
    import controls
if not os.getenv("SKIP_BUTTONS"):
    from gpiozero import Button  # pylint: disable=import-error

CONFIG = configparser.ConfigParser(strict=False, interpolation=None)
SETTINGS_CONF = os.getenv("SETTINGS_CONF")
if not SETTINGS_CONF:
    SETTINGS_CONF = "/tmp/settings.conf"
CONFIG.read(SETTINGS_CONF)

if "TIMERS" not in CONFIG:
    CONFIG["PATTERNS"] = {}
    CONFIG["PATTERNS"]["designs"] = "[]"
    CONFIG["TIMERS"] = {}
    CONFIG["TIMERS"]["TurnOn"] = "16:00"
    CONFIG["TIMERS"]["AutoOff"] = "4"
    with open(SETTINGS_CONF, mode="w", encoding="utf-8") as defaultfile:
        CONFIG.write(defaultfile)

app = Flask(__name__)


class LightState:
    """Controller of the light state settings"""

    def __init__(self):
        """Initializes the shared memory"""
        self.pattern = Array("c", bytearray(1024))
        self.brightness = Value("i", 0)
        self.power_on = Value("i", 0)
        self.lock = Lock()

    def toggle_power(self):
        """Gets the shared-memory power state"""
        with self.lock:
            if self.power_on.value == 0:
                self.power_on.value = 1
            else:
                self.power_on.value = 0

    def get_power(self):
        """Get the shared-memory power state"""
        with self.lock:
            return self.power_on.value

    def adjust_brightness(self):
        """Toggles the shared-memory brightness"""
        with self.lock:
            if self.brightness.value * 2 > 100:
                self.brightness.value = 5
            else:
                self.brightness.value = self.brightness.value * 2

    def get_brightness(self):
        """Gets the shared-memory brightness"""
        with self.lock:
            return self.brightness.value

    def set_pattern(self, pattern):
        """Toggles the shared-memory pattern"""
        with self.lock:
            self.pattern.value = bytes(pattern, "utf-8")

    def get_pattern(self):
        """Gets the shared-memory pattern"""
        with self.lock:
            return self.pattern.value.decode("utf-8")


PRESET_SPOT = 0
DAILY_TIMER = False
TURN_ON_TIMER = False
TURN_OFF_TIMER = False


def daily_reset():
    """Every morning, schedules the time that the lightbar should turn on"""
    global DAILY_TIMER, TURN_ON_TIMER  # pylint: disable=global-statement

    if DAILY_TIMER:
        DAILY_TIMER.cancel()

    time_tomorrow = datetime.datetime.combine(
        datetime.date.today() + datetime.timedelta(days=1), datetime.time(0)
    )
    time_now = datetime.datetime.now()
    time_diff = time_tomorrow - time_now

    DAILY_TIMER = Timer(time_diff.total_seconds(), daily_reset)
    DAILY_TIMER.start()

    if CONFIG["TIMERS"] and CONFIG["TIMERS"]["TurnOn"]:
        turn_on_time = datetime.datetime.strptime(
            CONFIG["TIMERS"]["TurnOn"], "%H:%M"
        ).time()
        turn_on_date_time = datetime.datetime.combine(
            datetime.date.today(), turn_on_time
        )
        if TURN_ON_TIMER:
            TURN_ON_TIMER.cancel()
        TURN_ON_TIMER = Timer((turn_on_date_time - time_now).total_seconds(), turn_on)
        TURN_ON_TIMER.start()


def turn_on():
    """Turns the lightbar on"""
    global TURN_OFF_TIMER  # pylint: disable=global-statement
    if LIGHT_STATE.get_power() == 0:
        LIGHT_STATE.toggle_power()
    if TURN_OFF_TIMER:
        TURN_OFF_TIMER.cancel()
    time_now = datetime.datetime.now()
    turn_off_time = datetime.datetime.now() + datetime.timedelta(
        hours=int(CONFIG["TIMERS"]["AutoOff"])
    )
    TURN_OFF_TIMER = Timer((turn_off_time - time_now).total_seconds(), turn_off)
    TURN_OFF_TIMER.start()


def turn_off():
    """Turns the lightbar off"""
    if LIGHT_STATE.get_power() == 1:
        LIGHT_STATE.toggle_power()


def adjust_brightness():
    """Cycles the lightbar's brightness"""
    LIGHT_STATE.adjust_brightness()


def next_preset():
    """Sends the next pattern to the lightbar"""
    global PRESET_SPOT  # pylint: disable=global-statement
    if LIGHT_STATE.get_power() == 0:
        LIGHT_STATE.toggle_power()
    patterns = json.loads(CONFIG["PATTERNS"]["designs"])
    if PRESET_SPOT + 1 >= len(patterns):
        PRESET_SPOT = 0
    else:
        PRESET_SPOT = PRESET_SPOT + 1
    run_preset(patterns[PRESET_SPOT])
    return 1


def prev_preset():
    """Sends the previous pattern to the lightbar"""
    global PRESET_SPOT  # pylint: disable=global-statement
    if LIGHT_STATE.get_power() == 0:
        LIGHT_STATE.toggle_power()
    patterns = json.loads(CONFIG["PATTERNS"]["designs"])
    if PRESET_SPOT <= 0:
        PRESET_SPOT = len(patterns) - 1
    else:
        PRESET_SPOT = PRESET_SPOT - 1
    run_preset(patterns[PRESET_SPOT])
    return 1


def run_preset(preset):
    """Sends a preset to the lightbar"""
    if LIGHT_STATE.get_power() == 0:
        LIGHT_STATE.toggle_power()
    LIGHT_STATE.set_pattern(preset)


DAILY_TIMER = Timer(1.0, daily_reset)
DAILY_TIMER.start()
LIGHT_STATE = LightState()

if not os.getenv("SKIP_BUTTONS"):
    button1 = Button(16)
    button1.when_released = next_preset

    button2 = Button(20)
    button2.when_released = prev_preset

    button3 = Button(26)
    button3.when_pressed = adjust_brightness

    button4 = Button(12)
    button4.when_pressed = LIGHT_STATE.toggle_power


@app.route("/button/<number>", methods=["GET"])
def button(number):
    """Handles when the virtual buttons are pushed"""
    if number == "4":
        LIGHT_STATE.toggle_power()
    elif number == "3":
        adjust_brightness()
    elif number == "2":
        prev_preset()
    else:
        next_preset()
    return "", 204


@app.route("/favicon.ico")
def favicon():
    """Returns a favicon"""
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/", methods=["GET", "POST"])
def index():
    """Serves & saves the web portal"""
    if request.method == "POST":
        if request.form["method"] == "run-pattern":
            run_preset(request.form["pattern"])
            return "", 204

        if request.form["method"] == "save-patterns":
            if "PATTERNS" not in CONFIG:
                CONFIG["PATTERNS"] = {}

            CONFIG["PATTERNS"]["designs"] = request.form["patterns"]
        else:
            if "TIMERS" not in CONFIG:
                CONFIG["TIMERS"] = {}

            CONFIG["TIMERS"]["TurnOn"] = request.form["turn_on"]
            CONFIG["TIMERS"]["AutoOff"] = request.form["auto_off"]
        with open(SETTINGS_CONF, mode="w", encoding="utf-8") as configfile:
            CONFIG.write(configfile)

        if request.form["method"] == "save-patterns":
            return "", 204
        return redirect("/", code=302)

    if "PATTERNS" in CONFIG:
        patterns = json.loads(CONFIG["PATTERNS"]["designs"])
    else:
        patterns = []

    if "TIMERS" in CONFIG:
        timers = CONFIG["TIMERS"]
    else:
        timers = {}
        timers["TurnOn"] = "16:00"
        timers["AutoOff"] = "4"
    return render_template("index.html", timers=timers, patterns=patterns)


if __name__ == "__main__":
    HOST = "127.0.0.1"
    if os.getenv("HOST"):
        HOST = os.getenv("HOST")
    PORT = 8000
    if os.getenv("PORT"):
        PORT = os.getenv("PORT")
    DEBUG = False
    if os.getenv("DEBUG"):
        DEBUG = os.getenv("DEBUG")
    RELOADER = False
    if os.getenv("RELOADER"):
        RELOADER = os.getenv("RELOADER")

    if not os.getenv("SKIP_LIGHTS"):
        p = Process(target=controls.lights, args=(LIGHT_STATE,))
        p.start()

    app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=RELOADER)

    if not os.getenv("SKIP_LIGHTS"):
        p.join()
