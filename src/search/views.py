import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from beanie import PydanticObjectId
from starlette.responses import JSONResponse
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
    UploadFile,
)
from src.explore.services import create_explore_task
from src.chat.models import TGChat
from src.search.schemas import (
    Pagination,
    SearchRequest,
    SearchResponse,
    SearchStatusResponse,
    TGBotResponse,
    TGChatResponse,
    TGUserResponse,
    TaskSummary,
)
from src.search.utils import (
    get_match_score,
    is_english,
    merge_and_deduplicate,
    paginate,
)
from src.explore import Explore, OperationsStatus
from src.search.models import Search
from src.user.models import TGBot, TGUser

search_router = APIRouter()


@search_router.post("/")
async def create_search(request: SearchRequest):
    search = Search(
        primary=request.primary,
        secondaries=request.secondaries,
        real_time=request.real_time,
        accounts_count=1,
        depth=1,
    )
    await search.insert()

    if request.real_time:
        explore = Explore(
            request=search,
            target=request.primary,
            accounts_count=1,
            status=OperationsStatus.pending,
            is_primary=True,
        )
        await explore.insert()

        if request.value > 0:
            await create_explore_task(search)

    return JSONResponse(
        content={"message": "Searching...", "search_id": str(search.id)},
        status_code=200,
    )


@search_router.get("/{search_id}/status", response_model=SearchStatusResponse)
async def get_search_status(search_id: PydanticObjectId) -> SearchStatusResponse:

    search = await Search.get(search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    explores = await Explore.find(Explore.request.id == search.id).to_list()

    if not explores:
        raise HTTPException(
            status_code=404, detail="No Explore tasks found for this Search request"
        )

    total_tasks = len(explores)
    completed_tasks = sum(
        1 for exp in explores if exp.status == OperationsStatus.completed
    )
    failed_tasks = sum(1 for exp in explores if exp.status == OperationsStatus.failed)
    in_process_tasks = sum(
        1 for exp in explores if exp.status == OperationsStatus.in_process
    )
    pending_tasks = sum(1 for exp in explores if exp.status == OperationsStatus.pending)

    completed_percentage = (
        ((completed_tasks + failed_tasks) / total_tasks) * 100 if total_tasks > 0 else 0
    )

    if completed_tasks == total_tasks:
        search_status = OperationsStatus.completed
    elif failed_tasks == total_tasks:
        search_status = OperationsStatus.failed
    elif in_process_tasks == 0 and pending_tasks == 0:
        search_status = OperationsStatus.completed
    else:
        search_status = search.status

    search.status = search_status
    await search.save_changes()

    return SearchStatusResponse(
        search_id=str(search.id),
        status=search_status,
        completed_percentage=completed_percentage,
        total_tasks=total_tasks,
        tasks_summary=TaskSummary(
            completed=completed_tasks,
            failed=failed_tasks,
            in_process=in_process_tasks,
            pending=pending_tasks,
        ),
    )


@search_router.get("/{search_id}", response_model=Pagination)
async def get_search_results(
    search_id: PydanticObjectId,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
):
    search = await Search.get(search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    explores = await Explore.find(
        Explore.request.id == search_id, fetch_links=True
    ).to_list()

    chats = [
        link
        for explore in explores
        for link in explore.results
        if isinstance(link, TGChat)
    ]
    users = [
        link
        for explore in explores
        for link in explore.results
        if isinstance(link, TGUser)
    ]
    bots = [
        link
        for explore in explores
        for link in explore.results
        if isinstance(link, TGBot)
    ]

    real_time_results = (
        [{**TGChatResponse(**chat.model_dump()).model_dump()} for chat in chats]
        + [{**TGUserResponse(**user.model_dump()).model_dump()} for user in users]
        + [{**TGBotResponse(**bot.model_dump()).model_dump()} for bot in bots]
    )

    primary_and_secondaries = [search.primary] + search.secondaries

    if all(is_english(term) for term in primary_and_secondaries):
        chat_search_fields = (
            [
                {"title": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"username": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"usernames": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"about": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
        )
        user_search_fields = (
            [
                {"first_name": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"last_name": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"username": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"usernames": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"about": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
        )
        bot_search_fields = (
            [
                {"first_name": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"last_name": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"username": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"about": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
        )
    else:
        chat_search_fields = [
            {"title": {"$regex": term, "$options": "i"}}
            for term in primary_and_secondaries
        ] + [
            {"about": {"$regex": term, "$options": "i"}}
            for term in primary_and_secondaries
        ]
        user_search_fields = (
            [
                {"first_name": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"last_name": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"about": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
        )
        bot_search_fields = (
            [
                {"first_name": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"last_name": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
            + [
                {"about": {"$regex": term, "$options": "i"}}
                for term in primary_and_secondaries
            ]
        )

    matching_chats = await TGChat.find({"$or": chat_search_fields}).to_list()
    matching_users = await TGUser.find({"$or": user_search_fields}).to_list()
    matching_bots = await TGBot.find({"$or": bot_search_fields}).to_list()

    historical_results = (
        [
            {**TGChatResponse(**chat.model_dump()).model_dump()}
            for chat in matching_chats
        ]
        + [
            {**TGUserResponse(**user.model_dump()).model_dump()}
            for user in matching_users
        ]
        + [{**TGBotResponse(**bot.model_dump()).model_dump()} for bot in matching_bots]
    )

    # Step 1: Find related searches (exclude the current search by id)
    related_searches = await Search.find(
        {"primary": {"$regex": search.primary, "$options": "i"}, "real_time": True}
    ).to_list()
    related_searches = [
        s for s in related_searches if s.id != search_id
    ]  # Exclude current search

    # Step 2: Get explores from related searches (no current search explores here)
    related_explores = []
    for related_search in related_searches:
        related_explores.extend(
            await Explore.find(
                Explore.request.id == related_search.id, fetch_links=True
            ).to_list()
        )

    # Add related explores to historical results
    historical_results.extend(
        [
            {**TGChatResponse(**chat.model_dump()).model_dump()}
            for explore in related_explores
            for chat in explore.results
            if isinstance(chat, TGChat)
        ]
        + [
            {**TGUserResponse(**user.model_dump()).model_dump()}
            for explore in related_explores
            for user in explore.results
            if isinstance(user, TGUser)
        ]
        + [
            {**TGBotResponse(**bot.model_dump()).model_dump()}
            for explore in related_explores
            for bot in explore.results
            if isinstance(bot, TGBot)
        ]
    )

    merged_results = merge_and_deduplicate(real_time_results, historical_results)
    sorted_results = sorted(merged_results, key=lambda x: get_match_score(x, search))

    paginated_results, total_count, total_pages, next_page, prev_page = paginate(
        sorted_results, page, limit
    )

    return Pagination(
        data=paginated_results,
        page=page,
        limit=limit,
        total_count=total_count,
        total_pages=total_pages,
        next_page=next_page,
        previous_page=prev_page,
    )


@search_router.get("/", response_model=List[SearchResponse])
async def get_searches(
    descending: bool = True, status: Optional[OperationsStatus] = None
):
    """
    Fetch a list of searches sorted by the updated_at field.

    Args:
        descending (bool): Whether to sort in descending order. Defaults to True.

    Returns:
        List[SearchResponse]: List of sorted Search documents in the response schema.
    """

    sort_order = -1 if descending else 1  # -1 for descending, 1 for ascending
    filters = {"is_active": True}
    if status is not None:
        filters["status"] = status

    searches = (
        await Search.find_many(filters).sort((Search.updated_at, sort_order)).to_list()
    )
    # Convert Search documents to SearchResponse format
    response = [
        SearchResponse(
            id=search.id,
            primary=search.primary,
            secondaries=search.secondaries,
            real_time=search.real_time,
            depth=search.depth,
            accounts_count=search.accounts_count,
            status=search.status.value,  # Convert Enum to string
            updated_at=search.updated_at,
            created_at=search.created_at,
        )
        for search in searches
    ]
    return response
