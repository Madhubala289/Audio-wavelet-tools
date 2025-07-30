import os
import requests
import zipfile
import shutil
import sys

def download_ffmpeg():
    print("Downloading FFmpeg for Windows...")
    
    # Create a directory for FFmpeg if it doesn't exist
    ffmpeg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg")
    if not os.path.exists(ffmpeg_dir):
        os.makedirs(ffmpeg_dir)
    
    # Download FFmpeg
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
    
    try:
        print("Downloading FFmpeg from", ffmpeg_url)
        response = requests.get(ffmpeg_url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("Download complete. Extracting...")
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # Find the bin directory in the extracted folder
        extracted_dir = None
        for item in os.listdir(ffmpeg_dir):
            if item.startswith("ffmpeg-master") and os.path.isdir(os.path.join(ffmpeg_dir, item)):
                extracted_dir = os.path.join(ffmpeg_dir, item)
                break
        
        if extracted_dir:
            bin_dir = os.path.join(extracted_dir, "bin")
            
            # Copy FFmpeg executables to the main directory
            for file in os.listdir(bin_dir):
                if file.endswith(".exe"):
                    shutil.copy2(os.path.join(bin_dir, file), os.path.dirname(os.path.abspath(__file__)))
            
            print("FFmpeg executables have been copied to the current directory.")
            print("You can now run the wavelet_tr.py script with MP3 support.")
        else:
            print("Could not find the extracted FFmpeg directory.")
        
        # Clean up
        os.remove(zip_path)
        shutil.rmtree(ffmpeg_dir)
        
        return True
    
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return False

if __name__ == "__main__":
    download_ffmpeg()
