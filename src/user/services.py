from src.user.models import TGBot, TGUser
from telethon.tl.types import (
    UserStatusOffline,
)
from beanie.operators import Set


async def insert_user_data(user, full_user):
    status = type(user.status).__name__ if user.status else None
    was_online = (
        getattr(user.status, "was_online", None)
        if isinstance(user.status, UserStatusOffline)
        else None
    )

    return await TGUser.find_one(TGUser.tg_id == user.id).upsert(
        Set(
            {
                TGUser.first_name: user.first_name,
                TGUser.last_name: getattr(user, "last_name", None),
                TGUser.username: getattr(user, "username", None),
                TGUser.phone: getattr(user, "phone", None),
                TGUser.lang_code: getattr(user, "lang_code", None),
                TGUser.premium: getattr(user, "premium", False),
                TGUser.emoji_status: getattr(user, "emoji_status", None),
                TGUser.status: status,
                TGUser.was_online: was_online,
                TGUser.support: getattr(user, "support", False),
                TGUser.verified: getattr(user, "verified", False),
                TGUser.fake: getattr(user, "fake", False),
                TGUser.scam: getattr(user, "scam", False),
                TGUser.restricted: getattr(user, "restricted", False),
                TGUser.restriction_reason: getattr(user, "restriction_reason", None),
                TGUser.deleted: getattr(user, "deleted", False),
                TGUser.stories_unavailable: getattr(user, "stories_unavailable", False),
                TGUser.stories_hidden: getattr(user, "stories_hidden", False),
                TGUser.about: getattr(full_user, "about", None),
                TGUser.birthday: getattr(full_user, "birthday", None),
                TGUser.private_forward_name: getattr(
                    full_user, "private_forward_name", None
                ),
                TGUser.contact_require_premium: getattr(
                    full_user, "contact_require_premium", False
                ),
                TGUser.phone_calls_available: getattr(
                    full_user, "phone_calls_available", False
                ),
                TGUser.phone_calls_private: getattr(
                    full_user, "phone_calls_private", False
                ),
                TGUser.personal_channel_id: getattr(
                    full_user, "personal_channel_id", None
                ),
                TGUser.personal_channel_message: getattr(
                    full_user, "personal_channel_message", None
                ),
                TGUser.business_away_message: getattr(
                    full_user, "business_away_message", None
                ),
                TGUser.business_greeting_message: getattr(
                    full_user, "business_greeting_message", None
                ),
                TGUser.business_intro: getattr(full_user, "business_intro", None),
                TGUser.business_location: getattr(full_user, "business_location", None),
                TGUser.business_work_hours: getattr(
                    full_user, "business_work_hours", None
                ),
            }
        ),
        on_insert=TGUser(
            tg_id=user.id,
            first_name=user.first_name,
            last_name=getattr(user, "last_name", None),
            username=getattr(user, "username", None),
            phone=getattr(user, "phone", None),
            lang_code=getattr(user, "lang_code", None),
            premium=getattr(user, "premium", False),
            emoji_status=getattr(user, "emoji_status", None),
            status=status,
            was_online=was_online,
            support=getattr(user, "support", False),
            verified=getattr(user, "verified", False),
            fake=getattr(user, "fake", False),
            scam=getattr(user, "scam", False),
            restricted=getattr(user, "restricted", False),
            restriction_reason=getattr(user, "restriction_reason", None),
            deleted=getattr(user, "deleted", False),
            stories_unavailable=getattr(user, "stories_unavailable", False),
            stories_hidden=getattr(user, "stories_hidden", False),
            about=getattr(full_user, "about", None),
            birthday=getattr(full_user, "birthday", None),
            private_forward_name=getattr(full_user, "private_forward_name", None),
            contact_require_premium=getattr(
                full_user, "contact_require_premium", False
            ),
            phone_calls_available=getattr(full_user, "phone_calls_available", False),
            phone_calls_private=getattr(full_user, "phone_calls_private", False),
            personal_channel_id=getattr(full_user, "personal_channel_id", None),
            personal_channel_message=getattr(
                full_user, "personal_channel_message", None
            ),
            business_away_message=getattr(full_user, "business_away_message", None),
            business_greeting_message=getattr(
                full_user, "business_greeting_message", None
            ),
            business_intro=getattr(full_user, "business_intro", None),
            business_location=getattr(full_user, "business_location", None),
            business_work_hours=getattr(full_user, "business_work_hours", None),
        ),
    )


async def insert_bot_data(user, full_user):
    bot_info = full_user.bot_info
    if not bot_info:
        return

    return await TGBot.find_one(TGBot.tg_id == user.id).upsert(
        Set(
            {
                TGBot.first_name: user.first_name,
                TGBot.last_name: getattr(user, "last_name", None),
                TGBot.username: getattr(user, "username", None),
                TGBot.about: getattr(full_user, "about", None),
                TGBot.bot_active_users: getattr(user, "bot_active_users", None),
                TGBot.description: getattr(bot_info, "description", None),
                TGBot.description_document: getattr(
                    bot_info, "description_document", None
                ),
                TGBot.user_id: getattr(bot_info, "user_id", None),
                TGBot.privacy_policy_url: getattr(bot_info, "privacy_policy_url", None),
                TGBot.bot_info_version: getattr(user, "bot_info_version", None),
                TGBot.commands: (
                    [command.command for command in bot_info.commands]
                    if bot_info.commands
                    else None
                ),
                TGBot.menu_button: getattr(bot_info, "menu_button", None),
            }
        ),
        on_insert=TGBot(
            tg_id=user.id,
            first_name=user.first_name,
            last_name=getattr(user, "last_name", None),
            username=getattr(user, "username", None),
            about=getattr(full_user, "about", None),
            bot_active_users=getattr(user, "bot_active_users", None),
            description=getattr(bot_info, "description", None),
            description_document=getattr(bot_info, "description_document", None),
            user_id=getattr(bot_info, "user_id", None),
            privacy_policy_url=getattr(bot_info, "privacy_policy_url", None),
            bot_info_version=getattr(user, "bot_info_version", None),
            commands=(
                [command.command for command in bot_info.commands]
                if bot_info.commands
                else None
            ),
            menu_button=getattr(bot_info, "menu_button", None),
        ),
    )
