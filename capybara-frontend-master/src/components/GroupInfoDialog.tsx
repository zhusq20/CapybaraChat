import React, { useEffect, useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import md5 from "md5";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import AddIcon from "@mui/icons-material/Add";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import Button from "@mui/material/Button";
import Avatar from "@mui/material/Avatar";
import { conversationsDB, friendsDB } from "../api/db";
import { findFriend, addFriend } from "../api/friend";
import Divider from "@material-ui/core/Divider";
import Menu from "@material-ui/core/Menu";
import { Box } from "@mui/material";
import SupervisedUserCircleIcon from "@mui/icons-material/SupervisedUserCircle";
import CustomInput from "./CustomInput";
import { getGroupNotice, addGroupNotice, leaveGroup, inviteFriend } from "../api/group";
import { Notice, Message } from "../api/types";
import { addMessage } from "../api/chat";

export default function GroupInfoDialog(props: any) {
  const [avatars, setAvatars] = useState<{ [key: string]: string }>({});
  const [master, setMaster] = useState<{ [key: string]: string }>({});
  const [managers, setManagers] = useState<{ [key: string]: string }>({});
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [friendUserName, setFriendUserName] = useState<string>("");
  const [friendNickName, setFriendNickName] = useState<string>("");
  const [friendPhone, setFriendPhone] = useState<string>("");
  const [friendEmail, setFriendEmail] = useState<string>("");
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [newMaster, setNewMaster] = useState<string>("");
  const [newManager, setNewManager] = useState<string>("");
  const [deleteManager, setDeleteManager] = useState<string>("");
  const [removeMember, setRemoveMember] = useState<string>("");
  const [groupNotice, setGroupNotice] = useState<Notice[]>([]);
  const [newNotice, setNewNotice] = useState<string>("");
  const [showAddNotice, setShowAddNotice] = useState<boolean>(false);
  const [showInviteFriend, setShowInviteFriend] = useState<boolean>(false);
  const [invitedFriend, setInvitedFriend] = useState<string>("");

  const handleSettingsOpen = () => {
    setShowSettings(true);
  };

  const handleSettingsClose = () => {
    setShowSettings(false);
  };

  const handleAddNoticeOpen = () => {
    setShowAddNotice(true);
  };

  const handleAddNoticeClose = () => {
    setShowAddNotice(false);
  };

  const handleInviteFriendOpen = () => {
    setShowInviteFriend(true);
  };

  const handleInviteFriendClose = () => {
    setShowInviteFriend(false);
  };

  const getHash = async (username: string) => {
    const friends = await friendsDB.friends.toArray();
    for (const friend of friends) {
      if (friend.username === username) {
        return md5(friend.email.trim().toLowerCase());
      }
    }
    try {
      const res = await findFriend(username).then(res => res.json());
      if (Number(res.code) === 0) {
        return md5(res.userinfo.email.trim().toLowerCase());
      }
      else {
        alert(res.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
    return null;
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
        if (conversation.type === 0) {
          setAvatars(newAvatars);
          setMaster({});
          setManagers({});
        }
        else {
          const newMaster: { [key: string]: string } = {};
          const newManagers: { [key: string]: string } = {};
          const group = await conversationsDB.groups
            .filter(group => group.conversation === props.activateConversationId)
            .toArray();
          if (group) {
            if (group[0].master !== "undefined") {
              newMaster[group[0].master] = newAvatars[group[0].master];
              delete newAvatars[group[0].master];
            }
            group[0].manager.forEach((manager) => {
              if (manager !== "undefined") {
                newManagers[manager] = newAvatars[manager];
                delete newAvatars[manager];
              }
            });
          }
          setAvatars(newAvatars);
          setMaster(newMaster);
          setManagers(newManagers);
        }
      }
    };
    fetchAvatars();
  }, [props.activateConversationId, props.groupMemberChange]);

  useEffect(() => {
    getGroupNotice(props.activateGroupId)
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          setGroupNotice(res.notices);
        }
      });
  }, [props.activateGroupId, props.groupNoticeChange]);

  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleFindFriend = (username: string) => {
    findFriend(username)
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          setFriendUserName(res.userinfo.username);
          setFriendNickName(res.userinfo.nickname);
          setFriendPhone(res.userinfo.phone);
          setFriendEmail(res.userinfo.email);
        }
        else {
          alert(res.info);
        }
      })
      .catch((error) => {
        alert(error.info);
      });
  };

  const handleSubmitFriendRequest = () => {
    addFriend(friendUserName)
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          alert(`Friend request sent to ${friendUserName}.`);
        }
        else {
          alert(res.info);
        }
      })
      .catch((error) => {
        alert(error.info);
      });
  };

  const handleSubmitNewManager = (groupId: number, manager: string) => {
    conversationsDB.addNewManager(groupId, manager);
    setManagers(preManagers => {
      return { ...preManagers, [manager]: avatars[manager] };
    });
    setAvatars(preAvatars => {
      delete preAvatars[manager];
      return preAvatars;
    });
  };

  const handleSubmitDeleteManager = (groupId: number, manager: string) => {
    conversationsDB.deleteManager(groupId, manager);
    setAvatars(preAvatars => {
      return { ...preAvatars, [manager]: managers[manager] };
    });
    setManagers(preManagers => {
      delete preManagers[manager];
      return preManagers;
    });
  };

  const handleSubmitChangeMaster = (groupId: number, masterUserName: string) => {
    conversationsDB.changeMaster(groupId, masterUserName);
    const newMaster: { [key: string]: string } = {};
    if (managers[masterUserName]) {
      newMaster[masterUserName] = managers[masterUserName];
      setMaster(newMaster);
      setManagers(preManagers => {
        delete preManagers[masterUserName];
        return preManagers;
      });
      setAvatars(preAvatars => {
        const masterKeys = Object.keys(master);
        preAvatars[masterKeys[0]] = master[masterKeys[0]];
        return preAvatars;
      });
    }
    else {
      newMaster[masterUserName] = avatars[masterUserName];
      setMaster(newMaster);
      setAvatars(preAvatars => {
        const masterKeys = Object.keys(master);
        preAvatars[masterKeys[0]] = master[masterKeys[0]];
        delete preAvatars[masterUserName];
        return preAvatars;
      });
    }
  };

  const handleSubmitRemoveMember = (groupId: number, member: string) => {
    if (Object.keys(master)[0] === props.authUserName) {
      conversationsDB.removeMember(groupId, member);
      if (managers[member]) {
        setManagers(preManagers => {
          delete preManagers[member];
          return preManagers;
        });
      }
      else {
        setAvatars(preAvatars => {
          delete preAvatars[member];
          return preAvatars;
        });
      }
    }
    else if (Object.keys(managers).includes(props.authUserName)) {
      if (member === Object.keys(master)[0]) {
        alert("You cannot remove Master.");
      }
      else if (Object.keys(managers).includes(member)) {
        alert("You cannot remove Manager.");
      }
      else {
        conversationsDB.removeMember(groupId, member);
        setAvatars(preAvatars => {
          delete preAvatars[member];
          return preAvatars;
        });
      }
    }
  };

  const addNewGroupNotice = (groupId: number, notice: string) => {
    addGroupNotice(groupId, notice)
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          alert("Group notice added.");
          setGroupNotice(preGroupNotice => {
            return [...preGroupNotice, res.notice];
          });
          const finalReplyMessage = "[New Group Notice]\n-------------------------\n" + res.notice.content;
          addMessage(res.notice.conversation, finalReplyMessage, -1)
            .then((res) => res.json())
            .then((res) => {
              if (Number(res.code) === 0) {
                const newMessage: Message = res.message;
                props.addNewMessage(newMessage);
              }
              else {
                alert(res.info);
              }
            })
            .catch((error) => {
              alert(error.info);
            });
        }
      })
      .catch((error) => {
        alert(error.info);
      });
  };

  const handleleaveGroup = (groupId: number) => {
    if (Object.keys(master)[0] === props.authUserName) {
      alert("Master cannot leave group.");
    }
    else if (Object.keys(managers).includes(props.authUserName)) {
      delete managers[props.authUserName];
      leaveGroup(groupId);
      conversationsDB.leaveGroup(groupId);
      props.onSetConversationChange((pre: boolean) => {
        return !pre;
      });
    }
    else {
      delete avatars[props.authUserName];
      leaveGroup(groupId);
      conversationsDB.leaveGroup(groupId);
      props.onSetConversationChange((pre: boolean) => {
        return !pre;
      });
    }
    props.onSetActivateConversationId(-1);
    props.onhandleClose();
  };

  const handleInviteFriend = (groupId: number) => {
    inviteFriend(groupId, invitedFriend)
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          alert(`You have invited Friend ${invitedFriend} successfully. Wait for Master or Manager to Accept.`);
        }
        else {
          alert(res.info);
        }
      })
      .catch((error) => {
        alert(error.info);
      });
  };

  return (
    <Dialog open={props.open} onClose={props.onhandleClose}>
      <DialogTitle>
        Group Information
        <IconButton aria-label="close" onClick={props.onhandleClose} style={{ position: "absolute", top: 10, right: 10 }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Divider />
          </Grid>
          <Grid item xs={12}>
            <Grid container alignItems="center" style={{ justifyContent: "space-between" }}>
              <Grid item xs={10}>
                <Typography variant="h6">Members</Typography>
              </Grid>
              {(Object.keys(master)[0] === props.authUserName || Object.keys(managers).includes(props.authUserName)) && (
                <Grid item xs={1}>
                  <IconButton onClick={handleSettingsOpen} style={{ right: 10 }}>
                    <SupervisedUserCircleIcon />
                  </IconButton>
                  <Dialog
                    open={showSettings}
                    onClose={handleSettingsClose}
                    PaperProps={{
                      style: {
                        width: "500px",
                        maxHeight: "90vh",
                        overflowY: "auto"
                      }
                    }}
                  >
                    <DialogTitle>
                      Group Settings
                      <IconButton aria-label="close" onClick={handleSettingsClose} style={{ position: "absolute", top: 10, right: 10 }}>
                        <CloseIcon />
                      </IconButton>
                    </DialogTitle>
                    {Object.keys(master)[0] === props.authUserName && (
                      <div>
                        <Divider />
                          <DialogContent sx={{ overflowY: "visible" }}>
                            <Typography style={{marginBottom: "8px"}}>Add Manager</Typography>
                            <CustomInput
                              label="Type Member Username"
                              id="member"
                              name="member"
                              value={newManager}
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewManager(e.target.value)}
                              autoFocus
                            ></CustomInput>
                            <DialogActions>
                              <Button
                                style={{ textTransform: "none", fontSize: "1.1rem" }}
                                onClick={() => {
                                  handleSubmitNewManager(props.activateGroupId, newManager);
                                  setNewManager("");
                                  handleSettingsClose();
                                }}
                              >
                                Submit
                              </Button>
                            </DialogActions>
                          </DialogContent>
                          <Divider />
                          <DialogContent sx={{ overflowY: "visible" }}>
                            <Typography style={{marginBottom: "8px"}}>Delete Manager</Typography>
                            <CustomInput
                              label="Type Member Username"
                              id="member"
                              name="member"
                              value={deleteManager}
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDeleteManager(e.target.value)}
                              autoFocus
                            ></CustomInput>
                            <DialogActions>
                              <Button
                                style={{ textTransform: "none", fontSize: "1.1rem" }}
                                onClick={() => {
                                  handleSubmitDeleteManager(props.activateGroupId, deleteManager);
                                  setDeleteManager("");
                                  handleSettingsClose();
                                }}
                              >
                                Submit
                              </Button>
                            </DialogActions>
                          </DialogContent>
                          <Divider />
                          <DialogContent sx={{ overflowY: "visible" }}>
                            <Typography style={{marginBottom: "8px"}}>Change Master</Typography>
                            <CustomInput
                              label="Type Member Username"
                              id="member"
                              name="member"
                              value={newMaster}
                              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewMaster(e.target.value)}
                              autoFocus
                            ></CustomInput>
                            <DialogActions>
                              <Button
                                style={{ textTransform: "none", fontSize: "1.1rem" }}
                                onClick={() => {
                                  handleSubmitChangeMaster(props.activateGroupId, newMaster);
                                  setNewMaster("");
                                  handleSettingsClose();
                                }}
                              >
                                Submit
                              </Button>
                            </DialogActions>
                          </DialogContent>
                      </div>
                    )}
                    <Divider />
                    <DialogContent sx={{ overflowY: "visible" }}>
                      <Typography style={{marginBottom: "8px"}}>Remove Member</Typography>
                      <CustomInput
                        label="Type Member Username"
                        id="member"
                        name="member"
                        value={removeMember}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setRemoveMember(e.target.value)}
                        autoFocus
                      ></CustomInput>
                      <DialogActions>
                        <Button
                          style={{ textTransform: "none", fontSize: "1.1rem" }}
                          onClick={() => {
                            handleSubmitRemoveMember(props.activateGroupId, removeMember);
                            setRemoveMember("");
                            handleSettingsClose();
                          }}
                        >
                          Submit
                        </Button>
                      </DialogActions>
                    </DialogContent>
                  </Dialog>
                </Grid>
              )}
              <Grid item xs={1}>
                <IconButton onClick={handleInviteFriendOpen} style={{ right: 10 }}>
                  <AddIcon />
                </IconButton>
                <Dialog
                  open={showInviteFriend}
                  onClose={handleInviteFriendClose}
                  PaperProps={{
                    style: {
                      width: "500px",
                      maxHeight: "90vh",
                      overflowY: "auto"
                    }
                  }}
                >
                  <DialogTitle>
                    Invite Friend
                    <IconButton aria-label="close" onClick={handleInviteFriendClose} style={{ position: "absolute", top: 10, right: 10 }}>
                      <CloseIcon />
                    </IconButton>
                  </DialogTitle>
                  <Divider />
                  <DialogContent sx={{ overflowY: "visible" }}>
                    <CustomInput
                      label="Type Friend Username to invite"
                      id="InviteFriend"
                      name="InviteFriend"
                      value={invitedFriend}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInvitedFriend(e.target.value)}
                      autoFocus
                    ></CustomInput>
                    <DialogActions>
                      <Button
                        style={{ textTransform: "none", fontSize: "1.1rem" }}
                        onClick={() => {
                          handleInviteFriend(props.activateGroupId);
                          setInvitedFriend("");
                          handleInviteFriendClose();
                        }}
                      >
                        Submit
                      </Button>
                    </DialogActions>
                  </DialogContent>
                </Dialog>
              </Grid>
            </Grid>
            <Grid container direction="row" style={{ margin: "10px 0" }}>
              {Object.keys(master).map((key) => {
                const avatarUrl = `https://www.gravatar.com/avatar/${master[key]}?d=identicon&s=150`;
                return key === "undefined" ? null : (
                  <Grid item container direction="column" alignItems="center" justifyContent="center" style={{ margin: "10px 0", width: "80px" }}>
                    <Typography>Master</Typography>
                    <IconButton onClick={(event) => {
                    handleMenuOpen(event);
                    handleFindFriend(key);
                  }}>
                      <Avatar alt={key} src={avatarUrl} />
                    </IconButton>
                    <Typography>{key}</Typography>
                  </Grid>
                );
              })}
              {Object.keys(managers).map((key) => {
                const avatarUrl = `https://www.gravatar.com/avatar/${managers[key]}?d=identicon&s=150`;
                return key === "undefined" ? null : (
                  <Grid item container direction="column" alignItems="center" justifyContent="center" style={{ margin: "10px 0", width: "80px" }}>
                    <Typography>Manager</Typography>
                    <IconButton onClick={(event) => {
                    handleMenuOpen(event);
                    handleFindFriend(key);
                  }}>
                      <Avatar alt={key} src={avatarUrl} />
                    </IconButton>
                    <Typography>{key}</Typography>
                  </Grid>
                );
              })}
            </Grid>
            <Grid style={{ marginLeft: "7px", marginTop: "6px", marginBottom: "-20px" }}>
              <Typography>Members</Typography>
            </Grid>
            <Grid container direction="row" style={{ margin: "10px 0" }}>
              {Object.keys(avatars).map((key) => {
                const avatarUrl = `https://www.gravatar.com/avatar/${avatars[key]}?d=identicon&s=150`;
                return key === "undefined" ? null : (
                  <Grid item container direction="column" alignItems="center" justifyContent="center" style={{ margin: "10px 0", width: "80px" }}>
                    <IconButton onClick={(event) => {
                    handleMenuOpen(event);
                    handleFindFriend(key);
                  }}>
                      <Avatar alt={key} src={avatarUrl} />
                    </IconButton>
                    <Typography>{key}</Typography>
                  </Grid>
                );
              })}
            </Grid>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              anchorOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
              transformOrigin={{
                vertical: "top",
                horizontal: "left",
              }}
              PaperProps={{
                style: { width: "350px" }
              }}
            >
              <Box sx={{ padding: 1, display: "flex", alignItems: "center", marginLeft: 2 }}>
                <Avatar
                  alt={props.friendUsername}
                  src={`https://www.gravatar.com/avatar/${md5(friendEmail.trim().toLowerCase())}?d=identicon&s=150`}
                  style={{ width: "60px", height: "60px" }}
                />
                <Box sx={{ marginLeft: 3 }}>
                  <Typography variant="body1">Nickname: {friendNickName}</Typography>
                  <Typography variant="body1">Phone: {friendPhone}</Typography>
                  <Typography variant="body1">Email: {friendEmail}</Typography>
                </Box>
              </Box>
              <Box sx={{ display: "flex", justifyContent: "flex-end", padding: 1 }}>
                <Button sx={{ textTransform: "none", fontSize: "1.1rem", marginRight: 1 }} onClick={handleMenuClose}>Cancel</Button>
                <Button
                  sx={{ textTransform: "none", fontSize: "1.1rem" }}
                  onClick={() => {
                    handleSubmitFriendRequest();
                    props.onSetFriendRequestChange((preFriendRequestChange: boolean) => {
                      return !preFriendRequestChange;
                    });
                    handleMenuClose();
                  }}
                  color="primary"
                >
                  Add
                </Button>
              </Box>
            </Menu>
          </Grid>
          <Grid item xs={12}>
            <Divider />
          </Grid>
          <Grid item xs={12}>
            <Grid container alignItems="center" justifyContent="space-between">
              <Grid item xs={11}>
                <Typography variant="h6">Announcements</Typography>
              </Grid>
              { (Object.keys(master)[0] === props.authUserName || Object.keys(managers).includes(props.authUserName)) && (
                <Grid item xs={1}>
                  <IconButton aria-label="AddGroupNotice" onClick={handleAddNoticeOpen} style={{ right: 10 }}>
                    <AddIcon />
                  </IconButton>
                  <Dialog
                    open={showAddNotice}
                    onClose={handleAddNoticeClose}
                    PaperProps={{
                      style: {
                        width: "500px",
                        maxHeight: "90vh",
                        overflowY: "auto"
                      }
                    }}
                  >
                    <DialogTitle>
                      Add Group Notice
                      <IconButton aria-label="close" onClick={handleAddNoticeClose} style={{ position: "absolute", top: 10, right: 10 }}>
                        <CloseIcon />
                      </IconButton>
                    </DialogTitle>
                    <Divider />
                    <DialogContent sx={{ overflowY: "visible" }}>
                      <CustomInput
                        label="Type Group Notice"
                        id="GroupNotice"
                        name="GroupNotice"
                        value={newNotice}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewNotice(e.target.value)}
                        autoFocus
                      ></CustomInput>
                      <DialogActions>
                        <Button
                          style={{ textTransform: "none", fontSize: "1.1rem" }}
                          onClick={() => {
                            addNewGroupNotice(props.activateGroupId, newNotice);
                            setNewNotice("");
                            handleAddNoticeClose();
                          }}
                        >
                          Submit
                        </Button>
                      </DialogActions>
                    </DialogContent>
                  </Dialog>
                </Grid>
              )}
              <List>
                {groupNotice.map((notice) => (
                  <ListItem key={notice.id}>
                    <Grid container style={{width: "500px"}}>
                      <Grid item xs={10}>
                        <ListItemText
                          primary={notice.content}
                        />
                      </Grid>
                      <Grid item xs={2}>
                      <ListItemText
                          primary={notice.sender}
                          secondary={
                            (() => {
                              const date = new Date(notice.timestamp);
                              const formattedDate = `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes() < 10 ? "0" : ""}${date.getMinutes()}`;
                              return formattedDate;
                            })()
                          }
                          primaryTypographyProps={{ style: { textAlign: "right" } }}
                          secondaryTypographyProps={{ style: { textAlign: "right" } }}
                        />
                      </Grid>
                    </Grid>
                  </ListItem>
                ))}
              </List>
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <Divider />
          </Grid>
          <Grid item xs={12} style={{ display: "flex", justifyContent: "center" }}>
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => handleleaveGroup(props.activateGroupId)}
              style={{
                backgroundColor: "rgba(255, 0, 0, 0.7)",
                color: "white",
                width: "300px",
                height: "50px",
                borderRadius: "10px",
                justifyContent: "center"
              }}
            >
              Leave Group
            </Button>
          </Grid>
        </Grid>
      </DialogContent>
    </Dialog>
  );
}