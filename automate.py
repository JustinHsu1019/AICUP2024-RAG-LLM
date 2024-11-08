import requests
import json

# Load question examples from JSON file
with open('/content/questions_example.json', 'r', encoding='utf-8') as file:
    questions = json.load(file)['questions']  # Access the list of questions directly

# Initialize the output list
output_data = []

# URL for the API endpoint
url = "http://127.0.0.1:5002/api/chat"

# Iterate through each question example
for question in questions:
    print("讀取到的 JSON:", question)  # Print each loaded JSON object
    
    # Send POST request to the API
    response = requests.post(url, json=question)
    
    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        output_data.append(response_json)
        print("成功取得 JSON:", response_json)
    else:
        print("請求失敗，狀態碼:", response.status_code)

# Save the combined output to a JSON file
with open('pred_retrieve.json', 'w', encoding='utf-8') as output_file:
    json.dump(output_data, output_file, ensure_ascii=False, indent=4)

print("合併輸出已保存到 pred_retrieve.json 文件中。")

