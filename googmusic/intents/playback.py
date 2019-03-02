from flask_ask import statement, audio
from googmusic import app, ask, music_queue, client

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
def play_next():
    stream = _get_next()
    if stream is None:
        return audio('That was the last song').stop()
    return audio().play(stream)

@ask.intent("AMAZON.PreviousIntent")
def prev():
    stream = _get_prev()
    if stream is None:
        return audio('That was the first song').stop()
    return audio().play(stream)

@ask.on_playback_stopped()
def stopped(token, offset):
    queue.paused_offset = offset
    app.logger.debug("Playback of stream with token {} stopped at {}".format(token, offset))
    return empty_response()

@ask.on_playback_started()
def started(token, offset):
    app.logger.debug("Playback of stream with token {} started from {}".format(token, offset))
    return empty_response()

@ask.on_playback_nearly_finished()
def nearly_finished():
    stream = _get_next()
    if stream is None:
        return empty_response()
    return audio().enqueue(stream)

@ask.on_playback_finished()
def finished():
    return empty_response()

def _get_next():
    if len(music_queue) > 0:
        next_id = music_queue.next()['nid']
        app.logger.debug("Finding the next song with id: {}".format(next_id))
        stream = client.get_stream_url(next_id)
        app.logger.debug("Got stream url: {}".format(stream))
        return stream

def _get_prev():
    if len(music_queue) > 0:
        prev_id = music_queue.prev()['nid']
        app.logger.debug("Finding the previous song with the id: {}".format(prev_id))
        stream = client.get_stream_url(prev_id)
        app.logger.debug("Got stream url: {}".format(stream))
        return stream

def empty_response():
    return json.dumps({"response": {}, "version": "1.0"}), 200
