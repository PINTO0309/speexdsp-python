import sounddevice as sd
sd._terminate()
sd._initialize()

# PulseAudio のホスト API を使用するように設定（index 1 は通常 PulseAudio）
sd.default.hostapi = 1

# PulseAudioデバイスも含むすべてのデバイス情報を表示
print(sd.query_devices())


# import pyaudio

# # PyAudioの初期化
# p = pyaudio.PyAudio()

# # 各デバイスの情報を表示
# for i in range(p.get_device_count()):
#     device_info = p.get_device_info_by_index(i)
#     print(f"Index {i}: {device_info['name']} - Channels: {device_info['maxInputChannels']} (Input), {device_info['maxOutputChannels']} (Output)")

# # PyAudioの終了処理
# p.terminate()