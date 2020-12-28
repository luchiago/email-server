from typing import Optional

from database import find_user, search_in_database


def get_reply(message_id: Optional[int]):
    if message_id is not None:
        reply = (search_in_database("SELECT * FROM message WHERE id = ?", message_id),)
        return format_message(reply)
    return None


def format_message(message: tuple):
    reply = get_reply(message[5])
    json = {
        "id": message[0],
        "sender": find_user(id=message[1])[1],
        "receiver": find_user(id=message[2])[1],
        "subject": message[3],
        "body": message[4],
        "reply": reply,
    }
    return json


def format_messages(messages: list):
    json = []
    for message in messages:
        json.append(format_message(message))
    return json


def format_user(user: tuple):
    json = {"id": user[0], "user": user[1]}
    return json
