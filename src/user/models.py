from datetime import datetime
from typing import List, Optional
from beanie import (
    Document,
    Indexed,
    UnionDoc,
    Link,
    Insert,
    Replace,
    Save,
    SaveChanges,
    Update,
    after_event,
    before_event,
)
from pydantic import Field

class TekegramUserParent(UnionDoc):  # Union
    class Settings:
        name = "tg_users"
        class_id = "_class_id"
        
class TGUser(Document):
    tg_id: Indexed(int, unique=True)  # type: ignore
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    username: Optional[str] = Field(None, description="Username")
    usernames: Optional[str] = Field(None, description="Additional usernames")
    phone: Optional[str] = Field(None, description="Phone number")
    lang_code: Optional[str] = Field(None, description="Language code")
    premium: bool = Field(False, description="Indicates if the user is premium")
    emoji_status: Optional[str] = Field(None, description="Emoji status")
    status: str = Field(..., description="Current status")
    was_online: Optional[datetime] = Field(None, description="Last seen online")
    support: bool = Field(False, description="Indicates if the user is support")
    verified: bool = Field(False, description="Indicates if the user is verified")
    fake: bool = Field(False, description="Indicates if the user is fake")
    scam: bool = Field(False, description="Indicates if the user is a scammer")
    restricted: bool = Field(False, description="Indicates if the user is restricted")
    restriction_reason: Optional[str] = Field(
        None, description="Reason for restriction"
    )
    deleted: bool = Field(False, description="Indicates if the user is deleted")
    stories_unavailable: bool = Field(
        False, description="Indicates if stories are unavailable"
    )
    stories_hidden: bool = Field(False, description="Indicates if stories are hidden")
    about: Optional[str] = Field(None, description="About information")
    birthday: Optional[datetime] = Field(None, description="Birthday")
    private_forward_name: Optional[str] = Field(
        None, description="Private forward name"
    )
    contact_require_premium: bool = Field(False, description="Contact requires premium")
    phone_calls_available: bool = Field(False, description="Phone calls available")
    phone_calls_private: bool = Field(False, description="Phone calls are private")
    personal_channel_id: Optional[int] = Field(None, description="Personal channel ID")
    personal_channel_message: Optional[str] = Field(
        None, description="Personal channel message"
    )
    business_away_message: Optional[str] = Field(
        None, description="Business away message"
    )
    business_greeting_message: Optional[str] = Field(
        None, description="Business greeting message"
    )
    business_intro: Optional[str] = Field(None, description="Business intro")
    business_location: Optional[str] = Field(None, description="Business location")
    business_work_hours: Optional[str] = Field(
        None, description="Business working hours"
    )
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    # Skip items:
        # bot
        # photo
    class Settings:
        name = "users"
        union_doc = TekegramUserParent
        
        @before_event(Update)
        def update_time(self):
            self.updated_at = datetime.now()


class TGBot(Document):
    tg_id: Indexed(int, unique=True)  # type: ignore
    first_name: Optional[str] = Field(None, description="First name of the bot")
    last_name: Optional[str] = Field(None, description="Last name of the bot")
    username: Optional[str] = Field(None, description="Username of the bot")
    about: Optional[str] = Field(None, description="About information")
    verified: bool = Field(False, description="Indicates if the bot is verified")
    bot_active_users: Optional[int] = Field(None, description="Active users of the bot")
    description: Optional[str] = Field(None, description="Description of the bot")
    description_document: Optional[str] = Field(None, description="Description document for the bot")
    user_id: Optional[int] = Field(None, description="ID of the bot's creator")
    commands: Optional[List[str]] = Field(None, description="List of bot commands")
    menu_button: Optional[str] = Field(None, description="Bot menu button configuration")
    privacy_policy_url: Optional[str] = Field(None, description="privacy policy url")    
    bot_info_version:  Optional[int] = Field(None, description="bot version")
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Skip items:
        # full_user.bot_info.description_photo
        # photo
    class Settings:
        name = "bots"
        union_doc = TekegramUserParent
        
        @before_event(Update)
        def update_time(self):
            self.updated_at = datetime.now()