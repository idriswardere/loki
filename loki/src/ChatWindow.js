import { Box } from "@mui/material";
import axios from 'axios';

export default function ChatWindow(props) {
    const { sessionDetails } = props;

    const baseInstance = axios.create({
        baseURL: "http://localhost:5000/",
        timeout: undefined
    });

    const createSession = () => {
        baseInstance.get("/initialize/" + sessionDetails.llm + "/" + sessionDetails.name + 
        "/" + sessionDetails.worldDetails + "/" + sessionDetails.playerDescription +
         "/" + sessionDetails.initialPlayerMessage).then((firstResponse) => {
            console.log(firstResponse);
         }).catch((e) => console.log(e));
    }

    return (
        <Box sx={{width: "100%", height: "100%", backgroundColor: "lightgray"}}>

        </Box>
    );
}