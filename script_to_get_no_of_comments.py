import json

def filter_fields(input_path):
    """Process a .jsonl file and retain only relevant fields."""
    with open(input_path, 'r', encoding='utf-8') as infile:
        
        line_no = 0
        for line in infile:
            line_no += 1
            # try:
            #     post = json.loads(line)
            #     # Keep only relevant fields (skip missing ones)
            #     filtered = {key: post[key] for key in RELEVANT_FIELDS if key in post}
            #     outfile.write(json.dumps(filtered) + '\n')
            # except json.JSONDecodeError:
            #     print(f"Skipping invalid JSON line: {line.strip()}")

        print("line_no: ", line_no)

if __name__ == "__main__":
    input_file_path = "2_months_data/r_fednews_comments.jsonl"  # Replace with your input file
    #$output_file_path = "2_months_data/filtered_posts.jsonl"  # Replace with desired output
    filter_fields(input_file_path)
    # print(f"Filtered data saved to {output_file_path}")