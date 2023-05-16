import openai
import pinecone
import os

class Details():

    def __init__(self, npc_name):
        pass

    def query(self, player_msg) -> list[str]:
        # Returns list of details
        pass

class Shu(Details):

    def __init__(self):
        self.npc_name = "shu"

        # init apis
        openai.api_key = os.getenv("OPENAI_API_KEY")
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment="asia-southeast1-gcp-free")

        self.index = pinecone.Index(index_name=self.npc_name)

    def query(self, player_msg) -> list[str]:
        # getting embeddings
        query_embedding = openai.Embedding.create(input = [player_msg], model='text-embedding-ada-002')['data'][0]['embedding']

        # querying
        query_response = self.index.query(
            vector=query_embedding,
            top_k = 3,
            include_values=False
        )

        return [query_response['matches'][i]['id'] for i in range(len(query_response['matches']))]