from flask import Flask, request
from flask_ask import Ask, statement
from gmusicapi import Mobileclient

app = Flask(__name__)
app.config.from_object('config')

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

ask = Ask(app, '/alexa')

client = Mobileclient()

print('Logging in as:', app.config['GOOGLE_EMAIL'], 'with ANDROID_ID', app.config['ANDROID_ID'])

if client.login(app.config['GOOGLE_EMAIL'], app.config['GOOGLE_PASSWORD'], app.config['ANDROID_ID']):
    print('Login successful!')
else:
    raise Exception('Login failed')

from . import utils
musicman = utils.musicmanager.MusicManager(client)
music_queue = utils.queue.MusicQueue()

from . import intents
