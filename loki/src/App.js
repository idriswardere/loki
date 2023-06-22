import './App.css';
import { Grid, Box } from "@mui/material";
import SessionCreator from './SessionCreator';
import ChatWindow from './ChatWindow';
import FaceView from './FaceView';
import { useState } from 'react';

export default function App() {

  const [sessionDetails, setSessionDetails] = useState({});

  return (
    <Box sx={{ height: "100vh", width: "100vw" }}>
      <Grid container columns={2} direction="row" wrap='nowrap' sx={{ height: "100%", width: "100%" }}>
        <Grid container item columns={2} direction="column" xs={1} wrap='nowrap'>
          <Grid item xs={1}>
            <FaceView />
          </Grid>
          <Grid item xs={1}>
            <SessionCreator sessionDetails={sessionDetails} setSessionDetails={setSessionDetails} />
          </Grid>
        </Grid>
        <Grid item xs={1}>
          <ChatWindow sessionDetails={sessionDetails} />
        </Grid>
      </Grid>
    </Box>
  );
}
