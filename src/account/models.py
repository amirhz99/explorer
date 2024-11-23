from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional,TYPE_CHECKING
from beanie import Document, Link, Update, before_event,Indexed
from pydantic import Field

class TGAccount(Document):
    tg_id: Optional[int]
    session_string: Indexed(str,unique=True) # type: ignore
    api_id: int  
    api_hash: str 
    phone_number: Optional[str]
    
    # Basic user information
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    date_of_birth: Optional[str]  # You could parse this as `datetime` if needed
    date_of_birth_integrity: Optional[str]
    is_premium: Optional[bool]
    has_profile_pic: Optional[bool]
    sex: Optional[int]

    # System and application details
    sdk: Optional[str]
    device: Optional[str]
    app_version: Optional[str]
    system_lang_pack: Optional[str]
    lang_pack: Optional[str]
    lang_code: Optional[str]

    # Two-factor authentication and security
    twoFA: Optional[str]

    # Session and spam control
    spamblock: Optional[str]
    spamblock_end_date: Optional[str]
    stats_spam_count: Optional[int]
    stats_invites_count: Optional[int]

    # Dates and times
    last_connect_date: Optional[datetime]
    session_created_date: Optional[datetime]
    register_time: Optional[int]
    last_check_time: Optional[int]

    # Proxy and network information
    proxy: Optional[List[Any]]
    ipv6: Optional[bool] = False
    tz_offset: Optional[int]
    
    flood_wait: Optional[Dict[str,datetime]] = {}
    # Program-related information
    is_active: bool = True
    # is_processing: bool = False
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    class Settings:
        name = "tg_accounts"
        use_state_management = True
        
        @before_event(Update)
        def update_time(self):
            self.updated_at = datetime.now()