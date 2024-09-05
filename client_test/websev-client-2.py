import requests
import json
import io
import wave

# 设置 HTTP API URL
vosk_api_url = "http://127.0.0.1:2700/api/v1/recognize"

# 本地音频文件路径
audio_file_path = "D:\\CODE\\output.wav"


def recognize_audio(file_path):
    try:
        # 打开本地音频文件
        with open(file_path, 'rb') as f:
            wav_io = io.BytesIO(f.read())

        # 将音频数据写入WAV文件格式的字节流
        wav_io.seek(0)
        files = {'audio': ('audio.wav', wav_io, 'audio/wav')}

        # 将字节流发送到Vosk HTTP API进行语音识别
        response = requests.post(vosk_api_url, files=files)

        recognized_text = ""
        if response.status_code == 200:
            result = response.json()
            for res_str in result:  # 处理返回的列表，解析每个字符串
                res_dict = json.loads(res_str)  # 将字符串解析为字典
                # 将识别结果存入字符串
                recognized_text += res_dict.get("text", "") + " "
                # print(recognized_text)

            # recognized_text = result.get("text", "")
            # print("Recognized:", recognized_text)
            # return recognized_text
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return None


if __name__ == "__main__":
    recognized_text = recognize_audio(audio_file_path)
    if recognized_text:
        print(recognized_text)
        output_file = "recognized_text.txt"
        with open(output_file, "w") as f:
            f.write(recognized_text + "\n")
            print(f"Recognition result written to {output_file}")
