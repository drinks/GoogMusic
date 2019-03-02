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
def next():
    if len(music_queue) > 0:
        next_id = music_queue.next()['nid']
        print('Enqueuing next song with id: %s' % next_id)

        stream = client.get_stream_url(next_id)
        print('Got stream url: %s' % stream)

        return audio().enqueue(stream)

@ask.intent("AMAZON.PreviousIntent")
def prev():
    if len(music_queue) > 0:
        prev_id = music_queue.prev()['nid']
        print('Enqueuing previous song with id: %s' % prev_id)

        stream = client.get_stream_url(prev_id)
        print('Got stream url: %s' % stream)

        return audio().enqueue(stream)

@ask.on_playback_nearly_finished()
def nearly_finished():
    next()

@ask.on_playback_finished()
def finished():
    pass