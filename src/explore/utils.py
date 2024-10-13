from fastapi import FastAPI, HTTPException
from beanie import PydanticObjectId
from typing import List, Dict, Any, Optional, Tuple, TypeVar
from src.explore.models import Search, Explore, TGChat, TGUser, TGBot
from math import ceil

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

    # Check matches in title/first_name/last_name (higher priority)
    title_match = (
        primary in item.get("title", "").lower()
        or primary in item.get("first_name", "").lower()
        or (
            primary in item.get("last_name", "").lower()
            if item.get("last_name", "")
            else ""
        )
    )
    secondary_matches = [
        s
        for s in secondaries
        if s in item.get("title", "").lower()
        or s in item.get("first_name", "").lower()
        or (s in item.get("last_name", "").lower() if item.get("last_name", "") else "")
    ]

    # Check matches in "about" (lower priority)
    about_match = primary in item.get("about", "").lower() if item.get("about", "") else ""
    about_secondary_matches = [
        s for s in secondaries if (s in item.get("last_name", "").lower() if item.get("last_name", "") else "")
    ]

    # Calculate priority: Primary > Secondary > About matches
    if title_match:
        return (
            0,
            -len(secondary_matches),
        )  # Higher priority for primary in title/first_name/last_name
    elif about_match:
        return (1, -len(about_secondary_matches))  # Lower priority for primary in about
    else:
        return (2, 0)  # No match
