import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import CustomInput from "./CustomInput";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import React from "react";
import Avatar from "@material-ui/core/Avatar";
import md5 from "md5";

export default function AddFriendDialog(props: any) {
  const hash = md5(props.friendEmail.trim().toLowerCase());
  return (
    <Dialog open={props.open} onClose={props.onhandleClose}>
      <DialogTitle>Add Friend</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Enter username to find friend:
        </DialogContentText>
        <CustomInput
          id="friendUsername"
          name="friendUsername"
          value={props.friendUsername}
          req={true}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => props.setFriendUsername(e.target.value)}
          type="friendUsername"
          title="Friend Username"
          autoFocus
        ></CustomInput>
        {props.showInfo && (
          <div style={{ display: "flex", alignItems: "center", marginTop: "20px", marginLeft: "15px" }}>
            <Avatar
              alt={props.friendUsername}
              src={`https://www.gravatar.com/avatar/${hash}?d=identicon&s=150`}
              style={{ width: "60px", height: "60px" }}
            />
            <div style={{ marginLeft: "25px" }}>
              <Typography variant="body1">Nickname: {props.friendNichname}</Typography>
              <Typography variant="body1">Phone: {props.friendPhone}</Typography>
              <Typography variant="body1">Email: {props.friendEmail}</Typography>
            </div>
          </div>
        )}
      </DialogContent>
      <DialogActions>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={props.onhandleAddFriendClose}>Cancel</Button>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={props.onhandleFindFriend} color="primary">
          Find
        </Button>
        <Button
          style={{ textTransform: "none", fontSize: "1.1rem" }}
          onClick={() => {
            props.onhandleSubmitFriendRequest();
          }}
          color="primary"
        >
          Submit
        </Button>
      </DialogActions>
    </Dialog>
  );
}