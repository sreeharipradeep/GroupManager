import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


START_IMAGES = [
    "https://graph.org/file/62386b57bf0394d7bd917-959daf5976f788890f.jpg",
    "https://graph.org/file/1d87e8717b0675ac15730-c491930774a108b163.jpg",
    "https://graph.org/file/dbc886d8bb5922d2ac2a6-7a3bbc2919ef5588a6.jpg",
]


def register_commands(app):

    # =========================
    # /START
    # =========================
    @app.on_message(filters.command("start"))
    async def start(_, message):
        image = random.choice(START_IMAGES)

        text = (
    "🍿✨ **Welcome!** ✨🍿\n\n"
    "🎬 I am the **Filter Bot** of the **Trixel Movie Group**.\n"
    "➕ You can add ⭐ **me** to your **Channel / Group** and use me easily.\n\n"
    "✯ ━━━━━━ ✧━━━━━━✯\n\n"
    "🍿✨ **സ്വാഗതം!** ✨🍿\n\n"
    "🎥 ഞാൻ **Trixel Movie** 🎬 ഗ്രൂപ്പിന്റെ **ഫിൽട്ടർ ബോട്ട്** ആണ്.\n"
    "➕ നിങ്ങൾ ⭐ **എന്നെ** നിങ്ങളുടെ **Channel / Group**-ൽ add ചെയ്ത്\n"
    "സൗകര്യമായി use ചെയ്യാവുന്നതാണ് 😊"
)

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Add me to your group",
                        url=f"https://t.me/{_.me.username}?startgroup=true"
                    )
                ],
                [
                    InlineKeyboardButton("ℹ️ Help", callback_data="help_menu"),
                    InlineKeyboardButton("🌐 Bot Updates", url="https://t.me/jb_links")
                ]
            ]
        )

        await message.reply_photo(
            photo=image,
            caption=text,
            reply_markup=buttons
        )

    # =========================
    # /HELP
    # =========================
    @app.on_message(filters.command("help"))
    async def help_cmd(_, message):
        await send_help_menu(message)

    async def send_help_menu(message):
        text = (
            "ℹ️ **Miyamizu Help Menu**\n\n"
            "Choose a category below to see commands."
        )

        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🧠 Filters", callback_data="help_filters")],
                [InlineKeyboardButton("⚠️ Warnings", callback_data="help_warns")],
                [InlineKeyboardButton("🛠 Admin Commands", callback_data="help_admin")],
                [InlineKeyboardButton("👤 User Commands", callback_data="help_user")],
            ]
        )

        await message.reply(text, reply_markup=buttons)

    # =========================
    # CALLBACK HANDLER
    # =========================
    @app.on_callback_query()
    async def callbacks(_, query):
        data = query.data

        if data == "help_menu":
            text = (
                "ℹ️ **Miyamizu Help Menu**\n\n"
                "Select a category:"
            )
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🧠 Filters", callback_data="help_filters")],
                    [InlineKeyboardButton("⚠️ Warnings", callback_data="help_warns")],
                    [InlineKeyboardButton("🛠 Admin Commands", callback_data="help_admin")],
                    [InlineKeyboardButton("👤 User Commands", callback_data="help_user")],
                ]
            )
            await query.message.edit_text(text, reply_markup=buttons)

        elif data == "help_filters":
            text = (
                "🧠 **Filters Commands**\n\n"
                "/filter <keyword> – Add filter (reply)\n"
                "/stop <keyword> – Remove filter\n"
                "/filters – List all filters\n"
                "**Button Adding Example:**\n\n"
                "[Button Name](buttonurl:https://google.com)"
            )
            await back_menu(query, text)

        elif data == "help_warns":
            text = (
                "⚠️ **Warning Commands**\n\n"
                "/warn – Warn a user\n"
                "/rmwarn – Remove one warn\n"
                "/warnings – Check warns\n"
                "/warnlimit – Set warn limit"
            )
            await back_menu(query, text)

        elif data == "help_admin":
            text = (
                "🛠 **Admin Commands**\n\n"
                "/ban / unban\n"
                "/mute / unmute\n"
                "/pin\n"
                "/purge\n"
                "/warn / rmwarn"
            )
            await back_menu(query, text)

        elif data == "help_user":
            text = (
                "👤 **User Commands**\n\n"
                "/id – Get user / group ID\n"
                "/start – Start bot\n"
                "/help – Help menu"
            )
            await back_menu(query, text)

        await query.answer()

    async def back_menu(query, text):
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="help_menu")]]
        )
        await query.message.edit_text(text, reply_markup=buttons)

    # =========================
    # /ID
    # =========================
    @app.on_message(filters.command("id"))
    async def id_cmd(_, message):
        if message.chat.type == "private":
            await message.reply(f"🆔 **Your ID:** `{message.from_user.id}`")
        else:
            await message.reply(
                f"🙋 **Your ID:** `{message.from_user.id}`"
            )
