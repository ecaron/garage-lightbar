import os
from flask import Flask, render_template, request, redirect, send_from_directory
import configparser
import json
import adafruit_led_animation
config = configparser.ConfigParser()
config.read('settings.conf')
app = Flask(__name__)

@app.route('/button/<number>', methods=['GET'])
def button(number):
    print("Pressed number ", number)
    return redirect("/", code=302)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        config['TIMERS']['TurnOn'] = request.form['turn_on']
        config['TIMERS']['TurnOff'] = request.form['turn_off']
        config['TIMERS']['AutoOff'] = request.form['auto_off']
        with open('settings.conf', 'w') as configfile:
            config.write(configfile)
        return redirect("/", code=302)
    else:
        patterns = []
        for key in config['PATTERNS']:
            patterns.append(json.loads(config['PATTERNS'][key]))
        return render_template('index.html', timers=config['TIMERS'], patterns=patterns)

@app.route('/patterns', methods=['POST'])
def patterns():
    #Get inspiration from https://github.com/sanc909/C.H.I.P.-NeoPixel-SPI-Control-Visualiser/blob/master/ChipNeoController.py
    config['PATTERNS'] = {}
    for x in range(request.form['count']):
        config['PATTERNS']['pattern', x] = x
        with open('settings.conf', 'w') as configfile:
            config.write(configfile)
        return redirect("/", code=302)

if __name__ == '__main__':
    app.run(debug=True)
