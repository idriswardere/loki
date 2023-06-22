import {
    Box, Grid, Typography, FormControl, FormLabel, MenuItem,
    RadioGroup, FormControlLabel, Radio, InputLabel, Select, Slider, TextField, Button
} from "@mui/material";
import { llmOptions, npcOptions } from "./SessionOptionsEnums";
import { useTheme } from "@emotion/react";


export default function SessionCreator(props) {
    const { sessionDetails, setSessionDetails } = props;

    const theme = useTheme();

    return (
        <Box sx={{ width: "100%", height: "100%", backgroundColor: theme.palette.backgroundColor }}>
            <Grid container columns={12} direction="column" wrap="nowrap" sx={{ width: "100%", height: "100%" }}>
                <Grid item xs={1}>
                    <Box sx={{ mt: 1, borderBottom: "3px solid " + theme.palette.primary.main }}>
                        <Typography variant="h4" textAlign={"center"}>
                            Session Creator
                        </Typography>
                    </Box>
                </Grid>
                <Grid container item xs={11} columns={8} direction="row" wrap="nowrap" >
                    <Grid item xs={2}>
                        <Box sx={{ mt: 2.5, position: "relative" }}>
                            <FormControl sx={{ position: "absolute", left: "50%", transform: "translateX(-50%)", width: "80%" }}>
                                <FormLabel>Large Language Model</FormLabel>
                                <RadioGroup
                                    value={sessionDetails.llm}
                                    onChange={(e) => setSessionDetails({ ...sessionDetails, llm: e.target.value })}
                                >
                                    {Object.keys(llmOptions).map((key) => <FormControlLabel
                                        key={key}
                                        value={llmOptions[key].key}
                                        control={<Radio />}
                                        label={llmOptions[key].name}
                                    />)}
                                </RadioGroup>
                            </FormControl>
                        </Box>
                    </Grid>
                    <Grid container item columns={12} direction="column" wrap="nowrap">
                        <Grid container item xs={1} columns={2} direction="row" wrap="nowrap">
                            <Grid item xs={1}>
                                <Box sx={{ mt: 3, position: "relative" }}>
                                    <FormControl sx={{ position: "absolute", left: "40%", transform: "translateX(-40%)", width: "50%" }}>
                                        <InputLabel>NPC</InputLabel>
                                        <Select
                                            value={sessionDetails.name}
                                            label="NPC"
                                            onChange={(e) => setSessionDetails({ ...sessionDetails, name: e.target.value })}
                                        >
                                            {npcOptions.map((name) => <MenuItem key={name} value={name}>{name}</MenuItem>)}
                                        </Select>
                                    </FormControl>
                                </Box>
                            </Grid>
                            <Grid item xs={1}>
                                <Box sx={{ mt: 2, width: "85%" }}>
                                    <Typography color={"rgba(255, 255, 255, 0.7)"}>
                                        World Details Stored
                                    </Typography>
                                    <Slider
                                        sx={{ mt: -1 }}
                                        value={sessionDetails.worldDetails}
                                        onChange={(e) => setSessionDetails({ ...sessionDetails, worldDetails: e.target.value })}
                                        valueLabelDisplay="auto"
                                        step={1}
                                        marks={[{
                                            value: 1,
                                            label: '1',
                                        },
                                        {
                                            value: 20,
                                            label: '20',
                                        }]}
                                        min={1}
                                        max={20}
                                    />
                                </Box>
                            </Grid>
                        </Grid>
                        <Grid item xs={10}>
                            <Box sx={{ position: "relative"}}>
                                <Box sx={{ position: "absolute", left: "50%", width: "90%", transform: "translateX(-50%)" }}>
                                    <TextField
                                        variant="filled"
                                        label="Initial Player Description"
                                        multiline
                                        minRows={5}
                                        maxRows={5}
                                        fullWidth
                                        value={sessionDetails.playerDescription}
                                        onChange={(e) => setSessionDetails({ ...sessionDetails, playerDescription: e.target.value })} />
                                </Box>
                            </Box>
                        </Grid>
                        <Grid container item xs={1} spacing={1} columns={2} direction="row" wrap="nowrap">
                            <Grid item xs={1}>
                                <Box sx={{ position: "relative" }}>
                                    <Button sx={{ position: "absolute", left: "50%", width: "70%", transform: "translateX(-50%)" }} size="large" variant="contained">
                                        Create Session
                                    </Button>
                                </Box>
                            </Grid>
                            <Grid item xs={1}>
                                <Box sx={{ position: "relative" }}>
                                    <Button sx={{ backgroundColor: theme.palette.error.main, position: "absolute", left: "50%", width: "70%", transform: "translateX(-50%)" }} size="large" variant="contained">
                                        Reset Session
                                    </Button>
                                </Box>
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Box>
    );
}