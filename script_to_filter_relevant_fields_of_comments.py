import json

# Define fields to KEEP (based on your research goals)
RELEVANT_FIELDS = {
    "author",  # Track user activity
    "author_flair_*",  # Potential role indicator
    "banned_at_utc",  # Moderation insight
    "banned_by",  # Moderation insight
    "body",  # Primary analysis target
    "controversiality",  # Engagement metric
    "created",  # Time-series analysis
    "created_utc",  # Time-series analysis
    "edited",  # Content changes
    "id",  # Reference key to comment id
    "is_submitter",  # Conversation role -- If author is OP
    "link_id",  # Thread mapping -- Parent post ID
    "locked",  # Moderation insight
    "mod_note",  # Moderation insight
    "mod_reason_*",  # Moderation insight
    "mod_reports",  # Controversy flag
    "num_reports",  # Controversy metric
    "parent_id",  # Thread structure -- Parent comment ID 
    "permalink",  # Reference
    "removal_reason",  # Moderation insight
    "replies",  # Conversation depth
    "report_reasons",  # Moderation insight
    "score",  # Engagement metric -- Net votes (ups - downs)
    "user_reports"  # Controversy
}

def filter_fields(input_path, output_path):
    """Process a .jsonl file and retain only relevant fields."""
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        
        line_no = 0
        for line in infile:
            line_no += 1
            try:
                post = json.loads(line)
                # Keep only relevant fields (skip missing ones)
                filtered = {key: post[key] for key in RELEVANT_FIELDS if key in post}
                outfile.write(json.dumps(filtered) + '\n')
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line.strip()}")

        print("line_no: ", line_no)

if __name__ == "__main__":
    input_file_path = "2_months_data/r_fednews_comments.jsonl"  # Replace with your input file
    output_file_path = "2_months_data/filtered_comments.jsonl"  # Replace with desired output
    filter_fields(input_file_path, output_file_path)
    print(f"Filtered data saved to {output_file_path}")
