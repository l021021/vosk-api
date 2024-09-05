from flask import Flask, render_template, request, jsonify
from ollama import AsyncClient, ResponseError
import asyncio
import os
import requests
import io
import wave
import json
import wave

client = AsyncClient(host='http://127.0.0.1:11434')
vosk_api_url = 'http://127.0.0.1:2700/api/v1/recognize'  # 替换为你的Vosk API URL


async def chat(input):
    message = {'role': 'user', 'content': input}
    try:
        response = await client.chat(model='qwen', messages=[message])
        return response['message']['content']
    except ResponseError as e:
        print(
            f"Error: {e.response.text} (status code: {e.response.status_code})")
        return f"Error: {e.response.text} (status code: {e.response.status_code})"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"Unexpected error: {str(e)}"

app = Flask(__name__)

# 存储对话历史
conversation_history = []


def get_lama_response(user_input):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(chat(user_input))
    loop.close()
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        response = get_lama_response(user_input)
        # 保存对话历史
        conversation_history.append({'user': user_input, 'response': response})
    return render_template('index.html', history=conversation_history)


@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    '''
        我们看到一个典型的用于处理文件上传的语句，通常出现在基于 Flask 框架的 Python Web 应用中。让我们逐步解析这行代码的含义：

    request 对象：request 是 Flask 提供的一个全局对象，代表当前的 HTTP 请求。它包含了客户端发送到服务器的所有数据，包括表单数据、文件、cookies、headers 等。

    **request.files**：request.files 是一个字典对象，包含了所有通过 HTTP POST 请求上传的文件。每个文件都以表单字段的名字作为键，文件对象作为值。

    **['audio']**：这里的 ['audio'] 是字典的键，表示我们希望从上传的文件中获取名为 audio 的文件。这个名字通常是在 HTML 表单中定义的 <input type="file" name="audio">。

    file 变量：file 变量用于存储从 request.files 中提取出来的文件对象。这个文件对象通常是一个 Werkzeug FileStorage 对象，包含了文件的内容和元数据（如文件名、内容类型等）。

    总结来说，这行代码的作用是从客户端上传的文件中提取名为 audio 的文件，并将其存储在变量 file 中，以便后续处理。这个处理过程可能包括保存文件到服务器、进行音频处理或其他操作。'''
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        # 读取音频数据
        audio_data = file.read()
        samplerate = 16000  # 假设采样率为16000 Hz

    # 将音频数据写入WAV文件格式的字节流
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_data)

    wav_io.seek(0)
    files = {'audio': ('audio.wav', wav_io, 'audio/wav')}
    response = requests.post(vosk_api_url, files=files)
    # print(response.text)

    if response.status_code == 200:

        result = response.json()
        recognized_text = ""
        for res_str in result:  # 处理返回的列表，解析每个字符串
            res_dict = json.loads(res_str)  # 将字符串解析为字典
            # 将识别结果存入字符串
            recognized_text += res_dict.get("text", "") + " "
            # print(recognized_text)

        # 将字节流发送到Vosk HTTP API进行语音识别
        # wav_io.seek(0)
        # vosk_api_url = 'http://127.0.0.1:2700/api/v1/recognize'  # 替换为你的Vosk API URL
        # files = {'audio': ('audio.wav', wav_io, 'audio/wav')}

        # files 变量：files 是一个字典对象，用于存储将要上传的文件信息。字典的键是文件的字段名，值是一个包含文件详细信息的元组。

        # **字典键 'audio'**：这里的 'audio' 是字典的键，表示文件在上传表单中的字段名。这个字段名通常是在 HTML 表单中定义的 <input type="file" name="audio">。

        # **元组 ('audio.wav', wav_io, 'audio/wav')**：这个元组包含了三个元素，分别是文件名、文件对象和文件的 MIME 类型。

        # **'audio.wav'**：这是文件的名称。在上传过程中，这个名称将作为文件的名字。
        # **wav_io**：这是一个文件对象，通常是一个包含音频数据的字节流或文件流。在这个上下文中，wav_io 可能是一个 BytesIO 对象或其他类似的文件对象。
        # **'audio/wav'**：这是文件的 MIME 类型，表示文件的内容类型。在这里，'audio/wav' 表示这是一个 WAV 格式的音频文件。'''

        # # response = requests.post(vosk_api_url, files=files)
        # result = response.json()
    return render_template('index.html', history=recognized_text)
    # # for res_str in result:  # 处理返回的列表，解析每个字符串
    #     res_dict = json.loads(res_str)  # 将字符串解析为字典
    #     # 将识别结果存入字符串
    #     recognized_text += res_dict.get("text", "") + " "
    # print(recognized_text)
    # response = get_lama_response(recognized_text)
    # conversation_history.append(
    #     {'user': recognized_text, 'response': response})
    # return render_template('index.html', history=conversation_history)
    # return (recognized_text)
    # # return


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)

'''

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
'''
