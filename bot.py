#!/usr/bin/env python3


"""Importing"""
# Importing External Packages
from pyrogram import (
    Client,
    filters
)
from pyrogram.types import (
    Update,
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from pyrogram.errors.exceptions.bad_request_400 import (
    PeerIdInvalid,
    UserNotParticipant,
    ChannelPrivate,
    ChatIdInvalid,
    ChannelInvalid
)
from pymongo import MongoClient
import requests
from pyrogram.errors import MediaEmpty, BadRequest
import json
from urllib.parse import quote_plus
from collections import Counter
from bs4 import BeautifulSoup
from unidecode import unidecode

from typing import List


# Importing Credentials & Required Data
try:
    from testexp.config import *
except ModuleNotFoundError:
    from config import *

# Importing built-in module
from re import match, search


"""Connecting to Bot"""
app = Client(
    session_name = "RequestTrackerBot",
    api_id = Config.API_ID,
    api_hash = Config.API_HASH,
    bot_token = Config.BOT_TOKEN
)


'''Connecting To Database'''
mongo_client = MongoClient(Config.MONGO_STR)
db_bot = mongo_client['RequestTrackerBot']
collection_ID = db_bot['channelGroupID']

'''Admin'''
NANO = [1852823985]

# Check if the user is an admin
async def is_admin(user_id):
    return user_id in NANO

# Regular Expression for #request
requestRegex = "#[rR][eE][qQ][uU][eE][sS][tT] "


"""Handlers""" 

# Start Handler
@app.on_message(filters.private & filters.command("start"))
async def start_handler(bot: Update, msg: Message):
    botInfo = await bot.get_me()
    await bot.send_photo(
        chat_id=msg.chat.id,
        photo="https://graph.org/file/80a46dfbbc510295212ae.jpg", 
        caption="<b>Hi, I am Request Tracker Bot🤖.\nIf you haven't added me to your Group & Channel yet, ➕add me now.\n\nHow to Use me?</b>\n\t1. Add me to your Group & Channel.\n\t2. Make me admin in both the Channel & Group.\n\t3. Give me permission to Post, Edit & Delete Messages.\n\t4. Now send Group ID & Channel ID in this format <code>/add GroupID ChannelID</code>.\nNow the Bot is ready to be used.\n\n<b>😊Join @AJPyroVerse & @AJPyroVerseGroup for more awesome 🤖bots like this.</b>",
        parse_mode="html",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕Add me to your Group.",
                        url=f"https://telegram.me/{botInfo.username}?startgroup=true"
                    )
                ]
            ]
        ),
    )

# Help Handler
@app.on_message(filters.private & filters.command("help"))
async def help_handler(bot: Update, msg: Message):
    help_message = """
    <b>Commands:</b>
    /start - Start using the bot.
    /help - Get help and usage instructions.
    /add GroupID ChannelID - Add your Group and Channel IDs to the bot's database.
    /remove GroupID - Remove your Group and Channel IDs from the bot's database.
    /imdb MovieName - Search for a movie on IMDb.
    
    <b>How to Use:</b>
    1. Add the bot to your Group and Channel.
    2. Make the bot admin in both the Channel and Group.
    3. Give the bot permission to Post, Edit, and Delete Messages.
    4. Use /add to add your GroupID and ChannelID to the bot.
    5. Use /remove to remove your GroupID and ChannelID from the bot.
    6. Use /imdb followed by a movie name to search for movies on IMDb.
    
    <b>😊Join @NanoSTestingArea for more awesome 🤖bots like this.</b>
    """

    await bot.send_message(
        chat_id=msg.chat.id,
        text=help_message,
        parse_mode="html",
    )


# return group id when bot is added to group
@app.on_message(filters.new_chat_members)
async def chatHandler(bot:Update, msg:Message):
    if msg.new_chat_members[0].is_self: # If bot is added
        await msg.reply_text(
            f"<b>Hey😁, Your Group ID is <code>{msg.chat.id}</code></b>",
            parse_mode = "html"
        )
    return

# return channel id when message/post from channel is forwarded
@app.on_message(filters.forwarded & filters.private)
async def forwardedHandler(bot:Update, msg:Message):
    forwardInfo = msg.forward_from_chat
    if forwardInfo.type == "channel":   # If message forwarded from channel
        await msg.reply_text(
            f"<b>Hey😁, Your Channel ID is <code>{forwardInfo.id}</code>\n\n😊Join @AJPyroVerse & @AJPyroVerseGroup for getting more awesome 🤖bots like this.</b>",
            parse_mode = "html"
        )
    return

@app.on_message(filters.command("imdb"))
async def imdb_search(_, message):
    msg = await message.reply("🔍 Searching......")
    if len(message.command) < 2:
        await msg.edit("Give me a query.")
        return
    q = message.text.split(None, 1)[1]
    k = requests.get(f"https://api.safone.me/tmdb?query={q}%20&limit=10").json()
    im = k["results"]
    if not im:
        await msg.edit("Refine your search 🔍.")
        return
    btn = [
        [
            InlineKeyboardButton(
                text=f"{movie.get('title')} - {movie.get('releaseDate').split('-')[0]}",
                callback_data=f"imdb#{movie.get('id')}",
            )
        ]
        for movie in im
    ]
    await msg.edit('💝 Here is what I found on IMDb.', reply_markup=InlineKeyboardMarkup(btn))

@app.on_callback_query(filters.regex(pattern=r"imdb#(.*)"))
async def imdb_callback(_, query):
    msg = await query.message.edit_text("🔍 Searching.........")
    id = int(query.data.split("#")[1])
    tmdb = requests.get(f"https://api.safone.me/tmdb?query=%20&tmdb_id={id}").json()
    imdb = tmdb["results"][0]
    text = f"📀 Title : {imdb['title']}\n\n"
    text += f"⏱️ Runtime : {imdb['runtime']} minutes\n"
    text += f"🌟 Rating : {imdb['rating']}/10\n"
    text += f"🗳️ ID : {imdb['id']}\n\n"
    text += f"📆 Release Date : {imdb['releaseDate']}\n"
    text += f"🎭 Genre : \n"
    for x in imdb['genres']:
        text += f"{x}, "
    text = text[:-2] + '\n'
    text += f"🥂 Popularity : {imdb['popularity']}\n\n"
    text += f"⚡ Status : {imdb['status']}\n"
    text += f"🎫 IMDb ID : {imdb['imdbId']}\n\n"
    text += f"🗒  Plot : {imdb['overview']}"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🎟️ IMDb", url=imdb["imdbLink"])]])
    try:
        if imdb["poster"]:
            await query.message.reply_photo(photo=imdb["poster"], caption=text, reply_markup=buttons)
        else:
            await query.message.reply_text(text, reply_markup=buttons)
    except (MediaEmpty, BadRequest):
        await query.message.reply_text(text, reply_markup=buttons)
    except Exception as a:
        await query.message.reply_text("Something went wrong.")
        print(a)
    await msg.delete()  

# /add handler to add group id & channel id with database
@app.on_message(filters.command("add"))
async def groupChannelIDHandler(bot: Client, msg: Message):
    if msg.from_user.id not in NANO:
        await msg.reply_text(
            "<b>You are not authorized to use this command. Contact: @SexyNano</b>",
            parse_mode="html"
        )
        return

    message = msg.text.split(" ")
    if len(message) == 3:   # If command is valid
        _, groupID, channelID = message
        try:
            int(groupID)
            int(channelID)
        except ValueError:  # If Ids are not integer type
            await msg.reply_text(
                "<b>Group ID & Channel ID should be integer type😒.</b>",
                parse_mode="html"
            )
        else:   # If Ids are integer type
            documents = collection_ID.find()
            for document in documents:
                try:
                    document[groupID]
                except KeyError:
                    pass
                else:   # If group id found in database
                    await msg.reply_text(
                        "<b>Your Group ID already Added.</b>",
                        parse_mode="html"
                    )
                    break
                for record in document:
                    if record == "_id":
                        continue
                    else:
                        if document[record][0] == channelID:    # If channel id found in database
                            await msg.reply_text(
                                "<b>Your Channel ID already Added.</b>",
                                parse_mode="html"
                            )
                            break
            else:   # If group id & channel not found in db
                try:
                    botSelfGroup = await bot.get_chat_member(int(groupID), 'me')
                except (PeerIdInvalid, ValueError):   # If given group id is invalid
                    await msg.reply_text(
                        "<b>😒Group ID is wrong.\n\n😊Join @AJPyroVerse & @AJPyroVerseGroup for getting more awesome 🤖bots like this.</b>",
                        parse_mode="html"
                    )
                except UserNotParticipant:  # If bot is not in group
                    await msg.reply_text(
                        "<b>😁Add me in group and make me admin, then use /add.\n\n😊Join @AJPyroVerse & @AJPyroVerseGroup for getting more awesome 🤖bots like this.</b>",
                        parse_mode="html"
                    )
                else:
                    if botSelfGroup.status != "administrator":  # If bot is not admin in group
                        await msg.reply_text(
                            "<b>🥲Make me admin in Group, Then add use /add.\n\n😊Join @AJPyroVerse & @AJPyroVerseGroup for getting more awesome 🤖bots like this.</b>",
                            parse_mode="html"
                        )
                    else:   # If bot is admin in group
                        try:
                            botSelfChannel = await bot.get_chat_member(int(channelID), 'me')
                        except (UserNotParticipant, ChannelPrivate):    # If bot not in channel
                            await msg.reply_text(
                                "<b>😁Add me in Channel and make me admin, then use /add.</b>",
                                parse_mode="html"
                            )
                        except (ChatIdInvalid, ChannelInvalid): # If given channel id is invalid
                            await msg.reply_text(
                                "<b>😒Channel ID is wrong.\n\n😊Join @AJPyroVerse & @AJPyroVerseGroup for getting more awesome 🤖bots like this.</b>",
                                parse_mode="html"
                            )
                        else:
                            if not (botSelfChannel.can_post_messages and botSelfChannel.can_edit_messages and botSelfChannel.can_delete_messages):  # If bot has not enough permissions
                                await msg.reply_text(
                                    "<b>🥲Make sure to give Permissions like Post Messages, Edit Messages & Delete Messages.</b>",
                                    parse_mode="html"
                                )
                            else:   # Adding Group ID, Channel ID & User ID in group
                                collection_ID.insert_one(
                                    {
                                        groupID: [channelID, msg.chat.id]
                                    }
                                )
                                await msg.reply_text(
                                    "<b>Your Group and Channel have now been added SuccessFully🥳.\n\n😊Join @AJPyroVerse & @AJPyroVerseGroup for getting more awesome 🤖bots like this.</b>",
                                    parse_mode="html"
                                )
    else:   # If command is invalid
        await msg.reply_text(
            "<b>Invalid Format😒\nSend Group ID & Channel ID in this format <code>/add GroupID ChannelID</code>.\n\n😊Join @AJPyroVerse & @AJPyroVerseGroup for getting more awesome 🤖bots like this.</b>",
            parse_mode="html"
        )
    return

# /remove handler to remove group id & channel id from database
@app.on_message(filters.command("remove"))
async def channelgroupRemover(bot: Client, msg: Message):
    if msg.from_user.id not in NANO:
        await msg.reply_text(
            "<b>You are not authorized to use this command. Contact: @SexyNano</b>",
            parse_mode="html"
        )
        return

    message = msg.text.split(" ")
    if len(message) == 2:   # If command is valid
        _, groupID = message
        try:
            int(groupID)
        except ValueError:  # If group id not integer type
            await msg.reply_text(
                "<b>Group ID should be integer type😒.</b>",
                parse_mode="html"
            )
        else:   # If group id is integer type
            documents = collection_ID.find()
            for document in documents:
                try:
                    document[groupID]
                except KeyError:
                    continue
                else:   # If group id found in database
                    if document[groupID][1] == msg.chat.id: # If group id, channel id is removing by one who added
                        collection_ID.delete_one(document)
                        await msg.reply_text(
                            "<b>Your Channel ID & Group ID have now been deleted😢 from our Database.\nYou can add them again by using <code>/add GroupID ChannelID</code>.</b>",
                            parse_mode="html"
                        )
                    else:   # If group id, channel id is not removing by one who added
                        await msg.reply_text(
                            "<b>😒You are not the one who added this Channel ID & Group ID.</b>",
                            parse_mode="html"
                        )
                    break
            else:   # If group id not found in database
                await msg.reply_text(
                    "<b>Given Group ID is not found in our Database🤔.\n\n😊Join @AJPyroVerse & @AJPyroVerseGroup for getting more awesome 🤖bots like this.</b>",
                    parse_mode="html"
                )
    else:   # If command is invalid
        await msg.reply_text(
            "<b>Invalid Command😒\nUse <code>/remove GroupID</code></b>.",
            parse_mode="html"
        )
    return
                
# #request handler
@app.on_message(filters.group & filters.regex(requestRegex + "(.*)"))
async def requestHandler(bot:Update, msg:Message):
    groupID = str(msg.chat.id)

    documents = collection_ID.find()
    for document in documents:
        try:
            document[groupID]
        except KeyError:
            continue
        else:   # If group id found in database
            channelID = document[groupID][0]
            fromUser = msg.from_user
            mentionUser = f"<a href='tg://user?id={fromUser.id}'>{fromUser.first_name}</a>"
            requestText = f"<b>Request by {mentionUser}\n\n{msg.text}</b>"
            originalMSG = msg.text
            findRegexStr = match(requestRegex, originalMSG)
            requestString = findRegexStr.group()
            contentRequested = originalMSG.split(requestString)[1]
            
            try:
                groupIDPro = groupID.removeprefix(str(-100))
                channelIDPro = channelID.removeprefix(str(-100))
            except AttributeError:
                groupIDPro = groupID[4:]
                channelIDPro = channelID[4:]

            # Sending request in channel
            requestMSG = await bot.send_message(
                int(channelID),
                requestText,
                reply_markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Requested Message",
                                url = f"https://t.me/c/{groupIDPro}/{msg.message_id}"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "🚫Reject",
                                "reject"
                            ),
                            InlineKeyboardButton(
                                "Done✅",
                                "done"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "⚠️Unavailable⚠️",
                                "unavailable"
                            )
                        ]
                    ]
                )
            )

            replyText = f"<b>👋 Hello {mentionUser} !!\n\n📍 Your Request for {contentRequested} has been submitted to the admins.\n\n🚀 Your Request Will Be Uploaded soon.\n📌 Please Note that Admins might be busy. So, this may take more time.\n\n👇 See Your Request Status Here 👇</b>"

            # Sending message for user in group
            await msg.reply_text(
                replyText,
                parse_mode = "html",
                reply_to_message_id = msg.message_id,
                reply_markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⏳Request Status⏳",
                                url = f"https://t.me/c/{channelIDPro}/{requestMSG.message_id}"
                            )
                        ]
                    ]
                )
            )
            break
    return
        
# callback buttons handler
@app.on_callback_query()
async def callBackButton(bot:Update, callback_query:CallbackQuery):
    channelID = str(callback_query.message.chat.id)

    documents = collection_ID.find()
    for document in documents:
        for key in document:
            if key == "_id":
                continue
            else:
                if document[key][0] != channelID:
                    continue
                else:   # If channel id found in database
                    groupID = key

                    data = callback_query.data  # Callback Data
                    if data == "rejected":
                        return await callback_query.answer(
                            "This request is rejected💔...\nAsk admins in group for more info💔",
                            show_alert = True
                        )
                    elif data == "completed":
                        return await callback_query.answer(
                            "This request Is Completed🥳...\nCheckout in Channel😊",
                            show_alert = True
                        )
                    user = await bot.get_chat_member(int(channelID), callback_query.from_user.id)
                    if user.status not in ("administrator", "creator"): # If accepting, rejecting request tried to be done by neither admin nor owner
                        await callback_query.answer(
                            "Who the hell are you?\nYour are not Admin😒.",
                            show_alert = True
                        )
                    else:   # If accepting, rejecting request tried to be done by either admin or owner
                        if data == "reject":
                            result = "REJECTED"
                            groupResult = "has been Rejected💔."
                            button = InlineKeyboardButton("Request Rejected🚫", "rejected")
                        elif data == "done":
                            result = "COMPLETED"
                            groupResult = "is Completed🥳."
                            button = InlineKeyboardButton("Request Completed✅", "completed")
                        elif data == "unavailable":
                            result = "UNAVAILABLE"
                            groupResult = "has been rejected💔 due to Unavailablity🥲."
                            button = InlineKeyboardButton("Request Rejected🚫", "rejected")

                        msg = callback_query.message
                        userid = 12345678
                        for m in msg.entities:
                            if m.type == "text_mention":
                                userid = m.user.id
                        originalMsg = msg.text
                        findRegexStr = search(requestRegex, originalMsg)
                        requestString = findRegexStr.group()
                        contentRequested = originalMsg.split(requestString)[1]
                        requestedBy = originalMsg.removeprefix("Request by ").split('\n\n')[0]
                        mentionUser = f"<a href='tg://user?id={userid}'>{requestedBy}</a>"
                        originalMsgMod = originalMsg.replace(requestedBy, mentionUser)
                        originalMsgMod = f"<s>{originalMsgMod}</s>"

                        newMsg = f"<b>{result}</b>\n\n{originalMsgMod}"

                        # Editing reqeust message in channel
                        await callback_query.edit_message_text(
                            newMsg,
                            parse_mode = "html",
                            reply_markup = InlineKeyboardMarkup(
                                [
                                    [
                                        button
                                    ]
                                ]
                            )
                        )

                        # Result of request sent to group
                        replyText = f"<b>Dear {mentionUser}🧑\nYour request for {contentRequested} {groupResult}\n👍Thanks for requesting!</b>"
                        await bot.send_message(
                            int(groupID),
                            replyText,
                            parse_mode = "html"
                        )
                    return
    return


API_URL: str = "https://sasta-api.vercel.app/google_reverse"

COMMANDS: List[str] = [
    "reverse",
    "grs",
    "pp"
    ]

async_client: httpx.AsyncClient = httpx.AsyncClient(timeout=120)

class STRINGS:
    REPLY_TO_MEDIA: str = "ℹ️ Please reply to a media types, such as a photo, sticker, or image file."
    UNSUPPORTED_MEDIA_TYPE: str = "⚠️ <b>Unsupported media type!</b>\nℹ️ Please reply with a supported media type: image, sticker, or image file."
    
    DOWNLOADING_MEDIA: str = "⏳ Downloading media..."
    UPLOADING_TO_API_SERVER: str = "📡 Uploading media to <b>Google Server</b>... 📶"
    PARSING_RESULT: str = "💻 Parsing result..."
    
    EXCEPTION_OCCURRED: str = "❌ <b>Exception occurred!</b>\n\n<b>Exception:</b> {}"
    
    RESULT: str = """
🔤 <b>Result:</b> <code>{query}</code>
    """
    OPEN_PAGE: str = "↗️ Open Page"

@app.on_message(filters.command(COMMANDS))
async def on_reverse(client: Client, message: Message) -> None:
    if not message.reply_to_message:
        await message.reply(STRINGS.REPLY_TO_MEDIA)
        return
    elif message.reply_to_message.media not in (MessageMediaType.PHOTO, MessageMediaType.STICKER, MessageMediaType.DOCUMENT):
        await message.reply(STRINGS.UNSUPPORTED_MEDIA_TYPE)
        return
    
    start_time: float = time.time()
    status_msg: Message = await message.reply(STRINGS.DOWNLOADING_MEDIA)
    file_path: str = f"temp_download/{uuid4()}"
    try:
        await message.reply_to_message.download(file_path)
    except Exception as exc:
        text: str = STRINGS.EXCEPTION_OCCURRED.format(exc)
        await message.reply(text)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
        return
    
    await status_msg.edit(STRINGS.UPLOADING_TO_API_SERVER)
    files: Dict[str, BinaryIO] = {"file": open(file_path, "rb")}
    response: httpx.Response = await async_client.post(API_URL, files=files)
    os.remove(file_path)
    
    if response.status_code == 404:
        text: str = STRINGS.EXCEPTION_OCCURRED.format(response.json()["error"])
        await message.reply(text)
        await status_msg.delete()
        return
    elif response.status_code != 200:
        text: str = STRINGS.EXCEPTION_OCCURRED.format(response.text)
        await message.reply(text)
        await status_msg.delete()
        return
    
    await status_msg.edit(STRINGS.PARSING_RESULT)
    response_json: Dict[str, str] = response.json()
    query: str = response_json["query"]
    page_url: str = response_json["url"]
    
    end_time: float = time.time() - start_time
    time_taken: str = "{:.2f}".format(end_time)
    
    text: str = STRINGS.RESULT.format(
        query=query,
        page_url=page_url,
        time_taken=time_taken
        )
    buttons: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(STRINGS.OPEN_PAGE, url=page_url)]
        ]
    await message.reply(text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))
    await status_msg.delete()

"""Bot is Started"""
print("Bot has been Started!!!")
app.run()

