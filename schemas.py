from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import binascii

SECRET_KEY = "1ee73eb5386d6262a6bda668c366de60b5f6eb5fae90c283"

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    date_posted: datetime
    class Config:
        orm_mode = True

class BlogPostBase(BaseModel):
    title: str
    content: str

class BlogPostCreate(BlogPostBase):
    pass

class BlogPost(BlogPostBase):
    id: int
    date_posted: datetime
    comments: List[Comment] = []
    class Config:
        orm_mode = True
