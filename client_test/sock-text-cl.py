import asyncio
import json
import websockets
import pyaudio
import wave

# Vosk服务器的WebSocket地址
VOSK_SERVER = "ws://127.0.0.1:2800"

# 音频参数
CHUNK = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 10


async def record_and_transcribe():
    # 初始化PyAudio
    p = pyaudio.PyAudio()

    # 打开音频流
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音...")

    # 连接到Vosk WebSocket服务器
    async with websockets.connect(VOSK_SERVER) as websocket:
        # 发送配置信息
        await websocket.send(json.dumps({"config": {"sample_rate": RATE}}))

        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
            await websocket.send(data)

        print("录音结束")

        # 发送结束信号
        await websocket.send('{"eof" : 1}')

        # 接收识别结果
        result = await websocket.recv()

    # 停止并关闭音频流
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 保存音频文件
    wf = wave.open("output.wav", "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # 保存识别结果到文件
    with open("transcription.json", "w", encoding="utf-8") as f:
        f.write(result)

    print("识别结果已保存到 transcription.json")

# 运行异步函数
asyncio.get_event_loop().run_until_complete(record_and_transcribe())
