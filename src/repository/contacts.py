from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.model import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.born_date = body.born_date
        contact.delete = body.delete
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contact(query: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter(
        (Contact.first_name.ilike(f"%{query}%"))
        | (Contact.last_name.ilike(f"%{query}%"))
        | (Contact.email.ilike(f"%{query}%")),
        Contact.user == user
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def upcoming_birthdays(db: AsyncSession, user: User):
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    stmt = select(Contact).filter(Contact.born_date.between(today, next_week)).filter_by(user=user)
    result = await db.execute(stmt)
    return result.scalars().all()
