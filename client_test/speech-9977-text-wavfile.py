import requests


def upload_wav_file(file_path):
    url = "http://127.0.0.1:9977/api"
    files = {"file": open(file_path, "rb")}
    data = {
        "language": "zh",
        "model": "medium",
        "response_format": "json"
    }
    response = requests.post(url, data=data, files=files)
    print(response.json().get("text", ""))
    response_data = response.json()

    if response_data.get("code") == 0:
        texts = [item["text"] for item in response_data.get("data", [])]
        full_text = " ".join(texts)
        print(full_text)
    else:
        print("Error:", response_data.get("msg"))


if __name__ == "__main__":
    file_path = "D:\\recording.wav"  # 替换为你的本地 WAV 文件路径
    upload_wav_file(file_path)
