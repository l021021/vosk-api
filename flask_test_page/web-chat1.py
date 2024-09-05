import requests
import json
import os
import wave
from flask import Flask, request, render_template

app = Flask(__name__)
vosk_api_url = 'http://10.0.0.64:2700/api/v1/recognize'
vosk_api_url = 'http://127.0.0.1:2700/api/v1/recognize'
conversation_history = []


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['audio']
        wav_io = file.stream

        # 将音频数据写入WAV文件格式的字节流
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)  # 假设采样率为16000
            wf.writeframes(file.read())

        # 将字节流发送到Vosk HTTP API进行语音识别
        wav_io.seek(0)
        files = {'audio': ('audio.wav', wav_io, 'audio/wav')}
        try:
            response = requests.post(vosk_api_url, files=files)
            response.raise_for_status()  # 检查请求是否成功
            result = response.json()
            recognized_text = ""
            for res_str in result:  # 处理返回的列表，解析每个字符串
                res_dict = json.loads(res_str)  # 将字符串解析为字典
                recognized_text += res_dict.get("text", "") + " "
            print(recognized_text)
            response_text = get_response(recognized_text)
            conversation_history.append(
                {'user': recognized_text, 'response': response_text})
            return render_template('index.html', history=conversation_history)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return "Error occurred while processing the request."

    return render_template('index.html', history=conversation_history)


def get_response(text):
    # 模拟一个简单的响应函数
    return f"Echo: {text}"


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
