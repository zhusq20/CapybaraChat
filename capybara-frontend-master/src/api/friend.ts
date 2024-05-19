import Cookies from "js-cookie";
import { FriendRequest } from "./types";

export async function findFriend(username: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/find_user/${username}`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function addFriend(username: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    friendname: username,
  };
  const response = fetch(`/api/chat/add_friend`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function getFriends() {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/get_friend_list`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function getFriendRequests() {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/get_friend_request`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function handleFriendRequest(request: FriendRequest, isAccept: boolean) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const decision = isAccept ? "Accept" : "Reject";
  const requestBody = {
    friendname: request.username,
    decision,
  };
  const response = fetch(`/api/chat/process_friend_request`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function deleteFriend(username: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    friendname: username,
  };
  const response = fetch(`/api/chat/delete_friend`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function addFriendTag(tagFriend: string, tag: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    friend_list: [tagFriend],
    tag,
  };
  const response = fetch(`/api/chat/add_friend_tag`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function getTagFriends(tag: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/get_friend_list_by_tag/${tag}`, {
    method: "GET",
    headers: header,
  });
  return response;
}