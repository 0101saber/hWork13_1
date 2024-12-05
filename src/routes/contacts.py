from fastapi import APIRouter, HTTPException, status, Depends, Path, Query, File, UploadFile
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.database.db import get_db
from src.entity.model import User
from src.repository import contacts as contacts_repository
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=list[ContactResponse], description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contacts = await contacts_repository.get_contacts(limit=limit, offset=offset, db=db, user=current_user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts_repository.get_contact(contact_id, db, current_user)
    if not contact:
        raise HTTPException()
    pass


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts_repository.create_contact(body=body, db=db, user=current_user)
    return contact


@router.put("/{contact_id}", description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts_repository.update_contact(contact_id, body, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts_repository.delete_contact(contact_id, db, current_user)
    return contact


@router.get("/search", response_model=list[ContactResponse], description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def search_contacts(query: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    contacts = await contacts_repository.search_contact(query, db, current_user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found.")
    return contacts


@router.get("/birthdays", response_model=list[ContactResponse], description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    contacts = await contacts_repository.upcoming_birthdays(db, current_user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No birthdays in the next 7 days.")
    return contacts
