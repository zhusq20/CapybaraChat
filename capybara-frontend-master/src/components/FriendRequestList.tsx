import React from "react";
import { List, ListItem, ListItemIcon, ListItemText, Avatar } from "@material-ui/core";
import md5 from "md5";
import { FriendRequest } from "../api/types";
import "./FriendRequestList.module.css";

interface FriendRequestListProps {
  friendRequests: FriendRequest[];
}

export const FriendRequestList: React.FC<FriendRequestListProps> = ({ friendRequests }) => {
  return (
    <List>
      {friendRequests.map((request) => {
        const hash = md5(request.email.trim().toLowerCase());
        const gravatarUrl = `https://www.gravatar.com/avatar/${hash}?d=identicon&s=150`;
        const requestStatus = request.status === "Pending" ? "Pending" : request.status === "Accept" ? "Accepted" : "Rejected";
        const requestRole = request.role === "receiver" ? "Receiver" : "Sender";
        return (
          <ListItem button key={request.username}>
            <ListItemIcon>
              <Avatar alt={request.username} src={gravatarUrl} />
            </ListItemIcon>
            <ListItemText primary={`${request.nickname} (${request.username})`} secondary={`Status: ${requestStatus}, Role: ${requestRole}, Time: ${request.timestamp}`} />
          </ListItem>
        );
      })}
    </List>
  );
};
