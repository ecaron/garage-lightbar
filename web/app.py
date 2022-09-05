import os
import configparser
import json
from controls import power, brightness,  cycle
from flask import Flask, render_template, request, redirect, send_from_directory

config = configparser.ConfigParser(strict=False, interpolation=None)
settings_conf = os.getenv('SETTINGS_CONF')
if not settings_conf:
    settings_conf = '/tmp/settings.conf'
config.read(settings_conf)

app = Flask(__name__)

@app.route('/button/<number>', methods=['GET'])
def button(number):
    if number == "4":
        power()
    elif number == "3":
        brightness()
    else:
        cycle()
    return '', 204

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['method'] == 'save-patterns':
            if 'PATTERNS' not in config:
                config['PATTERNS'] = {}

            config['PATTERNS']['designs'] = request.form['patterns']
        else:
            if 'TIMERS' not in config:
                config['TIMERS'] = {}

            config['TIMERS']['TurnOn'] = request.form['turn_on']
            config['TIMERS']['TurnOff'] = request.form['turn_off']
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
        timers['TurnOff'] = '22:00'
        timers['AutoOff'] = '4'
    return render_template('index.html', timers=timers, patterns=patterns)

if __name__ == '__main__':
    host = '127.0.0.1'
    if os.getenv('HOST'):
        host = os.getenv('HOST')
    port = 8000
    if os.getenv('PORT'):
        port = os.getenv('PORT')
    app.run(host=host,port=port,debug=True)
