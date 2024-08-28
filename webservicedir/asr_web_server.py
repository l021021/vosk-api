from vosk import Model, KaldiRecognizer
from flask import Flask, request, jsonify
import wave
import os

app = Flask(__name__)

# 加载 Vosk 模型
model_path = os.environ.get(
    "VOSK_MODEL_PATH", "D:\\CODE\\my-vosk-api\\model\\vosk-model-cn-0.22")
model = Model(model_path)


@app.route('/api/v1/recognize', methods=['POST'])
def recognize():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    # 获取音频文件
    audio_file = request.files['audio']

    # 保存临时音频文件
    audio_path = "temp.wav"
    audio_file.save(audio_path)

    results = []

    # 打开音频文件并进行识别
    with wave.open(audio_path, "rb") as wf:
        rec = KaldiRecognizer(model, wf.getframerate())

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = rec.Result()
                results.append(result)
            else:
                results.append(rec.PartialResult())

        final_result = rec.FinalResult()
        results.append(final_result)
        print(final_result)
        with open("results.txt", "w", encoding="utf-8") as f:
            for result in results:
                f.write(result + "\n")
                f.flush()
    # 删除临时文件
    os.remove(audio_path)

    # 将结果保存到文本文件

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2800)
