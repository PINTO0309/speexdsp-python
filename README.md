speexdsp for python
===================

Python implementation of acoustic echo cancellation using speexdsp.

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
```

## Results

https://github.com/PINTO0309/speexdsp-python/blob/python3/tests/output.wav
