import requests
import json
import time  # Import time module for timing

# Load questions from the JSON file
with open('data/questions_example.json', 'r', encoding='utf-8') as file:
    questions = json.load(file)['questions']

output_data = {"answers": []}  # Initialize output format with "answers" array

url = "http://127.0.0.1:5000/api/chat"

total_start_time = time.time()  # Start timing for the entire process

for question in questions:
    question_start_time = time.time()  # Start timing for each question
    
    # Send POST request
    response = requests.post(url, json=question)

    if response.status_code == 200:
        response_json = response.json()
        
        # Extract qid and retrieve from the API response
        qid = question.get("qid")  # Assuming each question has a unique "qid" field
        retrieve = response_json.get("retrieve")
        
        # Append formatted result to the answers array
        output_data["answers"].append({
            "qid": qid,
            "retrieve": retrieve
        })
        print("成功取得 JSON:", response_json)
    else:
        print("請求失敗，狀態碼:", response.status_code)
    
    # Calculate and print time for each question
    question_end_time = time.time()
    question_duration = question_end_time - question_start_time
    print(f"QID: {qid} - 花費時間: {question_duration:.2f} 秒")

# Calculate and print total time
total_end_time = time.time()
total_duration = total_end_time - total_start_time
print(f"全部題目處理完成，總共花費時間: {total_duration:.2f} 秒")

# Save the output data to a new JSON file
with open('data/pred_retrieve.json', 'w', encoding='utf-8') as output_file:
    json.dump(output_data, output_file, ensure_ascii=False, indent=4)

print("合併輸出已保存到 pred_retrieve.json 文件中。")
