import requests
import json
import io
import wave
import os

# 配置
VOSK_API_URL = 'http://127.0.0.1:2700/api/v1/recognize'  # 替换为你的 Vosk API 服务器地址和端口
LOCAL_WAV_FILE = 'D:\\record.wav'
# LOCAL_WAV_FILE = 'D:\\recording2.wav'
# LOCAL_WAV_FILE = 'D:\\test.wav'
# LOCAL_WAV_FILE = 'D:\\test_recording.wav'


def check_wav_file(file_path):
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在")
        return False

    try:
        with wave.open(file_path, 'rb') as wf:
            print(f"Channels: {wf.getnchannels()}")
            print(f"Sample width: {wf.getsampwidth()}")
            print(f"Frame rate: {wf.getframerate()}")
            print(f"Number of frames: {wf.getnframes()}")
            print(f"Parameters: {wf.getparams()}")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                print("WAV 文件格式不符合要求")
                return False
    except wave.Error as e:
        print(f"WAV 文件格式错误: {e}")
        return False
    return True


def send_to_vosk_api(file_path):
    # 检查 WAV 文件格式
    if not check_wav_file(file_path):
        return "WAV 文件格式错误"
    recognized_text = ''
    # 将本地文件读取到字节流中
    with open(file_path, 'rb') as f:
        wav_io = io.BytesIO(f.read())

    # 将字节流发送到 Vosk HTTP API 进行语音识别
    wav_io.seek(0)
    files = {'audio': ('record.wav', wav_io, 'audio/wav')}
    response = requests.post(VOSK_API_URL, files=files)
    # response.raise_for_status()  # 检查请求是否成功
    result = response.json()
    for res_str in result:  # 处理返回的列表，解析每个字符串
        res_dict = json.loads(res_str)  # 将字符串解析为字典
        # 将识别结果存入字符串
        recognized_text += res_dict.get("text", "") + " "
        # print(recognized_text)

    return recognized_text


# 主程序
if __name__ == "__main__":
    print("发送音频到 Vosk API...")
    try:
        recognized_text = send_to_vosk_api(LOCAL_WAV_FILE)
        print("识别结果:", recognized_text)
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
    except json.JSONDecodeError as e:
        print(f"解析响应时发生错误: {e}")
