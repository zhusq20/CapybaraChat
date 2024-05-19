import Cookies from "js-cookie";

export async function addGroup(groupName: string, members: string[]) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    name: groupName,
    members,
  };
  const response = fetch(`/api/chat/group`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function getWholeGroups() {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/group`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function getGroup(groupId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/group?id=${groupId}`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function addManager(groupId: number, manager: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    group: groupId,
    add: [manager],
    delete: [],
  };
  const response = fetch(`/api/chat/manager`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function deleteManager(groupId: number, manager: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    group: groupId,
    add: [],
    delete: [manager],
  };
  const response = fetch(`/api/chat/manager`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function changeMaster(groupId: number, master: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    group: groupId,
    master
  };
  const response = fetch(`/api/chat/master`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function removeMember(groupId: number, member: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    group: groupId,
    remove: [member],
  };
  const response = fetch(`/api/chat/remove_member`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function getGroupNotice(groupId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/group_notice?group=${groupId}`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function addGroupNotice(groupId: number, content: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    group: groupId,
    content,
  };
  const response = fetch(`/api/chat/group_notice`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function leaveGroup(groupId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    group: groupId,
  };
  const response = fetch(`/api/chat/leave_group`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function inviteFriend(groupId: number, friend: string) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    group: groupId,
    friend,
  };
  const response = fetch(`/api/chat/invite`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function getWholeGroupRequests() {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/group_request`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function getGroupRequests(groupId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/group_request?group=${groupId}`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function handleGroupRequest(groupId: number, user: string, isAccept: boolean) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const decision = isAccept ? "Accept" : "Reject";
  const requestBody = {
    group: groupId,
    user,
    decision,
  };
  const response = fetch(`/api/chat/process_group_request`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}