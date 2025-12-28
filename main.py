from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# Register functions
from handlers.admin import register_admin
from handlers.filters import register_filters
from handlers.commands import register_commands


def main():
    app = Client(
        "GroupManager",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    # Register handlers
    register_admin(app)
    register_filters(app)
    register_commands(app)

    print("🤖 GroupManager Bot Started")
    app.run()


if __name__ == "__main__":
    main()
