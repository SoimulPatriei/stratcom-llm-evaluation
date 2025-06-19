
#CoT ASSA: Python script
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import logging
import os
import re
import sys
import time

def setup_logging():
    logging.basicConfig(
        filename='absa.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_config(config_file):
    # Open the JSON file
    with open(config_file, 'r') as file:
        config = json.load(file)
        return config

def run_prompt(llm, prompt, **kwargs):
    prompt_template = PromptTemplate(template=prompt, input_variables=list(kwargs.keys()))
    chain = prompt_template | llm 
    return chain.invoke(kwargs).content

def setup_llm_client(config,llm_model):
    api_key = config['openrouter']['api_key']
    api_base = config['openrouter']['api_base']
    model = config['model'][llm_model]
    return  ChatOpenAI(
        openai_api_key= api_key,
        openai_api_base= api_base,
        model_name=model
        #temperature=0,
        #model_kwargs={
        #    "headers": {
        #    "HTTP-Referer": getenv("APP_URL"),
        #    "X-Title": getenv("APP_TITLE"),
        #    }
        #},
    )    

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_output(output, output_path, mode='w'):
    with open(output_path, mode=mode, encoding='utf-8') as file:
        file.write(output)

def load_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_entities(article):
    # Define the patterns to extract the lists
    location_pattern = re.compile(r'Location:\s*\[(.*?)\]', re.DOTALL)
    actor_pattern = re.compile(r'Actor:\s*\[(.*?)\]', re.DOTALL)
    event_pattern = re.compile(r'Event:\s*\[(.*?)\]', re.DOTALL)

    # Find the matches
    location_match = location_pattern.search(article)
    actor_match = actor_pattern.search(article)
    event_match = event_pattern.search(article)

    # Extract and clean the lists
    locations = location_match.group(1).split(', ') if location_match else []
    actors = actor_match.group(1).split(', ') if actor_match else []
    events = event_match.group(1).split(', ') if event_match else []

    return locations, actors, events

def process_directory(indirectory_path, outdirectory_path, llm, config):
    article_content = ''
    narrative_out_content = ''
    #Extract proposed aspects
    pa = ''
    with open(config["prop_aspects"], 'r') as file:
        pa = json.load(file)
    loc_pa = "\n".join(pa["location"])
    act_pa = "\n".join(pa["actor"])
    eve_pa = "\n".join(pa["event"])

    #Read subtask and maintask prompt
    subtask_prompt = load_template(config["prompt-files"]["subtask"])  
    main_prompt = load_template(config["prompt-files"]["maintask"])

    for filename in os.listdir(indirectory_path):
        # Record the start time
        start_time = time.time()
        if filename.endswith('.txt') and not filename.endswith('_out.txt'):
            file_path = os.path.join(indirectory_path, filename)
            print(f"Processing file: {filename}")
            article_content = read_file(file_path)

            #Extract pre-identified entities
            file_path = os.path.join(indirectory_path, str(filename).replace('.txt','_out.txt'))
            narrative_out_content = read_file(file_path)
            locations, actors, events = extract_entities(narrative_out_content)

            #output settings
            output_filename = filename.replace('.txt', '_absa_out.txt')
            output_path = os.path.join(outdirectory_path, output_filename)

            #Subtasks
            #subtasks: Analysis of Locations, Actors & Events
            #subtask:Location
            location_output = run_prompt(llm,
                                         prompt= subtask_prompt,
                                         entity_type='LOCATION',
                                         entities= locations, 
                                         proposed_aspects=loc_pa, 
                                         article_content= article_content, 
                                         language= 'English'
                                         )
            save_output(location_output + '\n\n', output_path, 'a')
            #subtask:Actor
            actor_output = run_prompt(llm,
                                      prompt=subtask_prompt,
                                      entity_type='ACTOR',
                                      entities= actors, 
                                      proposed_aspects=act_pa, 
                                      article_content= article_content, 
                                      language= 'English'
                                      )
            save_output(actor_output+ '\n\n', output_path, 'a')
            #subtask:Event 
            event_output = run_prompt(llm,
                                      prompt=subtask_prompt,
                                      entity_type='EVENT',
                                      entities= events, 
                                      proposed_aspects=eve_pa, 
                                      article_content= article_content, 
                                      language= 'English'
                                      )
            save_output(event_output+ '\n\n', output_path, 'a')
            
            #main-task
            absa_output = run_prompt(llm,
                                     prompt=main_prompt, 
                                     article_content= article_content, 
                                     language= 'English', 
                                     locations= locations, 
                                     actors= actors, 
                                     events= events,
                                     locations_analysis= location_output,
                                     actors_analysis= actor_output,
                                     events_analysis= event_output
                                     )
            save_output(absa_output, output_path, 'a')
            # Record the end time
            end_time = time.time()
            #print(f"Output saved in file: {output_filename}")
            # Calculate the task time
            task_time = end_time - start_time
            print(f"{output_filename} completed in {task_time:.2f} seconds.")
            #break
        

def main():
    config = get_config('config.json')
    """
    if len(sys.argv) != 3:
        model_list = [k for k,v in config['model'].items()]
        print(f"Usage: python script_name.py <llm-model-name = {model_list}>")
        sys.exit(1)
    """
    MODEL_NAME= "gpt-4"
    llm = setup_llm_client(config,MODEL_NAME )
    indirectory_path = config['dir']['in-dir']
    outdirectory_path = config['dir']['out-dir']
    process_directory(indirectory_path, outdirectory_path, llm, config)

if __name__ == "__main__":
    main()