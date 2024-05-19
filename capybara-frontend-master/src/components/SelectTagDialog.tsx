import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import Grid from "@material-ui/core/Grid";

export default function SelectFriendTagDialog(props: any) {
  return (
    <Dialog open={props.open} onClose={props.onhandleSelechTagClose}>
      <DialogTitle>Select Friend Tag</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Select friends with tag:
        </DialogContentText>
      </DialogContent>
      <DialogActions style={{ justifyContent: "center" }}>
        <Grid container spacing={2} direction="column" alignItems="center">
          {props.tags.map((tag: string) => (
            <Grid item key={tag}>
              <Button
                variant="contained"
                color="primary"
                style={{ textTransform: "none", fontSize: "1.1rem", padding: "5px 10px", borderWidth: "2px" }}
                onClick={() => props.onhandleSelectTag(tag)}
              >
                {tag}
              </Button>
            </Grid>
          ))}
          <Grid item style={{ marginTop: "10px" }}>
            <Button style={{ textTransform: "none", fontSize: "1.1rem" }} onClick={props.onhandleSelechTagClose}>Cancel</Button>
          </Grid>
        </Grid>
      </DialogActions>
    </Dialog>
  );
}