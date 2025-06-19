import os
import re

def parse_file(file_path):
    """Parse the file with the agreed structure and return a dictionary of topics and their details."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data = {}
    current_topic = None
    in_keywords_section = False  # To track when we are inside the [Keywords] section
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("[Topic]"):
            current_topic = line.split("[Topic]")[1].strip()
            data[current_topic] = {"keywords": [], "weight": 0, "total_weight": 0, "normalized_significance": 0}
            in_keywords_section = False  # Reset whenever a new topic starts
        
        elif line.startswith("[Weight]"):
            weight = int(line.split("[Weight]")[1].strip())
            data[current_topic]["weight"] = weight
        
        elif line.startswith("[Keywords]"):
            in_keywords_section = True  # Enable keyword processing
        
        elif in_keywords_section and "=" in line:
            # Split keyword and score by the equal sign
            keyword, score = line.split("=")
            keyword = keyword.strip()
            score = int(score.strip())
            data[current_topic]["keywords"].append((keyword, score))
        
        elif line.startswith("[Total Weight]"):
            total_weight = int(line.split("[Total Weight]")[1].strip())
            data[current_topic]["total_weight"] = total_weight
        
        elif line.startswith("[Normalized Significance]"):
            try:
                normalized_significance = float(line.split("[Normalized Significance]")[1].strip())
            except ValueError:
                normalized_significance = "N/A"  # Handle cases where it's not a float
                print(f"Warning: Unable to convert Normalized Significance to float in {file_path}, set to 'N/A'.")
            data[current_topic]["normalized_significance"] = normalized_significance
    
    return data

def compare_files(human_file, machine_file, output_file):
    """Compare the topics and keywords from two files and write the comparison to an output file."""
    
    # Print the files being compared
    print(f"Comparing files:\n - Human file: {human_file}\n - Machine file: {machine_file}")
    
    # Read topics and keywords from both files
    human_data = parse_file(human_file)
    machine_data = parse_file(machine_file)

    # Initialize counters for statistics
    total_common_topics = 0
    total_human_topics = len(human_data)
    total_machine_topics = len(machine_data)
    total_common_keywords = 0
    total_human_keywords = 0
    total_machine_keywords = 0

    # Compare topics
    human_topics = set(human_data.keys())
    machine_topics = set(machine_data.keys())

    common_topics = human_topics.intersection(machine_topics)
    human_only_topics = human_topics.difference(machine_topics)
    machine_only_topics = machine_topics.difference(human_topics)

    # Write the comparison to the output file
    with open(output_file, 'w') as f:
        for topic in common_topics:
            # Write topic with both human and machine weights
            human_weight = human_data[topic]["weight"]
            machine_weight = machine_data[topic]["weight"]
            f.write(f"Topic: {topic}={human_weight}={machine_weight}\n")
            total_common_topics += 1  # Increment common topic count

            # Compare keywords for this topic
            human_keywords = {kw: score for kw, score in human_data[topic]["keywords"]}
            machine_keywords = {kw: score for kw, score in machine_data[topic]["keywords"]}

            common_keywords = human_keywords.keys() & machine_keywords.keys()
            human_only_keywords = human_keywords.keys() - machine_keywords.keys()
            machine_only_keywords = machine_keywords.keys() - human_keywords.keys()

            total_human_keywords += len(human_keywords)  # Count human keywords
            total_machine_keywords += len(machine_keywords)  # Count machine keywords

            # Write common keywords with both weights
            if common_keywords:
                f.write("  Common Keywords:\n")
                for keyword in common_keywords:
                    human_weight = human_keywords[keyword]
                    machine_weight = machine_keywords[keyword]
                    f.write(f"   {keyword}={human_weight}={machine_weight}\n")
                total_common_keywords += len(common_keywords)  # Count common keywords
                f.write("\n")  # Add an extra blank line for separation

            # Write human-only keywords with their weights
            if human_only_keywords:
                f.write("  Keywords Assigned by Human but Not by Machine:\n")
                for keyword in human_only_keywords:
                    f.write(f"   {keyword}={human_keywords[keyword]}\n")
                f.write("\n")  # Add an extra blank line for separation

            # Write machine-only keywords with their weights
            if machine_only_keywords:
                f.write("  Keywords Assigned by Machine but Not by Human:\n")
                for keyword in machine_only_keywords:
                    f.write(f"   {keyword}={machine_keywords[keyword]}\n")
                f.write("\n")  # Add an extra blank line for separation

            # Add a blank line to separate topics
            f.write("\n")

        # Write topics that are assigned by the human but not the machine
        if human_only_topics:
            f.write("Topics Assigned by Human but Not by Machine:\n")
            for topic in human_only_topics:
                f.write(f"Topic: {topic}={human_data[topic]['weight']}\n")  # Write the human weight for this topic
            f.write("\n")

        # Write topics that are assigned by the machine but not the human
        if machine_only_topics:
            f.write("Topics Assigned by Machine but Not by Human:\n")
            for topic in machine_only_topics:
                f.write(f"Topic: {topic}={machine_data[topic]['weight']}\n")  # Write the machine weight for this topic
            f.write("\n")

        # Add statistics section
        f.write("Statistics:\n")
        f.write(f"Common Topics: {total_common_topics}\n")
        f.write(f"Topics Assigned by Human: {total_human_topics}\n")
        f.write(f"Topics Assigned by Machine: {total_machine_topics}\n")
        f.write(f"Common Keywords: {total_common_keywords}\n")
        f.write(f"Keywords Assigned by Human: {total_human_keywords}\n")
        f.write(f"Keywords Assigned by Machine: {total_machine_keywords}\n")

    print(f"Comparison written to {output_file}")

def find_pairs_and_compare(directory, suffix):
    """Find file pairs and perform comparison."""
    files = os.listdir(directory)
    print(f"Files in directory: {files}")  # Debug print to see files

    human_files = [f for f in files if f.endswith("-human.txt")]
    print(f"Human files: {human_files}")  # Debug print to see human files

    for human_file in human_files:
        base_name = human_file.replace("-human.txt", "")
        machine_file = f"{base_name}-{suffix}.txt"
        human_path = os.path.join(directory, human_file)
        machine_path = os.path.join(directory, machine_file)
        
        print(f"Checking for machine file: {machine_path}")  # Debug print

        if os.path.exists(machine_path):
            output_file = os.path.join(directory, f"{base_name}-compare.txt")
            print(f"Comparing: {human_file} with {machine_file}")  # Debug print
            compare_files(human_path, machine_path, output_file)
        else:
            print(f"Missing machine file for {base_name}, skipping comparison.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python compare_topics.py <directory> <machine_file_suffix>")
    else:
        find_pairs_and_compare(sys.argv[1], sys.argv[2])
