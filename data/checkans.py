import json
from collections import defaultdict

# Load ground truth data
with open('data/ground_truths_example.json', 'r') as f:
    ground_truths = json.load(f)["ground_truths"]

# Load predicted data with the new format
with open('data/pred_retrieve.json', 'r') as f:
    pred_retrieves = json.load(f)["answers"]

# Create a dictionary from predictions for easy lookup
pred_dict = {item["qid"]: item["retrieve"] for item in pred_retrieves}

# Initialize counters and data structures
incorrect_qids = []
correct_count = 0
category_counts = defaultdict(lambda: {"correct": 0, "total": 0})

# Compare predictions to ground truth
for ground in ground_truths:
    qid = ground["qid"]
    category = ground["category"]
    correct_retrieve = ground["retrieve"]
    predicted_retrieve = pred_dict.get(qid)

    if predicted_retrieve == correct_retrieve:
        correct_count += 1
        category_counts[category]["correct"] += 1
    else:
        incorrect_qids.append(qid)

    category_counts[category]["total"] += 1

# Print results
print("錯誤的題目 QID:", incorrect_qids)
print(f"總正確題數: {correct_count} / {len(ground_truths)}")

for category, counts in category_counts.items():
    print(f"類別 {category}: {counts['correct']} / {counts['total']}")
