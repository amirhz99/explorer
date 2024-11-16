from src.user.models import TGBot, TGUser
from telethon.tl.types import (
    UserStatusOffline,
)
from beanie.operators import Set
from datetime import datetime


async def insert_user_data(user, full_user):
    status = type(user.status).__name__ if user.status else None
    was_online = (
        getattr(user.status, "was_online", None)
        if isinstance(user.status, UserStatusOffline)
        else None
    )

    await TGUser.find_one(TGUser.tg_id == user.id).upsert(
        Set(
            {
                TGUser.first_name: user.first_name,
                TGUser.last_name: getattr(user, "last_name", None),
                TGUser.username: getattr(user, "username", None),
                TGUser.usernames: (
                    (item.username for item in user.usernames)
                    if getattr(user, "usernames", False)
                    else None
                ),
                TGUser.phone: getattr(user, "phone", None),
                TGUser.lang_code: getattr(user, "lang_code", None),
                TGUser.premium: getattr(user, "premium", False),
                TGUser.emoji_status: (
                    user.emoji_status.document_id
                    if getattr(user, "emoji_status", None)
                    else None
                ),
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
                TGUser.birthday: (
                    (
                        datetime(
                            year=full_user.birthday.year,
                            month=full_user.birthday.month,
                            day=full_user.birthday.day,
                        )
                        if full_user.birthday.year
                        else None
                    )
                    if getattr(full_user, "birthday", None)
                    else None
                ),
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
                TGUser.business_intro: (
                    {
                        "title": full_user.business_intro.title,
                        "description": full_user.business_intro.description,
                    }
                    if getattr(full_user, "business_intro", None)
                    else None
                ),
                TGUser.business_location: (
                    {
                        "address": full_user.business_location.address,
                        "geo_point": full_user.business_location.geo_point,
                    }
                    if getattr(full_user, "business_location", None)
                    else None
                ),
                TGUser.business_work_hours: (
                    {
                        "timezone_id": full_user.business_work_hours.timezone_id,
                        "weekly_open": full_user.business_work_hours.weekly_open,
                        "open_now": full_user.business_work_hours.open_now,
                    }
                    if getattr(full_user, "business_work_hours", None)
                    else None
                ),
            }
        ),
        on_insert=TGUser(
            tg_id=user.id,
            first_name=user.first_name,
            last_name=getattr(user, "last_name", None),
            username=getattr(user, "username", None),
            usernames=(
                (item.username for item in user.usernames)
                if getattr(user, "usernames", False)
                else None
            ),
            phone=getattr(user, "phone", None),
            lang_code=getattr(user, "lang_code", None),
            premium=getattr(user, "premium", False),
            emoji_status=(
                user.emoji_status.document_id
                if getattr(user, "emoji_status", None)
                else None
            ),
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
            birthday=(
                (
                    datetime(
                        year=full_user.birthday.year,
                        month=full_user.birthday.month,
                        day=full_user.birthday.day,
                    )
                    if full_user.birthday.year
                    else None
                )
                if getattr(full_user, "birthday", None)
                else None
            ),
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
            business_intro=(
                {
                    "title": full_user.business_intro.title,
                    "description": full_user.business_intro.description,
                }
                if getattr(full_user, "business_intro", None)
                else None
            ),
            business_location=(
                {
                    "address": full_user.business_location.address,
                    "geo_point": full_user.business_location.geo_point,
                }
                if getattr(full_user, "business_location", None)
                else None
            ),
            business_work_hours=(
                {
                    "timezone_id": full_user.business_work_hours.timezone_id,
                    "weekly_open": full_user.business_work_hours.weekly_open,
                    "open_now": full_user.business_work_hours.open_now,
                }
                if getattr(full_user, "business_work_hours", None)
                else None
            ),
        ),
    )

    return await TGUser.find_one(TGUser.tg_id == user.id)


async def insert_bot_data(user, full_user):
    bot_info = full_user.bot_info
    if not bot_info:
        return

    await TGBot.find_one(TGBot.tg_id == user.id).upsert(
        Set(
            {
                TGBot.first_name: user.first_name,
                TGBot.last_name: getattr(user, "last_name", None),
                TGBot.username: getattr(user, "username", None),
                TGBot.about: getattr(full_user, "about", None),
                TGBot.bot_active_users: getattr(user, "bot_active_users", None),
                TGBot.description: getattr(bot_info, "description", None),
                TGBot.user_id: getattr(bot_info, "user_id", None),
                TGBot.privacy_policy_url: getattr(bot_info, "privacy_policy_url", None),
                TGBot.bot_info_version: getattr(user, "bot_info_version", None),
                TGBot.commands: (
                    [command.command for command in bot_info.commands]
                    if bot_info.commands
                    else None
                ),
                TGBot.menu_button: (
                    getattr(bot_info.menu_button, "url", None)
                    if getattr(bot_info, "menu_button", None)
                    else None
                ),
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
            user_id=getattr(bot_info, "user_id", None),
            privacy_policy_url=getattr(bot_info, "privacy_policy_url", None),
            bot_info_version=getattr(user, "bot_info_version", None),
            commands=(
                [command.command for command in bot_info.commands]
                if bot_info.commands
                else None
            ),
            menu_button=(
                getattr(bot_info.menu_button, "url", None)
                if getattr(bot_info, "menu_button", None)
                else None
            ),
        ),
    )

    return await TGBot.find_one(TGBot.tg_id == user.id)
