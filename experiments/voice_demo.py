import scipy.io.wavfile as wavfile
import torch
from transformers import AutoTokenizer, VitsModel, pipeline

TEXT = "Strong on Python and system design, weak on SQL. I would move forward with this candidate."

# 1. Text to speech
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")
tts = VitsModel.from_pretrained("facebook/mms-tts-eng")
with torch.no_grad():
    audio = tts(**tokenizer(TEXT, return_tensors="pt")).waveform
wavfile.write("experiments/feedback.wav", tts.config.sampling_rate, audio[0].numpy())
print("Saved experiments/feedback.wav (play it!)")

# 2. Speech to text on that same file
asr = pipeline("automatic-speech-recognition", model="openai/whisper-small")
result = asr("experiments/feedback.wav")
print("Transcript:", result["text"])