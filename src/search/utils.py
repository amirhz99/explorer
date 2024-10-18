from fastapi import FastAPI, HTTPException
from beanie import PydanticObjectId
from typing import List, Dict, Any, Optional, Tuple, TypeVar
from src.explore.models import Explore, TGChat, TGUser, TGBot
from src.search.models import Search
from math import ceil
import re

T = TypeVar("T")  # Generic type for paginated data


def paginate(
    data: List[T], page: int, limit: int
) -> Tuple[List[T], int, int, Optional[int], Optional[int]]:
    """Paginate the given data."""
    total_count = len(data)
    total_pages = ceil(total_count / limit)

    # Ensure page and limit are within valid range
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    start = (page - 1) * limit
    end = start + limit

    # Get paginated data
    paginated_data = data[start:end]

    # Calculate next and previous pages
    next_page = page + 1 if page < total_pages else None
    previous_page = page - 1 if page > 1 else None

    return paginated_data, total_count, total_pages, next_page, previous_page


def merge_and_deduplicate(
    real_time: List[Dict[str, Any]], historical: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Merge real-time and historical results, remove duplicates, and tag them."""
    merged = {item["tg_id"]: item for item in historical}

    for item in real_time:
        item["source"] = "real_time"
        merged[item["tg_id"]] = item

    return list(merged.values())


def get_match_score(item: Dict[str, Any], search: Search) -> Tuple[int, int]:
    """Calculate match score based on search criteria."""
    primary = search.primary.lower()
    secondaries = [s.lower() for s in search.secondaries]

    primary_in_main_fields = (
        primary in (item.get("title", "") or "").lower()
        or primary in (item.get("first_name", "") or "").lower()
        or primary in (item.get("last_name", "") or "").lower()
        or primary in (item.get("username", "") or "").lower()
        or any(primary in u.lower() for u in (item.get("usernames") if item.get("usernames") else []))
    )

    secondary_in_main_fields = [
        s
        for s in secondaries
        if (
            s in (item.get("title", "") or "").lower()
            or s in (item.get("first_name", "") or "").lower()
            or s in (item.get("last_name", "") or "").lower()
            or s in (item.get("username", "") or "").lower()
            or any(s in u.lower() for u in (item.get("usernames") if item.get("usernames") else []))
        )
    ]

    primary_in_about = primary in (item.get("about", "") or "").lower()
    secondaries_in_about = [
        s for s in secondaries if (s in (item.get("about", "") or "").lower())
    ]

    if primary_in_main_fields:
        return (0, -len(secondary_in_main_fields))  
    elif primary_in_about:
        return (1, -len(secondaries_in_about))
    elif secondary_in_main_fields:
        return (2, -len(secondary_in_main_fields))
    elif secondaries_in_about:
        return (2, -len(secondaries_in_about))
    else:
        return (3,0)


def is_english(text: str) -> bool:
    """Check if the given text contains only English characters."""
    return bool(re.match(r"^[a-zA-Z0-9_ ]*$", text))
