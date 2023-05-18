#pylint:disable=W0703
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from decouple import config
import logging, sys
import time
import os
import threading
import subprocess

# variables

API_ID = config("API_ID", default=24748535, cast=int)
API_HASH = config("API_HASH", default="7600412f97699a960c218fa1240a0822")
BOT_TOKEN = config("BOT_TOKEN", default="5854415227:AAHS8_8P2DC_hZokbgXijqyjZUaNjG-Qgdo")
SESSION = config("SESSION", default="AQBhPFxrmxMjobupLs54ZaLmwCv3IDGjiSOZS9CSoUenH-DfNUjZnXamwZ5vabZMAeJDaKM-gaCpf0_fWBiuAPBh1CWno2ICXBkpLmUd6BADn3kx3cjAOCbranR1BntU46ryLdK-qf08rELhYIT7LQnnj-U6HQ3qaOkfethlR7eweDNOZepijU0SEhxO-qfJiGT4uKwNdSxBKlNuSizYD29j3is7ceEl0K-SMvVo3h3OmG8UUzNh-QkSC6LsvYPdUc1dxOsvd4VTeqQiJZcarnPRegtutLAqTOAX5zIKlcvR9T1YspzpW3d2xHJN9KHIZ0hvZo0UY2XGrtDEZDJvnAxnAAAAAVbqnxYA")

bot = Client("mybot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) 

if SESSION is not None:
    acc = Client(
    session_name=SESSION, 
    api_hash=API_HASH, 
    api_id=API_ID)
    
    try:
            acc.start()
    except BaseException:
            print("Userbot Error ! Have you added SESSION while deploying??")
            sys.exit(1)
        
else: acc = None

# download status
def downstatus(statusfile,message):
	while True:
		if os.path.exists(statusfile):
			break

	time.sleep(3)      
	while os.path.exists(statusfile):
		with open(statusfile,"r") as downread:
			txt = downread.read()
		try:
			bot.edit_message_text(message.chat.id, message.message_id, f"__Downloaded__ : **{txt}**")
			time.sleep(10)
		except:
			time.sleep(5)


# upload status
def upstatus(statusfile,message):
	while True:
		if os.path.exists(statusfile):
			break

	time.sleep(3)      
	while os.path.exists(statusfile):
		with open(statusfile,"r") as upread:
			txt = upread.read()
		try:
			bot.edit_message_text(message.chat.id, message.message_id, f"__Uploaded__ : **{txt}**")
			time.sleep(10)
		except:
			time.sleep(5)


# progress writter
def progress(current, total, message, type):
	with open(f'{message.chat.id}{message.message_id}{type}status.txt',"w") as fileup:
		fileup.write(f"{current * 100 / total:.1f}%")


# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
	bot.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by it's post link__",
	reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton("🌐 Source Code", url="https://github.com/bipinkrish/Save-Restricted-Bot")]]), reply_to_message_id=message.message_id)


@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):

	# joining chats
	if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

		if acc is None:
			bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.message_id)
			return

		try:
			try: acc.join_chat(message.text)
			except Exception as e: 
				bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.message_id)
				return
			bot.send_message(message.chat.id,"**Chat Joined**", reply_to_message_id=message.message_id)
		except UserAlreadyParticipant:
			bot.send_message(message.chat.id,"**Chat alredy Joined**", reply_to_message_id=message.message_id)
		except InviteHashExpired:
			bot.send_message(message.chat.id,"**Invalid Link**", reply_to_message_id=message.message_id)
	
	# getting message
	elif "https://t.me/" in message.text:

		datas = message.text.split("/")
		msgid = int(datas[-1].split("?")[0])

		# private
		if "https://t.me/c/" in message.text:
			chatid = int("-100" + datas[-2])
			if acc is None:
				bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.message_id)
				return
			try: handle_private(message,chatid,msgid)
			except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.message_id)
		
		# public
		else:
			username = datas[-2]
			msg  = bot.get_messages(username,msgid)
			try: bot.copy_message(message.chat.id, msg.chat.id, msg.id)
			except:
				if acc is None:
					bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.message_id)
					return
				try: handle_private(message,username,msgid)
				except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.message_id)
	

# handle private
def handle_private(message,chatid,msgid):
		msg  = acc.get_messages(chatid,msgid)

		if "text" in str(msg):
			bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.message_id)
			return

		smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.message_id)
		dosta = threading.Thread(target=lambda:downstatus(f'{message.chat.id}{message.message_id}downstatus.txt',smsg),daemon=True)
		dosta.start()
		file = acc.download_media(msg, progress=progress, progress_args=[message,"down"])
		os.remove(f'{message.chat.id}{message.message_id}downstatus.txt')

		upsta = threading.Thread(target=lambda:upstatus(f'{message.chat.id}{message.message_id}upstatus.txt',smsg),daemon=True)
		upsta.start()
		
		if "Document" in str(msg):
			try:
				thumb = acc.download_media(msg.document.thumbs[0].file_id)
			except: thumb = None
			
			bot.send_document(message.chat.id, file, thumb=None, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id, progress=progress, progress_args=[message,"up"])
			if thumb != None: os.remove(thumb)

		elif "Video" in str(msg):
			try: 
				thumb = acc.download_media(msg.video.thumbs[0].file_id)
				if not os.path.isdir(Config.DOWNLOAD_LOCATION): os.makedirs(Config.DOWNLOAD_LOCATION)
				video_input_path=file
				img_output_path = Config.DOWNLOAD_LOCATION + \
				"/" + message.chat.id + "/" + message.message_id + "thumb.jpg"
				subprocess.call(['ffmpeg', '-i', video_input_path, '-ss', '00:00:02.000', '-vframes', '1', img_output_path])
				thumb=img_output_path
				"""width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                if tg_send_type == "vm":
                    height = width
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb).convert(
                    "RGB").save(thumb)
                img = Image.open(thumb)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                if tg_send_type == "file":
                    img.resize((320, height))
                else:
                    img.resize((90, height))
                img.save(thumb, "JPEG")"""
			except: thumb = None

			bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id, progress=progress, progress_args=[message,"up"])
			if thumb != None: os.remove(thumb)

		elif "Animation" in str(msg):
			bot.send_animation(message.chat.id, file, reply_to_message_id=message.message_id)
			   
		elif "Sticker" in str(msg):
			bot.send_sticker(message.chat.id, file, reply_to_message_id=message.message_id)

		elif "Voice" in str(msg):
			bot.send_voice(message.chat.id, file, caption=msg.caption, thumb=thumb, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id, progress=progress, progress_args=[message,"up"])

		elif "Audio" in str(msg):
			try:
				thumb = acc.download_media(msg.audio.thumbs[0].file_id)
			except: thumb = None
				
			bot.send_audio(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id, progress=progress, progress_args=[message,"up"])   
			if thumb != None: os.remove(thumb)

		elif "Photo" in str(msg):
			bot.send_photo(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.message_id)

		os.remove(file)
		if os.path.exists(img_output_path): os.remove(img_output_path)
		if os.path.exists(f'{message.chat.id}{message.message_id}upstatus.txt'): os.remove(f'{message.chat.id}{message.message_id}upstatus.txt')
		bot.delete_messages(message.chat.id,[smsg.message_id])


# infinty polling
bot.run()