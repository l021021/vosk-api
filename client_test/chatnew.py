import sounddevice as sd
import requests
import json
import numpy as np
import sys
import signal
import io
import wave

# 设置 HTTP API URL
vosk_api_url = "http://10.0.0.64:2700/api/v1/recognize"
llama_api_url = "http://10.168.1.224:11434/api/chat"
model = "llama3.1"  # 使用的对话模型

# 创建队列用于音频数据传输
audio_queue = []
recognized_text = ""

# 定义音频回调函数


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # 将 indata 转换为 numpy 数组并放入队列中
    audio_queue.append(np.frombuffer(indata, dtype='int16'))
# 处理 `Ctrl+C` 信号以安全地停止录音并处理数据


def stop_recording(signal, frame):
    print("\nRecording stopped.")
    process_audio()
    print("\nFinal recognized text:", recognized_text)
    if recognized_text.strip():
        chat_with_model(recognized_text.strip())  # 发送到大模型进行对话
    sys.exit(0)


# 绑定 `SIGINT` 信号处理
signal.signal(signal.SIGINT, stop_recording)

# 设置音频流参数
samplerate = 16000  # 将采样率设置为 16000Hz
blocksize = 32000  # 读取更多的音频数据

# 处理所有累积的音频数据并进行识别


def process_audio():
    global recognized_text
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

        # 将字节流发送到 Vosk HTTP API 进行语音识别
        wav_io.seek(0)
        files = {'audio': ('audio.wav', wav_io, 'audio/wav')}
        response = requests.post(vosk_api_url, files=files)

        if response.status_code == 200:
            result = response.json()
            print(result)
            for res_str in result:  # 处理返回的列表，解析每个字符串
                res_dict = json.loads(res_str)  # 将字符串解析为字典
                recognized_text += res_dict.get("text", "") + " "  # 将识别结果存入字符串
                print("Recognized:", res_dict.get("text", ""))
        else:
            print(f"Error {response.status_code}: {response.text}")

# 与大模型交互的函数


def chat_with_model(text):
    messages = [{"role": "user", "content": text}]
    response = requests.post(
        llama_api_url,
        json={"model": model, "messages": messages, "stream": True},
        stream=True
    )
    response.raise_for_status()

    print("\nResponse from model:")
    for line in response.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            print(content, end="", flush=True)


# 启动音频流
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

            # 将字节流发送到 Vosk HTTP API 进行语音识别
            wav_io.seek(0)
            files = {'audio': ('audio.wav', wav_io, 'audio/wav')}
            response = requests.post(vosk_api_url, files=files)

            if response.status_code == 200:
                result = response.json()
                for res_str in result:  # 处理返回的列表，解析每个字符串
                    res_dict = json.loads(res_str)  # 将字符串解析为字典
                    # 将识别结果存入字符串
                    recognized_text += res_dict.get("text", "") + " "
                    print("Recognized:", res_dict.get("text", ""))
            else:
                print(f"Error {response.status_code}: {response.text}")
