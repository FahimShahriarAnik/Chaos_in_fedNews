import os
import json
import csv

def extract_author_date_to_csv(input_file, output_csv):
    """
    Extract 'author' and 'date' values from a JSONL file and save them to a CSV file,
    ensuring that only unique authors are included.

    Args:
        input_file (str): Path to the input JSONL file.
        output_csv (str): Path to save the CSV file.
    """
    unique_authors = set()  # Track unique authors

    with open(input_file, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        
        # Write the header row
        writer.writerow(["author", "date"])
        
        for line in infile:
            try:
                # Parse the JSON object
                data = json.loads(line)
                
                # Extract 'author' and 'date'
                author = data.get("author", "").strip()
                date = data.get("date", "").strip()
                
                # Skip entries where 'author' is "[deleted]" or already processed
                if author == "[deleted]" or author in unique_authors:
                    continue
                
                # Add the author to the set of unique authors
                unique_authors.add(author)
                
                # Write to the CSV file
                writer.writerow([author, date])
            
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line}")

# Main function to process multiple files
if __name__ == "__main__":
    # File paths
    input_and_outputfiles = {
        "jobs_posts.jsonl": "authors_of_jobs_subreddit.csv",
        "fednews_posts.jsonl": "authors_of_fednews_subreddit.csv",
        "layoffs_posts.jsonl": "authors_of_layoffs_subreddit.csv"
    }
    
    for input_file, output_csv in input_and_outputfiles.items():
        print(f"Processing file: {input_file}")
        
        # Ensure the input file exists
        if not os.path.exists(input_file):
            print(f"Input file {input_file} does not exist. Skipping.")
            continue
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_csv)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Process the file and extract 'author' and 'date'
        print(f"Extracting 'author' and 'date' from {input_file} to {output_csv}")
        extract_author_date_to_csv(input_file, output_csv)
        print(f"Data saved to {output_csv}")