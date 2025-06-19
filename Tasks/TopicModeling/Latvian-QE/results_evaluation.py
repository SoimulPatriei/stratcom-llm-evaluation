import os
import re

# Use the current directory as the main directory
main_directory = os.getcwd()

# Iterate through each subdirectory in the current directory
for subdir in os.listdir(main_directory):
    subdir_path = os.path.join(main_directory, subdir, 'Results_comparison')
    
    if os.path.isdir(subdir_path):
        # Initialize statistics for the current directory
        common_topics = topics_human = topics_machine = common_keywords = keywords_human = keywords_machine = 0
        file_count = 0

        # Iterate through each file in the Results_comparison directory
        for file in os.listdir(subdir_path):
            if file.endswith('-compare.txt'):
                file_path = os.path.join(subdir_path, file)
                
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Extract statistics using regular expressions
                    common_topics += int(re.search(r'Common Topics:\s*(\d+)', content).group(1))
                    topics_human += int(re.search(r'Topics Assigned by Human:\s*(\d+)', content).group(1))
                    topics_machine += int(re.search(r'Topics Assigned by Machine:\s*(\d+)', content).group(1))
                    common_keywords += int(re.search(r'Common Keywords:\s*(\d+)', content).group(1))
                    keywords_human += int(re.search(r'Keywords Assigned by Human:\s*(\d+)', content).group(1))
                    keywords_machine += int(re.search(r'Keywords Assigned by Machine:\s*(\d+)', content).group(1))
                    file_count += 1

        # Print statistics for the current directory
        if file_count > 0:
            print(f"Statistics for Directory: {subdir}")
            print(f"  Files Processed: {file_count}")
            print(f"  Common Topics: {common_topics}")
            print(f"  Topics Assigned by Human: {topics_human}")
            print(f"  Topics Assigned by Machine: {topics_machine}")
            print(f"  Common Keywords: {common_keywords}")
            print(f"  Keywords Assigned by Human: {keywords_human}")
            print(f"  Keywords Assigned by Machine: {keywords_machine}\n")
