# This script serves as a music player. It play, pause, unpause, stop, and closes mixer to save resources

import pygame
import pygame.mixer as mixer
import os

music = mixer.music
mixer.init()
path_dir = "project4/songs" # Path to song Folder

files = os.listdir(path_dir)
name_to_path = {}
# Make a dictionary. Song name (lowercase) is the key and value is relative path to song
for file in files:
    name_and_ext = os.path.splitext(file)
    name = name_and_ext[0]
    name = name.lower()
    name_to_path[name] = os.path.join(path_dir, file)

def play(song : str):
    """Play song requested 
    
    Args: exact name of the song
    
    Returns: string saying the song is playing"""

    # In case the LLM does not replaces whitespaces with underscores. Also, convert to lowercase.
    song_processed = song.lower().replace("_", " ") 

    path = name_to_path.get(song_processed, "unknown")
    
    if path == "unknown":
        return "song not available"
    
    music.load(path)
    music.play()
    
    return "Playing song"

def stop():
    music.unload()
    return "song stopped"

def pause():
    music.pause()
    return "song paused"

def unpause():
    music.unpause()
    return "song unpaused"

def volume(value : str):
    """Set volume.
        Args:
        value is a string of a float between 0-1, inclusive"""
    music.set_volume(float(value))

    return "volume adjusted"

def close_mixer():
    pygame.mixer.quit()

# dictionary with all the functions
functions = {
    "play" : play,
    "stop" : stop,
    "pause" : pause,
    "unpause" : unpause,
    "volume" : volume,
}    
def control_player(command : str, value : str ="") -> str:
    """Controls song player.
    
        Args:
            command: command to be called. Available commands: play, stop, pause, unpause, volume
            value: if command is play then value should be name of song in lower case, if command is volume value must be a string of a float between 0 and 1, \
                inclusive. Default value is "" 
                
        Returns:
            A string saying what the command did"""

    func = functions.get(command, "unknown")

    if func == "unknown":
        return "Unknown command"
    elif value != "":
        return func(value)
    return func()

# For testing: type command, then argument (if any)
if __name__ == "__main__":
    volume = 0.08
    music.set_volume(0.08)
    print(name_to_path)
    while True:
        command = input(">>> ")
        value = input(">>> ")
        print(control_player(command, value))