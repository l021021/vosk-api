import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

# 设置录音参数
samplerate = 44100  # 采样率
duration = 5  # 录音时长（秒）
output_file = "test_recording.wav"  # 输出文件名

print("Recording...")

# 录制音频
audio_data = sd.rec(int(samplerate * duration),
                    samplerate=samplerate, channels=2, dtype='int16')
sd.wait()  # 等待录音结束

print("Recording finished. Saving to file...")

# 保存为 WAV 文件
wav.write(output_file, samplerate, audio_data)

print(f"Audio saved to {output_file}")
