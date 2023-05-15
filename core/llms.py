import openai
import os

# Interface between LLM and character response generation
class LLM():

    def __init__(self):
        # Initialize the LLM details here.
        pass

    def get_response(self, prompt):
        # Return (reply, reflection) given the prompt.
        pass


class GPT3(LLM):

    def __init__(self, debug=False):
        self.debug = debug
        openai.api_key = os.getenv("OPENAI_API_KEY")

    # Get the raw response from GPT-3 with prompt using OpenAI API
    def get_raw_response(self, prompt):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=512,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response


    # Parses reply out of the OpenAI response object
    def get_reply_reflection(self, response):
        response_str = response['choices'][0]['text']

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

        if self.debug:
            print("---REPLY NOT FOUND--RESPONSE BELOW---")
            print(response_str)
            print("-------------------------------------")
        return None, None
    
    # Returns (reply, reflection) from the given prompt.
    def get_response(self, prompt):
        raw_response = self.get_raw_response(prompt)
        reply, reflection = self.get_reply_reflection(raw_response)
        return reply, reflection