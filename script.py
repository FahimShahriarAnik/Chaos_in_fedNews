import json

############################# used this script to find all posts that contained 'trump' or 'Trump' in the title.

# Initialize a list to store all entries
data = []

# Step 1: Load the JSON file
with open('r_fednews_posts.jsonl', 'r', encoding='utf-8') as file:
    for line in file:
        # Parse each line as a JSON object
        entry = json.loads(line.strip())
        data.append(entry)
    #data = json.load(file)  # Assuming the JSON file is an array of objects

# Step 2: Initialize a list to store matching entries
matching_entries = []

# Step 3: Iterate through each entry
for entry in data:
    # Check if the title contains "trump" or "Trump"
    title = entry.get('title', '').lower()  # Convert to lowercase for case-insensitive search
    if 'trump' in title:
        matching_entries.append(entry)  # Add matching entry to the list

# Step 4: Output the results
print(f"Found {len(matching_entries)} entries with 'trump' or 'Trump' in the title.")
# for entry in matching_entries:
#     print(entry['title'])  # Print the title of each matching entry

# Optional: Save the matching entries to a new JSON file
with open('matching_entries.json', 'w', encoding='utf-8') as output_file:
    json.dump(matching_entries, output_file, indent=4)