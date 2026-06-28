from typing import List

from pydantic import BaseModel


class SourceBackedItem(BaseModel):
    id: str
    title: str | None = None
    name: str | None = None
    business_domain: str
    summary: str | None = None
    description: str | None = None
    source_links: List[str]
    match_reasons: List[str]


class NewsSummaryResponse(BaseModel):
    business_domain: str
    summary: str
    source_links: List[str]
    item_count: int
