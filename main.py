import os
from datetime import datetime
import time
import asyncio
from telegram import ChatPermissions
from telegram.ext import ChatJoinRequestHandler
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters, 
)
WELCOME_DB = {}
SET_WELCOME_MODE = {}
WARN_DB = {}
LINKS_DISABLED = {}
GIF_DISABLED = {}
STICKER_DISABLED = {}
LINKS_LOCKED = {}
MEDIA_LOCKED = set()
FILTERS = {}
FILTER_MODE = {}
FLOOD_USERS = {}

# 🔥 SETTINGS 
FLOOD_LIMIT = 6        # কয়টা message
FLOOD_SECONDS = 5      # কয় সেকেন্ডের মধ্যে
FLOOD_MUTE_TIME = 60   # কত সেকেন্ড mute
TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "Sathiwelbot"   # without @
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type not in ["group", "supergroup"]:
            return await func(update, context)

        member = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
        )

        if member.status not in ["administrator", "creator"]:
            return await update.message.reply_text("❌ Only Group Admins Can Use This Command.")

        return await func(update, context)

    return wrapper

# ===== WELCOME TEXT =====
WELCOME_TEXT = (
"*✦ ʜєʟʟᴏ {name} ηɪᴄє ᴛᴏ ϻєєᴛ ʏσᴜ 🥀*\n\n"
"*⊚ ᴛʜɪꜱ ɪꜱ {bot}*\n\n"
"*➻ ᴧ ᴘʀєᴍɪᴜᴍ ᴅєꜱɪɢηєᴅ ʙσᴛ ꜰσʀ ᴛєʟєɢʀᴧϻ ɢʀσᴜᴘ & ᴄʜᴧηηєʟ.*\n\n"
"*» ɪғ ᴧηʏ ʜєʟᴘ ᴛᴧᴘ ᴛᴏ ʜєʟᴘ ʙᴜᴛᴛση.*\n\n"
"*•── ⋅ ⋅  ────── ⋅᯽⋅ ────── ⋅ ⋅ ⋅──•*"
)

DEFAULT_GROUP_WELCOME = (
"*✦ ʜєʟʟᴏ {name} ηɪᴄє ᴛᴏ ϻєєᴛ ʏσᴜ 🥀*\n\n"
"*⊚ ᴛʜɪꜱ ɪꜱ ✧ ˹sᴧᴛʜɪ ᴡєʟᴄσᴍє ʙσᴛ˼ ✧*\n\n"
"*➻ ᴧ ᴘʀєᴍɪᴜᴍ ᴅєꜱɪɢηєᴅ ʙσᴛ ꜰσʀ ᴛєʟєɢʀᴧϻ ɢʀσᴜᴘ & ᴄʜᴧηηєʟ.*\n\n"
"*•── ⋅ ⋅  ────── ⋅᯽⋅ ────── ⋅ ⋅ ⋅──•*"
) 

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.full_name
    bot_name = context.bot.first_name

    text = WELCOME_TEXT.format(name=user_name, bot=bot_name)

    keyboard = [
        [InlineKeyboardButton("✧ ˹ᴧᴅᴅ ᴍє ɪɴ ʏσᴜʀ ɢʀσᴜᴘ˼ ✧",
         url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],

        [InlineKeyboardButton("✧ ˹ᴧᴅᴅ ᴍє ɪɴ ʏσᴜʀ ᴄʜᴧɴɴєʟ˼ ✧",
         url=f"https://t.me/{BOT_USERNAME}?startchannel=true")],

        [
          InlineKeyboardButton("˹σᴡɴєʀ˼",
    url="https://t.me/SANTANUGAMING1"),
          InlineKeyboardButton("˹ᴧʙσᴜᴛ ᴍє˼", callback_data="about")],

        [InlineKeyboardButton("˹ʜєʟᴘ & ᴄσᴍᴍᴧηᴅ˼", callback_data="help")]
    ]

    await update.message.reply_photo(
        caption=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
@admin_only
async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    member = await context.bot.get_chat_member(chat.id, user.id)

    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only Admin Can Use This Command")
        return

    rules_text = (
        "⚠️ Welcome Message Rules ⚠️\n\n"
        "• Premium Emoji Use Kar Sakte Ho 😎\n"
        "• Bold / Stylish Text Allowed\n"
        "• Multiple Language Allowed\n"
        "• {name} Use Karna Mandatory (User Name Ke Liye)\n\n"
        "✅ Ab Apna Welcome Message Send Karo..."
    )

    SET_WELCOME_MODE[chat.id] = True
    await update.message.reply_text(rules_text)

async def save_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in SET_WELCOME_MODE:
        WELCOME_DB[chat_id] = update.message.text
        del SET_WELCOME_MODE[chat_id]
        await update.message.reply_text("✅ Welcome Message Saved Successfully")

async def welcome_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    for member in update.message.new_chat_members:
        name = member.first_name

        caption = WELCOME_DB.get(chat_id, DEFAULT_GROUP_WELCOME)
        caption = caption.replace("{name}", name)

        await update.message.reply_photo(
            caption=caption,
            parse_mode="Markdown"
        )

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1️⃣ Reply method
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user

    # 2️⃣ Username / ID method
    if context.args:
        user_input = context.args[0]

        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id,
                user_input
            )
            return member.user
        except:
            return None

    return None

@admin_only
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_target_user(update, context)

    if not user:
        return await update.message.reply_text("Reply or give username to ban.")

    await context.bot.ban_chat_member(update.effective_chat.id, user.id)

    await update.message.reply_text(f"🚫 {user.first_name} banned.")

@admin_only
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_target_user(update, context)

    if not user:
        return await update.message.reply_text("Reply or give username to unban.")

    await context.bot.unban_chat_member(update.effective_chat.id, user.id)

    await update.message.reply_text(f"✅ {user.first_name} unbanned.")

from telegram import ChatPermissions

@admin_only
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_target_user(update, context)

    if not user:
        return await update.message.reply_text("Reply or give username to mute.")

    permissions = ChatPermissions(
        can_send_messages=False
    )

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        permissions=permissions
    )

    await update.message.reply_text(f"🔇 {user.first_name} muted.")

from telegram import ChatPermissions

@admin_only
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_target_user(update, context)

    if not user:
        return await update.message.reply_text("Reply or give username to unmute.")

    permissions = ChatPermissions(
        can_send_messages=True
    )

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        permissions=permissions
    )

    await update.message.reply_text(f"🔊 {user.first_name} unmuted.")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

WARN_DB = {}

@admin_only
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_target_user(update, context)

    if not user:
        return await update.message.reply_text("Reply or give username to warn.")

    chat_id = update.effective_chat.id

    WARN_DB.setdefault(chat_id, {})
    WARN_DB[chat_id].setdefault(user.id, 0)

    WARN_DB[chat_id][user.id] += 1
    warns = WARN_DB[chat_id][user.id]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Remove Warn", callback_data=f"removewarn_{chat_id}_{user.id}")]
    ])

    await update.message.reply_text(
        f"⚠ {user.first_name} warned!\nTotal Warns: {warns}/3",
        reply_markup=keyboard
    )

    if warns >= 3:
        await context.bot.ban_chat_member(chat_id, user.id)
        await update.message.reply_text(f"🚫 {user.first_name} banned (3 warns).")

@admin_only
async def remove_warn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    chat_id = int(data[1])
    user_id = int(data[2])

    if chat_id in WARN_DB and user_id in WARN_DB[chat_id]:
        if WARN_DB[chat_id][user_id] > 0:
            WARN_DB[chat_id][user_id] -= 1

        warns = WARN_DB[chat_id][user_id]

        await query.edit_message_text(
            f"✅ Warn removed.\nCurrent Warns: {warns}/3"
        )


from telegram import ChatPermissions

@admin_only
async def linkslock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("❌ Admin Only.")

    LINKS_LOCKED[update.effective_chat.id] = True
    await update.message.reply_text("🔗 Links Fully Locked.")

@admin_only
async def linksunlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    LINKS_LOCKED[update.effective_chat.id] = False
    await update.message.reply_text("🔓 Links Unlocked.")

async def link_delete_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    chat_id = message.chat.id

    if not LINKS_LOCKED.get(chat_id, False):
        return

    member = await context.bot.get_chat_member(chat_id, message.from_user.id)

    if member.status in ["administrator", "creator"]:
        return

    text = (message.text or message.caption or "").lower()

    if any(word in text for word in ["http", "t.me", "@"]):
        try:
            await message.delete()
        except:
            pass

from telegram import ChatPermissions

@admin_only
async def gifslock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("❌ Admin Only.")

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_other_messages=False  # 🔥 this blocks GIF & stickers
    )

    await context.bot.set_chat_permissions(update.effective_chat.id, permissions)
    await update.message.reply_text("🎞 GIF & Stickers Locked.")

@admin_only
async def gifsunlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_other_messages=True
    )

    await context.bot.set_chat_permissions(update.effective_chat.id, permissions)
    await update.message.reply_text("🎞 GIF & Stickers Unlocked.")

@admin_only
async def stickerslock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )
    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("❌ Admin Only.")

    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_other_messages=False
    )

    await context.bot.set_chat_permissions(update.effective_chat.id, permissions)
    await update.message.reply_text("🧷 Stickers Locked.")

@admin_only
async def stickersunlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_other_messages=True
    )

    await context.bot.set_chat_permissions(update.effective_chat.id, permissions)
    await update.message.reply_text("🧷 Stickers Unlocked.")

@admin_only
async def group_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("❌ Group only command.")

    chat_id = update.effective_chat.id
    user = None

    # Reply method
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user

    # Username method
    elif context.args:
        try:
            member = await context.bot.get_chat_member(chat_id, context.args[0])
            user = member.user
        except:
            return await update.message.reply_text("❌ User not found.")

    else:
        return await update.message.reply_text("Reply or give username.")

    try:
        await context.bot.promote_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_video_chats=True
        )

        await update.message.reply_text(f"👑 {user.first_name} is now Group Admin.")

    except:
        await update.message.reply_text("❌ I don't have Add Admin permission.")

@admin_only
async def group_rmapprove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("❌ Group only command.")

    chat_id = update.effective_chat.id
    user = None

    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user

    elif context.args:
        try:
            member = await context.bot.get_chat_member(chat_id, context.args[0])
            user = member.user
        except:
            return await update.message.reply_text("❌ User not found.")

    else:
        return await update.message.reply_text("Reply or give username.")

    await context.bot.promote_chat_member(
        chat_id=chat_id,
        user_id=user.id,
        can_delete_messages=False,
        can_restrict_members=False,
        can_invite_users=False,
        can_pin_messages=False,
        can_manage_video_chats=False
    )

    await update.message.reply_text(f"❌ {user.first_name} removed from Admin.")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def kickme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    user = update.effective_user

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm Leave", callback_data=f"confirm_kick_{user.id}")]
    ])

    await update.message.reply_text(
        f"🥺 ʜᴇʏ {user.first_name}...\n\n"
        "ɪꜰ ʏᴏᴜ ʀᴇᴀʟʟʏ ᴡᴀɴᴛ ᴛᴏ ʟᴇᴀᴠᴇ ᴛʜɪꜱ ɢʀᴏᴜᴘ,\n"
        "ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴄᴏɴꜰɪʀᴍ ʙᴇʟᴏᴡ 👇\n\n"
        "💔 ɢᴏᴏᴅʙʏ ɪɴ ᴀᴅᴠᴀɴᴄᴇ...",
        reply_markup=keyboard
    )

async def confirm_kick_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    chat_id = query.message.chat.id

    data = query.data.split("_")
    target_id = int(data[2])

    # Ensure only same user can press
    if user.id != target_id:
        return await query.answer("❌ This button is not for you.", show_alert=True)

    await context.bot.ban_chat_member(chat_id, user.id)
    await context.bot.unban_chat_member(chat_id, user.id)

    await query.message.edit_text(
        "👋 ʏᴏᴜ ʜᴀᴠᴇ ʟᴇꜰᴛ ᴛʜᴇ ɢʀᴏᴜᴘ.\n\n"
        "ᴛᴀᴋᴇ ᴄᴀʀᴇ ʙʀᴏᴛʜᴇʀ 💔"
    )

@admin_only
async def medialock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    MEDIA_LOCKED.add(chat_id)

    await update.message.reply_text(
        "📵 ᴍᴇᴅɪᴀ ʟᴏᴄᴋ ᴇɴᴀʙʟᴇᴅ.\nOnly Admins Can Send Media."
    )

@admin_only
async def mediaunlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    MEDIA_LOCKED.discard(chat_id)

    await update.message.reply_text(
        "📂 ᴍᴇᴅɪᴀ ʟᴏᴄᴋ ᴅɪꜱᴀʙʟᴇᴅ.\nEveryone Can Send Media."
    )

async def media_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id not in MEDIA_LOCKED:
        return

    member = await context.bot.get_chat_member(chat_id, user_id)

    if member.status in ["administrator", "creator"]:
        return

    if (
        message.photo
        or message.video
        or message.document
        or message.audio
        or message.voice
        or message.sticker
        or message.animation
    ):
        try:
            await message.delete()
        except:
            pass

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 1️⃣ Reply method
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user

    # 2️⃣ Username / ID
    elif context.args:
        try:
            member = await context.bot.get_chat_member(
                update.effective_chat.id,
                context.args[0].replace("@","")
            )
            user = member.user
        except:
            return await update.message.reply_text(
                "❌ User not found in this group."
            )

    # 3️⃣ Self info
    else:
        user = update.effective_user

    name = user.full_name
    username = f"@{user.username}" if user.username else "No Username"
    user_id = user.id

    # Account type
    account = "Bot 🤖" if user.is_bot else "Human 👤"

    # Role detect
    role = "Member"

    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user.id)

        if member.status == "creator":
            role = "Owner 👑"

        elif member.status == "administrator":
            role = "Admin 🔱"

        else:
            role = "Member 👤"

    except:
        pass

    text = (
        f"*❖ ᴜꜱᴇʀ ɪɴꜰᴏ*\n\n"
        f"*👤 ɴᴀᴍᴇ : {name}*\n"
        f"*🔗 ᴜꜱᴇʀɴᴀᴍᴇ : {username}*\n"
        f"*🆔 ᴜꜱᴇʀ ɪᴅ : `{user_id}`*\n"
        f"*👑 ʀᴏʟᴇ : {role}*\n"
        f"*🤖 ᴀᴄᴄᴏᴜɴᴛ : {account}*\n\n"
        f"•── ⋅ ⋅ ────── ⋅᯽⋅ ────── ⋅ ⋅ ──•"
    )

    await update.message.reply_text(text, parse_mode="Markdown")

# ===== SAVE FILTER COMMAND =====
async def filter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("❌ Admin Only Command.")

    if not context.args:
        return await update.message.reply_text("Use: /filter keyword")

    chat_id = update.effective_chat.id
    keyword = context.args[0].lower()

    FILTER_MODE[chat_id] = keyword

    await update.message.reply_text(
        f"✦ Send reply message for filter: {keyword}"
    )


# ===== SAVE FILTER REPLY =====
async def save_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    if chat_id not in FILTER_MODE:
        return

    keyword = FILTER_MODE[chat_id]

    reply = update.message.text or update.message.caption

    FILTERS.setdefault(chat_id, {})
    FILTERS[chat_id][keyword] = reply

    del FILTER_MODE[chat_id]

    await update.message.reply_text(
        f"✅ Filter Saved : {keyword}"
    )

# ===== AUTO FILTER =====
async def auto_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if not message:
        return

    chat_id = message.chat.id

    if chat_id not in FILTERS:
        return

    text = message.text.lower()

    for word, reply in FILTERS[chat_id].items():

        if word in text:
            await message.reply_text(reply, parse_mode="Markdown")
            break
# ===== REMOVE FILTER =====
async def rmfilter(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("❌ Admin Only Command.")

    if not context.args:
        return await update.message.reply_text("Use: /rmfilter keyword")

    chat_id = update.effective_chat.id
    keyword = context.args[0].lower()

    if chat_id not in FILTERS:
        return await update.message.reply_text("No filters found.")

    if keyword not in FILTERS[chat_id]:
        return await update.message.reply_text("Filter not found.")

    del FILTERS[chat_id][keyword]

    await update.message.reply_text(
        f"❌ Filter Removed : {keyword}"
    )

from telegram import ChatPermissions

async def lockall(update: Update, context: ContextTypes.DEFAULT_TYPE):

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("❌ Admin Only Command.")

    permissions = ChatPermissions(
        can_send_messages=False
    )

    await context.bot.set_chat_permissions(
        update.effective_chat.id,
        permissions
    )

    await update.message.reply_text(
        "🔒 Group Locked.\nOnly Admins Can Send Messages."
    )

async def unlockall(update: Update, context: ContextTypes.DEFAULT_TYPE):

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("❌ Admin Only Command.")

    permissions = ChatPermissions(
        can_send_messages=True
    )

    await context.bot.set_chat_permissions(
        update.effective_chat.id,
        permissions
    )

    await update.message.reply_text(
        "🔓 Group Unlocked.\nEveryone Can Send Messages."
    )

async def auto_flood_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await context.bot.get_chat_member(chat_id, user_id)

    # 👑 Admin & Owner immune
    if member.status in ["administrator", "creator"]:
        return

    now = time.time()

    FLOOD_USERS.setdefault(chat_id, {})
    FLOOD_USERS[chat_id].setdefault(user_id, [])

    # পুরানো timestamp remove
    FLOOD_USERS[chat_id][user_id] = [
        t for t in FLOOD_USERS[chat_id][user_id]
        if now - t < FLOOD_SECONDS
    ]

    FLOOD_USERS[chat_id][user_id].append(now)

    if len(FLOOD_USERS[chat_id][user_id]) >= FLOOD_LIMIT:

        permissions = ChatPermissions(can_send_messages=False)

        await context.bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=permissions
        )

        await message.reply_text(
            f"🚫 Flood Detected!\n🔇 Muted for {FLOOD_MUTE_TIME} seconds."
        )

        asyncio.create_task(auto_unmute(context, chat_id, user_id))

        FLOOD_USERS[chat_id][user_id] = []

async def auto_unmute(context, chat_id, user_id):
    await asyncio.sleep(FLOOD_MUTE_TIME)

    permissions = ChatPermissions(can_send_messages=True)

    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        permissions=permissions
    )

async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request

    await context.bot.approve_chat_join_request(
        chat_id=request.chat.id,
        user_id=request.from_user.id
    )

    # Send message to user private chat
    try:
        await context.bot.send_message(
            chat_id=request.from_user.id,
            text="✅ You have been approved in the channel!"
        )
    except:
        print("User has not started the bot.")
# ===== ABOUT CALLBACK =====
async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "*⋟ 𝐈 ᴧϻ  ˹sᴧᴛʜɪ ᴡєʟᴄσᴍє ʙσᴛ˼ 🙊 ᴧ  ϻᴧηᴧɢєϻєηт ʙσт  ɢʀσᴜᴘ/ᴄʜᴧηηєʟ*\n\n"

"*✦ 𝐊єʏ 𝐅єᴧтᴜʀєs*\n\n"

"*▸  𝐈 ᴄᴧη єᴧsɪʟʏ ʜᴧηᴅʟє ɢʀσᴜᴘs.*\n"
"*▸. 𝐇ɪsᴛᴏʀʏ, ɪɴғᴏ, ᴧηтɪ ғʟσσᴅ ᴧᴄтɪσηs.*\n"
"*▸  𝐌σʀє ᴅєтᴧɪʟs → тᴧᴘ ʜєʟᴘ ʙᴜттση.*\n"
"*────────────────────────*",
        parse_mode="Markdown"
    )

# ===== HELP CALLBACK =====
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    HELP_TEXT = (
        "*❖ ᴄʜσσsє ᴛʜє ᴄᴧᴛєɢσʀʏ ғσʀ ᴡʜɪᴄʜ ʏσυ ᴡᴧηηᴧ ɢєᴛ ʜєʟᴩ*\n\n"
        "*❖ ᴧsᴋ ʏσυʀ ᴅσυʙᴛs ᴧᴛ sυᴘᴘσʀᴛ ᴄʜᴧᴛ ᴧʟʟ ᴄσϻϻᴧηᴅs ᴄᴧη ʙє υsєᴅ ᴡɪᴛʜ : /*\n\n"
        "*❖ ɴᴏᴛᴇ :- ɪꜰ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ ᴅᴏᴇs ɴᴏᴛ ᴡᴏʀᴋ, ᴛʏᴘᴇ /bug reason ɪɴ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ.*"
    )

    keyboard = [
        [
            InlineKeyboardButton("• ᴧᴄᴛɪση •", callback_data="action"),
            InlineKeyboardButton("• ᴧᴘᴘʀσᴠᴧʟ •", callback_data="approval"),
        ],
        [
            InlineKeyboardButton("• ʟσᴄᴋs •", callback_data="locks"),
            InlineKeyboardButton("• ɪɴғσ •", callback_data="info"),
        ],
        [
            InlineKeyboardButton("≡ ʙᴧᴄᴋ ≡", callback_data="back")
        ]
    ]

    await update.callback_query.message.reply_photo(
        caption=HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    user_name = update.effective_user.full_name
    bot_name = context.bot.first_name

    text = WELCOME_TEXT.format(name=user_name, bot=bot_name)

    keyboard = [
        [InlineKeyboardButton("✧ ˹ᴧᴅᴅ ᴍє ɪɴ ʏσᴜʀ ɢʀσᴜᴘ˼ ✧",
         url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("✧ ˹ᴧᴅᴅ ᴍє ɪɴ ʏσᴜʀ ᴄʜᴧɴɴєʟ˼ ✧",
         url=f"https://t.me/{BOT_USERNAME}?startchannel=true")],
        [
            InlineKeyboardButton("˹σᴡɴєʀ˼", url="https://t.me/SANTANUGAMING1"),
            InlineKeyboardButton("˹ᴧʙσᴜᴛ ᴍє˼", callback_data="about")
        ],
        [InlineKeyboardButton("˹ʜєʟᴘ & ᴄσᴍᴍᴧηᴅ˼", callback_data="help")]
    ]

    await update.callback_query.message.reply_photo(
        caption=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    TEXT = (
        "*❖ ᴧᴄᴛɪση ᴄσϻϻᴧηᴅs*\n\n"
        "*➤ /ban* – ᴜsєʀ ʙᴧη\n"
        "*➤ /unban* – ᴜsєʀ ᴜηʙᴧη\n"
        "*➤ /mute* – ᴜsєʀ ϻᴜᴛє\n"
        "*➤ /unmute* – ᴜsєʀ ᴜηϻᴜᴛє\n"
        "*➤ /warn* – ᴡᴧʀη ᴜsєʀ\n"
        "*➤ /kickme* – ʟєᴧᴠє ɢʀσᴜᴘ\n\n"
        "*────────────────────────*"
    )

    keyboard = [
        [InlineKeyboardButton("≡ ʙᴧᴄᴋ ≡", callback_data="help")]
    ]

    await update.callback_query.message.reply_photo(
        caption=TEXT,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    TEXT = (
        "*❖ ᴧᴘᴘʀσᴠᴧʟ ᴄσϻϻᴧηᴅs*\n\n"
        "*➤ /approve* – ᴧᴅᴅ ᴧᴅϻɪη\n"
        "*➤ /rmapprove* – ʀєϻσᴠє ᴧᴅϻɪη\n\n"
        "*────────────────────────*"
    )

    keyboard = [[InlineKeyboardButton("≡ ʙᴧᴄᴋ ≡", callback_data="help")]]

    await update.callback_query.message.reply_photo(
        caption=TEXT,
        parse_mode="Markdown",
        
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def locks_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    TEXT = (
        "*❖ ʟσᴄᴋ ᴄσϻϻᴧηᴅs*\n\n"
        "*➤ /linkslock* – ʟσᴄᴋ ʟɪηᴋs\n"
        "*➤ /linksunlock* – ᴜηʟσᴄᴋ ʟɪηᴋs\n"
        "*➤ /gifslock* – ʟσᴄᴋ ɢɪғs\n"
        "*➤ /gifsunlock* – ᴜηʟσᴄᴋ ɢɪғs\n"
        "*➤ /stickerslock* – ʟσᴄᴋ sᴛɪᴄᴋєʀs\n"
        "*➤ /stickersunlock* – ᴜηʟσᴄᴋ sᴛɪᴄᴋєʀs\n"
        "*➤ /medialock* – ʟσᴄᴋ ϻєᴅɪᴧ\n"
        "*➤ /mediaunlock* – ᴜηʟσᴄᴋ ϻєᴅɪᴧ\n\n"
        "*────────────────────────*"
    )

    keyboard = [[InlineKeyboardButton("≡ ʙᴧᴄᴋ ≡", callback_data="help")]]

    await update.callback_query.message.reply_photo(
        caption=TEXT,
        parse_mode="Markdown",
        
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    TEXT = (
        "*❖ ɪηғσ ᴄσϻϻᴧηᴅs*\n\n"
        "*➤ /info* – ᴜsєʀ ɪηғσ\n"
        "*➤ /filter* – sᴧᴠє ғɪʟᴛєʀ\n"
        "*➤ /rmfilter* – ʀєϻσᴠє ғɪʟᴛєʀ\n\n"
        "*────────────────────────*"
    )

    keyboard = [[InlineKeyboardButton("≡ ʙᴧᴄᴋ ≡", callback_data="help")]]

    await update.callback_query.message.reply_photo(
        caption=TEXT,
        parse_mode="Markdown",
        
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
# ===== MAIN =====
app = ApplicationBuilder().token(TOKEN).build()

# ===== COMMANDS =====
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setwelcome", setwelcome))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))

app.add_handler(CommandHandler("linkslock", linkslock))
app.add_handler(CommandHandler("linksunlock", linksunlock))

app.add_handler(CommandHandler("gifslock", gifslock))
app.add_handler(CommandHandler("gifsunlock", gifsunlock))

app.add_handler(CommandHandler("stickerslock", stickerslock))
app.add_handler(CommandHandler("stickersunlock", stickersunlock))
app.add_handler(CommandHandler("approve", group_approve))
app.add_handler(CommandHandler("rmapprove", group_rmapprove))
app.add_handler(CommandHandler("kickme", kickme))
app.add_handler(CallbackQueryHandler(confirm_kick_callback, pattern="confirm_kick_"))
app.add_handler(CommandHandler("medialock", medialock))
app.add_handler(CommandHandler("mediaunlock", mediaunlock))

app.add_handler(
    MessageHandler(
        filters.PHOTO
        | filters.VIDEO
        | filters.Document.ALL
        | filters.AUDIO
        | filters.VOICE
        | filters.Sticker.ALL
        | filters.ANIMATION,
        media_filter
    ),
    group=0
)

app.add_handler(CommandHandler("info", info))
# ===== CALLBACK =====
app.add_handler(CallbackQueryHandler(remove_warn_callback, pattern="removewarn_"))
app.add_handler(CallbackQueryHandler(about_callback, pattern="about"))
app.add_handler(CallbackQueryHandler(help_callback, pattern="help"))
app.add_handler(CallbackQueryHandler(back_callback, pattern="back"))

# ===== FILTERS (IMPORTANT ORDER) =====
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, link_delete_filter), group=1)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_welcome), group=2)

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, auto_flood_check),
    group=0
)

app.add_handler(ChatJoinRequestHandler(auto_approve))

# ===== FILTER SYSTEM =====

app.add_handler(CommandHandler("filter", filter_cmd))
app.add_handler(CommandHandler("rmfilter", rmfilter))

# save filter first
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, save_filter),
    group=3
)

# auto reply filter
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, auto_filter),
    group=4
)

app.add_handler(CommandHandler("lockall", lockall))
app.add_handler(CommandHandler("unlockall", unlockall))

app.add_handler(CallbackQueryHandler(action_callback, pattern="action"))
app.add_handler(CallbackQueryHandler(approval_callback, pattern="approval"))
app.add_handler(CallbackQueryHandler(locks_callback, pattern="locks"))
app.add_handler(CallbackQueryHandler(info_callback, pattern="info"))

app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    webhook_url="https://telegramwelcombot-5.onrender.com"
)
