import os
import json
import pinecone
import numpy as np
from numpy.linalg import norm
from .utils import get_embedding

class Details():

    def __init__(self, npc_name):
        pass

    def query(self, player_msg, k) -> list[str]:
        # Returns list of details
        pass

class Pinecone(Details):

    def __init__(self, npc_name):
        self.npc_name = npc_name
        index_name = f"{npc_name.lower()}-index"
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment="asia-southeast1-gcp-free")
        self.index = pinecone.Index(index_name=index_name)

    def query(self, player_msg, k) -> list[str]:
        # getting embeddings
        query_embedding = get_embedding(player_msg)

        # querying
        query_response = self.index.query(
            vector=query_embedding,
            top_k = k,
            include_values=False
        )

        return [query_response['matches'][i]['id'] for i in range(len(query_response['matches']))]
    

class LokiVDB:
    def __init__(self, npc_name):
        # initializing vars
        self.vector_dict = {} # detail: embedding 

        # getting paths for each details file from the character module list
        NPC_MAP_PATH = "./modules/characters/npc_map.json"
        with open(NPC_MAP_PATH) as f:
            npc_map = json.loads(f.read())
        char_modules = npc_map[npc_name]['modules']
        char_details_paths = ["./modules/" + module + "_details.txt" for module in char_modules]

        # collecting all of the details from each module's details file
        all_details = []
        for path in char_details_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as txt_file:
                    details_raw = txt_file.read()
                    details = [raw_detail.strip() for raw_detail in details_raw.split('\n')]
                    all_details.extend(details)

        # embedding each detail and storing the data
        for detail in all_details:
            embedding = get_embedding(detail)
            self.vector_dict[detail] = embedding
            
    def query(self, player_msg, k) -> list[str]:
        msg_embed = get_embedding(player_msg)
        cos_sim_pairs = []
        for detail in self.vector_dict:
            detail_embed = self.vector_dict[detail]
            cos_sim = np.dot(msg_embed, detail_embed) / (norm(msg_embed)*norm(detail_embed))
            cos_sim_pairs.append((detail, cos_sim))

        cos_sim_pairs.sort(key=lambda x: x[1], reverse=True)
        most_relevant_details = [tup[0] for tup in cos_sim_pairs[:k]]

        return most_relevant_details
