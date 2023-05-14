import os
import openai
from dotenv import load_dotenv

# Create modules dict containing text from the modules directory
def load_modules(root="modules"):
    modules = dict()
    files = os.listdir(root)

    # processing .txt files
    txt_file_names = [file for file in files if file.endswith(".txt")]
    for txt_file_name in txt_file_names: # defining module key/value pairs for each file
        path = os.path.join(root, txt_file_name)
        module_name = txt_file_name[:-4] # removing .txt
        with open(path, "r", encoding="utf-8") as txt_file:
            modules[module_name] = txt_file.read()

    # processing folders recursively
    folder_names = [file for file in files if "." not in file]
    for folder_name in folder_names:
        next_root = os.path.join(root, folder_name)
        modules[folder_name] = load_modules(root=next_root)
    
    return modules


# Get response from GPT-3 with prompt using OpenAI API
def get_response(prompt):
  load_dotenv()
  openai.api_key = os.getenv("OPENAI_API_KEY")
  response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    temperature=0.7,
    max_tokens=512,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
  )
  return response


# Parses reply out of the OpenAI response object
def get_reply(response):
  response_str = response['choices'][0]['text']

  reply_start_tag, reply_end_tag = "<r>", "</r>"
  reply_start_idx = response_str.find(reply_start_tag)
  reply_end_idx = response_str.find(reply_end_tag)

  # Safety checks on response
  tags_exist = (reply_start_idx >= 0 and reply_end_idx >= 0) # both exist
  tags_ordered_correctly = (reply_start_idx+3 < reply_end_idx)  # start tag is before end tag
  tags_occur_once = (response_str.count(reply_start_tag) == 1 and response_str.count(reply_end_tag) == 1) # both only occur once


  if tags_exist and tags_ordered_correctly and tags_occur_once:
    reply = response_str[reply_start_idx+3:reply_end_idx]
    reflection = response_str[:reply_start_idx]
    return reply, reflection
  else:
    print("---REPLY NOT FOUND--RESPONSE BELOW---")
    print(response_str)
    print("-------------------------------------")
    return None, None

def create_prompt(modules, module_names):
    prompt_list = [modules[name] for name in module_names]
    prompt = "\n\n".join(prompt_list)
    return prompt