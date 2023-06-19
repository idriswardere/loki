# Importing appropriate libraries
debug = True
from dotenv import load_dotenv
from core.utils import load_modules, create_prompt
from core.llms import GPT3
from core.details import Details, Shu
from flask import Flask

app = Flask(__name__)

max_failed_prompts = 1

modules = load_modules()
load_dotenv()

@app.route("/initialize/<new_llm>/<new_npc_name>/<new_k>/<player_desc>/<player_msg>")
def main(new_llm, new_npc_name, new_k, player_desc, player_msg):
    global llm
    global details
    global relevant_details_list
    global relevant_details
    global original_task
    global module_names
    global prompt
    global npc_name
    global k

    new_k = int(new_k)

    k = new_k
    npc_name = new_npc_name

    llms_dict = {"GPT3" : GPT3}

    # Initializing conversation details with input
    # llm_names = llms_dict.keys()
    # llm_name = input("Which LLM would you like to use for response generation?\nOptions: [" + " ".join(llm_names) + "]\n> ")
    # while llm_name not in llms_dict:
    #     llm_name = input("LLM not found. Please try again. (Note: LLM name is case-sensitive.)\n> ")

    llm = llms_dict[new_llm]()

    # npc_names = modules['characters'].keys()
    # npc_name = input("Who would you like to speak to?\nOptions: [" + " ".join(npc_names) + "]\n> ") # character being spoken to

    # while npc_name not in modules['characters']:
    #     npc_name = input("Character not found. Please try again. (Note: Character name is case-sensitive.)\n> ")

    # k = int(input("How many world details would you like the character to be able to pull from the database?\n> "))
    # player_desc = input("Write a description of your player's character.\n(e.g. A non-magical goblin who is wearing chainmail armor and leather boots. Is very strong physically.)\n> ")
    # player_msg = input(f"You are speaking to {npc_name}. What do you want to say?\n> ")

    # Initializing relevant details
    details = Shu()
    relevant_details_list = "" #details.query(player_msg, k=new_k)
    relevant_details = "\n".join(relevant_details_list)
    modules['relevant_details'] = modules['relevant_details_template'].format(relevant_details=relevant_details)


    # Initializing prompt parts
    modules['player'] = modules['player'].format(player_desc=player_desc)
    modules['current_interaction'] = modules['current_interaction'].format(npc_name=new_npc_name, player_msg=player_msg)
    original_task = modules['task']
    modules['task'] = modules['task'].format(npc_name=new_npc_name, player_msg=player_msg)

    # Defining response prompt (with reflection)
    # TODO: prompt_list should also automatically include modules available to npc_name added after global
    module_names = ['global', 'relevant_details', 'characters/' + new_npc_name, 'player', 'current_interaction', 'task']
    prompt = create_prompt(modules, module_names)
    reply, reflection = llm.get_response(prompt)
    if not reply or not reflection: # if prompt fails, allow retry until we retry a certain amount of times
        failed_prompts += 1
        if failed_prompts >= max_failed_prompts:
            return "Failed"
        newPlayerMessageRepeated(failed_prompts, prompt)
    modules['current_interaction'] += f"""\n{npc_name} responded: {reply}"""

    return reply
    

@app.route("/newMessage/<player_msg>")
def newPlayerMessage(player_msg):
    return newPlayerMessageRepeated(0, player_msg)

def newPlayerMessageRepeated(failed_prompts, player_msg):
    # Get response from prompt and extract reply/reflections from it
    # print("Loading response...", end='\r')

    # print("-----------------------------")
    # print("--RELEVANT DETAILS--")
    # print(relevant_details + "\n")
    # print("--REFLECTIONS--")
    # print(reflection)
    # print("--CURRENT INTERACTION--")
    # print(modules['current_interaction'] + "\n")
    # print("-----REPLY-----")
    # print(reply + "\n")

    # Updating prompt list with new current interaction
    modules['current_interaction'] += f"""\nThe player responded: “{player_msg}”"""

    # Updating relevant details
    relevant_details_list = "" # details.query(player_msg, k=k)
    relevant_details = "\n".join(relevant_details_list)
    modules['relevant_details'] = modules['relevant_details_template'].format(relevant_details=relevant_details)

    modules['task'] = original_task.format(npc_name=npc_name, player_msg=player_msg)

    module_names = ['global', 'relevant_details', 'characters/'+npc_name, 'player', 'current_interaction', 'task']
    prompt = create_prompt(modules, module_names)

    reply, reflection = llm.get_response(prompt)
    if not reply or not reflection: # if prompt fails, allow retry until we retry a certain amount of times
        failed_prompts += 1
        if failed_prompts >= max_failed_prompts:
            return "Failed"
        newPlayerMessageRepeated(failed_prompts, prompt)
    modules['current_interaction'] += f"""\n{npc_name} responded: {reply}"""

    # Printing the prompt for debugging purposes
    if debug:
        print('--PROMPT--')
        print(prompt + "\n")

    return reply