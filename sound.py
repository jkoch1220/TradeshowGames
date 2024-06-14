from pydub import AudioSegment
from pydub.generators import Sine

# Create a sine wave sound
sine_wave = Sine(440).to_audio_segment(duration=500)  # 440 Hz for 500 ms
sine_wave = sine_wave + Sine(880).to_audio_segment(duration=500)  # 880 Hz for 500 ms

# Export the sound to a wav file
sine_wave.export("success.wav", format="wav")
