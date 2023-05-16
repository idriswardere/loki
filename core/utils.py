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


def parse_reply_reflection(response_str, debug=False):
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

    if debug:
        print("---REPLY NOT FOUND--RESPONSE BELOW---")
        print(response_str)
        print("-------------------------------------")
    return None, None

def create_prompt(modules, module_names):
    module_splits = [name.split("/") for name in module_names]
    for i, split in enumerate(module_splits):
        module = modules
        for part in split:
            module = module[part]
        module_splits[i] = module
        
    prompt = "\n\n".join(module_splits)
    return prompt