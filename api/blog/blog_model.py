from pydantic import BaseModel
from datetime import datetime
from typing import List


class BlogPost(BaseModel):
    title: str
    content: str
    date: datetime
    tags: List[str]
    is_published: bool
    summary: str

    