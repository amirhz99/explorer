from typing import List
from pydantic import BaseModel


class Pagination(BaseModel):
    data: List[BaseModel]
    page: int
    limit: int
    total_count: int
    total_pages: int
    next_page: int|None
    previous_page: int|None
    

