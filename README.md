# Loki

<img src="loki.png" width=100 />

## Overview

The goal of this project was to make a prototype for NPCs that could generate dialogue to speak to players. These generative agents would be able to have the appropriate knowledge of their world, memory of the conversation, and meaningful responses to the player. We achieved this by leveraging large language models, vector databases, text-to-speech models, and some prompt engineering. In addition, we developed a system that could be used to create many different characters easily within an MMORPG world. This system is dependent on the idea of **modular prompting**. The important part of this concept is to separate world information into distinct character-agnostic parts so that it can be reused for different characters that share similar sets of information. It will be described in further detail in a later section.

This project was intended to show how MMORPG NPCs can be improved to make in-game worlds more immersive. This idea was inspired by the upcoming Riot Games MMORPG. In most games within this genre, NPCs use the same archaic system as some of their earliest predecessors. Most of the time, you interact with an NPC, it responds with one of multiple pre-scripted responses, and you move on. We believe that recent advancements in generative language models will soon be able to innovate this area, so we decided to work on this project to give a proof-of-concept.

## The Prompt

At a high level, we are simply looking to prompt a large language model to get a character’s response. This means that we need to pay close attention to the information that we give the model. There are a few goals that we have with our prompt. First, we need to design our prompt in such a way that we only give the character information that they would be able to know. This is mostly achieved through modular prompting which is discussed later. Second, we also want to minimize any hallucinations (i.e. making up stuff) or references to the real world since that will break immersion. For this, we added some directives in the global module to help guide the model from breaking character in a response. Finally, we want the responses to be relatively consistent and reasonable. We repeatedly iterated over the prompt to help achieve this and generally improve results.

During the early iterations of the prompt, one big issue we noticed was that the large language model was not sufficient at drawing conclusions as the character.  We mitigated this by using _reflections_. This was inspired by the paper titled _Generative Agents: Interactive Simulacra of Human Behavior_<sup>1</sup>. This concept’s effectiveness was also further shown in Sal Khan’s TED talk about AI in education<sup>3</sup>. These researchers showed that asking the large language model to make inferences and use those as a part of the context helps generative agents produce better responses. For their case, they even used inferences about previous inferences that they stored in memory (higher-order reflections). We experimented with this and found first-order reflections to be sufficient for our characters’ responses. 

## Modular Prompting

The goal of modular prompting is to make it easy to manage any given character’s known set of information while also promoting reusability to make character creation easier. The way this works is simple – the world’s information is divided into modules. These modules represent information that a certain group of potential characters should know. Some modules may be used by many characters (e.g. a module for every character in a certain continent), and some modules may be limited to just a single character. One example of this is the ‘Relics’ module (`modules/Relics.txt`) that contains information known to characters familiar with our world’s relics. Modules are split into two main parts: the core and its accompanying details. In the case of the ‘Relics’ module, its details can be found in the file `modules/Relics_details.txt` In this section we are referencing the core module, but the relevance of the details will be described later.

When writing modules, this means that the information has to be written in a way that is general enough to ensure effective use for all future characters. This sacrifices information personalization for the benefit of reusability. Due to the power of reflections, however, this cost is mostly mitigated and characters are still able to draw strong conclusions using the information available to them. Considering the scale of MMORPGs, this modularity would likely turn out to be very necessary if you were aiming to make each NPC interactable in this way. This project has implemented a system supporting modular prompting which is detailed in the ‘Setup’ section.

## Details

One of the issues you’ll run into when trying to create a prompt for a complex character is length. Currently, large language models have a limit to how much you can put into a prompt called the context window size. While they can sometimes be quite large, a large enough set of information for an MMORPG character will make the limits very easy to hit. This is because these characters are within a world entirely different from our own. For this project, details refer to pieces of information that are not very important to modules most of the time they’re being used for a character. For example, if we were writing a module for residents of a particular city, we should consider the paint color of its Town Hall as a detail because that information is usually irrelevant. However, it’s important to keep it as a detail because we would expect citizens to know what the Town Hall looks like. These kinds of details can be found in files with names like `modules/modulename_details.txt`.

While information in the core module is always included in the prompt, details are not. To help save space in the context window, we only pull the most relevant details across all of the available details modules into the prompt. We are able to find out what’s the most relevant by leveraging the user’s query and utilizing vector databases. The way it works is by creating semantically meaningful embeddings for each of the details across all of the modules along with creating an embedding for the user’s message to the character. These are typically created using machine learning models, and their outputs are designed to have pairs of texts which are relevant to each other have higher similarity values than pairs of text which are not related. Then we can get similarity values between the user’s query and each of the details that’s available to the character and only choose the details with the highest values since they are the most relevant.

To illustrate how this works, we will use an example. Let’s assume the player asks a character who has access to the ‘Forgery’ module the following question: “What proportion of people are Forgers?” The detail with the highest similarity score to the player’s question would likely be “Forgers make up five percent of the total population ”, while a detail like “The universal symbol for forgers is a hand wrapped around a staff that is shaped like a tree” may be among the least relevant.

## Creating Immersion

The goal for any MMORPG that’s using technology like this is to build immersion. One of the easiest ways to add immersion to this project is to simply take the output of the large language model and put it through a text-to-speech model. This simple addition adds life to the character’s response. We did this in our project’s demonstration to show its impact. There are other cool ways we’ve seen immersion be prioritized in similar work, [including allowing the character to have simple actions using tags within the response](https://www.youtube.com/watch?v=FpSJX59L7N4)<sup>2</sup>.

## Limitations and Future Work

Though we were able to achieve some interesting results, our approach has many limitations that stop it from being used in actual MMORPGs. Among these is hallucination. While it is largely mitigated by some key directives in the global module for characters, the model occasionally outputs responses containing information that is partially or entirely fabricated when it is adversarially queried. Similarly, it will also sometimes accidentally reveal real-world information. This does not usually happen in normal use, however – we have only seen it when the player is deliberately trying to get it to say something it shouldn’t. Our approach also sometimes produces repetitive responses during longer conversations.

An issue that may pop up for games with very in-depth lore and information sets is the context window limit of the large language model powering the responses. Our world is small compared to established IPs, so we didn’t run into any major issues with the context window size. With the use of modular prompting and the details system, these problems can be reduced, but at a certain scale they may still appear. There is currently work being done to expand the context window sizes of large language models, so this problem may fix itself in the future.

While we’re hopeful that generative models are used in the near future for game NPCs, we suspect that some of these issues will take time to be appropriately addressed. We’re excited to see the progression of generative models being used within game development over the next few years.

## Implementation

This project was done using Python and React. We leveraged OpenAI’s API to make calls to the `gpt-3.5-turbo` model. We also used the OpenAI embedder to create the embeddings for the details vector database. For text-to-speech, we used Coqui Studio API since we found their voices to be among the most realistic while also being very affordable for demonstration. We created our own lightweight vector database as an alternative to using an existing software since our demo is at a small scale. We used React and Flask to make a page to interact with the application.

## Demo

TODO: Video

# World

The world that these generative agents are based in is called Talis. Talis is as adjacent to Earth as possible, in the sense that there is a heaven and hell that are physically above and below Talis. Talis has seven main regions, and all NPCs within the project hail from one of these seven regions. Along with each region comes its own unique government, culture, economy, and more. 

The largest region is called Wei, and is based on China in regards to etymology and culture, as well as certain motifs that are important for the region’s characters. Wei is the strongest region in terms of magic, and is bordered by Valterre in the West. 

Valterre is based on England and Old Briton, taking inspiration from the legend of King Arthur. Valterre is not bordered by any country to the West, but off its coast is the island region of Dadelos. 

Dadelos is based on Greece, and has much of its worldbuilding aspects from Greek mythology and history, including but not limited to: the myth of Icarus, the Colossus of Rhodes, Hephaestus’ forge, and more. Dadelos and Wei host the only two schools for learning magic in Talis, which we will elaborate upon below. 

The only other island region in Talis is called Atropa, which, unlike the other six regions, does not follow the in-place magic system. It is located in the center of the South Sea in Talis, and is the land marking where the old gods of Talis were banished to the underworld. As such, Atropa is characterized as dark and mysterious, and does not particularly draw on any sort of civilization for inspiration. 

In the far North is the snowy region of Ragnavik. Ragnavik is based on Norway, and is the only region with a continual winter season, unlike its source inspiration. Ragnavik is considered isolated and primitive by some, and it is very difficult to travel over, as it is directly positioned over a large mountain range. 

Attached to Wei in the South is the desert region of Kairos, which is based on the old Persian Empire. Despite the fact that Kairos is based on the Persian Empire, its geography and environment more so mimic the Gobi Desert. 

Lastly, beneath Kairos is the coastal region known as Oer, which is based on old African kingdoms, with a heavy contribution coming from the Mali Empire. Each region comes with its own common module, as well as a list of detailed modules. 

Furthermore, the magic system that we use is referred to as Forgery. In simple terms, Talis has energy that certain demographics can manipulate to accomplish certain feats, much of which is largely free and dependent on each user. Energy is innately within every living thing in Talis, but it can also be found in Relics, which we established as remnants of old gods in this world. This is information that is largely esoteric, and only available to characters who have magic, or are born from magic, like homunculi. 

One of the primary uses for Forgery that we established for this project was creating homunculi, which, in our world, are artificial humanoids that can be brought to life using energy and Forgery. This is important to note as homunculi were a significant species to note in this world. 

Alongside the region of origin, as well as whether the character was magical or not, mortal or homunculi, etc., the system pulls certain common and detailed modules regarding each world detail when creating a holistic character. 

One of the first characters we tested our system out on was Attacca. Attacca is a homunculus prison guard from the region of Dadelos. Unlike most homunculi, she has the capacity to feel emotion, but this is a fact she keeps hidden to protect herself from being disassembled. Because she is a homunculus, she is knowledgeable about Forgery, despite the fact that she cannot perform it herself. 

In this case, the system would pull modules from Dadelos, homunculi, and Forgery. Details that are only pertinent to Attacca would appear in her initial prompt, such as her appearance, or her unique ability to feel emotions. 

# Setup

This project uses [Node.js](https://nodejs.org/en/download) and Python. To install the necessary packages for Node, run the following commands from the project directory:
```
cd loki
npm install
```

Be sure to also install the appropriate Python packages in your environment. To do this, run the following command in the project directory:
```
pip install -r requirements.txt
```

Depending on your session configuration, this demo may use API calls to operate. Create a file called `.env` in the main directory filled in with the appropriate API keys. Follow this format:
```
OPENAI_API_KEY=<INSERT KEY HERE>
COQUI_STUDIO_TOKEN=<INSERT KEY HERE>
```

## Starting the Demo

To start the demo, all you need to do is run the following command from the main directory. This will take you to a local webpage where you can create a session and interact with characters.
```
bash start.sh
```

## Creating a Character

Characters have their information defined in two files. To add a character to the demo, you will need to modify them both. If you want to add more information for a character to work with, you may need to create `.txt` files in the `modules` directory.

To define a character's information, navigate to `modules/characters/npc_map.json`. In this file, you can define new characters by a _key_ that will be used to refer to the character in the other file. A character has the properties _modules_ and _speaker_. The _modules_ property dictates which `.txt` files from the `modules` directory will be used to construct the prompt. The _speaker_ property is a description of your speaker that will be turned into a voice in Coqui Studio. Note that "current_interaction" is a special module that is updated throughout the conversation to hold its history. Here is a basic version of `npc_map.json`:

```json
{
    "Shu": {
        "modules": ["global", "relevant_details", "characters/Shu", "player", "current_interaction", "task"],
        "speaker": "A male human necromancer who is grizzled and vengeful."
    },
    "ExChar": {
        "modules": ["global", "relevant_details", "player", "current_interaction", "task"],
        "speaker": "An example description."
    },
}
```

To add this to the demo webpage, navigate to `loki/src/SessionOptionsEnums.js`. Here you can modify the `const npcOptions` array to add a character. You can also add a picture for the page to show when the character is used. Here is an example of what it may look like:
```js
import ShuPic from "./npcImages/Shu.jpg";
import ExPic from "./npcImages/Ex.jpg"

export const npcOptions = {
    Shu: { "name": "Demo - Shu", "key": "Shu", "pic": ShuPic },
    ExampleChar: {"name": "Example Character", "key": "ExChar", "pic": ExPic}
}
```
The _name_ property is the name that will appear on the demo webpage. The _key_ property must match what appears in `npc_map.json`. The _pic_ property is the picture that will be shown for the character.

## Modules

The modules directory holds the `.txt` files that construct a prompt. Each module represents information that will be available to the character. There are four tags that can be included within these modules to give special information. These tags are `{npc_name}`, `{player_desc}`, `{player_msg}`, and `{relevant_details}`. The `{npc_name}` tag will become the character's name, the `{player_desc}` tag will become the inputted player description, the `{player_msg}` tag will become the player's most recent message to the character, and the `{relevant_details}` tag will become the most relevant details to the player's message pulled from the vector database. Here is an example of the 'player' module which represents the character's knowledge of the player:
```
Here is a description of the player: 

{player_desc}
```
The details of a module can be written in a `.txt` file named the module name with `_details` appended to the end. For example, the Valterre module `Valterre.txt` contains information about the Valterre, and `Valterre_details.txt` contains the details about Valterre used within the vector database. This naming convention is important since it is expected in order to appropriately populate the database during session initialization. Note that details are not required for every module. A details file should have units of information separated by newline characters. Here is an example of a miniature details file: 
```
Valterre has mountains, lakes, waterfalls, rainforests, and wetlands.
Valterre’s main export is magical items.
Valterre houses the largest military in Talis.
```


# References

<sup>1</sup>Park, Joon Sung, et al. "Generative agents: Interactive simulacra of human behavior." _arXiv preprint arXiv:2304.03442 (2023)_.

<sup>2</sup>“Spirtual Voice Chat with a CHATGPT-Driven Monk in VR.” _YouTube_, 6 June 2023, www.youtube.com/watch?v=FpSJX59L7N4.

<sup>3</sup>“How AI Could Save (Not Destroy) Education | Sal Khan | Ted.” _YouTube_, 1 May 2023, www.youtube.com/watch?v=hJP5GqnTrNo. 
