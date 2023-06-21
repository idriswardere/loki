# Importing appropriate libraries
debug = True
from dotenv import load_dotenv
from core.utils import load_modules, create_prompt, prepare_for_tts
from core.llms import GPT3
from core.details import Pinecone
from TTS.api import TTS
import winsound
import json

load_dotenv() # Loading secret API keys
modules = load_modules() # Defining prompt modules

llms_dict = {"GPT3" : GPT3}

# Initializing conversation details with input
llm_names = llms_dict.keys()
llm_name = input("Which LLM would you like to use for response generation?\nOptions: [" + " ".join(llm_names) + "]\n> ")
while llm_name not in llms_dict:
    llm_name = input("LLM not found. Please try again. (Note: LLM name is case-sensitive.)\n> ")

llm = llms_dict[llm_name]()

npc_names = modules['characters'].keys()
npc_name = input("Who would you like to speak to?\nOptions: [" + " ".join(npc_names) + "]\n> ") # character being spoken to

while npc_name not in modules['characters']:
    npc_name = input("Character not found. Please try again. (Note: Character name is case-sensitive.)\n> ")

k = int(input("How many world details would you like the character to be able to pull from the database?\n> "))
player_desc = input("Write a description of your player's character.\n(e.g. A non-magical goblin who is wearing chainmail armor and leather boots. Is very strong physically.)\n> ")
player_msg = input(f"You are speaking to {npc_name}. What do you want to say?\n> ")

# Initializing relevant details
details = Pinecone(npc_name)
relevant_details_list = details.query(player_msg, k=k)
relevant_details = "\n".join(relevant_details_list)
modules['relevant_details'] = modules['relevant_details_template'].format(relevant_details=relevant_details)

# Initializing prompt parts
modules['player'] = modules['player'].format(player_desc=player_desc)
modules['current_interaction'] = modules['current_interaction'].format(npc_name=npc_name, player_msg=player_msg)
original_task = modules['task']
modules['task'] = modules['task'].format(npc_name=npc_name, player_msg=player_msg)

# TODO: jsonify
#module_names = ['global', 'relevant_details', 'characters/'+npc_name, 'player', 'current_interaction', 'task']
#speaker_name = "Abrahan Mack" # Shu's speaker
NPC_MAP_PATH = "./modules/characters/npc_map.json"

with open(NPC_MAP_PATH) as f:
    npc_map = json.load(f)

module_names = npc_map[npc_name]["modules"]
speaker = npc_map[npc_name]["speaker"]

# Defining response prompt (with reflection)
prompt = create_prompt(modules, module_names)

# Initializing Coqui Studio TTS
tts_model_name = f"coqui_studio/en/{speaker}/coqui_studio"
tts = TTS(model_name=tts_model_name)
SPEECH_OUTPUT_PATH = "./speech.wav"

failed_prompts = 0
max_failed_prompts = 1
while player_msg.lower() != "exit":
    # Get response from prompt and extract reply/reflections from it
    print("Loading response...", end='\r')
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

    # Creating & play sound
    tts.tts_to_file(text=prepare_for_tts(reply), file_path=SPEECH_OUTPUT_PATH)
    winsound.PlaySound(SPEECH_OUTPUT_PATH, winsound.SND_FILENAME) # TODO: replace winsound with a better audio library

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