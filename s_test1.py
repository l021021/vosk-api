import pyaudio
import wave
import json
from vosk import Model, KaldiRecognizer

# 配置
MODEL_PATH = "D:\\CODE\\my-vosk-api\\model\\vosk-model-cn-0.22"  # 替换为你的 Vosk 模型路径
AUDIO_OUTPUT = "output.wav"
SAMPLE_RATE = 16000
CHUNK_SIZE = 4000

# 初始化 Vosk 模型
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

# 录制音频



def record_audio(output_file):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1,
                        rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE)
    frames = []

    print("开始录音...")

    try:
        while True:
            data = stream.read(CHUNK_SIZE)
            frames.append(data)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                print(json.loads(result)["text"])
    except KeyboardInterrupt:
        print("录音结束")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(frames))


# 主程序
if __name__ == "__main__":
    record_audio(AUDIO_OUTPUT)
