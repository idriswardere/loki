# Importing appropriate libraries
debug = True
from dotenv import load_dotenv
from core.utils import load_modules, create_prompt, prepare_for_tts
from core.llms import GPT3
from core.details import Pinecone
#from TTS.api import TTS
import winsound
import json
from flask import Flask

app = Flask(__name__)

max_failed_prompts = 1
SPEECH_OUTPUT_PATH = "./speech.wav"

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
    global tts

    new_k = int(new_k)

    k = new_k
    npc_name = new_npc_name

    llms_dict = {"GPT3" : GPT3}
    llm = llms_dict[new_llm]()

    # Initializing relevant details
    details = Pinecone(npc_name)
    relevant_details_list = details.query(player_msg, k=k)
    relevant_details = "\n".join(relevant_details_list)
    modules['relevant_details'] = modules['relevant_details_template'].format(relevant_details=relevant_details)

    # Initializing prompt parts
    modules['player'] = modules['player'].format(player_desc=player_desc)
    modules['current_interaction'] = modules['current_interaction'].format(npc_name=new_npc_name, player_msg=player_msg)
    original_task = modules['task']
    modules['task'] = modules['task'].format(npc_name=new_npc_name, player_msg=player_msg)


    NPC_MAP_PATH = "./modules/characters/npc_map.json"
    with open(NPC_MAP_PATH) as f:
        npc_map = json.load(f)
    module_names = npc_map[npc_name]["modules"]
    speaker = npc_map[npc_name]["speaker"]

    # Defining response prompt (with reflection)
    prompt = create_prompt(modules, module_names)

    # Initializing Coqui Studio TTS
    tts_model_name = f"coqui_studio/en/{speaker}/coqui_studio"
    #tts = TTS(model_name=tts_model_name)
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
    relevant_details_list = details.query(player_msg, k=k)
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

    #tts.tts_to_file(text=prepare_for_tts(reply), file_path=SPEECH_OUTPUT_PATH)
    #winsound.PlaySound(SPEECH_OUTPUT_PATH, winsound.SND_FILENAME) # TODO: replace winsound with a better audio library

    # Printing the prompt for debugging purposes
    if debug:
        print('--PROMPT--')
        print(prompt + "\n")

    return reply