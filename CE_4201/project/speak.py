# Speak using google translate api and pygame

import pygame.mixer as mixer
import pygame
from gtts import gTTS

directory = "/audios/"

def speak_no_file(msg, volume):
    tts = gTTS(msg)
    tts.save(directory + "temp.mp3")

    mixer.init()
    message = mixer.Sound(directory + "temp.mp3")
    message.set_volume(volume)
    playing = message.play() 
    while playing.get_busy():
        pygame.time.delay(100)

def speak(filename, volume=0.1):
    mixer.init()
    message = mixer.Sound(directory + filename + ".mp3")
    message.set_volume(volume)
    playing = message.play() 
    while playing.get_busy():
        pygame.time.delay(100)

def add_audio(msg, file_path):
    tts = gTTS(msg)
    tts.save(file_path + ".mp3")

if __name__ == "__main__":
    add_audio("Please, face camera", directory + "face_camera")