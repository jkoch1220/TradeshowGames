import numpy as np
import wave

def create_tone(frequency, duration, filename):
    framerate = 44100
    amplitude = 32767
    t = np.linspace(0, duration, int(framerate * duration), endpoint=False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    wave_data = wave_data.astype(np.int16)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(framerate)
        wav_file.writeframes(wave_data.tobytes())

# Create sound files for notes A-G
frequencies = {"A": 440.0, "B": 493.88, "C": 523.25, "D": 587.33, "E": 659.25, "F": 698.46, "G": 783.99}
for note, freq in frequencies.items():
    create_tone(freq, 1.0, f"{note}.wav")
