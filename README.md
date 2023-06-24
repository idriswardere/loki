# Loki

## Setup

This project uses [Node.js](https://nodejs.org/en/download) and Python. To install the necessary packages for Node, run the following commands:
```
cd loki
npm install
```

Be sure to also install the appropriate Python packages in your environment.

This demo uses API calls to operate. Create a file called `.env` in the main directory filled in with the appropriate API keys. Follow this format:
```
OPENAI_API_KEY=<INSERT KEY HERE>
PINECONE_API_KEY=<INSERT KEY HERE>
COQUI_STUDIO_TOKEN=<INSERT KEY HERE>
```

## Starting the Demo

To start the demo, all you need to do is run the following command from the main directory. This will take you to a local webpage where you can create a session and interact with characters.
```
bash start.sh
```

## Creating a Character

Characters have their information defined in two files. To add a character to the demo, you will need to modify them both. If you want to add more information for a character to work with, you may need to create `.txt` files in the `modules` directory.

To define a character's information, navigate to `modules/characters/npc_map.json`. In this file, you can define new characters by a _key_ that will be used to refer to the character in the other file. A character has the properties _modules_ and _speaker_. The _modules_ property dictates which `.txt` files from the `modules` directory will be used to construct the prompt. The _speaker_ property is the TTS speaker used from your Coqui Studio. Note that "relevant_details", "current_interaction", and "task" are special modules. Here is a basic version:

```
{
    "Shu": {
        "modules": ["global", "relevant_details", "characters/Shu", "player", "current_interaction", "task"],
        "speaker": "Abrahan Mack"
    },
    "ExChar": {
        "modules": ["global", "relevant_details", "player", "current_interaction", "task"],
        "speaker": "Example Speaker"
    },
}
```

To add this to the demo webpage, navigate to `loki/src/SessionOptionsEnums.js`. Here you can modify the `const npcOptions` array to add a character. You can also add a picture for the page to show when the character is used. Here is an example of what it may look like:
```
import ShuPic from "./npcImages/Shu.jpg";
import ExPic from "./npcImages/Ex.jpg"

export const npcOptions = {
    Shu: { "name": "Demo - Shu", "key": "Shu", "pic": ShuPic },
    ExampleChar: {"name": "Example Character", "key": "ExChar", "pic": ExPic}
}
```
The _name_ property is the name that will appear on the demo webpage. The _key_ property must match what appears in `npc_map.json`. The _pic_ property is the picture that will be shown for the character.


