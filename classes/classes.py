from dataclasses import dataclass
from datetime import datetime


@dataclass
class Category:
    category_id: int
    category_name: str
    goodtypes_count: int


@dataclass
class GoodType:
    goodtype_id: int
    article: int
    name: str
    category_name: str
    measure_unit: str
    available_units: int
    booked_units: int
    sell_price: int


@dataclass
class OrderLine:
    line_id: int
    goodtype: GoodType
    quantity: int
    price: int


@dataclass
class Order:
    order_id: int
    created_at: datetime
    status: str
    lines: list[OrderLine]
    total_price: int


@dataclass
class User:
    u_id: int
    password_hash: str
    username: str
    real_name: str
    role: str
