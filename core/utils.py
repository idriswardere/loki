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

def create_prompt(modules, module_names):
    module_splits = [name.split("/") for name in module_names]
    for i, split in enumerate(module_splits):
        module = modules
        for part in split:
            module = module[part]
        module_splits[i] = module
        
    prompt = "\n\n".join(module_splits)
    return prompt