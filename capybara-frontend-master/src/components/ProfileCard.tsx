import Card from "@mui/material/Card";
import { useState } from "react";
import Typography from "@mui/material/Typography";
import { Grid } from "@mui/material";
import Avatar from "@mui/material/Avatar";
import Badge from "@mui/material/Badge";
import Button from "@mui/material/Button";
import { useRouter } from "next/router";
import Cookies from "js-cookie";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import CustomInput from "./CustomInput";
import sha256 from "../utils/sha256";
import md5 from "md5";

const styles = {
  details: {
    padding: "1rem",
    borderTop: "1px solid #e1e1e1"
  },
  value: {
    padding: "1rem 2rem",
    borderTop: "1px solid #e1e1e1",
    color: "#899499"
  }
};

export default function ProfileCard(props: any) {
  const router = useRouter();

  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");

  const handleClickOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  const handleAvatarChange = () => {
    alert("You should use Gravatar to change your profile photo.");
    window.location.href = "https://gravatar.com/";
  };

  const handleSubmit = () => {
    const requestBody = {
      password: sha256(password),
    };
    const header = new Headers();
    const jwtToken = Cookies.get("jwt_token");
    if (jwtToken) {
      header.append("authorization", jwtToken);
    }
    else {
      router.push(`/SignIn`);
    }
    fetch(`/api/chat/delete_account`, {
      method: "DELETE",
      headers: header,
      body: JSON.stringify(requestBody),
    })
    .then((res) => res.json())
    .then((res) => {
      if (Number(res.code) === 0) {
        alert("Account deleted successfully!");
        Cookies.remove("jwt_token");
        router.push(`/SignIn`);
      }
    })
    .catch((error) => {
      alert(error.info);
    });
    setOpen(false);
  };

  const hash = md5(props.email.trim().toLowerCase());
  const gravatarUrl = `https://www.gravatar.com/avatar/${hash}?d=identicon&s=150`;

  return (
    <Card variant="outlined">
      <Grid
        container
        direction="column"
        justifyContent="center"
        alignItems="center"
      >
        {/* CARD HEADER START */}
        <Grid item sx={{ p: "1.5rem 0rem", textAlign: "center" }}>
          {/* PROFILE PHOTO */}
          <Badge
            overlap="circular"
            anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
          >
            <Avatar
              sx={{ width: 100, height: 100, mb: 1.5 }}
              src={gravatarUrl}
            ></Avatar>
          </Badge>

          {/* DESCRIPTION */}
          <Typography variant="h6">{props.nickname === "" ? "No Nick Name": props.nickname}</Typography>
          <Typography color="text.secondary">{props.username}</Typography>
        </Grid>
        {/* CARD HEADER END */}

        {/* BUTTON */}
        <Grid item style={styles.details} sx={{ width: "100%" }}>
          <Button
            variant="contained"
            color="secondary"
            sx={{ width: "99%", p: 1, my: 2 }}
            component="span"
            onClick={handleAvatarChange}
          >
            Change Profile Photo
          </Button>
          <Button
            variant="contained"
            color="secondary"
            sx={{ width: "99%", p: 1, my: 2 }}
            onClick={() => {
              Cookies.remove("jwt_token");
              router.push(`/SignIn`);
            }}
          >
            Log Out
          </Button>
          <Button
            variant="contained"
            color="secondary"
            sx={{ width: "99%", p: 1, my: 2 }}
            onClick={handleClickOpen}
          >
            Delete Account
          </Button>
          <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Edit Information</DialogTitle>
            <DialogContent>
              <DialogContentText>
                Please enter new information:
              </DialogContentText>
              <CustomInput
                id="Password"
                name="Password"
                value={password}
                required={true}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                title="Password"
                autoFocus
              ></CustomInput>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>Cancel</Button>
              <Button onClick={handleSubmit} color="primary">
                Submit
              </Button>
            </DialogActions>
          </Dialog>
        </Grid>
      </Grid>
    </Card>
  );
}
