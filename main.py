# Importing appropriate libraries
import os
import openai
from dotenv import load_dotenv

from core.utils import load_modules, get_response, get_reply, create_prompt

debug = True

# Defining prompt modules
modules = load_modules()

# Initializing conversation details with input
npc_name = input("Who would you like to speak to?\nOptions: [Shu]\n") # character being spoken to
player_desc = input("Write a description of your player's character.\n(e.g. A non-magical goblin who is wearing chainmail armor and leather boots. Is very strong physically.)\n")
player_msg = input(f"You are speaking to {npc_name}. What do you want to say?\n")

# Initializing prompt parts
modules['player'] = modules['player'].format(player_desc=player_desc)
modules['current_interaction'] = modules['initial_interaction'].format(npc_name=npc_name, player_msg=player_msg)
modules['task'] = modules['task'].format(npc_name=npc_name)

# Defining response prompt (with reflection)
# TODO: prompt_list should also automatically include modules available to npc_name added after global
module_names = ['global', npc_name, 'player', 'current_interaction', 'task']
prompt = create_prompt(modules, module_names)

failed_prompts = 0
max_failed_prompts = 1
while player_msg.lower() != "exit":
    # Get response from prompt and extract reply/reflections from it
    response = get_response(prompt)
    reply, reflection = get_reply(response)
    if not reply or not reflection: # if prompt fails, allow retry until we retry a certain amount of times
        failed_prompts += 1
        if failed_prompts >= max_failed_prompts:
            break
        continue
    
    if debug:
        print("--REFLECTIONS--")
        print(reflection)
        
    print("--CURRENT INTERACTION--")
    print(modules['current_interaction'] + "\n")
    print("-----REPLY-----")
    print(reply + "\n")

    # Update prompt list with new current interaction
    modules['current_interaction'] += f"""\n{npc_name} responded: {reply}"""
    player_msg = input("Enter a response: ")
    modules['current_interaction'] += f"""\nThe player responded: “{player_msg}”"""

    module_names = ['global', npc_name, 'player', 'current_interaction', 'task']
    prompt = create_prompt(modules, module_names)

    # Printing the prompt for debugging purposes
    if debug:
        print('--PROMPT--')
        print(prompt + "\n")