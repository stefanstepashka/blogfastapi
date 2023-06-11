from typing import List

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from schemas import BlogPost, BlogPostCreate, Comment, CommentCreate
from models import BlogPost as ModelBlogPost, Comment as ModelComment
from sqlalchemy import or_
from datetime import datetime, timedelta

from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()


@app.post("/posts/", response_model=BlogPost)
def create_post(post: BlogPostCreate, db: Session = Depends(get_db)):
    db_post = ModelBlogPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.post("/posts/{post_id}/comments/", response_model=Comment)
def create_comment_for_post(post_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    # проверка существования поста
    db_post = db.query(ModelBlogPost).filter(ModelBlogPost.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_comment = ModelComment(**comment.dict(), post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@app.get("/posts/", response_model=List[BlogPost])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(ModelBlogPost).offset(skip).limit(limit).all()
    return posts


@app.get('/posts/{post_id}/', response_model=BlogPost)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(ModelBlogPost).filter(ModelBlogPost.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post not Found')
    return db_post


@app.get('/posts/search_query/', response_model=List[BlogPost])
def search_post(query: str, db: Session = Depends(get_db)):
    print(f"Query: {query}")
    posts = db.query(ModelBlogPost).filter(or_(ModelBlogPost.title.contains(query), ModelBlogPost.content.contains(query))).all()
    print(f"Posts: {posts}")
    return posts

# возможность редактирования поста
@app.put("/posts/{post_id}/", response_model=BlogPost)
def update_post(post_id: int, post: BlogPostCreate, db: Session = Depends(get_db)):
    db_post = db.query(ModelBlogPost).filter(ModelBlogPost.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post not Found')
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

# добавляет возможность удаления поста
@app.delete("/posts/{post_id}/", response_model=BlogPost)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(ModelBlogPost).filter(ModelBlogPost.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post not Found')
    db.delete(db_post)
    db.commit()
    return {"detail": "Post Deleted"}


