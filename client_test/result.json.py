import json

# 示例数据
data = ["{\n  \"partial\" : \"\"\n}", "{\n  \"partial\" : \"\"\n}", "{\n  \"partial\" : \"\"\n}", "{\n  \"partial\" : \"\"\n}", "{\n  \"partial\" : \"\"\n}",
        "{\n  \"partial\" : \"\"\n}", "{\n  \"partial\" : \"\u53ef\u662f\"\n}", "{\n  \"partial\" : \"\u53ef\u662f\"\n}", "{\n  \"text\" : \"\u53ef\u662f \u554a\"\n}"]

# 初始化一个空字符串用于存储识别的文本
recognized_text = ""

# 遍历列表中的每个 JSON 字符串
for json_str in data:
    # 将 JSON 字符串解析为字典
    res_dict = json.loads(json_str)

    # 从字典中提取 "text" 字段并拼接到 recognized_text
    recognized_text += res_dict.get("text", "")

# 打印识别的文本
print("Recognized Text:", recognized_text)
