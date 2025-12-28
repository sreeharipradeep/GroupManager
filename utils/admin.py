from pyrogram.errors import ChatAdminRequired


async def is_admin(client, message):
    """
    Central admin checker for the whole bot.

    Rules:
    - If message sent as sender_chat (anonymous admin / send as group):
        -> ALLOW (Rose-style relaxed)
    - Else:
        -> Check from_user is admin/owner
    """

    # Case 1: Message sent as channel / group (anonymous admin)
    # Telegram bug / feature → treat as admin
    if message.sender_chat:
        return True

    # Case 2: No user info at all
    if not message.from_user:
        return False

    try:
        member = await client.get_chat_member(
            message.chat.id,
            message.from_user.id
        )
        return member.status in ("administrator", "owner")

    except ChatAdminRequired:
        # Bot itself is not admin (should not happen normally)
        return False

    except Exception:
        # Any other unexpected error
        return False
