import os
import configparser
import json
if not os.getenv('SKIP_LIGHTS'):
    import controls
from multiprocessing import Process, Value, Lock
from flask import Flask, render_template, request, redirect, send_from_directory

if not os.getenv('SKIP_BUTTONS'):
    from gpiozero import Button

config = configparser.ConfigParser(strict=False, interpolation=None)
settings_conf = os.getenv('SETTINGS_CONF')
if not settings_conf:
    settings_conf = '/tmp/settings.conf'
config.read(settings_conf)

app = Flask(__name__)

class LightState(object):
    def __init__(self):
        self.patterns = Value('i', 0)
        self.power_on = Value('i', 0)
        self.patterns = Value('i', 0)
        self.sequence_spot = Value('i', 0)
        self.lock = Lock()

    def toggle_power(self):
        with self.lock:
            if self.power_on.value == 0:
                self.power_on.value = 1
            else:
                self.power_on.value = 0

    def get_power(self):
        with self.lock:
            return self.power_on.value

lightState = LightState()

def adjust_brightness():
    return 1

def next_preset():
    return 1
def prev_preset():
    return 1

if not os.getenv('SKIP_BUTTONS'):
    button1 = Button(16)
    button1.when_released = next_preset

    button2 = Button(20)
    button2.when_released = prev_preset

    button3 = Button(26)
    button3.when_pressed = adjust_brightness

    button4 = Button(12)
    button4.when_pressed = lightState.toggle_power

@app.route('/button/<number>', methods=['GET'])
def button(number):
    if number == '4':
        lightState.toggle_power()
    elif number == '3':
        adjust_brightness()
    elif number == '2':
        next_preset()
    else:
        prev_preset()
    return '', 204

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['method'] == 'run-pattern':
            print (request.form['pattern'])
            return '', 204

        if request.form['method'] == 'save-patterns':
            if 'PATTERNS' not in config:
                config['PATTERNS'] = {}

            config['PATTERNS']['designs'] = request.form['patterns']
        else:
            if 'TIMERS' not in config:
                config['TIMERS'] = {}

            config['TIMERS']['TurnOn'] = request.form['turn_on']
            config['TIMERS']['AutoOff'] = request.form['auto_off']
        with open(settings_conf, 'w') as configfile:
            config.write(configfile)

        if request.form['method'] == 'save-patterns':
            return '', 204
        else:
            return redirect("/", code=302)

    if 'PATTERNS' in config:
        patterns = json.loads(config['PATTERNS']['designs'])
    else:
        patterns = []

    if 'TIMERS' in config:
        timers = config['TIMERS']
    else:
        timers = {}
        timers['TurnOn'] = '16:00'
        timers['AutoOff'] = '4'
    return render_template('index.html', timers=timers, patterns=patterns)

if __name__ == '__main__':
    host = '127.0.0.1'
    if os.getenv('HOST'):
        host = os.getenv('HOST')
    port = 8000
    if os.getenv('PORT'):
        port = os.getenv('PORT')
    debug = False
    if os.getenv('DEBUG'):
        debug = os.getenv('DEBUG')
    reloader = False
    if os.getenv('RELOADER'):
        reloader = os.getenv('RELOADER')

    if not os.getenv('SKIP_LIGHTS'):
        p = Process(target=controls.lights, args=(lightState,))
        p.start()

    app.run(host=host,port=port,debug=debug, use_reloader=reloader)

    if not os.getenv('SKIP_LIGHTS'):
        p.join()
