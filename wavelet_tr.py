import librosa
import pywt
import numpy as np
from pydub import AudioSegment
import soundfile as sf
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# Step 1: Load the audio file (.mp3) and convert to a waveform
def load_audio(file_path):
    # Load the MP3 file using librosa, which gives a numpy array of the audio data
    audio_data, sample_rate = librosa.load(file_path, sr=None)
    return audio_data, sample_rate

# Step 2: Apply Wavelet Transform (Decompose the signal)
def wavelet_transform(audio_data):
    # Perform a discrete wavelet transform (DWT) on the audio data
    coeffs = pywt.wavedec(audio_data, 'db2', level=6)  # Using Daubechies wavelets (db2), level 6 decomposition
    return coeffs

# Step 3: Compress the audio by thresholding wavelet coefficients
def compress_wavelet(coeffs, threshold=0.1):
    # Apply thresholding on wavelet coefficients (set small coefficients to zero)
    compressed_coeffs = [pywt.threshold(c, threshold, mode='soft') for c in coeffs]
    return compressed_coeffs

# Step 4: Reconstruct the audio signal from the compressed coefficients
def reconstruct_audio(compressed_coeffs):
    # Reconstruct the signal using the inverse wavelet transform
    compressed_audio = pywt.waverec(compressed_coeffs, 'db2')
    return compressed_audio

# Function to check if FFmpeg is available
def check_ffmpeg():
    try:
        # Try to run ffmpeg -version
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

# Function to download FFmpeg if not available
def download_ffmpeg():
    # Only download for Windows
    if platform.system() != "Windows":
        print("Automatic FFmpeg download is only supported on Windows.")
        print("Please install FFmpeg manually and add it to your PATH.")
        return False
    
    try:
        import requests
        import zipfile
        
        print("Downloading FFmpeg for Windows...")
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        
        # Create a temporary directory
        temp_dir = Path("./temp_ffmpeg")
        temp_dir.mkdir(exist_ok=True)
        zip_path = temp_dir / "ffmpeg.zip"
        
        # Download FFmpeg
        print("Downloading from", ffmpeg_url)
        response = requests.get(ffmpeg_url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("Download complete. Extracting...")
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the bin directory in the extracted folder
        extracted_dir = None
        for item in os.listdir(temp_dir):
            if item.startswith("ffmpeg-master") and os.path.isdir(temp_dir / item):
                extracted_dir = temp_dir / item
                break
        
        if extracted_dir:
            bin_dir = extracted_dir / "bin"
            
            # Copy FFmpeg executables to the current directory
            for file in os.listdir(bin_dir):
                if file.endswith(".exe"):
                    shutil.copy2(bin_dir / file, Path("./"))
            
            print("FFmpeg executables have been copied to the current directory.")
            
            # Clean up
            shutil.rmtree(temp_dir)
            return True
        else:
            print("Could not find the extracted FFmpeg directory.")
            return False
    
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return False

# Step 5: Save the processed (compressed) audio as a new MP3 file
def save_audio(output_path, audio_data, sample_rate):
    # First, save to a temporary WAV file
    temp_wav_path = "temp_output.wav"
    sf.write(temp_wav_path, audio_data, sample_rate)
    
    # Check if FFmpeg is available
    ffmpeg_available = check_ffmpeg()
    
    # If FFmpeg is not available, try to download it (Windows only)
    if not ffmpeg_available and platform.system() == "Windows":
        print("FFmpeg not found. Attempting to download...")
        try:
            ffmpeg_available = download_ffmpeg()
        except ImportError:
            print("Could not download FFmpeg: requests module not found.")
            print("Please install the requests module with: pip install requests")
    
    # Using pydub to convert WAV to MP3
    try:
        audio = AudioSegment.from_wav(temp_wav_path)
        audio.export(output_path, format="mp3")
        print(f"Successfully saved compressed audio to {output_path}")
        # Clean up temporary file
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
    except Exception as e:
        print(f"Error during MP3 conversion: {e}")
        print(f"Saving as WAV file instead")
        # If MP3 conversion fails, at least we have the WAV file
        output_wav = os.path.splitext(output_path)[0] + ".wav"
        if temp_wav_path != output_wav:
            shutil.copy(temp_wav_path, output_wav)
            print(f"Saved audio as {output_wav}")
        # Clean up temporary file if we copied it
        if os.path.exists(temp_wav_path) and temp_wav_path != output_wav:
            os.remove(temp_wav_path)

# Main function to load, process, and save the compressed audio
def main(input_file, output_file):
    # Step 1: Load the audio file
    audio_data, sample_rate = load_audio(input_file)

    # Step 2: Apply Wavelet Transform
    coeffs = wavelet_transform(audio_data)

    # Step 3: Compress the audio by thresholding wavelet coefficients
    compressed_coeffs = compress_wavelet(coeffs)

    # Step 4: Reconstruct the audio from compressed coefficients
    compressed_audio = reconstruct_audio(compressed_coeffs)

    # Step 5: Save the compressed audio to an MP3 file
    save_audio(output_file, compressed_audio, sample_rate)

# Example usage: Provide input and output file paths
if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file = "input.mp3"
        output_file = "compressed_output.mp3"
        print(f"Using default filenames: {input_file} and {output_file}")
        print("You can also specify input and output files as command line arguments:")
        print(f"python {os.path.basename(__file__)} input_file.mp3 output_file.mp3")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Please place an MP3 file with this name in the current directory or specify a different file.")
        sys.exit(1)
    
    main(input_file, output_file)