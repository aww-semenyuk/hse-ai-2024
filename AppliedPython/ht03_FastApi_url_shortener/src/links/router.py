from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_cache.decorator import cache
from fastapi_cache.coder import JsonCoder
from sqlmodel import Session, select, func
from pydantic import HttpUrl
import datetime
import random
import string

from links.schemas import ShortURL, RequestLog, URLCreate, URLResponse, StatsResponse
from database import get_db
from auth.schemas import User
from auth.router import get_current_user

def generate_short_code():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))

router = APIRouter(prefix='/links')

@router.post("/shorten", response_model=URLResponse)
def shorten(data: URLCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    custom_alias = data.custom_alias
    original_url = str(data.original_url)
    user_id=user.id
    expires_at=data.expires_at

    if custom_alias:
        if db.query(ShortURL).filter(ShortURL.short_code == custom_alias).first():
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Custom alias already taken")
        short_code = custom_alias
    else:
        for _ in range(3):
            short_code = generate_short_code()
            if not db.query(ShortURL).filter(ShortURL.short_code == short_code).first():
                break
        else:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Failed to generate unique short code")

    db_url = ShortURL(original_url=original_url, short_code=short_code, user_id=user_id, expires_at=expires_at)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return db_url

def key_builder_search(func, *args, **kwargs):
    return f"{func.__name__}:{str(kwargs.get('original_url'))}"

@router.get("/search", response_model=list[URLResponse])
@cache(expire=60, key_builder=key_builder_search, coder=JsonCoder)
async def search(original_url: HttpUrl, db: Session = Depends(get_db)):
    original_url = str(original_url)
    return [URLResponse.model_validate_json(result.model_dump_json()) for result in db.query(ShortURL).filter(ShortURL.original_url == original_url).all()]

def key_builder_stats(func, *args, **kwargs):
    return f"{func.__name__}:{kwargs.get('short_code')}"

@router.get("/{short_code}/stats", response_model=StatsResponse)
@cache(expire=60, key_builder=key_builder_stats, coder=JsonCoder)
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    db_url = db.query(ShortURL).filter(ShortURL.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    num_requests = db.query(RequestLog).filter(RequestLog.short_code == short_code).count()
    
    statement = select(func.max(RequestLog.request_timestamp)).where(RequestLog.short_code == short_code)
    last_requested = db.exec(statement).one_or_none()

    return StatsResponse(short_code=short_code, created_at=db_url.created_at, last_requested=last_requested, num_requests=num_requests)

@router.get("/{short_code}", responses={status.HTTP_307_TEMPORARY_REDIRECT: {"description": "Temporary Redirect"}})
@cache(expire=60)
def get_by_short_code(short_code: str, db: Session = Depends(get_db)):
    db_log = RequestLog(short_code=short_code)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    db_url = db.query(ShortURL).filter(ShortURL.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    if db_url.expires_at and db_url.expires_at < datetime.datetime.utcnow():
        db.delete(db_url)
        db.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="URL expired")

    return RedirectResponse(url=db_url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.delete("/{short_code}")
def delete_by_short_code(short_code: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_url = db.query(ShortURL).filter(ShortURL.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    if user.id != db_url.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Removal is only granted for creator")
    
    db.delete(db_url)
    db.commit()

    return {"message": "Short URL deleted"}

@router.put("/{short_code}", response_model=URLResponse)
def update_by_short_code(short_code: str, new_url: HttpUrl, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_url = db.query(ShortURL).filter(ShortURL.short_code == short_code).first()
    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    if user.id != db_url.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Editing is only granted for creator")

    db_url.original_url = str(new_url)
    db.commit()
    db.refresh(db_url)

    return db_url
