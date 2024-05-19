import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import React from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import Avatar from "@material-ui/core/Avatar";
import md5 from "md5";
import { FriendRequest } from "../api/types";
import { handleFriendRequest } from "../api/friend";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import Grid from "@material-ui/core/Grid";
import Box from "@mui/material/Box";

export default function FriendRequestDialog(props: any) {

  const getTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes() < 10 ? "0" : ""}${date.getMinutes()}`;
  };

  return (
    <Dialog open={props.open} onClose={props.onhandleClose}>
      <DialogTitle>Friend Requests</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Your Friend Requests:
        </DialogContentText>
        <List>
          {props.friendRequests && props.friendRequests.map((request: FriendRequest) => (
              <ListItem key={request.username}>
              <ListItemAvatar>
                <Avatar alt={request.username} src={`https://www.gravatar.com/avatar/${md5(request.email.trim().toLowerCase())}?d=identicon&s=150`} />
              </ListItemAvatar>
              <Grid style={{ width: "350px" }}>
                <ListItemText
                  primary={`${request.username}`}
                  secondary={getTime(request.timestamp)}
                />
              </Grid>
              <Grid container direction="row" alignItems="center" justifyContent="flex-end" spacing={1} style={{ marginRight: "3px" }}>
                {request.role === "sender" && (
                  <Grid item>
                    <ArrowForwardIcon />
                  </Grid>
                )}
                <Grid item>
                  <ListItemText primary={`${request.status}`} />
                </Grid>
              </Grid>
              {(request.status === "Pending" && request.role === "receiver") ? (
                <>
                  <Grid container direction="row" alignItems="center" justifyContent="flex-end" spacing={1} style={{ width: "500px" }}>
                    <Grid item>
                      <Button
                        style={{ textTransform: "none", padding: "5px 10px", borderWidth: "2px" }}
                        variant="contained"
                        color="primary"
                        onClick={() => {
                          handleFriendRequest(request, true)
                            .then((res) => res.json())
                            .then((res) => {
                              if (Number(res.code) === 0) {
                                alert("You have accepted the friend request.");
                                props.onSetFriendChange(!props.friendChange);
                                props.onhandleFriendRequestClose();
                                props.onhandleNewPrivateConversation(request.username);
                              }
                              else {
                                alert(res.info);
                              }
                            })
                            .catch((error) => {
                              alert(error.info);
                            });
                        }}>Accept</Button>
                    </Grid>
                    <Grid item>
                      <Box width={3}></Box>
                    </Grid>
                    <Grid item>
                      <Button
                        style={{ textTransform: "none", padding: "5px 10px", borderWidth: "2px" }}
                        variant="contained"
                        color="primary"
                        onClick={() => {
                          handleFriendRequest(request, false)
                            .then((res) => res.json())
                            .then((res) => {
                              if (Number(res.code) === 0) {
                                alert("You have rejected the friend request.");
                                props.onSetFriendChange(!props.friendChange);
                                props.onSetFriendRequestChange(!props.friendRequestChange);
                                props.onhandleFriendRequestClose();
                              }
                              else {
                                alert(res.info);
                              }
                            })
                            .catch((error) => {
                              alert(error.info);
                            });
                        }}>Reject</Button>
                    </Grid>
                  </Grid>
                </>
              ) : null}
            </ListItem>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={props.onhandleFriendRequestClose}>Cancel</Button>
      </DialogActions>
    </Dialog>
  );
}