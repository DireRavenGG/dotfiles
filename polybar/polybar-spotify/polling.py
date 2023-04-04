#!/usr/bin/env python
import math
import sys
import dbus
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '-t',
    '--trunclen',
    type=int,
    metavar='trunclen'
)
parser.add_argument(
    '-f',
    '--format',
    type=str,
    metavar='custom format',
    dest='custom_format'
)
parser.add_argument(
    '-p',
    '--playpause',
    type=str,
    metavar='play-pause indicator',
    dest='play_pause'
)
parser.add_argument(
    '--font',
    type=str,
    metavar='the index of the font to use for the main label',
    dest='font'
)
parser.add_argument(
    '--playpause-font',
    type=str,
    metavar='the index of the font to use to display the playpause indicator',
    dest='play_pause_font'
)
parser.add_argument(
    '-q',
    '--quiet',
    action='store_true',
    help="if set, don't show any output when the current song is paused",
    dest='quiet',
)

args = parser.parse_args()


def fix_string(string):
    # corrects encoding for the python version used
    if sys.version_info.major == 3:
        return string
    else:
        return string.encode('utf-8')


def truncate(name, trunclen):
    if len(name) > trunclen:
        name = name[:trunclen]
        name += '...'
        if ('(' in name) and (')' not in name):
            name += ')'
    return name

def current_bar(seconds, length): 
    bar = "▬"
    indicator = "|"
    fill_color = "#d3d3d3"
    empty_color = "#3f3f3f"
    
    width = 45
    precentage = seconds / length
    filled_pos = math.floor(precentage * width)

    string = "%{F" + fill_color + "}"   
    
    
    for i in range(width):
        if i == filled_pos:
             string += "%{F-}"
             string += indicator 
             string += "%{F" + empty_color + "}" 

        else:
            string += bar
    string += "%{F-}" 
    return string

def time_formatted(seconds, length):
    formatted = ""
    song_hours = str(math.trunc(length // 3600))
    curr_hours = str(math.trunc(seconds // 3600))
    song_mins = str(math.trunc((length % 3600) // 60))
    curr_mins = str(math.trunc((seconds % 3600) // 60))
    song_seconds = str(math.trunc((length % 3600) % 60))
    curr_seconds = str(math.trunc((seconds % 3600) % 60))
    if len(curr_seconds) == 1:
        curr_seconds =  "0" + curr_seconds
    if len(song_seconds) == 1: 
        song_seconds = "0" + song_seconds
    if (length // 3600) > 0: 
        hour_curr_format = curr_hours + ":" + curr_mins + ":" + curr_seconds
        hour_song_format = song_hours + ":" + song_mins + ":" + song_seconds
        formatted = hour_curr_format + "/" + hour_song_format 
    else:
        min_curr_format = curr_mins + ":" + curr_seconds
        min_song_format = song_mins + ":" + song_seconds
        formatted = min_curr_format + "/" + min_song_format
    return formatted   
def mouse_functionality(status, loop, shuffle):
    play_pause = ""
    if status == 'Playing':
        play_pause = "%{A1:playerctl --player=spotify pause:}  %{A}"
    elif status == 'Paused':
        play_pause = "%{A1:playerctl --player=spotify play:}  %{A}"
    skip = "%{A1:playerctl --player=spotify next:}  %{A}"
    prev = "%{A1:playerctl --player=spotify previous:}  %{A}"
    shuffle_icon ="%{A1:playerctl --player=spotify shuffle on:}%{F#3f3f3f}  %{F-}%{A}" 
    loop_icon = ""
    match loop:
        case "Playlist":
            loop_icon = "%{A1:playerctl --player=spotify loop Track:}%{A}"  
        case "Track":
            loop_icon = "%{A1:playerctl --player=spotify loop None:}%{F#00FF00}%{F-}%{A}" 
        case _:
           loop_icon = "%{A1:playerctl --player=spotify loop Playlist:}%{F#3f3f3f}%{F-}%{A}"  
    if shuffle:
        shuffle_icon ="%{A1:playerctl --player=spotify shuffle off:}  %{A}"    
    
    return prev + "%{O5}" + play_pause + "%{O5}"+ skip + "%{O5}" + shuffle_icon + "%{O5}" + loop_icon

# Default parameters
output = fix_string(u'{play_pause} {artist}: {song}')
trunclen = 35
play_pause = fix_string(u'\u25B6,\u23F8') # first character is play, second is paused

label_with_font = '%{{T{font}}}{label}%{{T-}}'
font = args.font
play_pause_font = args.play_pause_font

quiet = args.quiet
# parameters can be overwritten by args
if args.trunclen is not None:
    trunclen = args.trunclen
if args.custom_format is not None:
    output = args.custom_format
if args.play_pause is not None:
    play_pause = args.play_pause

try:
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object(
        'org.mpris.MediaPlayer2.spotify',
        '/org/mpris/MediaPlayer2'
    )

    spotify_properties = dbus.Interface(
        spotify_bus,
        'org.freedesktop.DBus.Properties'
    )

    metadata = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
    status = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
    curr_time = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Position')
    shuffle = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'Shuffle') 
    loop = spotify_properties.Get('org.mpris.MediaPlayer2.Player', 'LoopStatus')
    # Handle play/pause label

    play_pause = play_pause.split(',')

    if play_pause_font:
        play_pause = label_with_font.format(font=play_pause_font, label=play_pause)

    # Handle main label

    artist = fix_string(metadata['xesam:artist'][0]) if metadata['xesam:artist'] else ''
    song = fix_string(metadata['xesam:title']) if metadata['xesam:title'] else ''
    album = fix_string(metadata['xesam:album']) if metadata['xesam:album'] else ''
    song_length = metadata['mpris:length'] if metadata['mpris:length'] else ''
    if (quiet and status == 'Paused') or (not artist and not song and not album):
        print('')
    else:
        if font:
            artist = label_with_font.format(font=font, label=artist)
            song = label_with_font.format(font=font, label=song)
            album = label_with_font.format(font=font, label=album)

        # Add 4 to trunclen to account for status symbol, spaces, and other padding characters
        song_data = truncate(output.format(artist=artist, song=song, play_pause=play_pause, album=album), trunclen + 4)
        
        seconds = curr_time / 1000000
        length = song_length / 1000000
        print("%{O20}" + mouse_functionality(status,loop,shuffle) + "%{O20}" + current_bar(seconds, length) + "%{O20}" + time_formatted(seconds, length) + "%{O20}" + song_data)


except Exception as e:
    if isinstance(e, dbus.exceptions.DBusException):
        print('')
    else:
        print(e)
