import React, { useEffect, useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import Avatar from "@material-ui/core/Avatar";
import md5 from "md5";
import { GroupRequest } from "../api/types";
import { handleGroupRequest } from "../api/group";
import Grid from "@material-ui/core/Grid";
import Box from "@mui/material/Box";
import { conversationsDB } from "../api/db";

export default function GroupRequestDialog(props: any) {
  const [groupNames, setGroupNames] = useState<{ [key: number]: string }>({});
  const [conversationIds, setConversationIds] = useState<{ [key: number]: number }>({});

  useEffect(() => {
    const fetchGroups = async () => {
      const newGroupNames: { [key: number]: string } = {};
      const newConversationIds: { [key: number]: number } = {};
      const group = await conversationsDB.groups.toArray();
      props.groupRequest.forEach((request: GroupRequest) => {
        const groupInfo = group.find((g) => g.id === request.group);
        if (groupInfo) {
          newGroupNames[request.group] = groupInfo.name;
          newConversationIds[request.group] = groupInfo.conversation;
        }
      });
      setGroupNames(newGroupNames);
      setConversationIds(newConversationIds);
    };
    fetchGroups();
  }, [props.groupRequest]);

  const getTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes() < 10 ? "0" : ""}${date.getMinutes()}`;
  };

  return (
    <Dialog open={props.open} onClose={props.onhandleGroupRequestClose}>
      <DialogTitle>Group Request</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Your Group Requests:
        </DialogContentText>
        <List>
          {props.groupRequest && props.groupRequest.map((request: GroupRequest) => (
              <ListItem key={request.sender}>
                <ListItemAvatar>
                  <Avatar alt={request.sender} src={`https://www.gravatar.com/avatar/${md5(request.email.trim().toLowerCase())}?d=identicon&s=150`} />
                </ListItemAvatar>
                <Grid style={{ width: "400px" }}>
                  <ListItemText
                    primary={`${request.sender} => ${groupNames[request.group]}`}
                    secondary={getTime(request.timestamp)}
                  />
                </Grid>
                <Grid container direction="row" alignItems="center" justifyContent="flex-end" spacing={1} style={{ marginRight: "3px" }}>
                  <Grid item>
                    <ListItemText primary={`${request.status}`} />
                  </Grid>
                </Grid>
                {(request.status === "Pending") ? (
                  <>
                    <Grid container direction="row" alignItems="center" justifyContent="flex-end" spacing={1} style={{ width: "500px" }}>
                      <Grid item>
                        <Button
                          style={{ textTransform: "none", padding: "5px 10px", borderWidth: "2px" }}
                          variant="contained"
                          color="primary"
                          onClick={() => {
                            handleGroupRequest(request.group, request.sender, true)
                              .then((res) => res.json())
                              .then((res) => {
                                if (Number(res.code) === 0) {
                                  alert("You have accepted the group request.");
                                  console.log(request.group, props.activateGroupId);
                                  conversationsDB.addNewMember(conversationIds[request.group], request.sender)
                                  .then(() => {
                                    if (request.group === props.activateGroupId) {
                                      console.log("add new member");
                                      props.setGroupMemberChange((pre: boolean) => {
                                        return !pre;
                                      });
                                    }
                                    props.setGroupRequestChange((pre: boolean) => {
                                      return !pre;
                                    });
                                    props.sendInviteMessage(conversationIds[request.group], request.sender);
                                  });
                                  props.onhandleGroupRequestClose();
                                }
                                else {
                                  alert(res.info);
                                }
                              })
                              .catch((error) => {
                                alert(error.info);
                              });
                          }}
                        >
                          Accept
                        </Button>
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
                            handleGroupRequest(request.group, request.sender, false)
                              .then((res) => res.json())
                              .then((res) => {
                                if (Number(res.code) === 0) {
                                  alert("You have rejected the group request.");
                                  props.setGroupRequestChange((pre: boolean) => {
                                    return !pre;
                                  });
                                  props.onhandleGroupRequestClose();
                                }
                                else {
                                  alert(res.info);
                                }
                              })
                              .catch((error) => {
                                alert(error.info);
                              });
                          }}
                        >
                          Reject
                        </Button>
                      </Grid>
                    </Grid>
                  </>
                ) : null
              }
            </ListItem>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={props.onhandleGroupRequestClose}>Cancel</Button>
      </DialogActions>
    </Dialog>
  );
}