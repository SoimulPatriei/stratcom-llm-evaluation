#!/usr/bin/env python
# coding: utf-8

"""
Topic Modeling Script

This script processes a directory of text files containing news articles to perform topic modeling.
It utilizes the OpenAI and Langchain libraries to assign topics to the articles.
The results are saved as new text files with detailed topic analysis.

Steps:
1. Setup Functions: Initialize the OpenAI client and Langchain model.
2. Template Loading and Prompt Creation: Load the topic modeling template from a file.
3. File Operations: Read and write file contents.
4. Directory Processing: Process each text file in the directory and save the output.
5. Main Function: Run the topic modeling and save the results.
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
        filename='topic_modeling.log',
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


def load_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
    except Exception as e:
        print(f"Error reading template file: {e}")
        logging.error(f"Error reading template file: {e}")
        return None
    return template_content


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


def extract_keywords_and_weights(output_text):
    pattern = re.compile(r'(\w+)\s*\((\d)\)', re.DOTALL)
    matches = pattern.findall(output_text)
    keywords_with_weights = [(match[0], int(match[1])) for match in matches]
    return keywords_with_weights


def normalize_weights(keywords_with_weights):
    total_weight = sum(weight for _, weight in keywords_with_weights)
    normalized_weights = [(keyword, round((weight / total_weight) * 10, 2)) for keyword, weight in keywords_with_weights]
    return normalized_weights


def process_directory(directory_path, chain, language):
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt') and not filename.endswith('-GPT4.0.txt'):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing file: {filename}")
            file_content = read_file(file_path)

            input_data = {
                'language': language,
                'text': file_content
            }

            logging.info(f"Processing file: {filename}")
            logging.info(f"Input data: {input_data}")

            output = chain.run(input_data)

            logging.info(f"Output for file {filename}: {output}")

            output_filename = filename.replace('.txt', '-GPT4.0.txt')
            output_path = os.path.join(directory_path, output_filename)
            save_output(output, output_path)

            print(f"Output saved in file: {output_filename}")


def main():
    setup_logging()
    setup_openai_client()
    chat_model = setup_langchain_model()

    template_content = load_template('topic_modeling_template.txt')

    if template_content:
        print("Template content after formatting:")
        print(template_content)
        logging.info(f"Template content after formatting: {template_content}")

        prompt = create_prompt_template(template_content)
        chain = LLMChain(llm=chat_model, prompt=prompt)

        if len(sys.argv) != 3:
            print("Usage: python script_name.py <directory_path> <language>")
            sys.exit(1)

        directory_path = sys.argv[1]
        language = sys.argv[2]

        if not os.path.isdir(directory_path):
            print(f"Error: {directory_path} is not a valid directory.")
            sys.exit(1)

        process_directory(directory_path, chain, language)


if __name__ == "__main__":
    main()
