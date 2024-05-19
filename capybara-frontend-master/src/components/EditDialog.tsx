import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import CustomInput from "./CustomInput";
import Button from "@mui/material/Button";

export default function EditDialog(props: any) {
  return (
    <Dialog open={props.open} onClose={props.onhandleClose}>
      <DialogTitle>Edit Information</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Please enter new information:<br />
          You must enter your old password for Identity Verification.
        </DialogContentText>
        <CustomInput
          id="oldPassword"
          name="oldPassword"
          value={props.oldPassword}
          req={true}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => props.setOldPassword(e.target.value)}
          type="password"
          title="Old Password"
          autoFocus
        ></CustomInput>
        <CustomInput
          id="newPassword"
          name="newPassword"
          value={props.newPassword}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => props.setNewPassword(e.target.value)}
          type="password"
          title="New Password"
          autoFocus
        ></CustomInput>
        <CustomInput
          id="newPasswordAgain"
          name="newPasswordAgain"
          value={props.newPasswordAgain}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => props.setNewPasswordAgain(e.target.value)}
          type="password"
          title="New Password Again"
          autoFocus
        ></CustomInput>
        <CustomInput
          id="newUserName"
          name="newUserName"
          value={props.newUserName}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => props.setNewUserName(e.target.value)}
          title="New User Name"
          autoFocus
        ></CustomInput>
        <CustomInput
          id="newNickName"
          name="newNickName"
          value={props.newNickName}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => props.setNewNickName(e.target.value)}
          title="New Nick Name"
          autoFocus
        ></CustomInput>
        <CustomInput
          id="newPhone"
          name="newPhone"
          value={props.newPhone}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => props.setNewPhone(e.target.value)}
          title="New Phone"
          autoFocus
        ></CustomInput>
        <CustomInput
          id="newEmail"
          name="newEmail"
          value={props.newEmail}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => props.setNewEmail(e.target.value)}
          title="New Email"
          autoFocus
        ></CustomInput>
      </DialogContent>
      <DialogActions>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={props.onhandleClose}>Cancel</Button>
        <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={props.onhandleSubmit} color="primary">
          Submit
        </Button>
      </DialogActions>
    </Dialog>
  );
}