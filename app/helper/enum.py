from enum import Enum

class constant(str, Enum):
    ERROR = "error"
    SUCCESS = "success"

class typeFunction(str, Enum):
    CHAT_ROOM = "chat_room"
    MESSAGE = "message"
    USER = "user"

class typeUser(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ALL = "all"

class typeSendChatRoom(str, Enum):
    PRIVATE = "private"
    ROOM = "room"
    GROUP = "group"
    ALL = "all"

class typeChatRoom(str, Enum):
    CREATE = "create_chat_room"
    DELETE = "delete_chat_room"
    GET_ALL = "get_all_chat_room"
    JOIN = "join_chat_room"
    LEAVE = "leave_chat_room"
    ACTIVE = "active_chat_room"
    INACTIVE = "inactive_chat_room"
    

class typeMessage(str, Enum):
    CREATE = "create_message"
    DELETE = "delete_message"
    UPDATE = "update_message"
    GET_ALL = "get_all_message"