#!/usr/bin/env python3
"""
Audio Denoising with Wavelets

This script takes an MP3 file as input, applies wavelet-based denoising,
and saves the denoised audio as a new file.

Usage:
    python denoise_audio.py input.mp3 output.wav
"""

import sys
import numpy as np
import pywt
import librosa
import soundfile as sf

def wavelet_denoise(data, wavelet='db4', level=10, threshold_factor=1.0):
    """
    Apply wavelet denoising to audio signal
    
    Parameters:
        data: Input audio data (numpy array)
        wavelet: Wavelet type (default: 'db4')
        level: Decomposition level (default: 10)
        threshold_factor: Controls threshold strength (default: 1.0)
        
    Returns:
        Denoised audio data
    """
    # Wavelet decomposition
    coeffs = pywt.wavedec(data, wavelet, level=level)
    
    # Estimate noise level using finest detail coefficients
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    
    # Calculate threshold
    threshold = threshold_factor * sigma * np.sqrt(2 * np.log(len(data)))
    
    # Apply soft thresholding to detail coefficients
    new_coeffs = [coeffs[0]]  # Keep approximation coefficients unchanged
    
    for i in range(1, len(coeffs)):
        # Apply more aggressive thresholding to higher frequencies (finer details)
        level_threshold = threshold * (1 + 0.1 * (len(coeffs) - i))
        new_coeffs.append(pywt.threshold(coeffs[i], level_threshold, mode='soft'))
    
    # Reconstruct signal
    denoised_data = pywt.waverec(new_coeffs, wavelet)
    
    # Trim to original length (reconstruction might add padding)
    if len(denoised_data) > len(data):
        denoised_data = denoised_data[:len(data)]
    
    return denoised_data

def main():
    
    input_file = 'noise.mp3'
    output_file = 'noise_denoised.mp3'
    
    print(f"Loading audio file: {input_file}")
    try:
        # Load audio file
        audio_data, sample_rate = librosa.load(input_file, sr=None)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        sys.exit(1)
    
    print(f"Applying wavelet denoising...")
    
    # Process stereo files (if applicable)
    if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
        # Process each channel separately
        denoised_data = np.zeros_like(audio_data)
        for channel in range(audio_data.shape[1]):
            denoised_data[:, channel] = wavelet_denoise(audio_data[:, channel])
    else:
        # Process mono audio
        denoised_data = wavelet_denoise(audio_data)
    
    print(f"Saving denoised audio to: {output_file}")
    try:
        # Save denoised audio
        sf.write(output_file, denoised_data, sample_rate)
        print("Done!")
    except Exception as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()