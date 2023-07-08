# Importing appropriate libraries
from dotenv import load_dotenv
from core.utils import load_modules, create_prompt, sanitize
from core.llms import GPT3
from core.details import Pinecone
#from TTS.api import TTS
import json
import requests
import os
from flask import Flask
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
cors = CORS(app)

debug = True
max_failed_prompts = 1
NPC_MAP_PATH = "./modules/characters/npc_map.json"
SPEECH_OUTPUT_PATH = "./speech.wav"

load_dotenv()

def messageToAudio(message):
    url = "https://app.coqui.ai/api/v2/samples/from-prompt/"
    payload = {
        "emotion": "Neutral",
        "speed": 1,
        "text": message[1: len(message) - 1],
        "prompt": "A male human necromancer who is grizzled and vengeful"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer " + os.getenv("COQUI_STUDIO_TOKEN")
    }
    return requests.post(url, json=payload, headers=headers)

@app.route("/initialize/<new_llm>/<new_npc_name>/<new_k>/<player_desc>/<player_msg>")
async def main(new_llm, new_npc_name, new_k, player_desc, player_msg):
    global llm
    global details
    global relevant_details_list
    global relevant_details
    global module_names
    global prompt
    global npc_name
    global k
    global modules
    global player_desc_global

    # Sanitizing inputs
    player_msg = sanitize(player_msg)
    player_desc = sanitize(player_desc)

    # Declaring variables (should probably refactor this)
    new_k = int(new_k)
    k = new_k
    npc_name = new_npc_name
    player_desc_global = player_desc

    # Gathering character information from npc_map.json
    with open(NPC_MAP_PATH) as f:
        npc_map = json.load(f)
    module_names = npc_map[npc_name]["modules"]
    speaker = npc_map[npc_name]["speaker"]

    llms_dict = {"GPT3" : GPT3}
    llm = llms_dict[new_llm]()
    modules = load_modules()

    # Initializing relevant details
    #details = Pinecone("Shu")#Pinecone(npc_name)
    #relevant_details_list = details.query(player_msg, k=k)
    #relevant_details = "\n".join(relevant_details_list)
    modules['relevant_details'] = ""#modules['relevant_details_template'].format(relevant_details=relevant_details)

    # Defining response prompt (with reflection)
    prompt = create_prompt(modules, module_names)

    reply, reflection = llm.get_response(prompt)
    if not reply or not reflection: # if prompt fails, allow retry until we retry a certain amount of times
        failed_prompts += 1
        if failed_prompts >= max_failed_prompts:
            return "Failed"
        newPlayerMessageRepeated(failed_prompts, prompt)
    modules['current_interaction'] += f"""\n{npc_name} responded: {reply}"""

    return "{\"reply\": \"" + reply[1: len(reply) - 1] +"\", \"audio\": " + messageToAudio(reply).text + "}"
    

@app.route("/newMessage/<player_msg>")
async def newPlayerMessage(player_msg):
    return await newPlayerMessageRepeated(0, player_msg)

async def newPlayerMessageRepeated(failed_prompts, player_msg):
    # Sanitizing player_msg
    player_msg = sanitize(player_msg)

    # Updating prompt list with new current interaction
    modules['current_interaction'] += f"\nThe player responded: “{player_msg}”"

    # Updating relevant details
    #relevant_details_list = details.query(player_msg, k=k)
    #relevant_details = "\n".join(relevant_details_list)
    modules['relevant_details'] = "";#modules['relevant_details_template'].format(relevant_details=relevant_details)

    # Constructing the prompt and replacing tags
    prompt = create_prompt(modules, module_names).format(npc_name=npc_name,
                                                         player_msg=player_msg,
                                                         player_desc=player_desc_global,
                                                         relevant_details=relevant_details
                                                         )
    
    # Get response from prompt and extract reply/reflections from it
    reply, reflection = llm.get_response(prompt)
    if not reply or not reflection: # if prompt fails, allow retry until we retry a certain amount of times
        failed_prompts += 1
        if debug:
            print("-----FAILED PROMPT-----")
        if failed_prompts >= max_failed_prompts:
            return "Failed"
        newPlayerMessageRepeated(failed_prompts, prompt)
    modules['current_interaction'] += f"\n{npc_name} responded: {reply}"

    # Printing the prompt for debugging purposes
    if debug:
        print("Loading response...", end='\r')
        print("-----------------------------")
        print("--RELEVANT DETAILS--")
        print(relevant_details + "\n")
        print("--REFLECTIONS--")
        print(reflection)
        print("--CURRENT INTERACTION--")
        print(modules['current_interaction'] + "\n")
        print("-----REPLY-----")
        print(reply + "\n")
        print('--PROMPT--')
        print(prompt + "\n")

    return "{\"reply\": \"" + reply[1: len(reply) - 1] +"\", \"audio\": " + messageToAudio(reply).text + "}"
