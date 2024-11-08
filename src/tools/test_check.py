import json

# Load the JSON data from the files
with open('/Users/justin.hsu/Downloads/dataset/preliminary/ground_truths_example.json', 'r') as f:
    ground_truths_data = json.load(f)

with open('/Users/justin.hsu/Downloads/dataset/preliminary/questions_example.json', 'r') as f:
    questions_data = json.load(f)

# Create a dictionary for quick lookup by (category, qid)
questions_dict = {(item['category'], item['qid']): item['source'] for item in questions_data['questions']}

# List to collect results of ground truths where retrieve is not in the corresponding source list
missing_retrieve_entries = []

# Iterate through each ground truth entry to check if retrieve is in source
for ground_truth in ground_truths_data['ground_truths']:
    category = ground_truth['category']
    qid = ground_truth['qid']
    retrieve = ground_truth['retrieve']
    
    # Check if (category, qid) exists in questions_dict and retrieve is in the source list
    if (category, qid) in questions_dict and retrieve not in questions_dict[(category, qid)]:
        missing_retrieve_entries.append(ground_truth)

# Output the missing retrieve entries
if missing_retrieve_entries:
    print("Entries with 'retrieve' not found in the corresponding 'source':")
    for entry in missing_retrieve_entries:
        print(entry)
else:
    print("All 'retrieve' values are present in the corresponding 'source' lists.")
