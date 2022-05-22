import datetime
import time
import logging
import sempfiross
import config
import vk_api
import threading

sempfiross.log(False, "Script started")

def bots():
    sempfiross.log(False, "Started listening longpull server")
    sempfiross.debug_array['start_time'] = time.time()
    for event in sempfiross.MyVkLongPoll.listen(sempfiross.longpoll):
        try:
            if event.type == sempfiross.VkBotEventType.MESSAGE_NEW:
                log_msg = f'[MESSAGE] #{event.message.conversation_message_id} in peer {event.message.peer_id}, by id{event.message.from_id}'
                if event.message.action:
                    log_msg += (
                        ', action: '
                        + event.message.action["type"]
                        + ', user id in action: '
                        + str(event.message.action["member_id"])
                    )

                if event.message.text != "":
                    log_msg += f', text: "{event.message.text}"'
                if event.message.attachments:
                    atch = ', attachments: '
                    for i in event.message.attachments:
                        if i['type'] == "sticker":
                            atch += f"sticker_id{i[i['type']]['sticker_id']}"
                        elif i['type'] == "wall":
                            atch += i['type'] + str(i[i['type']]['from_id']) + \
                                "_" + str(i[i['type']]['id']) + " "
                        elif i['type'] == "link":
                            atch +=  i['type'] + " " + i[i['type']]['title'] + " "
                        else:
                            atch += i['type'] + str(i[i['type']]['owner_id']) + \
                                "_" + str(i[i['type']]['id']) + " "
                    log_msg += atch
                sempfiross.log(False, log_msg)
                sempfiross.debug_array['messages_get'] += 1
                if event.message.peer_id not in sempfiross.bot:
                    u = sempfiross.db.get_all_users()
                    if str(event.message.peer_id) not in u:
                        sempfiross.bot[user_id] = sempfiross.VkBot(event.message.peer_id)
                    else:
                        i = sempfiross.db.get_from_users(event.message.peer_id)
                        sempfiross.bot[event.message.peer_id] = sempfiross.VkBot(event.message.peer_id)
                sempfiross.bot[event.message.peer_id].get_message(event)
            elif event.type == sempfiross.VkBotEventType.WALL_POST_NEW:
                if event.object.post_type == "post":
                    sempfiross.log(False, f"[NEW_POST] id{event.object.id}")
                    users = sempfiross.db.get_all_users()
                    for i in users:
                        sempfiross.bot[int(i)].event("post", event.object)
                else:
                    sempfiross.log(False, f"[NEW_OFFER] id{event.object.id}")
            elif event.type == sempfiross.VkBotEventType.MESSAGE_DENY:
                sempfiross.log(False,
                    f"User {event.object.user_id} deny messages from that group")
                del sempfiross.bot[int(event.object.user_id)]
                sempfiross.db.delete_user(event.object.user_id)
            else:
                sempfiross.log(False, f"Event {str(event.type)} happend")
        except Exception as kek:
            sempfiross.log(True, f"Проблемы с ботом: {str(kek)}")
            sempfiross.debug_array['bot_warnings'] += 1
            continue


def midnight():
    while True:
        current_time = time.time()+10800
        if int(current_time) % 86400 == 0:
            sempfiross.log(False, "[EVENT_STARTED] \"Midnight\"")
            users = sempfiross.db.get_all_users()
            for i in users:
                sempfiross.bot[int(i)].event("midnight")
            sempfiross.log(False, "[EVENT_ENDED] \"Midnight\"")
            time.sleep(1)
        else:
            time.sleep(0.50)


sempfiross.SPAMMER_LIST = sempfiross.db.read_spammers()
tread_bots = threading.Thread(target=bots)
tread_midnight = threading.Thread(target=midnight, daemon=True)
tread_bots.start()
tread_midnight.start()