import React from "react";
import ProfileApp from "./ProfileApp";
import { useState, useEffect } from "react";

const ProfilePage = () => {
  const [isClient, setIsClient] = useState(false);
  useEffect(() => {
    setIsClient(true);
  }, []);
  return <div> {isClient && (<ProfileApp/>)} </div>;
};

export default ProfilePage;