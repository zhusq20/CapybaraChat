import React, { useEffect, useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import CustomInput from "./CustomInput";
import Button from "@mui/material/Button";
import { List, ListItem, ListItemIcon, ListItemText, Avatar } from "@material-ui/core";
import md5 from "md5";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import { friendsDB, conversationsDB } from "../api/db";
import { Message, Friend } from "../api/types";

export default function ChatHistoryDialog(props: any) {
  const [anchorEls, setAnchorEls] = useState<{ [key: number]: HTMLElement | null }>({});
  const [mousePosition, setMousePosition] = useState<{ x: number, y: number }>({ x: 0, y: 0 });
  const [avatars, setAvatars] = useState<{ [key: string]: string }>({});
  const [showTimeOpen, setShowTimeOpen] = useState<boolean>(false);
  const [showMemberOpen, setShowMemberOpen] = useState<boolean>(false);
  const [time, setTime] = useState<string>("");
  const [timeMessages, setTimeMessages] = useState<Message[]>([]);
  const [showTimeMessages, setShowTimeMessages] = useState<boolean>(false);
  const [member, setMember] = useState<string>("");
  const [memberMessages, setMemberMessages] = useState<Message[]>([]);
  const [showMemberMessages, setShowMemberMessages] = useState<boolean>(false);

  const handleClick = (event: React.MouseEvent<HTMLElement>, messageId: number) => {
    event.preventDefault();
    setAnchorEls({ [messageId]: event.currentTarget });
    setMousePosition({ x: event.clientX, y: event.clientY });
  };

  const handleClose = () => {
    setAnchorEls({});
  };

  const getTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes() < 10 ? "0" : ""}${date.getMinutes()}`;
  };

  const getHash = async (username: string) => {
    return friendsDB.friends.filter(friend => friend.username === username).toArray()
      .then((friend: Friend[]) => {
        if (friend.length > 0) {
          return md5(friend[0].email.trim().toLowerCase());
        }
        else {
          return null;
        }
      });
  };

  useEffect(() => {
    const fetchAvatars = async () => {
      const newAvatars: { [key: string]: string } = {};
      const conversation = await conversationsDB.conversations
        .filter(conversation => conversation.id === props.activateConversationId)
        .first();
      if (conversation) {
        const memberPromises = conversation.members.map(member => getHash(member));
        const hashes = await Promise.all(memberPromises);
        newAvatars[props.authUserName] = md5(props.authEmail.trim().toLowerCase());
        conversation.members.forEach((member, index) => {
          const hash = hashes[index];
          if (hash !== null) {
            newAvatars[member] = hash;
          }
        });
        setAvatars(newAvatars);
      }
    };
    fetchAvatars();
  }, [props.messages]);

  const handleTimeOpen = () => {
    setShowTimeOpen(true);
  };

  const handleTimeClose = () => {
    setShowTimeOpen(false);
  };

  const handleMemberOpen = () => {
    setShowMemberOpen(true);
  };

  const handleMemberClose = () => {
    setShowMemberOpen(false);
  };

  const getMessagesByTime = (time: string) => {
    conversationsDB.getMessagesByTime(props.activateConversationId, time)
      .then((messages) => {
        setTimeMessages(messages);
        setShowTimeMessages(true);
        setShowTimeOpen(false);
        setShowMemberMessages(false);
        setTime("");
      });
  };

  const getMessagesByMember = (member: string) => {
    conversationsDB.getMessagesByMember(props.activateConversationId, member)
      .then((messages) => {
        setMemberMessages(messages);
        setShowMemberMessages(true);
        setShowMemberOpen(false);
        setShowTimeMessages(false);
        setMember("");
      });
  };

  const pickMessages = () => {
    if (showTimeMessages) {
      return timeMessages;
    }
    else if (showMemberMessages) {
      return memberMessages;
    }
    else {
      return props.messages;
    }
  };

  const resetMessages = () => {
    setShowTimeMessages(false);
    setShowMemberMessages(false);
  };

  const deleteTimeMessage = (messageId: number) => {
    const updatedMessages = timeMessages.filter(message => message.id !== messageId);
    setTimeMessages(updatedMessages);
  };

  const deleteMemberMessage = (messageId: number) => {
    const updatedMessages = memberMessages.filter(message => message.id !== messageId);
    setMemberMessages(updatedMessages);
  };

  return (
    <Dialog open={props.open} onClose={props.onhandleClose}>
      <DialogTitle>
        Chat History
        <IconButton aria-label="close" onClick={props.onhandleClose} style={{ position: "absolute", top: 10, right: 10 }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogActions style={{ justifyContent: "flex-start", margin: "0 10px" }}>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={handleTimeOpen}>Time</Button>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={handleMemberOpen}>Member</Button>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={resetMessages}>Reset</Button>
      </DialogActions>
      <Dialog open={showTimeOpen} onClose={handleTimeClose} PaperProps={{ style: { width: "500px" } }}>
        <DialogTitle>
          Find chats by Time
        </DialogTitle>
        <DialogContent>
          <CustomInput
            label="Find chats by time as the following format: 2024/12/31"
            id="time"
            name="time"
            value={time}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTime(e.target.value)}
            autoFocus
          ></CustomInput>
        </DialogContent>
        <DialogActions>
          <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={handleTimeClose}>Cancel</Button>
          <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={() => {getMessagesByTime(time);}}>Find</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={showMemberOpen} onClose={handleMemberClose} PaperProps={{ style: { width: "500px" } }}>
        <DialogTitle>
          Find chats by Member
        </DialogTitle>
        <DialogContent>
          <CustomInput
            label="Find chats by Member Username"
            id="member"
            name="member"
            value={member}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMember(e.target.value)}
            autoFocus
          ></CustomInput>
        </DialogContent>
        <DialogActions>
          <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={handleMemberClose}>Cancel</Button>
          <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={() => {getMessagesByMember(member);}}>Find</Button>
        </DialogActions>
      </Dialog>
      <div style={{ margin: "0 10px" }}>
        <List>
          {pickMessages().slice().reverse().map((message: Message) => (
            <ListItem
              key={message.id}
              button
              onContextMenu={(event) => handleClick(event, message.id)}
            >
              <ListItemIcon>
                <Avatar alt={message.sender} src={`https://www.gravatar.com/avatar/${avatars[message.sender]}?d=identicon&s=150`} />
              </ListItemIcon>
              <ListItemText
                primary={message.sender}
                secondary={
                  <div style={{ display: "flex", justifyContent: "space-between", width: "100%" }}>
                    <div style={{ width: "75%", whiteSpace: "normal", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {message.content}
                    </div>
                    <div style={{ width: "25%", textAlign: "right", whiteSpace: "nowrap" }}>
                      {getTime(message.timestamp)}
                    </div>
                  </div>
                }
              />
              <Menu
                id={`simple-menu-${message.id}`}
                anchorEl={anchorEls[message.id]}
                keepMounted
                open={Boolean(anchorEls[message.id])}
                onClose={handleClose}
                transformOrigin={{
                  vertical: "top",
                  horizontal: "right",
                }}
                anchorReference="anchorPosition"
                anchorPosition={
                  mousePosition.x !== 0 && mousePosition.y !== 0
                    ? { top: mousePosition.y, left: mousePosition.x }
                    : undefined
                }
                PaperProps={{
                  style: {
                    width: "fit-content",
                    height: "fit-content",
                    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
                  },
                }}
                style={{
                  display: "flex",
                  justifyContent: "center",
                  marginLeft: "80px",
                }}
              >
                <MenuItem
                  onClick={() => {
                    handleClose();
                    props.onDeleteMessage(message.id);
                    deleteTimeMessage(message.id);
                    deleteMemberMessage(message.id);
                  }}
                  style={{ textAlign: "center" }}
                >
                  Delete
                </MenuItem>
              </Menu>
            </ListItem>
          ))}
        </List>
      </div>
    </Dialog>
  );
}