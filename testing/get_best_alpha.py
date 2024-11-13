import json
from collections import defaultdict

import requests

# Load questions from the JSON file
with open('data/questions.json', encoding='utf-8') as file:
    questions = json.load(file)['questions']

# Load ground truth data
with open('data/ground_truths_example.json', encoding='utf-8') as f:
    ground_truths = json.load(f)['ground_truths']

# Dictionary to hold the best alpha and accuracy
best_alpha = 0.0
best_accuracy = 0

# Loop through alpha values from 0.0 to 1.0
for alpha in [round(x * 0.1, 1) for x in range(11)]:
    output_data = {'answers': []}  # Reset output format with "answers" array

    url = 'http://127.0.0.1:5000/api/chat'

    # Send each question to the API with the current alpha
    for question in questions:
        # Add the alpha key to the question payload
        question_with_alpha = {**question, 'alpha': alpha}

        # Send POST request
        response = requests.post(url, json=question_with_alpha)

        if response.status_code == 200:
            response_json = response.json()
            qid = question.get('qid')
            retrieve = response_json.get('retrieve')

            # Append formatted result to the answers array
            output_data['answers'].append({'qid': qid, 'retrieve': retrieve})
        else:
            print(f'請求失敗，狀態碼: {response.status_code}，Alpha 值: {alpha}')

    # Save predictions for the current alpha
    pred_file = f'data/pred_retrieve_alpha_{alpha}.json'
    with open(pred_file, 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)

    # Load predictions for comparison
    pred_dict = {item['qid']: item['retrieve'] for item in output_data['answers']}

    # Initialize counters and data structures for accuracy calculation
    correct_count = 0
    category_counts = defaultdict(lambda: {'correct': 0, 'total': 0})

    # Compare predictions to ground truth
    for ground in ground_truths:
        qid = ground['qid']
        category = ground['category']
        correct_retrieve = ground['retrieve']
        predicted_retrieve = pred_dict.get(qid)

        if predicted_retrieve == correct_retrieve:
            correct_count += 1
            category_counts[category]['correct'] += 1

        category_counts[category]['total'] += 1

    # Calculate accuracy for the current alpha
    accuracy = correct_count / len(ground_truths)
    print('Corrrect count: ', correct_count)
    print(f'Alpha: {alpha}, 正確率: {accuracy:.2%}')

    # Track the best alpha and accuracy
    if accuracy > best_accuracy:
        best_alpha = alpha
        best_accuracy = accuracy

# Output the best alpha and accuracy
print(f'最佳 Alpha 值: {best_alpha}, 準確率: {best_accuracy:.2%}')
