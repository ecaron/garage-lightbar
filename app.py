"""Main Application"""
import os
import configparser
import json
import datetime
from multiprocessing import Process, Value, Lock, Array
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
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
    CONFIG["TIMERS"]["MicLevel"] = "5"
    CONFIG["TIMERS"]["TurnOn"] = ""
    CONFIG["TIMERS"]["TurnOff"] = ""
    CONFIG["TIMERS"]["AutoOff"] = ""
    with open(SETTINGS_CONF, mode="w", encoding="utf-8") as defaultfile:
        CONFIG.write(defaultfile)

app = Flask(__name__)
tz = pytz.timezone("US/Central")
scheduler = BackgroundScheduler(timezone=tz)


class LightState:
    """Controller of the light state settings"""

    def __init__(self):
        """Initializes the shared memory"""
        self.pattern = Array("c", bytearray(1024))
        self.mic_level = Value("i", int(CONFIG["TIMERS"]["MicLevel"]))
        self.brightness = Value("i", 100)
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

    def get_mic(self):
        """Gets the shared-memory mic level"""
        with self.lock:
            return self.mic_level.value

    def set_mic(self, level):
        """Sets the shared-memory mic level"""
        with self.lock:
            self.mic_level.value = int(level)

    def adjust_brightness(self):
        """Toggles the shared-memory brightness"""
        with self.lock:
            levels = [5, 10, 25, 50, 100]
            for i in levels:
                if self.brightness.value < i:
                    self.brightness.value = i
                    return
            self.brightness.value = 5

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


def toggle_power():
    """If on, turn off. If off, turn on"""
    if LIGHT_STATE.get_power() == 0:
        turn_on()
    else:
        turn_off()


def auto_on():
    """If light isn't already on, revert to first preset & turn on"""
    global PRESET_SPOT  # pylint: disable=global-statement
    if LIGHT_STATE.get_power() == 0:
        PRESET_SPOT = -1
        turn_on()


def turn_on():
    """Turns the lightbar on"""
    global PRESET_SPOT  # pylint: disable=global-statement
    if LIGHT_STATE.get_power() == 0:
        LIGHT_STATE.toggle_power()
        PRESET_SPOT = -1
        next_preset()


def set_auto_off():
    """Whenever there's activity with the let, move out the auto-off job"""
    if scheduler.get_job("auto_off"):
        scheduler.remove_job("auto_off")
    if CONFIG["TIMERS"]["AutoOff"] != "":
        off_time = datetime.datetime.now(tz) + datetime.timedelta(
            hours=int(CONFIG["TIMERS"]["AutoOff"])
        )
        scheduler.add_job(turn_off, "date", run_date=off_time)


def turn_off():
    """Turns the lightbar off"""
    if scheduler.get_job("auto_off"):
        scheduler.remove_job("auto_off")
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
    set_auto_off()


LIGHT_STATE = LightState()

if not os.getenv("SKIP_BUTTONS"):
    button1 = Button(16)
    button1.when_released = next_preset

    button2 = Button(20)
    button2.when_released = prev_preset

    button3 = Button(26)
    button3.when_pressed = adjust_brightness

    button4 = Button(12)
    button4.when_pressed = toggle_power


@app.route("/button/<number>", methods=["GET"])
def button(number):
    """Handles when the virtual buttons are pushed"""
    if number == "4":
        toggle_power()
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
def index():# pylint: disable=too-many-branches,too-many-statements
    """Serves & saves the web portal"""
    if request.method == "POST":
        if request.form["method"] == "power":
            os.system("systemctl poweroff")
            run_preset(request.form["pattern"])
            return "Powering Down", 200

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

            if CONFIG["TIMERS"]["MicLevel"] != request.form["mic_level"]:
                LIGHT_STATE.set_mic(request.form["mic_level"])
                CONFIG["TIMERS"]["MicLevel"] = request.form["mic_level"]
                if LIGHT_STATE.get_power() == 1:
                    turn_off()
                    turn_on()

            if (
                CONFIG["TIMERS"]["TurnOn"] != request.form["turn_on"]
                or CONFIG["TIMERS"]["TurnOff"] != request.form["turn_off"]
                or CONFIG["TIMERS"]["AutoOff"] != request.form["auto_off"]
            ):
                if request.form["turn_on"] == "":
                    if scheduler.get_job("daily_run"):
                        scheduler.remove_job("daily_run")
                else:
                    time_parts = request.form["turn_on"].split(":")
                    if scheduler.get_job("daily_run"):
                        scheduler.reschedule_job(
                            "daily_run",
                            trigger="cron",
                            hour=time_parts[0],
                            minute=time_parts[1],
                        )
                    else:
                        scheduler.add_job(
                            turn_on,
                            "cron",
                            hour=time_parts[0],
                            minute=time_parts[1],
                            id="daily_run",
                        )

                if request.form["turn_off"] == "":
                    if scheduler.get_job("daily_off"):
                        scheduler.remove_job("daily_off")
                else:
                    time_parts = request.form["turn_off"].split(":")
                    if scheduler.get_job("daily_off"):
                        scheduler.reschedule_job(
                            "daily_off",
                            trigger="cron",
                            hour=time_parts[0],
                            minute=time_parts[1],
                        )
                    else:
                        scheduler.add_job(
                            turn_off,
                            "cron",
                            hour=time_parts[0],
                            minute=time_parts[1],
                            id="daily_off",
                        )

                if request.form["auto_off"] == "":
                    if scheduler.get_job("auto_off"):
                        scheduler.remove_job("auto_off")

                CONFIG["TIMERS"]["TurnOn"] = request.form["turn_on"]
                CONFIG["TIMERS"]["TurnOff"] = request.form["turn_off"]
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
        timers["TurnOn"] = ""
        timers["AutoOff"] = ""
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

    if not app.debug:
        if CONFIG["TIMERS"]["TurnOn"] != "":
            launch_time_parts = CONFIG["TIMERS"]["TurnOn"].split(":")
            scheduler.add_job(
                turn_on,
                "cron",
                hour=launch_time_parts[0],
                minute=launch_time_parts[1],
                id="daily_run",
            )
        if CONFIG["TIMERS"]["TurnOff"] != "":
            launch_time_parts = CONFIG["TIMERS"]["TurnOff"].split(":")
            scheduler.add_job(
                turn_off,
                "cron",
                hour=launch_time_parts[0],
                minute=launch_time_parts[1],
                id="daily_off",
            )
        scheduler.start()

    app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=RELOADER)

    if not os.getenv("SKIP_LIGHTS"):
        p.join()
