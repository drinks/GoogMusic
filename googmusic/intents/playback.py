import json
from flask_ask import statement, audio
from googmusic import app, ask, music_queue, client
from googmusic.utils.s3manager import S3Manager

s3 = S3Manager(app.config['AWS_BUCKET_NAME'])

@ask.intent('AMAZON.CancelIntent')
def cancel():
    return audio().stop()

@ask.intent("AMAZON.PauseIntent")
def pause():
    return audio('Pausing').stop()

@ask.intent("AMAZON.ResumeIntent")
def resume():
    return audio('Resuming').resume()

@ask.intent("AMAZON.NextIntent")
def next():
    song = music_queue.next()
    if song is None:
        return audio('That was the last song').stop()
    url = _get_and_enqueue(song)
    return audio().play(url)

@ask.intent("AMAZON.PreviousIntent")
def prev():
    song = music_queue.prev()
    if song is None:
        return audio('That was the first song').stop()
    url = _get_and_enqueue(song)
    return audio().play(url)

@ask.intent("GoogMusicCurrentSongIntent")
def identify():
    song = music_queue.current()
    return audio("This is {} by {}".format(song['title'], song['artist']))

@ask.on_playback_stopped()
def stopped(token, offset):
    music_queue.paused_offset = offset
    app.logger.debug("Playback of stream with token {} stopped at {}".format(token, offset))
    return empty_response()

@ask.on_playback_started()
def started(token, offset):
    app.logger.debug("Playback of stream with token {} started from {}".format(token, offset))
    return empty_response()

@ask.on_playback_nearly_finished()
def nearly_finished():
    song = music_queue.up_next()
    if song is None:
        return empty_response()
    url = _get_and_enqueue(song)
    return audio().enqueue(url)

@ask.on_playback_finished()
def finished():
    music_queue.next()
    return empty_response()

def _get_and_enqueue(song):
    nid = song['nid']
    app.logger.debug("Finding song with id{}".format(nid))
    stream = client.get_stream_url(nid)
    s3_url = s3.ensure_file_exists(nid, stream)
    app.logger.debug("Got s3_url: {} for stream url: {}".format(s3_url, stream))
    return s3_url

def empty_response():
    return json.dumps({"response": {}, "version": "1.0"}), 200
