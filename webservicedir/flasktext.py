from flask import Flask, request, jsonify
from vosk import Model, KaldiRecognizer
import wave
import json

app = Flask(__name__)
model_path = os.environ.get(
    "VOSK_MODEL_PATH", "D:\\CODE\\my-vosk-api\\model\\vosk-model-cn-0.22")
model = Model(model_path)

rec = KaldiRecognizer(model, 16000)

@app.route('/api/v1/recognize', methods=['POST'])
def recognize():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    wf = wave.open(file.stream, 'rb')
    rec.AcceptWaveform(wf.readframes(wf.getnframes()))
    result = rec.Result()
    wf.close()

    return jsonify(json.loads(result))


if __name__ == '__main__':
    app.run(debug=True)
