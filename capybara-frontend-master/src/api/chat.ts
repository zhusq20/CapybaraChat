import Cookies from "js-cookie";

export async function getWholeConversations() {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/conversation`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function getConversation(conversationId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/conversation?id=${conversationId}`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function addConversation(type: number, members: string[]) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    type,
    members,
  };
  const response = fetch(`/api/chat/conversation`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function addMessage(conversation: number, content: string, replyTo: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    conversation,
    content,
    reply_to: replyTo,
  };
  const response = fetch(`/api/chat/message`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function getWholeMessages(conversationId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/message?conversation=${conversationId}&after=0`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function getNewMessages(conversationId: number, lastMessageId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const response = fetch(`/api/chat/message?conversation=${conversationId}&after=${lastMessageId}`, {
    method: "GET",
    headers: header,
  });
  return response;
}

export async function readConversation(conversationId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    conversation: conversationId,
  };
  const response = fetch(`/api/chat/read_conversation`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}

export async function deleteMessage(messageId: number) {
  const header = new Headers();
  const jwtToken = Cookies.get("jwt_token");
  if (jwtToken) {
    header.append("authorization", jwtToken);
  }
  const requestBody = {
    message: messageId,
  };
  const response = fetch(`/api/chat/delete_message`, {
    method: "POST",
    headers: header,
    body: JSON.stringify(requestBody),
  });
  return response;
}