from flask_ask import statement, audio
from googmusic import ask, music_queue, client

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
    stream = _get_prev()
    return audio('That was the last song').stop() if stream is None
    return audio().play(stream)

@ask.intent("AMAZON.PreviousIntent")
def prev():
    stream = _get_prev()
    return audio('That was the first song').stop() if stream is None
    return audio().play(stream)

@ask.on_playback_nearly_finished()
def enqueue_next():
    stream = _get_next()
    return audio().stop() if stream is None
    return audio().enqueue(stream)

def _get_next():
    if len(music_queue) > 0:
        next_id = music_queue.next()['nid']
        print('Enqueuing next song with id: %s' % next_id)

        stream = client.get_stream_url(next_id)
        print('Got stream url: %s' % stream)
        return stream

def _get_prev():
    if len(music_queue) > 0:
        prev_id = music_queue.prev()['nid']
        print('Enqueuing previous song with id: %s' % prev_id)

        stream = client.get_stream_url(prev_id)
        print('Got stream url: %s' % stream)
        return stream