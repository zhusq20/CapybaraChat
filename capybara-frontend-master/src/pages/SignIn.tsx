import * as React from "react";
import Avatar from "@mui/material/Avatar";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import Link from "@mui/material/Link";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { useState, useEffect } from "react";
import { SUGNIN_SUCCESS} from "../constants/string";
import { useRouter } from "next/router";
import { createHash } from "crypto";
import Cookies from "js-cookie";
import { setName, setToken } from "../redux/auth";
import { useDispatch } from "react-redux";

function Copyright(props: any) {
  return (
    <Typography variant="body2" color="text.secondary" align="center" {...props}>
      {"Copyright © "}
      <Link color="inherit" href="https://mui.com/">
        Capybara
      </Link>{" "}
      {new Date().getFullYear()}
      {"."}
    </Typography>
  );
}

function sha256(input: string): string {
  const hash = createHash("sha256");
  input = "capybara" + input;
  hash.update(input);
  return hash.digest("hex");
}

// TODO remove, this demo shouldn't need to reset the theme.
const defaultTheme = createTheme();

export default function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const router = useRouter();
  const dispatch = useDispatch();

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const requestBody = {
      username,
      password,
    };
    fetch(`/api/chat/login`, {
      method: "POST",
      body: JSON.stringify(requestBody),
    })
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          alert(username + SUGNIN_SUCCESS);
          const expires = new Date(new Date().getTime() + 60 * 60 * 1000);
          Cookies.set("jwt_token", res.token, { expires });
          dispatch(setToken(res.token));
          dispatch(setName(username));
          router.push({
            pathname: "/Chatroom"
          });
        }
        else {
          alert(res.info);
        }
      })
      .catch((error) => {
        alert(error.info);
      });
  };

  useEffect(() => {
    const cookie_jwtToken = Cookies.get("jwt_token");
    if (cookie_jwtToken) {
      router.push({
        pathname: "/Chatroom"
      });
    }
  }, [router]);

  return (
    <ThemeProvider theme={defaultTheme}>
      <Container component="main" maxWidth="xs">
        <CssBaseline />
        <Box
          sx={{
            marginTop: 8,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Avatar sx={{ m: 1, bgcolor: "secondary.main" }}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Sign in
          </Typography>
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="User Name"
              name="username"
              autoComplete="username"
              autoFocus
              onChange={(e) => setUsername(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              onChange={(e) => setPassword(sha256(e.target.value))}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Sign In
            </Button>
            <Grid container>
              <Grid item xs>
                <Link href="#" variant="body2">
                  Forgot password?
                </Link>
              </Grid>
              <Grid item>
                <Link href="/SignUp" variant="body2">
                  {"Don't have an account? Sign Up"}
                </Link>
              </Grid>
            </Grid>
          </Box>
        </Box>
        <Copyright sx={{ mt: 8, mb: 4 }} />
      </Container>
    </ThemeProvider>
  );
}