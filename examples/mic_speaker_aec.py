"""
sudo apt-get update && sudo apt-get install libsndfile1
pip install SoundCard==0.4.3 soundfile==0.12.1 sounddevice==0.5.0

# python mic_speaker_aec.py [output_mode] [mic_index] [output_device_index]

# View a list of available audio devices
python mic_speaker_aec.py

=== Available audio devices ===
=== Microphones ===
Index 0: Monitor of Built-in Audio Digital Stereo (IEC958)
Index 1: Monitor of GA104 High Definition Audio Controller Digital Stereo (HDMI)
Index 2: Monitor of USB Microphone Analog Stereo
Index 3: USB Microphone Digital Stereo (IEC958)
=== Speakers ===
Index 0: Built-in Audio Digital Stereo (IEC958)
Index 1: GA104 High Definition Audio Controller Digital Stereo (HDMI)
Index 2: USB Microphone Analog Stereo
==============================
Usage: mic_speaker_aec.py [output_mode] [mic_index] [output_device_index]
output_mode: "wav" (default) or "speaker"
mic_index: Index of the microphone to use (optional, default is the system default microphone)
output_device_index: Index of the speaker used for outputting the echo-cancelled audio

# When executing without specifying the microphone index.
# When you want to save the audio after echo cancellation as a WAV file.
#   output_mode: Specify wav and save the audio after echo cancellation to echo_cancelled_output.wav.
#   mic_index: Use the default microphone.
#   output_device_index: Not specified as speakers are not used.
python mic_speaker_aec.py wav

# When manually specifying the microphone and speaker.
#   output_mode: Specify speaker to play the echo-canceled audio on the speaker.
#   mic_index: Use microphone number 0.
#   output_device_index: Use speaker number 1 as the output destination.
python mic_speaker_aec.py speaker 0 1

# When manually specifying the microphone and speaker.
#   output_mode: Specify speaker to play the echo-canceled audio on the speaker.
#   mic_index: Use the default microphone.
#   output_device_index: Null. No output_device_index specified. Using a virtual speaker as the default output.
python mic_speaker_aec.py speaker
"""

import soundcard as sc
import soundfile as sf
import sounddevice as sd
import numpy as np
import os
import sys
import subprocess
import atexit
import signal
from src.speexdsp import EchoCanceller
# 仮想スピーカーのパルスオーディオモジュール名
VIRTUAL_SPEAKER_NAME = "Virtual_Sink"
VIRTUAL_SPEAKER_DESCRIPTION = "Virtual_Speaker_for_AEC"
module_id = None  # 仮想スピーカーのモジュールIDを格納する変数

# デバイスのデフォルトサンプルレートを取得する関数
def get_device_sample_rate(device_name):
    """指定されたデバイスのデフォルトサンプルレートを取得する"""
    devices = sd.query_devices()
    for device in devices:
        if device['name'] == device_name:
            return int(device['default_samplerate'])  # デフォルトサンプルレートを整数で返す
    return 44100  # 見つからなかった場合のデフォルト値

# デバイス一覧を表示する関数
def list_audio_devices():
    print("=== Available audio devices ===")
    microphones = sc.all_microphones(include_loopback=True)
    speakers = sc.all_speakers()

    print("=== Microphones ===")
    for i, mic in enumerate(microphones):
        print(f"Index {i}: {mic.name}")

    print("=== Speakers ===")
    for i, speaker in enumerate(speakers):
        print(f"Index {i}: {speaker.name}")
    print("==============================")

# 仮想スピーカーを生成する関数
def create_virtual_speaker():
    """仮想スピーカー（Virtual_Sink）を作成する"""
    global module_id
    try:
        # 仮想スピーカーを作成するためのpactlコマンド
        result = subprocess.run([
            "pactl", "load-module", "module-null-sink",
            f"sink_name={VIRTUAL_SPEAKER_NAME}",
            f"sink_properties=device.description={VIRTUAL_SPEAKER_DESCRIPTION}"
        ], check=True, capture_output=True, text=True)

        # コマンド出力からモジュールIDを取得して保存
        module_id = result.stdout.strip()
        print(f"Created virtual speaker: {VIRTUAL_SPEAKER_NAME} with module ID: {module_id}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create virtual speaker: {e}")

# 仮想スピーカーを削除する関数
def remove_virtual_speaker():
    """作成した仮想スピーカーを削除する"""
    global module_id
    if module_id:
        try:
            subprocess.run(["pactl", "unload-module", module_id], check=True)
            print(f"Removed virtual speaker module with ID: {module_id}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove virtual speaker module: {e}")
        module_id = None

# 仮想スピーカーを取得する関数
def get_virtual_speaker():
    """仮想スピーカー（Virtual_Sink）を取得する。存在しない場合は生成する。"""
    speakers = sc.all_speakers()
    for speaker in speakers:
        if VIRTUAL_SPEAKER_DESCRIPTION in speaker.name:
            return speaker

    # 仮想スピーカーが見つからなかった場合は作成する
    print(f"Virtual speaker '{VIRTUAL_SPEAKER_NAME}' not found. Creating a new one...")
    create_virtual_speaker()

    # 再取得（仮想スピーカー作成後）
    speakers = sc.all_speakers()
    for speaker in speakers:
        if VIRTUAL_SPEAKER_DESCRIPTION in speaker.name:
            return speaker

    return None  # 仮想スピーカーの取得に失敗した場合

# プログラム終了時のクリーンアップ処理
def cleanup():
    """プログラム終了時に仮想スピーカーを削除する"""
    remove_virtual_speaker()

# クリーンアップ処理を登録
atexit.register(cleanup)

# SIGINT シグナル（Ctrl+C）のハンドラを設定
signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))

# コマンドライン引数の処理
if len(sys.argv) < 4:
    list_audio_devices()
    print(f'Usage: {os.path.basename(sys.argv[0])} [output_mode] [mic_index] [output_device_index]')
    print('output_mode: "wav" (default) or "speaker"')
    print('mic_index: Index of the microphone to use (optional, default is the system default microphone)')
    print('output_device_index: Index of the speaker used for outputting the echo-cancelled audio')
    if len(sys.argv) == 1:
        sys.exit(0)

output_mode = sys.argv[1] if len(sys.argv) > 1 else 'wav'  # 出力モードを指定、デフォルトは 'wav'
mic_index = int(sys.argv[2]) if len(sys.argv) > 2 else None  # 使用するマイクのインデックス（未指定の場合は None）
output_device_index = int(sys.argv[3]) if len(sys.argv) > 3 else None  # エコーキャンセル後の音声を出力するデバイスのインデックス

# 音声の設定
FRAME_SIZE = 256  # エコーキャンセルのフレームサイズ
BUFFER_SIZE = 2048  # バッファサイズ

# マイクの取得
microphones = sc.all_microphones(include_loopback=True)
if mic_index is not None:
    # 指定されたインデックスのマイクを取得
    selected_mic = microphones[mic_index]
else:
    # デフォルトのマイクを使用
    selected_mic = sc.default_microphone()

print(f"Using microphone: {selected_mic.name}")

# リファレンススピーカー (ループバック用のモニター)
reference_speaker = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)
print(f"Using reference speaker: {reference_speaker.name}")

# デフォルトサンプルレートを取得
mic_sample_rate = get_device_sample_rate(selected_mic.name)
ref_sample_rate = get_device_sample_rate(reference_speaker.name)

# サンプリングレートを自動設定（マイクとリファレンスのどちらか低い方を採用）
SAMPLE_RATE = min(mic_sample_rate, ref_sample_rate)
print(f"Auto-selected sample rate: {SAMPLE_RATE}")

# エコーキャンセル後の音声を別のスピーカーへ出力する設定
output_speaker = None
if output_mode == 'speaker':
    if output_device_index is None:
        print("No output_device_index specified. Using a virtual speaker as the default output.")
        output_speaker = get_virtual_speaker()  # 仮想スピーカーをデフォルトとして設定
        if output_speaker is None:
            print("Error: Could not create or find a virtual speaker.")
            sys.exit(1)
    else:
        # 全スピーカーの一覧を取得して、指定されたインデックスのスピーカーを選択
        speakers = sc.all_speakers()
        output_speaker = speakers[output_device_index]
    print(f"Outputting to speaker: {output_speaker.name}")

# エコーキャンセラの設定
echo_canceller = EchoCanceller.create(FRAME_SIZE, BUFFER_SIZE, SAMPLE_RATE)

# WAVファイルへの書き込み設定
output_filename_mic = "mic.wav"
output_filename_ref = "ref.wav"
output_filename_ec = "ec.wav"
wav_file_mic = None
wav_file_ref = None
wav_file_ec = None
if output_mode == 'wav':
    wav_file_mic = sf.SoundFile(output_filename_mic, mode='w', samplerate=SAMPLE_RATE, channels=1, subtype='PCM_16')
    wav_file_ref = sf.SoundFile(output_filename_ref, mode='w', samplerate=SAMPLE_RATE, channels=1, subtype='PCM_16')
    wav_file_ec = sf.SoundFile(output_filename_ec, mode='w', samplerate=SAMPLE_RATE, channels=1, subtype='PCM_16')

# 音声データを処理する関数
def process_audio_callback(mic_data: np.ndarray, reference_data: np.ndarray):
    # スケーリング係数を設定
    scaling_factor = np.iinfo(np.int16).max

    # float32 データを int16 にスケーリング
    mic_data_scaled = (mic_data.flatten() * scaling_factor).astype(np.int16)
    ref_data_scaled = (reference_data.flatten() * scaling_factor).astype(np.int16)

    # バイトデータに変換
    mic_data_bytes = mic_data_scaled.tobytes()
    ref_data_bytes = ref_data_scaled.tobytes()

    # エコーキャンセラの処理
    processed_data = echo_canceller.process(mic_data_bytes, ref_data_bytes)

    # バイトデータを numpy 配列に変換
    processed_data = np.frombuffer(processed_data, dtype=np.int16)

    # 出力先に応じて処理を行う
    if output_mode == 'speaker' and output_speaker:
        output_speaker.play(processed_data, samplerate=SAMPLE_RATE)
    elif output_mode == 'wav' and wav_file_mic and wav_file_ref:
        wav_file_mic.write(mic_data_scaled)
        wav_file_ref.write(ref_data_scaled)
        wav_file_ec.write(processed_data)

print("Starting audio processing...")

try:
    # マイクとリファレンススピーカーからの音声データを取得するレコーダーを起動
    with selected_mic.recorder(samplerate=SAMPLE_RATE, channels=1, blocksize=FRAME_SIZE) as mic_stream, \
        reference_speaker.recorder(samplerate=SAMPLE_RATE, channels=1, blocksize=FRAME_SIZE) as ref_stream:

        while True:
            # マイクとリファレンススピーカーからの音声データを取得
            mic_data = mic_stream.record(numframes=FRAME_SIZE)
            ref_data = ref_stream.record(numframes=FRAME_SIZE)

            # エコーキャンセル処理を行う
            process_audio_callback(mic_data, ref_data)

except KeyboardInterrupt:
    print("Stopping audio processing...")

finally:
    # WAVファイルを閉じる
    if wav_file_mic:
        wav_file_mic.close()
    if wav_file_ref:
        wav_file_ref.close()
    if wav_file_ec:
        wav_file_ec.close()

    print("Audio processing terminated.")
