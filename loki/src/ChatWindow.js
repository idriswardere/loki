import { useTheme } from "@emotion/react";
import {
    Avatar, Box, Grid, Typography, TextField, Stack, IconButton, Skeleton
} from "@mui/material";
import axios from 'axios';
import { npcOptions } from "./SessionOptionsEnums";
import { useEffect, useRef, useState } from "react";
import { Send } from "@mui/icons-material"

export default function ChatWindow(props) {
    const { sessionDetails, setSessionDetails } = props;

    const theme = useTheme();

    const [messages, setMessages] = useState([]);
    const [recievingMessage, setRecievingMessage] = useState(false);
    const [recievingResponse, setRecievingResponse] = useState(false);
    const [firstSend, setFirstSend] = useState(true);
    const recievingResponseTimer = useRef(null);

    useEffect(() => {
        if (sessionDetails === null) {
            setFirstSend(true);
            setRecievingMessage(false);
            setRecievingResponse(false);
            setMessages([]);
        }
    }, [sessionDetails]);

    const baseInstance = axios.create({
        baseURL: "http://localhost:5000/",
        timeout: undefined
    });

    const handleMessageSend = () => {
        recievingResponseTimer.current = setTimeout(() => {
            setRecievingResponse(true);
        }, 250 * (6 + (Math.random() * 6)));
        setRecievingMessage(true);
        messages.unshift({ sender: "user", message: sessionDetails.playerMessage });
        setMessages([...messages]);
        if (firstSend) {
            createSession();
        } else {
            sendMessage();
        }
        setSessionDetails({ ...sessionDetails, playerMessage: "" });
    }

    const createSession = () => {
        setFirstSend(false);
        baseInstance.get("/initialize/" + sessionDetails.llm + "/" + sessionDetails.name +
            "/" + sessionDetails.worldDetails + "/" + sessionDetails.playerDescription +
            "/" + sessionDetails.playerMessage).then((data) => {
                handleMessage(data.data);
            }).catch((e) => console.error(e));
    }

    const sendMessage = () => {
        baseInstance.get("/newMessage/" + sessionDetails.playerMessage).then((data) => {
            handleMessage(data.data);
        }).catch((e) => console.error(e));
    }

    const handleMessage = (message) => {
        setRecievingMessage(false);
        clearTimeout(recievingResponseTimer.current);
        setRecievingResponse(false);
        messages.unshift({ sender: "npc", message: message });
        setMessages([...messages]);
    }

    if (!sessionDetails) {
        return (
            <Box sx={{ width: "100%", height: "100%", backgroundColor: "#2b2a2a" }} />
        );
    }

    return (
        <Box sx={{ width: "100%", height: "100%", backgroundColor: "#2b2a2a" }}>
            <Grid container columns={50} direction="column" wrap="nowrap" sx={{ width: "100%", height: "100%" }} >
                <Grid item xs={"auto"}>
                    <Box sx={{ height: "150px", width: "100%", position: "relative" }}>
                        <Box sx={{ mt: 1, height: "70%", aspectRatio: 1, position: "absolute", left: "50%", transform: "translateX(-50%)" }}>
                            <Avatar
                                alt={npcOptions[Object.keys(npcOptions).find((key) => npcOptions[key].key === sessionDetails.name)]?.name}
                                sx={{ height: "100%", width: "100%" }}
                                src={npcOptions[Object.keys(npcOptions).find((key) => npcOptions[key].key === sessionDetails.name)]?.pic}
                            />
                            <Typography sx={{ mt: 1, width: "500%", position: "absolute", left: "50%", transform: "translateX(-50%)" }} variant="h5" textAlign="center">
                                {npcOptions[Object.keys(npcOptions).find((key) => npcOptions[key].key === sessionDetails.name)]?.name}
                            </Typography>
                        </Box>
                    </Box>
                </Grid>
                <Grid item xs={true} sx={{ overflowY: "auto" }}>
                    <Box sx={{ height: "100%", width: "100%", backgroundColor: "#1a1919" }}>
                        <Stack direction="column-reverse" sx={{ height: "100%", width: "100%", overflowY: "auto" }}>
                            {recievingResponse && (
                                <Skeleton
                                    variant="rectangular"
                                    animation="wave"
                                    sx={{
                                        m: 1,
                                        height: 30,
                                        width: 125,
                                        maxWidth: 150,
                                        borderRadius: 5,
                                        overflow: "visible",
                                        position: "relative"
                                    }}>
                                    <Skeleton
                                        variant="circular"
                                        animation="wave"
                                        sx={{
                                            overflow: "visible",
                                            visibility: "visible",
                                            positon: "absolute",
                                            left: "15%",
                                            top: "50%",
                                            transform: "translate(-15%, -50%)",
                                            height: 25,
                                            width: 25,
                                        }} />
                                    <Skeleton
                                        variant="circular"
                                        animation="wave"
                                        sx={{
                                            visibility: "visible",
                                            overflow: "visible",
                                            positon: "absolute",
                                            left: "50%",
                                            top: "calc(50% - 25px)",
                                            transform: "translate(-50%, -50%)",
                                            height: 25,
                                            width: 25,
                                        }} />
                                    <Skeleton
                                        variant="circular"
                                        animation="wave"
                                        sx={{
                                            visibility: "visible",
                                            overflow: "visible",
                                            positon: "absolute",
                                            left: "85%",
                                            top: "calc(50% - 50px)",
                                            transform: "translate(-85%, -50%)",
                                            height: 25,
                                            width: 25,
                                        }} />
                                </Skeleton>
                            )}
                            {messages.map((message, index) => (
                                <Box
                                    key={index} //NOSONAR
                                    sx={{
                                        m: 1,
                                        maxWidth: "40%", borderRadius: 5,
                                        backgroundColor: message.sender === "user" ? theme.palette.primary.main : theme.palette.secondary.main,
                                        alignSelf: message.sender === "user" ? "self-end" : null
                                    }}
                                >
                                    <Typography sx={{ m: 1, mx: 2, overflow: "auto" }}>
                                        {message.message}
                                    </Typography>
                                </Box>
                            ))}
                        </Stack>
                    </Box>
                </Grid>
                <Grid item xs={"auto"}>
                    <Stack direction="row">
                        <Box sx={{ height: "100px", ml: 1, mt: .5, width: "90%" }}>
                            <TextField
                                onKeyDown={(e) => {
                                    if (e.key === "Enter") {
                                        e.preventDefault();
                                        if (!recievingMessage && e.target.value !== "") {
                                            handleMessageSend();
                                        }
                                    }
                                }}
                                variant="filled"
                                placeholder="Message..."
                                multiline
                                hiddenLabel
                                minRows={3}
                                maxRows={3}
                                fullWidth
                                value={sessionDetails.playerMessage}
                                onChange={(e) => setSessionDetails({ ...sessionDetails, playerMessage: e.target.value })} />
                        </Box>
                        <IconButton sx={{ height: "110px", width: "110px" }} onClick={handleMessageSend} disabled={recievingMessage || sessionDetails.playerMessage === ""}>
                            <Send sx={{ height: "60px", width: "60px" }} />
                        </IconButton>
                    </Stack>
                </Grid>
            </Grid>
        </Box>
    );
}