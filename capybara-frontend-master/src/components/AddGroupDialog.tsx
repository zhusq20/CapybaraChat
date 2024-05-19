import React, { useEffect, useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import Grid from "@material-ui/core/Grid";
import { List, ListItem, ListItemIcon, ListItemText, Avatar } from "@material-ui/core";
import md5 from "md5";
import { Friend } from "../api/types";
import CustomInput from "./CustomInput";

export default function AddGroupDialog(props: any) {
  const [avatars, setAvatars] = useState<{ [key: string]: string }>({});
  const [members, setMembers] = useState<string[]>([]);
  const [groupName, setGroupName] = useState<string>("");

  useEffect(() => {
    const fetchAvatars = async () => {
      const newAvatars: { [key: string]: string } = {};
      for (const friend of props.friends) {
        const hash = md5(friend.email.trim().toLowerCase());
        newAvatars[friend.username] = hash;
      }
      setAvatars(newAvatars);
    };
    fetchAvatars();
  }, [props.friends]);

  const handleAddGroupMember = (member: string) => {
    if (!members.includes(member)) {
      setMembers([...members, member]);
    }
  };

  const handleDeleteGroupMember = (member: string) => {
    setMembers(members.filter((m: string) => m !== member));
  };

  return (
    <Dialog
      open={props.open}
      onClose={() => {
        props.onhandleGroupRequestClose();
        setMembers([]);
        setGroupName("");
      }}
      PaperProps={{ style: { width: "500px" } }}
    >
      <DialogTitle>Add Group Chat</DialogTitle>
      <Grid style={{ height: "10vh", marginLeft: "20px", marginRight: "20px" }}>
        <CustomInput
          label="Enter Group Name Here"
          id="groupName"
          name="groupName"
          value={groupName}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGroupName(e.target.value)}
          autoFocus
        ></CustomInput>
      </Grid>
      <div style={{ margin: "0 17px", marginTop: "5px", marginBottom: "5px" }}>
        {members && members.map((member: string) => (
          <Button
            key={member}
            variant="contained"
            color="primary"
            style={{ margin: "5px 5px", textTransform: "none", fontSize: "1.1rem", padding: "5px 10px", borderWidth: "2px" }}
            onClick={() => handleDeleteGroupMember(member)}
          >
            {member}
          </Button>
        ))}
      </div>
      <div style={{ margin: "0 10px", maxHeight: "60vh" , overflowY: "auto"}}>
        <List>
        {props.friends.map((friend: Friend) => (
          <ListItem button key={friend.username} onClick={() => handleAddGroupMember(friend.username)}>
            <ListItemIcon>
              <Avatar alt={friend.username} src={`https://www.gravatar.com/avatar/${avatars[friend.username]}?d=identicon&s=150`} />
            </ListItemIcon>
            <ListItemText primary={friend.username} secondary={friend.tag} />
          </ListItem>
        ))}
        </List>
      </div>
      <DialogActions>
      <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={() => {
          props.onhandleGroupRequestClose();
          setMembers([]);
          setGroupName("");
        }}>
        Cancel
      </Button>
      <Button
        style={{ textTransform: "none", fontSize: "1.1rem" }}
        onClick={() => {
          props.onhandleAddGroup(groupName, members);
          props.onhandleGroupRequestClose();
          setMembers([]);
          setGroupName("");
        }}
        color="primary"
      >
        Submit
      </Button>
      </DialogActions>
    </Dialog>
  );
}