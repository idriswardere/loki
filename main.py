# Importing appropriate libraries
debug = True
from dotenv import load_dotenv
from core.utils import load_modules, create_prompt
from core.llms import GPT3
from core.details import Details, Shu

load_dotenv() # Loading secret API keys
modules = load_modules() # Defining prompt modules

llms_dict = {"GPT3" : GPT3}

# Initializing conversation details with input
llm_names = llms_dict.keys()
llm_name = input("Which LLM would you like to use for response generation?\nOptions: [" + " ".join(llm_names) + "]\n")
llm = llms_dict[llm_name]()

npc_names = modules['characters'].keys()
npc_name = input("Who would you like to speak to?\nOptions: [" + " ".join(npc_names) + "]\n") # character being spoken to
k = int(input("How many world details would you like the character to be able to pull from the database?\n"))
player_desc = input("Write a description of your player's character.\n(e.g. A non-magical goblin who is wearing chainmail armor and leather boots. Is very strong physically.)\n")
player_msg = input(f"You are speaking to {npc_name}. What do you want to say?\n")

# Initializing relevant details
details = Shu()
relevant_details_list = details.query(player_msg, k=k)
relevant_details = "\n".join(relevant_details_list)
modules['relevant_details'] = modules['relevant_details_template'].format(relevant_details=relevant_details)


# Initializing prompt parts
modules['player'] = modules['player'].format(player_desc=player_desc)
modules['current_interaction'] = modules['current_interaction'].format(npc_name=npc_name, player_msg=player_msg)
original_task = modules['task']
modules['task'] = modules['task'].format(npc_name=npc_name, player_msg=player_msg)

# Defining response prompt (with reflection)
# TODO: prompt_list should also automatically include modules available to npc_name added after global
module_names = ['global', 'relevant_details', 'characters/'+npc_name, 'player', 'current_interaction', 'task']
prompt = create_prompt(modules, module_names)

failed_prompts = 0
max_failed_prompts = 1
while player_msg.lower() != "exit":
    # Get response from prompt and extract reply/reflections from it
    reply, reflection = llm.get_response(prompt)
    if not reply or not reflection: # if prompt fails, allow retry until we retry a certain amount of times
        failed_prompts += 1
        if failed_prompts >= max_failed_prompts:
            break
        continue

    print("-----------------------------")
    print("--RELEVANT DETAILS--")
    print(relevant_details + "\n")
    print("--REFLECTIONS--")
    print(reflection)
    print("--CURRENT INTERACTION--")
    print(modules['current_interaction'] + "\n")
    print("-----REPLY-----")
    print(reply + "\n")

    # Updating prompt list with new current interaction
    modules['current_interaction'] += f"""\n{npc_name} responded: {reply}"""
    player_msg = input("Enter a response: ")
    modules['current_interaction'] += f"""\nThe player responded: “{player_msg}”"""

    # Updating relevant details
    relevant_details_list = details.query(player_msg, k=k)
    relevant_details = "\n".join(relevant_details_list)
    modules['relevant_details'] = modules['relevant_details_template'].format(relevant_details=relevant_details)

    modules['task'] = original_task.format(npc_name=npc_name, player_msg=player_msg)

    module_names = ['global', 'relevant_details', 'characters/'+npc_name, 'player', 'current_interaction', 'task']
    prompt = create_prompt(modules, module_names)

    # Printing the prompt for debugging purposes
    if debug:
        print('--PROMPT--')
        print(prompt + "\n")