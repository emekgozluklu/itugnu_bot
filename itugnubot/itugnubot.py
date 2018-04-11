import json 
import requests
import time
import urllib
from DBitugnubot import DB
from cfg import cfg

DB = DB()

TOKEN = cfg['token']
URL = "https://api.telegram.org/bot{}/".format(TOKEN)



def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset = None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js
    

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_chat_administrators(chat):
	url = URL + "getChatAdministrators?chat_id={}".format(chat)
	js = get_json_from_url(url)
	admins=[]
	for admin in js["result"]:
		admins.append(admin["user"]["id"])
	return admins	


def timeout_user(chat, banner=None, username=None, until_date=None):
	u_id = DB.get_user_id(username)
	if username == 'emekgozluklu':
		send_message("Ya sen kime timeout atıyosun Emek Gözlüklü yer mi bunları", chat)
		return 0
	try:
		u_id = u_id[0]
	except:
		pass
	print(u_id)
	admins = get_chat_administrators(chat)
	unban_time = time.time() + int(until_date)
	print(admins)
	if banner in admins:
		url = URL + "restrictChatMember?user_id={}&chat_id={}&until_date={}&can_send_messages=False".format(u_id, chat, unban_time)
		send_message("{}, {}saniyeliğine banlandın.".format(username, until_date), chat)
		get_url(url)
	else:
		send_message("Yalnızca adminler timeout atabilir.", chat)



def send_message(text, chat_id, parse_mode=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if parse_mode:
        url += "&parse_mode={}".format(parse_mode)
    get_url(url)
    
def print_events(chat):
	events = DB.get_events()
	text = "Etkinlikler: \n\n\n"
	for event in events:
		text += "{:<40} | {:>20}\n\n".format(event[0], event[1]) 
	send_message(text, chat)

def print_misyon(chat):
	text = cfg['misyon']
	send_message(text, chat, parse_mode='HTML')

def print_help(chat):
	text = cfg['help']
	send_message(text, chat, parse_mode='HTML')

def take_event_date(event_name, chat, last_update_id):
	while True:
		ups = get_updates(last_update_id+2)
		if ups["result"]:
			for date in ups["result"]:
				event_date = date["message"]["text"]
			try:	
				DB.add_event(event_name, event_date)
				send_message("Event eklendi.", chat)
				print_events(chat)
				return None
			except:
				send_message("Event Eklenemedi",chat)
				return None
		else:
			time.sleep(0.5)

def take_event_name(chat, last_update_id):
	send_message("Event'in adı nedir?",chat)
	while True:
		ups = get_updates(last_update_id+1)
		if ups["result"]:
			for event_name in ups["result"]:
				event_name = event_name["message"]["text"]
				send_message("Tarih? (YYYY/AA/GG)", chat)
				take_event_date(event_name, chat, last_update_id)
				return event_name
		else:
			time.sleep(0.5)


def take_password(chat, last_update_id):
	message = "Parolayı yazınız."
	send_message(message, chat)
	while True:
		ups = get_updates(last_update_id)
		if ups:
			for password in ups["result"]:
				if password["message"]["text"] == cfg["password"]:
					take_event_name(chat, last_update_id)
					return None
	
				else:
					send_message("Yanlış. Başa döndük.", chat)
					return None
		else:
			time.sleep(0.5)	

def event_ekle(update, chat, last_update_id):
	if update["message"]["chat"]["type"] == "private":
		take_password(chat, last_update_id)
	else:
		message = "Yalnızca kişisel mesaj yoluyla etkinlik ekleyebilirsiniz."
		send_message(message, chat)
		return None



def itugnubot(updates, last_update_id):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            sender = update["message"]["from"]["id"]
            username = update["message"]["from"]["username"]
            DB.add_user(sender, username)
        except KeyError:
            continue

        if text[0] == "/":
        	if text == "/elif":
        		send_message("elif bye", chat_id)
        	if text == "/events" or text == "/events@itugnu_bot":
                print_events(chat)
            elif text == "/misyon" or text == "/misyon@itugnu_bot":
                print_misyon(chat)
            elif text == "/addevent" or text == "/addevent@itugnu_bot":
            	event_ekle(update, chat, last_update_id)
            elif text=="/help" or text=="/help@itugnu_bot":
            	print_help(chat)
            elif text.split(" ")[0] == "/timeout" or text.split(" ")[0]=="/timeout@itugnu_bot":
            	try:
            		ban_time = text.split(" ")[2]
            		user = text.split(" ")[1]
            		timeout_user(chat=chat, banner=sender, username=user, until_date=ban_time)
            	except IndexError:
            		send_message("Eksik parametre girdiniz. Doğru kullanım '/timeout username süre'", chat)   	
        else:
            continue
def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            itugnubot(updates, last_update_id)
        time.sleep(0.5)

if __name__ == "__main__":
	DB.setup()
	main()


