speexdsp for python
===================

Python implementation of acoustic echo cancellation using speexdsp.

This fork is simply a customized version of https://github.com/xiongyihui/speexdsp-python modified to run on Ubuntu 22.04.

## Requirements
+ Ubuntu 22.04
+ swig
+ build-essential
+ compile toolchain
+ python3.10
+ libspeexdsp-dev
+ python3-dev

## Build
```bash
sudo apt-get install -y libspeexdsp-dev swig python3-dev build-essential libsndfile1
pip install SoundCard==0.4.3 soundfile==0.12.1 sounddevice==0.5.0

git clone https://github.com/PINTO0309/speexdsp-python.git
cd speexdsp-python/src
make clean
make
```

## Get started
### 1. WAV + WAV (reference_wav) -> WAV
```bash
# Usage: examples/wav_aec.py near.wav far.wav out.wav
python examples/wav_aec.py tests/nearend_16k.wav tests/farend_16k.wav tests/output.wav

near - rate: 16000, channels: 1, length: 25.0
far - rate: 16000, channels: 1
```
### 2. View a list of available audio devices
```bash
python mic_speaker_aec.py

=== Available audio devices ===
=== Microphones ===
Index 0: Monitor of Built-in Audio Digital Stereo (IEC958)
Index 1: Monitor of USB Microphone Analog Stereo
Index 2: USB Microphone Digital Stereo (IEC958)
Index 3: Monitor of GA104 High Definition Audio Controller Digital Stereo (HDMI 2)
Index 4: Full HD webcam Mono
=== Speakers ===
Index 0: Built-in Audio Digital Stereo (IEC958)
Index 1: USB Microphone Analog Stereo
Index 2: GA104 High Definition Audio Controller Digital Stereo (HDMI 2)
==============================
Usage: mic_speaker_aec.py [output_mode] [mic_index] [output_device_index]
output_mode: "wav" (default) or "speaker"
mic_index: Index of the microphone to use (optional, default is the system default microphone)
output_device_index: Index of the speaker used for outputting the echo-cancelled audio
```
### 3. Mic + Speaker (reference_speaker) -> WAV
```bash
# python mic_speaker_aec.py [output_mode] [mic_index] [output_device_index]

# When executing without specifying the microphone index.
# When you want to save the audio after echo cancellation as a WAV file.
#   output_mode: Specify wav and save the audio after echo cancellation to echo_cancelled_output.wav.
#   mic_index: Use the default microphone.
#   output_device_index: Not specified as speakers are not used.
python mic_speaker_aec.py wav

ctrl + c
```
### 4. Mic + Speaker (reference_speaker) -> Speaker
```bash
# python mic_speaker_aec.py [output_mode] [mic_index] [output_device_index]

# When manually specifying the microphone and speaker.
#   output_mode: Specify speaker to play the echo-canceled audio on the speaker.
#   mic_index: Use microphone number 0.
#   output_device_index: Use speaker number 1 as the output destination.
python mic_speaker_aec.py speaker 0 1

ctrl + c
```
### 5. Mic + Speaker (reference_speaker) -> Virtual Speaker
```bash
# python mic_speaker_aec.py [output_mode] [mic_index] [output_device_index]

# When manually specifying the microphone and speaker.
#   output_mode: Specify speaker to play the echo-canceled audio on the speaker.
#   mic_index: Use the default microphone.
#   output_device_index: Null. No output_device_index specified. Using a virtual speaker as the default output.
python mic_speaker_aec.py speaker

ctrl + c
```

## Results
https://github.com/PINTO0309/speexdsp-python/blob/python3/tests/output.wav
