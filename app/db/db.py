import datetime
from itertools import count

from app.models.item import ItemCreate, ItemRead, ItemUpdate
from app.models.user import UserCreate, UserInDB, UserRead


class ItemDB:
    """Simple in-memory repository for tutorial purposes."""

    def __init__(self) -> None:
        self._items: dict[int, ItemRead] = {}
        self._id_counter = count(start=1)

    def create(self, payload: ItemCreate) -> ItemRead:
        new_id = next(self._id_counter)
        item = ItemRead(
            id=new_id,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            **payload.model_dump()
        )
        self._items[new_id] = item
        return item

    def list(self) -> list[ItemRead]:
        return list(self._items.values())

    def get(self, item_id: int) -> ItemRead | None:
        return self._items.get(item_id)

    def update(self, item_id: int, changes: ItemUpdate) -> ItemRead | None:
        existing = self._items.get(item_id)
        if not existing:
            return None
        data = existing.model_dump()
        diff = changes.model_dump(exclude_unset=True)
        data.update(diff)
        updated = ItemRead(**data)
        self._items[item_id] = updated
        return updated


class UserDB:
    def __init__(self) -> None:
        self._users: dict[str, UserInDB] = {}
        self._id_counter = count(start=1)
        # Seed a couple of users for demos:
        # 'alice' has read-only scope; 'bob' has read+write scopes.
        # Hashing added in security during signup; here we add placeholders.
        self._seed()

    def _seed(self) -> None:
        # Seed without password (set via signup) to keep flow consistent.
        pass

    def create(self, payload: UserCreate, hashed_password: str) -> UserRead:
        username = payload.username
        if username in self._users:
            raise ValueError("User already exists.")
        new_id = next(self._id_counter)
        user_in_db = UserInDB(
            username=username,
            full_name=payload.full_name,
            email=payload.email,
            is_active=payload.is_active,
            scopes=payload.scopes or [],
            hashed_password=hashed_password,
        )
        self._users[username] = user_in_db
        return UserRead(id=new_id, **user_in_db.model_dump(exclude={"hashed_password"}))

    def get_by_username(self, username: str) -> UserInDB | None:
        return self._users.get(username)

    def to_read(self, username: str, user: UserInDB) -> UserRead:
        # Simulate ID assignment by iteration order.
        # In a real DB, you'd persist IDs; for demo, compute index.
        idx = list(self._users).index(username) + 1
        return UserRead(id=idx, **user.model_dump(exclude={"hashed_password"}))


# Singleton-style in-memory database instance for the app lifetime.
ITEM_DB = ItemDB()
USER_DB = UserDB()

"""
/api/v2/store/items/bulk:
sample_items: list of dicts with sample item data for initial population or testing.
    [
        {
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse with USB receiver",
            "price": 799,
            "tags": ["electronics", "mouse", "wireless"],
            "in_stock": true
        },
        {
            "name": "Bluetooth Speaker",
            "description": "Portable speaker with 10 hours battery life",
            "price": 1599,
            "tags": ["audio", "portable", "bluetooth"],
            "in_stock": false
        },
        {
            "name": "Cotton T-shirt",
            "description": "100% cotton, unisex, size M",
            "price": 499,
            "tags": ["clothing", "t-shirt", "cotton"],
            "in_stock": true
        },
        {
            "name": "Stainless Steel Water Bottle",
            "description": "Insulated bottle, keeps drinks cold for 24 hours",
            "price": 650,
            "tags": ["bottle", "insulated", "kitchen"],
            "in_stock": true
        },
        {
            "name": "Yoga Mat",
            "description": "Eco-friendly, non-slip yoga mat",
            "price": 1200,
            "tags": ["fitness", "yoga", "mat"],
            "in_stock": false
        },
        {
            "name": "Notebook",
            "description": "200 pages, ruled, A5 size",
            "price": 150,
            "tags": ["stationery", "notebook", "paper"],
            "in_stock": true
        },
        {
            "name": "LED Desk Lamp",
            "description": "Touch control, dimmable, USB charging",
            "price": 899,
            "tags": ["lamp", "LED", "desk"],
            "in_stock": true
        },
        {
            "name": "Gaming Keyboard",
            "description": "Mechanical RGB keyboard, anti-ghosting",
            "price": 2499,
            "tags": ["electronics", "keyboard", "gaming"],
            "in_stock": false
        },
        {
            "name": "Cooking Oil 1L",
            "description": "Refined sunflower oil, 1 litre pack",
            "price": 110,
            "tags": ["grocery", "oil", "cooking"],
            "in_stock": true
        },
        {
            "name": "Smartphone Case",
            "description": "Shockproof silicone cover for phones",
            "price": 299,
            "tags": ["accessories", "phone", "case"],
            "in_stock": true
        },
        {
            "name": "Power Bank 10000mAh",
            "description": "Fast charging, dual USB output",
            "price": 1199,
            "tags": ["electronics", "powerbank", "charging"],
            "in_stock": false
        },
        {
            "name": "Men's Running Shoes",
            "description": "Lightweight sports shoes, size 9",
            "price": 2099,
            "tags": ["footwear", "running", "men"],
            "in_stock": true
        },
        {
            "name": "Bluetooth Earbuds",
            "description": "True wireless stereo earbuds with mic",
            "price": 1799,
            "tags": ["audio", "earbuds", "wireless"],
            "in_stock": true
        },
        {
            "name": "Children's Story Book",
            "description": "Illustrated fairy tales for kids aged 4-7",
            "price": 350,
            "tags": ["books", "children", "stories"],
            "in_stock": true
        },
        {
            "name": "Ceramic Coffee Mug",
            "description": "Dishwasher-safe, 350ml capacity",
            "price": 220,
            "tags": ["kitchen", "mug", "ceramic"],
            "in_stock": false
        }
    ]

"""

"""
/api/v1/auth/signup sample data:

{
    "username": "hari",
    "full_name": "poojary",
    "email": "hari@example.com",
    "is_active": true,
    "scopes": [
        "items:read", "items:write"
    ],
    "password": "haridx"
}
"""
