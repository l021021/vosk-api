

import sounddevice as sd
import requests
import json
import numpy as np
import sys
import signal
import io
import wave

# 设置 HTTP API URL
vosk_api_url = "http://127.0.0.1:2800/api/v1/recognize"

# 创建队列用于音频数据传输
audio_queue = []

# 定义音频回调函数


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # 将 indata 转换为 numpy 数组并放入队列中
    audio_queue.append(np.frombuffer(indata, dtype='int16'))

# 处理 `Ctrl+C` 信号以安全地停止录音


def stop_recording(signal, frame):
    print("\nRecording stopped.")
    sys.exit(0)


# 绑定 `SIGINT` 信号处理
signal.signal(signal.SIGINT, stop_recording)

# 设置音频流参数
samplerate = 16000  # 将采样率设置为 16000Hz
blocksize = 32000  # 读取更多的音频数据

# 启动音频流
recognized_text = ""
output_file = "recognized_text.txt"
with open(output_file, "w") as f:
    with sd.RawInputStream(samplerate=samplerate, blocksize=blocksize, device=None, dtype='int16',
                           channels=1, callback=callback):
        print('#' * 80)
        print('Press Ctrl+C to stop the recording')
        print('#' * 80)

        while True:
            if len(audio_queue) > 0:
                data = np.concatenate(audio_queue)  # 将队列中的音频数据拼接成一个大的数组
                audio_queue.clear()  # 清空队列
                wav_io = io.BytesIO()

                # 将音频数据写入WAV文件格式的字节流
                with wave.open(wav_io, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(samplerate)
                    wf.writeframes(data.tobytes())

                # 将字节流发送到Vosk HTTP API进行语音识别
                wav_io.seek(0)
                files = {'audio': ('audio.wav', wav_io, 'audio/wav')}
                response = requests.post(vosk_api_url, files=files)

                if response.status_code == 200:
                    result = response.json()
                    for res_str in result:  # 处理返回的列表，解析每个字符串
                        res_dict = json.loads(res_str)  # 将字符串解析为字典
                        print("Recognized:", res_dict.get("text", ""))
                        f.write(res_dict.get("text", "") + "\n")  # 将识别结果写入文件
                        f.flush()  # 确保数据被立即写入文件
                else:
                    print(f"Error {response.status_code}: {response.text}")
