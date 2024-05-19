import Dexie from "dexie";
import { Friend, FriendRequest, Conversation, ConversationMessage, Message, Group, GroupRequest } from "./types";
import { getFriends, getFriendRequests } from "./friend";
import { getWholeConversations, getWholeMessages, getNewMessages, getConversation, readConversation, deleteMessage } from "./chat";
import { getWholeGroups, addManager, deleteManager, changeMaster, removeMember, getWholeGroupRequests, getGroup } from "../api/group";

export function updateUnreadFriendRequestsCounts(friendRequests: FriendRequest[]) {
  const newRequests = friendRequests.filter((request) => request.status === "Pending");
  const newRequestsCount = newRequests.length;
  return newRequestsCount;
}

export function updateUnreadGroupRequestsCounts(groupRequests: GroupRequest[]) {
  const newRequests = groupRequests.filter((request) => request.status === "Pending");
  const newRequestsCount = newRequests.length;
  return newRequestsCount;
}

export class CachedFriends extends Dexie {
  friends: Dexie.Table<Friend, number>;
  friendRequests: Dexie.Table<FriendRequest, number>;

  constructor() {
    super("CachedFriends");
    this.version(1).stores({
      friends: "&username, email, tag",
      friendRequests: "&username, nickname, email, status, role, timestamp",
    });
    this.friends = this.table("friends");
    this.friendRequests = this.table("friendRequests");
  }

  async clearCachedData() {
    await this.friends.clear();
    await this.friendRequests.clear();
  }

  async pullFriends() {
    try {
      const res = await getFriends();
      const data = await res.json();
      if (Number(data.code) === 0) {
        this.friends.clear();
        this.friends.bulkPut(data.friends);
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async pullFriendRequests() {
    let newRequests: FriendRequest[] = [];
    let unreadCount = 0;
    try {
      const res = await getFriendRequests();
      const data = await res.json();
      if (Number(data.code) === 0) {
        newRequests = data.friends;
        const count = updateUnreadFriendRequestsCounts(newRequests);
        unreadCount = count;
        this.friendRequests.clear();
        this.friendRequests.bulkPut(data.friends);
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
    return unreadCount;
  }

  updateUnreadFriendRequestsCounts(friendRequests: FriendRequest[]) {
    const newRequests = friendRequests.filter((request) => request.status === "Pending");
    const newRequestsCount = newRequests.length;
    return newRequestsCount;
  }

  async getFriendsRequests() {
    const friendRequests = await this.friendRequests.toArray();
    return friendRequests;
  }
}

export class CachedConversations extends Dexie {
  conversations: Dexie.Table<Conversation, number>;
  conversationMessages: Dexie.Table<ConversationMessage, number>;
  groups: Dexie.Table<Group, number>;
  groupRequests: Dexie.Table<GroupRequest, number>;

  constructor() {
    super("CachedConversations");
    this.version(1).stores({
      conversations: "&id, type, members",
      conversationMessages: "&id",
      groups: "&id, name, conversation, master, manager, notice",
      groupRequests: "&group, sender, nickname, email, status, timestamp",
    });
    this.conversations = this.table("conversations");
    this.conversationMessages = this.table("conversationMessages");
    this.groups = this.table("groups");
    this.groupRequests = this.table("groupRequests");
  }

  async clearCachedData() {
    await this.conversations.clear();
    await this.conversationMessages.clear();
    await this.groups.clear();
    await this.groupRequests.clear();
  }

  async pullWholeConversations() {
    try {
      const res = await getWholeConversations();
      const data = await res.json();
      if (Number(data.code) === 0) {
        this.conversations.clear();
        this.conversations.bulkPut(data.conversations);
        return data.conversations;
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async pullWholeConversationMessages() {
    const conversations = await this.pullWholeConversations();
    const conversationUnreadCounts: { [key: number]: number } = {};
    for (const conversation of conversations) {
      try {
        const res = await getWholeMessages(conversation.id);
        const data = await res.json();
        if (Number(data.code) === 0) {
          this.conversationMessages.put({
            id: conversation.id,
            messages: data.messages,
          });
          conversationUnreadCounts[conversation.id] = data.unread;
        }
        else {
          alert(data.info);
        }
      }
      catch (error: any) {
        alert(error.info);
      }
    }
    return conversationUnreadCounts;
  }

  async addNewConversations(conversation: Conversation) {
    await this.conversations.put(conversation);
  }

  async addNewMessage(conversationId: number, message: Message) {
    const conversationMessage = await this.conversationMessages.get(conversationId);
    if (conversationMessage) {
      conversationMessage.messages.push(message);
      await this.conversationMessages.put(conversationMessage);
      return conversationMessage.messages;
    }
    else {
      const newConversation: ConversationMessage = {
        id: conversationId,
        messages: [message],
      };
      await this.conversationMessages.put(newConversation);
      return [message];
    }
  }

  async pullNewMessages(conversationId: number) {
    const conversationExists = await this.conversations.get(conversationId);
    if (!conversationExists) {
      try {
        const res = await getConversation(conversationId);
        const data = await res.json();
        if (Number(data.code) === 0) {
          await this.conversations.put(data.conversations[0]);
        }
        else {
          alert(data.info);
        }
      }
      catch (error: any) {
        alert(error.info);
      }
    }
    const conversationMessage = await this.conversationMessages.get(conversationId);
    if (conversationMessage) {
      const lastMessageId = conversationMessage.messages[conversationMessage.messages.length - 1].id;
      try {
        const res = await getNewMessages(conversationId, lastMessageId);
        const data = await res.json();
        if (Number(data.code) === 0) {
          for (const message of data.messages) {
            conversationMessage.messages.push(message);
            if (message.reply_to !== -1) {
              const index = conversationMessage.messages.findIndex(tempMessage => tempMessage.id === message.reply_to);
              if (index !== -1) {
                conversationMessage.messages[index].reply_by += 1;
              }
            }
          }
          await this.conversationMessages.put(conversationMessage);
          return data.unread;
        }
        else {
          alert(data.info);
        }
      }
      catch (error: any) {
        alert(error.info);
      }
    }
    else {
      try {
        const res = await getNewMessages(conversationId, -1);
        const data = await res.json();
        if (Number(data.code) === 0) {
          const newConversation: ConversationMessage = {
            id: conversationId,
            messages: data.messages,
          };
          await this.conversationMessages.put(newConversation);
          return data.unread;
        }
        else {
          alert(data.info);
        }
      }
      catch (error: any) {
        alert(error.info);
      }
    }
  }

  async addReplyByNumber(conversationId: number, messageId: number) {
    const conversationMessage = await this.conversationMessages.get(conversationId);
    if (conversationMessage) {
      const message = conversationMessage.messages.find(message => message.id === messageId);
      if (message) {
        message.reply_by += 1;
        await this.conversationMessages.put(conversationMessage);
        return conversationMessage.messages;
      }
    }
  }

  async sendReadConversation(conversationId: number, username: string) {
    const conversationMessage = await this.conversationMessages.get(conversationId);
    try {
      const res = await readConversation(conversationId);
      const data = await res.json();
      if (Number(data.code) === 0) {
        if (conversationMessage) {
          for (const message of conversationMessage.messages) {
            if (message.read.includes(username) === false) {
              message.read.push(username);
            }
          }
          await this.conversationMessages.put(conversationMessage);
          return conversationMessage.messages;
        }
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async processReadConversation(conversationId: number, username: string) {
    const conversationMessage = await this.conversationMessages.get(conversationId);
    if (conversationMessage) {
      for (const message of conversationMessage.messages) {
        if (message.read.includes(username) === false) {
          message.read.push(username);
        }
      }
      await this.conversationMessages.put(conversationMessage);
      return conversationMessage.messages;
    }
  }

  async getMessages(conversationId: number) {
    const conversationMessage = await this.conversationMessages.get(conversationId);
    if (conversationMessage) {
      return conversationMessage.messages;
    }
    else {
      return [];
    }
  }

  async getMessagesByTime(conversationId: number, time: string) {
    const conversationMessage = await this.conversationMessages.get(conversationId);
    if (conversationMessage) {
      const targetDate = new Date(time);
      const targetYear = targetDate.getFullYear();
      const targetMonth = targetDate.getMonth();
      const targetDay = targetDate.getDate();
      const filteredMessages = conversationMessage.messages.filter(message => {
        const messageDate  = new Date(message.timestamp);
        const messageYear = messageDate.getFullYear();
        const messageMonth = messageDate.getMonth();
        const messageDay = messageDate.getDate();
        return messageYear === targetYear && messageMonth === targetMonth && messageDay === targetDay;
      });
      return filteredMessages;
    }
    else {
      return [];
    }
}

  async getMessagesByMember(conversationId: number, member: string) {
    const conversationMessage = await this.conversationMessages.get(conversationId);
    if (conversationMessage) {
      const filteredMessages = conversationMessage.messages.filter(message => message.sender === member);
      return filteredMessages;
    }
    else {
      return [];
    }
  }

  async deleteMessage(conversationId: number, messageId: number) {
    deleteMessage(messageId)
      .then((res) => res.json())
      .then((res) => {
        if (Number(res.code) === 0) {
          alert("You have deleted the message.");
        }
        else {
          alert(res.info);
        }
      })
      .catch((error) => {
        alert(error.info);
      });
    const conversationMessage = await this.conversationMessages.get(conversationId);
    if (conversationMessage) {
      const filteredMessages = conversationMessage.messages.filter(message => message.id !== messageId);
      conversationMessage.messages = filteredMessages;
      await this.conversationMessages.put(conversationMessage);
      return filteredMessages;
    }
  }

  async addNewGroup(group: Group) {
    await this.groups.put(group);
  }

  async getGroups() {
    const groups = await this.groups.toArray();
    return groups;
  }

  async pullGroups() {
    try {
      const res = await getWholeGroups();
      const data = await res.json();
      if (Number(data.code) === 0) {
        this.groups.clear();
        this.groups.bulkPut(data.groups);
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async addNewManager(groupId: number, manager: string) {
    try {
      const res = await addManager(groupId, manager);
      const data = await res.json();
      if (Number(data.code) === 0) {
        const updatedGroup = await this.groups.get(groupId);
        if (updatedGroup) {
          updatedGroup.manager.push(manager);
          await this.groups.put(updatedGroup);
        }
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async deleteManager(groupId: number, manager: string) {
    try {
      const res = await deleteManager(groupId, manager);
      const data = await res.json();
      if (Number(data.code) === 0) {
        const updatedGroup = await this.groups.get(groupId);
        if (updatedGroup) {
          updatedGroup.manager = updatedGroup.manager.filter((m) => m !== manager);
          await this.groups.put(updatedGroup);
        }
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async changeMaster(groupId: number, master: string) {
    try {
      const res = await changeMaster(groupId, master);
      const data = await res.json();
      if (Number(data.code) === 0) {
        const updatedGroup = await this.groups.get(groupId);
        if (updatedGroup) {
          updatedGroup.master = master;
          await this.groups.put(updatedGroup);
        }
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async removeMember(groupId: number, member: string) {
    try {
      const res = await removeMember(groupId, member);
      const data = await res.json();
      if (Number(data.code) === 0) {
        const group = await this.groups.get(groupId);
        if (group) {
          const updatedConversation = await this.conversations.get(group.conversation);
          if (updatedConversation) {
            updatedConversation.members = updatedConversation.members.filter((m) => m !== member);
            await this.conversations.put(updatedConversation);
          }
        }
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async leaveGroup(groupId: number) {
    const group = await this.groups.get(groupId);
    if (group) {
      const updatedConversation = await this.conversations
        .filter((conversation) => conversation.id !== group.conversation)
        .toArray();
      await this.conversations.clear();
      await this.conversations.bulkPut(updatedConversation);
    }
  }

  async pullGroupRequests() {
    let newRequests: GroupRequest[] = [];
    let unreadCount = 0;
    try {
      const res = await getWholeGroupRequests();
      const data = await res.json();
      if (Number(data.code) === 0) {
        newRequests = data.requests;
        const count = updateUnreadGroupRequestsCounts(newRequests);
        unreadCount = count;
        this.groupRequests.clear();
        this.groupRequests.bulkPut(data.requests);
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
    return unreadCount;
  }

  async addNewMember(conversationId: number, member: string) {
    const conversation = await this.conversations.get(conversationId);
    if (conversation) {
      conversation.members.push(member);
      await this.conversations.put(conversation);
    }
  }

  async pullNewConversation(conversationId: number) {
    try {
      const res = await getConversation(conversationId);
      const data = await res.json();
      if (Number(data.code) === 0) {
        await this.conversations.put(data.conversations[0]);
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }

  async pullNewGroup(groupId: number) {
    try {
      const res = await getGroup(groupId);
      const data = await res.json();
      if (Number(data.code) === 0) {
        await this.groups.put(data.groups[0]);
        return data.groups[0].conversation;
      }
      else {
        alert(data.info);
      }
    }
    catch (error: any) {
      alert(error.info);
    }
  }
}

export const friendsDB = new CachedFriends();
export const conversationsDB = new CachedConversations();