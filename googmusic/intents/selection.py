from flask_ask import statement, audio, question
from googmusic import ask, app, musicman, client, music_queue
from fuzzywuzzy import fuzz, process

@ask.launch
def login():
    text = 'Welcome to Google Music ' \
           'Try asking me to play a song'
    prompt = 'For example say, play music by Nirvana'
    return question(text).reprompt(prompt).simple_card(title='Welcome to Google Music!', content='Try asking me to play a song')

@ask.intent("GoogMusicPlaySongIntent")
def play_song(song_name, artist_name):
    print('Fetching song %s by %s' % (song_name, artist_name))

    song = musicman.get_song(song_name, artist_name)
    if song is False:
        return statement('Sorry, I couldn\' find that song')

    print('storeId', song['storeId'])

    stream_url = client.get_stream_url(song['storeId'])
    print(stream_url)

    return audio('Playing %s' % song_name).play(stream_url)

@ask.intent('GoogMusicPlayArtistIntent')
def play_artist(artist_name):
    print('Fetching songs by artist: %s' % artist_name)

    artist = musicman.get_artist(artist_name)

    artist_info = client.get_artist_info(artist, include_albums = False, max_top_tracks=25, max_rel_artist=0)
    top_tracks = artist_info['topTracks']

    if not top_tracks:
        return statement('I\'m sorry, I couldn\'t find that artist')

    music_queue.clear()
    for track in top_tracks:
        music_queue.enqueue(track)

    return audio('Playing top 25 tracks by %s' % artist_info['name']).play(client.get_stream_url(music_queue.current()['storeId']))

@ask.intent('GoogMusicPlayGenreRadioIntent')
def play_genre_radio(genre_name):
    genres = client.get_genres()

    g_id = None

    for g in genres:
        if fuzz.partial_ratio(genre_name, g['name']) > 75:
            g_id = g['id']

    if g_id == None:
        return statement('Sorry, I couldn\'t find that genre')

    station = client.create_station(genre_name, genre_id=g_id)

    tracks = client.get_station_tracks(station, num_tracks=50)
    music_queue.clear()
    for track in tracks:
        music_queue.enqueue(track)
        #print(track['nid'])

    return audio('You have selected %s radio' % str(g_id)).play(client.get_stream_url(music_queue.current()['storeId']))

@ask.intent('GoogMusicSearchRadioIntent')
def play_search_radio(query):
    search_hits = client.search(query, max_results=2)
    stations = search_hits['station_hits']

    station = None
    key = query
    split = ' by '
    if split in key:
        key = key.split(split)[0]

    for s in stations:
        quality = fuzz.partial_ratio(key, s['station']['name'])
        print("%s, quality %d" % s['station']['name'], quality)
        if quality > 75:
            station = s['station']

    if station is None:
        return statement('Sorry, no results for %s' % query)

    matcher = [key for key in station['seed'].keys() if 'Id' in key][0]

    if matcher is None:
        return statement('Sorry, no results for %s' % query)

    tracks = client.get_station_tracks(station['seed'][matcher], num_tracks=500)
    music_queue.clear()
    for track in tracks:
        music_queue.enqueue(track)

    return audio('Playing %s radio' % station['name']).play(client.get_stream_url(music_queue.current()['storeId']))

