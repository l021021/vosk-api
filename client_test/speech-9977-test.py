import pyaudio
import wave
import requests

# 录音参数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# 录音功能


def record_audio():
    audio = pyaudio.PyAudio()

    # 开始录音
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("开始录音...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束")

    # 停止录音
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 保存为 WAV 文件
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# 发送请求并打印结果


def send_to_api():
    url = "http://127.0.0.1:9977/api"
    files = {"file": open(WAVE_OUTPUT_FILENAME, "rb")}
    data = {
        "language": "zh",
        "model": "models--Systran--faster-whisper-medium",
        "response_format": "json"
    }
    response = requests.post(url, data=data, files=files)
    print(response.json())


if __name__ == "__main__":
    record_audio()
    send_to_api()
