import pywt
import librosa
import soundfile as sf
from pydub import AudioSegment

# Step 1: Convert input.mp3 to WAV format (since librosa handles WAV better)
audio = AudioSegment.from_mp3('input.mp3')
audio.export('temp_input.wav', format='wav')

# Step 2: Load the WAV file
y, sr = librosa.load('temp_input.wav', sr=None)

# Step 3: Perform Wavelet Transform (using 'db8' wavelet)
wavelet = 'db8'
coeffs = pywt.wavedec(y, wavelet)

# Step 4: Reverse the wavelet coefficients (time-domain reversal)
coeffs_reversed = [c[::-1] for c in coeffs]

# Step 5: Reconstruct the reversed signal
y_reversed = pywt.waverec(coeffs_reversed, wavelet)

# Step 6: Save the reversed audio as a temporary WAV file
sf.write('temp_reversed.wav', y_reversed, sr)

# Step 7: Convert the reversed WAV file back to MP3
reversed_audio = AudioSegment.from_wav('temp_reversed.wav')
reversed_audio.export('output.mp3', format='mp3')

# Step 8: Clean up temporary files
import os
os.remove('temp_input.wav')
os.remove('temp_reversed.wav')

print("Audio reversal complete. Saved as output.mp3.")
