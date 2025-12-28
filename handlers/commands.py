from pyrogram import filters


def register_commands(app):

    # =========================
    # START COMMAND
    # =========================
    @app.on_message(filters.command("start"))
    async def start_cmd(client, message):
        text = (
            "👋 **Hello!**\n\n"
            "I am a **Group Manager Bot** 🤖\n"
            "Use /help to see available commands."
        )
        await message.reply(text)

    # =========================
    # HELP COMMAND
    # =========================
    @app.on_message(filters.command("help"))
    async def help_cmd(client, message):
        text = (
            "📖 **Available Commands**\n\n"
            "• /start – Start the bot\n"
            "• /help – Show this help menu\n"
            "• /id – Get your User ID or Group ID\n"
        )
        await message.reply(text)

    # =========================
    # ID COMMAND
    # =========================
    @app.on_message(filters.command("id"))
    async def id_cmd(client, message):

        # Private chat → User ID
        if message.chat.type == "private":
            await message.reply(
                f"👤 **Your User ID:** `{message.from_user.id}`"
            )
        else:
            # Group / Supergroup → Chat ID
            await message.reply(
                f"👥 **Group ID:** `{message.chat.id}`"
            )
