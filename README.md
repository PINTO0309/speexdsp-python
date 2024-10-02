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
There are two ways to build the package.

- using Makefile

    ```
    sudo apt-get install -y libspeexdsp-dev swig python3-dev build-essential
    
    git clone https://github.com/PINTO0309/speexdsp-python.git
    cd speexdsp-python/src
    make clean
    make
    ```

## Get started
```bash
# Usage: examples/wav_aec.py near.wav far.wav out.wav
python examples/wav_aec.py tests/nearend_16k.wav tests/farend_16k.wav tests/output.wav

near - rate: 16000, channels: 1, length: 25.0
far - rate: 16000, channels: 1
```

## Results

https://github.com/PINTO0309/speexdsp-python/blob/python3/tests/output.wav
