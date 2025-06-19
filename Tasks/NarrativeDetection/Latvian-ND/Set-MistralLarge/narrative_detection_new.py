#!/usr/bin/env python
# coding: utf-8

"""
Narrative Detection Script

This script processes a directory of text files containing news articles to perform narrative detection.
It utilizes the OpenAI and Langchain libraries to identify and analyze narratives within the articles.
The results are saved as new text files with detailed narrative analysis.

Steps:
1. Setup Functions: Initialize the OpenAI client and Langchain model.
2. Template Loading and Prompt Creation: Load the narrative detection template from a file.
3. File Operations: Read and write file contents.
4. Directory Processing: Process each text file in the directory and save the output.
5. Main Function: Run the narrative detection and save the results.
"""

import os
import logging
from collections import Counter
from openai import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import sys
import re


def setup_logging():
    logging.basicConfig(
        filename='narrative_detection.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def setup_openai_client():
    return AzureOpenAI(
        azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT'),
        api_key=os.environ.get('OPENAI_API_KEY'),
        api_version="2023-05-15"
    )


def setup_langchain_model():
    return AzureChatOpenAI(
        openai_api_version="2023-05-15",
        azure_deployment="gec"
    )


def load_examples(file_path):
    examples = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        current_layer = None
        for line in file:
            line = line.strip()
            if line.startswith('Layer:'):
                current_layer = line.split(':')[1].strip()
                examples[current_layer] = []
            elif current_layer and line:
                examples[current_layer].append(line)
    return examples


def load_template(file_path, examples):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
    except Exception as e:
        print(f"Error reading template file: {e}")
        logging.error(f"Error reading template file: {e}")
        return None

    formatted_content = template_content.replace(
        '{ner_examples}', '\n'.join(examples.get('Named Entity Recognition', ['']))
    ).replace(
        '{re_examples}', '\n'.join(examples.get('Relationship Extraction', ['']))
    ).replace(
        '{plot_examples}', '\n'.join(examples.get('Plot Discovery', ['']))
    ).replace(
        '{story_examples}', '\n'.join(examples.get('Story Evolution', ['']))
    )

    return formatted_content


def create_prompt_template(template_content):
    return PromptTemplate(
        input_variables=['language', 'text'],
        template=template_content
    )


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def save_output(output, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(output)


def count_entity_frequencies(document_text, entities):
    entity_counter = Counter()
    for entity in entities:
        entity_counter[entity] += document_text.lower().split().count(entity.lower())
    return entity_counter.most_common()


def process_directory(directory_path, chain):
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt') and not filename.endswith('_out.txt'):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {filename}")
            file_content = read_file(file_path)

            input_data = {
                'language': 'Latvian',  # Modify if the language varies
                'text': file_content
            }

            logging.info(f"Processing file: {filename}")
            logging.info(f"Input data: {input_data}")

            output = chain.run(input_data)

            logging.info(f"Output for file {filename}: {output}")

            #entities = extract_entities(output)
            #entity_frequencies = count_entity_frequencies(file_content, entities)

            output_filename = filename.replace('.txt', '_out.txt')
            output_path = os.path.join(directory_path, output_filename)
            save_output(output, output_path)
            print(f"Output saved in file: {output_filename}")


def extract_entities(output_text):
    entity_types = ['Location', 'Actor', 'Event', 'Timeline']
    entities = []

    for entity_type in entity_types:
        pattern = re.compile(rf'{entity_type}: \[(.*?)\]', re.DOTALL)
        matches = pattern.findall(output_text)

        for match in matches:
            # Split and clean the entities
            individual_entities = re.split(r',\s*(?![^[]*])', match)  # Handle nested commas
            cleaned_entities = [entity.strip() for entity in individual_entities]
            entities.extend(cleaned_entities)

    return entities


def format_entity_frequencies(entity_frequencies):
    formatted = "\n".join([f"{entity}: {frequency}" for entity, frequency in entity_frequencies])
    return formatted


def main():
    setup_logging()

    setup_openai_client()
    chat_model = setup_langchain_model()
    examples = load_examples('examples_layer.txt')
    template_content = load_template('narrative_detection_template.txt', examples)

    if template_content:
        print("Template content after formatting:")
        print(template_content)
        logging.info(f"Template content after formatting: {template_content}")

        prompt = create_prompt_template(template_content)
        chain = LLMChain(llm=chat_model, prompt=prompt)

        if len(sys.argv) != 2:
            print("Usage: python script_name.py <directory_path>")
            sys.exit(1)

        directory_path = sys.argv[1]

        if not os.path.isdir(directory_path):
            print(f"Error: {directory_path} is not a valid directory.")
            sys.exit(1)

        process_directory(directory_path, chain)


if __name__ == "__main__":
    main()
