import sounddevice as sd
import websocket
import json
import signal
import sys
import numpy as np
import threading

# 设置 WebSocket API URL
vosk_api_url = "ws://localhost:2900"

# 创建 WebSocket 客户端
ws = websocket.WebSocket()

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
    print("\nRecording stopped. Closing connection.")
    ws.close()  # 关闭 WebSocket 连接
    sys.exit(0)


# 绑定 `SIGINT` 信号处理
signal.signal(signal.SIGINT, stop_recording)

# 发送音频数据到 Vosk WebSocket API 并返回识别结果


def send_to_vosk(ws, audio_data):
    ws.send(audio_data.tobytes(), opcode=websocket.ABNF.OPCODE_BINARY)
    result = ws.recv()
    print(result)
    return result


# 启动 WebSocket 连接
print("Connecting to WebSocket server...")
ws.connect(vosk_api_url)
print("Connected!")

# 设置音频流参数
device_info = sd.query_devices(None, 'input')
# print(device_info)
samplerate = int(device_info['default_samplerate'])

# 启动音频流
recognized_text = ""
output_file = "recognized_text.txt"
running = True

with open(output_file, "w") as f:
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=1, dtype='int16',
                           channels=1, callback=callback):
        print('#' * 80)
        print('Press Ctrl+C to stop the recording')
        print('#' * 80)

        # 设置一个定时器，在5秒后调用 stop_recording 函数
        timer = threading.Timer(5.0, stop_recording)
        timer.start()

        while running:
            if len(audio_queue) > 0:
                data = audio_queue.pop(0)
                result = send_to_vosk(ws, data)
                text = result
                if text:
                    print("Recognized:", text)
                    recognized_text += text
                    f.write(text)  # 将识别结果写入文件
                    f.flush()  # 确保数据被立即写入文件

# 关闭 WebSocket 连接和文件（在 stop_recording 中已经处理）
