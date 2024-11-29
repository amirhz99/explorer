from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Response,
    UploadFile,
    status,
    Query,
)
from fastapi import FastAPI, UploadFile, File, HTTPException
from beanie import PydanticObjectId, init_beanie
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from src.explore.models import Explore
from src.account.schemas import ProcessingInfo, TGAccountListResponse, TGAccountResponse
from src.account.models import TGAccount
from src.account.utils import extract_zip
from src.account.services import convert_session_to_string
import os
import tempfile
import json

account_router = APIRouter()

DEFAULT_API_ID = 2040
DEFAULT_API_HASH = "b18441a1ff607e10a989891a5462e627"

# Route for getting one account
@account_router.get("/{account_id}", response_model=TGAccountResponse)
async def get_account_details(account_id: PydanticObjectId):
    """
    Get detailed information about a single account and its processing status.
    """
    account = await TGAccount.get(account_id, fetch_links=True)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return TGAccountResponse(
        id=account.id,
        tg_id=account.tg_id,
        session_string=account.session_string,
        phone_number=account.phone_number,
        first_name=account.first_name,
        last_name=account.last_name,
        username=account.username,
        flood_wait=account.flood_wait,
        is_active=account.is_active,
        updated_at=account.updated_at,
        created_at=account.created_at,
        processing_info=account.processes,
    )


# Route for getting all accounts
@account_router.get("", response_model=TGAccountListResponse)
async def get_all_accounts(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(10, ge=1, description="Limit the number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip for pagination"),
):
    """
    Get a list of all accounts with optional filters and pagination.
    """
    query = {}
    if is_active is not None:
        query["is_active"] = is_active

    # Query all accounts with optional filtering and pagination
    accounts = (
        await TGAccount.find(query, fetch_links=True).skip(skip).limit(limit).to_list()
    )

    # Build response
    return TGAccountListResponse(
        accounts=[
            TGAccountResponse(
                id=account.id,
                tg_id=account.tg_id,
                session_string=account.session_string,
                phone_number=account.phone_number,
                first_name=account.first_name,
                last_name=account.last_name,
                username=account.username,
                flood_wait=account.flood_wait,
                is_active=account.is_active,
                updated_at=account.updated_at,
                created_at=account.created_at,
                processing_info=account.processes,
            )
            for account in accounts
        ]
    )


@account_router.delete("/{account_id}")
async def get_account_details(account_id: PydanticObjectId):
    """
    Set account is active false
    """
    account = await TGAccount.get(account_id, fetch_links=True)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.is_active = False
    await account.save()
    
    return {"message":"account deleted successfuly"}


@account_router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Save uploaded ZIP to a temporary directory
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, file.filename)

    with open(zip_path, "wb") as f:
        f.write(await file.read())

    # Extract files from ZIP
    extracted_files = extract_zip(zip_path, temp_dir)

    # Iterate through each session/JSON pair
    for name, files in extracted_files.items():
        session_path = files.get("session")
        json_path = files.get("json")

        if not session_path:
            raise HTTPException(
                status_code=400, detail=f"Missing session file for '{name}'."
            )

        # Default API credentials
        api_id = DEFAULT_API_ID
        api_hash = DEFAULT_API_HASH
        account_data = {}

        # Load JSON if available and extract values
        if json_path:
            with open(json_path, "r") as f:
                account_data = json.load(f)
                api_id = account_data.get("app_id", api_id) or account_data.get(
                    "api_id", api_id
                )
                api_hash = account_data.get("app_hash", api_hash) or account_data.get(
                    "api_id", api_id
                )

        # Convert session file to session string
        session_string = await convert_session_to_string(session_path, api_id, api_hash)

        # Create TGAccount document with available data
        tg_account = TGAccount(
            session_string=session_string,
            api_id=api_id,
            api_hash=api_hash,
            tg_id=account_data.get("id") or account_data.get("user_id"),
            phone_number=account_data.get("phone"),
            first_name=account_data.get("first_name"),
            last_name=account_data.get("last_name"),
            username=account_data.get("username"),
            date_of_birth=account_data.get("date_of_birth"),
            date_of_birth_integrity=account_data.get("date_of_birth_integrity"),
            is_premium=account_data.get("is_premium"),
            has_profile_pic=account_data.get("has_profile_pic"),
            sex=account_data.get("sex"),
            sdk=account_data.get("sdk"),
            device=account_data.get("device"),
            app_version=account_data.get("app_version"),
            system_lang_pack=account_data.get("system_lang_pack"),
            lang_pack=account_data.get("lang_pack"),
            lang_code=account_data.get("lang_code"),
            twoFA=account_data.get("twoFA"),
            spamblock=account_data.get("spamblock"),
            spamblock_end_date=account_data.get("spamblock_end_date"),
            stats_spam_count=account_data.get("stats_spam_count"),
            stats_invites_count=account_data.get("stats_invites_count"),
            last_connect_date=account_data.get("last_connect_date"),
            session_created_date=account_data.get("session_created_date"),
            register_time=account_data.get("register_time"),
            last_check_time=account_data.get("last_check_time"),
            proxy=account_data.get("proxy"),
            ipv6=account_data.get("ipv6", False),
            tz_offset=account_data.get("tz_offset"),
        )

        # Insert the account into the database
        await tg_account.insert()

    # Cleanup temporary files
    os.remove(zip_path)
    for files in extracted_files.values():
        for file in files.values():
            if file:
                os.remove(file)

    return JSONResponse(
        content={
            "detail": "All accounts successfully uploaded and stored.",
        },
        status_code=200,
    )
