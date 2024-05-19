import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import CssBaseline from "@mui/material/CssBaseline";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import ProfileCard from "../components/ProfileCard";
import SettingsCard from "../components/SettingsCard";
import Cookies from "js-cookie";
import { useRouter } from "next/router";
import { setName, setToken } from "../redux/auth";
import { useDispatch } from "react-redux";
import { useSelector } from "react-redux";
import { RootState } from "../redux/store";
import Image from "next/image";

const theme = createTheme();

export default function ProfileApp() {
  const [username, setUsername] = useState("");
  const [nickname, setNickname] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");

  const router = useRouter();
  const dispatch = useDispatch();
  const authUserName = useSelector((state: RootState) => state.auth.name);

  const handleNicknameChange = (newNickname: string) => {
    setNickname(newNickname);
  };

  useEffect(() => {
    const cookie_jwtToken = Cookies.get("jwt_token");
    if (!cookie_jwtToken) {
      router.push(`/SignIn`);
    }
    else {
      const header = new Headers();
      header.append("authorization", cookie_jwtToken);
      fetch(`/api/chat/get_userinfo`, {
        method: "GET",
        headers: header,
      })
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          if (authUserName === undefined || authUserName === "") {
            dispatch(setToken(cookie_jwtToken));
            dispatch(setName(res.userinfo.username));
          }
          setUsername(res.userinfo.username);
          setNickname(res.userinfo.nickname);
          setPhone(res.userinfo.phone);
          setEmail(res.userinfo.email);
        }
        else {
          alert(res.info);
        }
      })
      .catch(() => {
        alert("Please sign in again.");
        Cookies.remove("jwt_token");
        router.push(`/SignIn`);
      });
    }
  }, [authUserName, dispatch, router]);

  const mainUser = {
    dt1: 32,
    dt2: 40,
    dt3: 50,
    userName: `${username}`,
    nickName: `${nickname}`,
    Phone: `${phone}`,
    Email: `${email}`,
  };

  const [viewportWidth, setViewportWidth] = useState(0);
  useEffect(() => {
    const handleResize = () => {
      setViewportWidth(window.innerWidth);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div>
      <ThemeProvider theme={theme}>
        <CssBaseline>
          {/* BACKGROUND */}
          <Grid container direction="column" sx={{ overflowX: "hidden" }}>
            <Grid item xs={12} md={6}>
              <Image
                alt="avatar"
                src="https://iris2.gettimely.com/images/default-cover-image.jpg"
                width={viewportWidth}
                height={viewportWidth * 0.15} // 设置高度为宽度的35%
                objectFit="cover"
                objectPosition="50% 50%"
              />
            </Grid>

            {/* COMPONENTS */}
            <Grid
              container
              direction={{ xs: "column", md: "row" }}
              spacing={3}
              sx={{
                position: "absolute",
                top: "15vh",
                bottom: "19vh",
                px: { xs: 0, md: 7 }
              }}
            >
              {/* PROFILE CARD */}
              <Grid item md={3}>
                <ProfileCard
                  nickname={mainUser.nickName}
                  username={mainUser.userName}
                  email={mainUser.Email}
                ></ProfileCard>
              </Grid>

              {/* SETTINGS CARD */}
              <Grid item md={9}>
                <SettingsCard
                  username={mainUser.userName}
                  nickname={mainUser.nickName}
                  phone={mainUser.Phone}
                  email={mainUser.Email}
                  onNicknameChange={handleNicknameChange}
                ></SettingsCard>
              </Grid>
            </Grid>
          </Grid>
        </CssBaseline>
      </ThemeProvider>
    </div>
  );
}