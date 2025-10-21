# Implement CRUD operations that use AsyncSession and convert ORM to Pydantic models.

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.models import Items, Users
from app.models.item import ItemCreate, ItemRead, ItemUpdate
from app.models.user import UserCreate, UserInDB, UserRead


class SQLItemRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: ItemCreate) -> ItemRead:
        obj = Items(**payload.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        await self.session.commit()  # commit the transaction
        return self._to_read(obj)

    async def list(self, q: str | None = None, limit: int = 25) -> list[ItemRead]:
        stmt = select(Items).order_by(Items.id)
        if q:
            stmt = stmt.filter(Items.name.ilike(f"%{q}%"))
        stmt = stmt.limit(limit)
        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        return [self._to_read(r) for r in rows]

    async def get(self, item_id: int) -> ItemRead | None:
        res = await self.session.get(Items, item_id)
        return self._to_read(res) if res else None

    async def update(self, item_id: int, changes: ItemUpdate) -> ItemRead | None:
        obj = await self.session.get(Items, item_id)
        if not obj:
            return None
        data = changes.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(obj, k, v)
        await self.session.flush()
        await self.session.refresh(obj)
        await self.session.commit()  # commit the transaction
        return self._to_read(obj)

    def _to_read(self, obj: Items) -> ItemRead:
        return ItemRead(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            price=obj.price,
            tags=obj.tags,
            in_stock=obj.in_stock,
            created_at=obj.created_at,
        )


class SQLUserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: UserCreate) -> UserRead:
        hashed = get_password_hash(payload.password)
        obj = Users(
            username=payload.username,
            full_name=payload.full_name,
            email=payload.email,
            is_active=payload.is_active,
            scopes=payload.scopes or [],
            hashed_password=hashed,
        )
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        await self.session.commit()  # commit the transaction
        return self._to_read(obj)

    async def get_by_username(self, username: str) -> UserInDB | None:
        stmt = select(Users).where(Users.username == username)
        res = await self.session.execute(stmt)
        obj = res.scalars().first()
        if not obj:
            return None
        return self._to_in_db(obj)

    def _to_read(self, obj: Users) -> UserRead:
        return UserRead(
            id=obj.id,
            username=obj.username,
            full_name=obj.full_name,
            email=obj.email,
            is_active=obj.is_active,
            scopes=obj.scopes,
        )

    def _to_in_db(self, obj: Users) -> UserInDB:
        return UserInDB(
            username=obj.username,
            full_name=obj.full_name,
            email=obj.email,
            is_active=obj.is_active,
            scopes=obj.scopes,
            hashed_password=obj.hashed_password,
        )
