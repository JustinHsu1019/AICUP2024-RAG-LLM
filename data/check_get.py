import json

# 載入 aicup_noocr.json 和 aicup_ref.json
with open('data/aicup_noocr.json', 'r', encoding='utf-8') as file:
    noocr_data = json.load(file)

with open('data/aicup_ref.json', 'r', encoding='utf-8') as file:
    ref_data = json.load(file)

# 建立 ref_data 的 dictionary，方便根據 category+pid 找到對應的 content
ref_dict = {(item["category"], item["pid"]): item["content"] for item in ref_data}

# 更新 noocr_data 中空的 content
for item in noocr_data:
    category = item["category"]
    pid = item["pid"]
    content = item["content"]

    # 如果 content 是 string 並且為空，則從 ref_data 裡填入對應的 content
    if isinstance(content, str) and content == "":
        if (category, pid) in ref_dict:
            item["content"] = ref_dict[(category, pid)]

# 將結果寫入 aicup_noocr_sec.json
with open('data/aicup_noocr_sec.json', 'w', encoding='utf-8') as file:
    json.dump(noocr_data, file, ensure_ascii=False, indent=4)

print("已完成比對並生成 aicup_noocr_sec.json")
