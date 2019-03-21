import io
import os

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Instantiates a client
client = speech.SpeechClient()

# The name of the audio file to transcribe
file_name = "efs/reformulations/3b8e5045-42db-4315-a9da-20ba22f7f162.ogg"

# Loads the audio into memory
with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio = types.RecognitionAudio(content=content)

config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
    sample_rate_hertz=48000,
    language_code='en-US')

# Detects speech in the audio file
response = client.recognize(config, audio)
print("Recognizing")
print(response)
for result in response.results:
    print('Transcript: {}'.format(result.alternatives[0].transcript))
