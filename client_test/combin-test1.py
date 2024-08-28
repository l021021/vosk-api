import sounddevice as sd
import requests
import json
import numpy as np
import sys
import signal
import io
import wave
import threading
from ollama import AsyncClient
import asyncio

# 设置 HTTP API URL
vosk_api_url = "http://127.0.0.1:2700/api/v1/recognize"
ollama_api_url = "http://127.0.0.1:11434"

# 创建队列用于音频数据传输
audio_queue = []

# 定义音频回调函数


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # 将 indata 转换为 numpy 数组并放入队列中
    audio_queue.append(np.frombuffer(indata, dtype='int16'))

# 处理 `Ctrl+C` 信号以安全地停止录音


def stop_recording(signal=None, frame=None):
    global running
    running = False
    print("\nRecording stopped.")


# 初始化异步客户端
client = AsyncClient(host=ollama_api_url)


async def chat(prompt):
    print('qustion:', prompt)
    prompt_ = {'role': 'user', 'content': prompt}
    response = await client.chat(model='qwen', messages=[prompt_])
    print(response['message']['content'])

# 绑定 `SIGINT` 信号处理
signal.signal(signal.SIGINT, stop_recording)

# 设置音频流参数
samplerate = 16000  # 将采样率设置为 16000Hz
blocksize = 32000  # 读取更多的音频数据

# 启动音频流
recognized_text = ""
output_file = "D:\\CODE\\my-vosk-api\\recognized_text.txt"
running = True

with open(output_file, "w", encoding="utf-8") as f:
    with sd.RawInputStream(samplerate=samplerate, blocksize=blocksize, device=None, dtype='int16',
                           channels=1, callback=callback):
        print('#' * 80)
        print('Press Ctrl+C to stop the recording')
        print('#' * 80)

        # 设置一个定时器，在10秒后调用 stop_recording 函数
        timer = threading.Timer(10.0, stop_recording)
        timer.start()

        while running:
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
                print(response.text)

                if response.status_code == 200:
                    result = response.text
                    if True:  # isinstance(result, dict):  # 假设返回的是一个JSON对象
                        res_dict = result
                        for word in res_dict:
                            print(word)
                            recognized_text += res_dict.get("text", "")
                            recognized_text += res_dict.get("partial", "")

                        # print("Recognized:", res_dict.get("text", ""))
                        # 合并返回的结果
                        print(recognized_text)

                        f.write(res_dict.get("text", ""))  # 将识别结果写入文件
                        f.flush()  # 确保数据被立即写入文件
                else:
                    print(f"Error {response.status_code}: {response.text}")

# 在录音结束后调用异步函数
asyncio.run(chat(recognized_text))
