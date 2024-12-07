from dataclasses import dataclass
from datetime import datetime
import enum


class UserRole(enum.Enum):
    CUSTOMER = "customer"
    SALES_MANAGER = "sales_manager"
    SUPPLY_MANAGER = "supply_manager"
    BOSS_OF_THE_GYM = "boss"

    @staticmethod
    def to_name(r) -> str:
        return {
            UserRole.CUSTOMER: "Покупатель",
            UserRole.SALES_MANAGER: "Менеджер по продажам",
            UserRole.SUPPLY_MANAGER: "Менеджер по закупкам",
            UserRole.BOSS_OF_THE_GYM: "Начальник",
        }[r]


class OrderStatus(enum.Enum):
    UNFORMED = "unformed"
    GOT_PAYMENT = "got_payment_unshipped"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

    @staticmethod
    def to_color(val: str):
        val = OrderStatus(val)
        match val:
            case OrderStatus.UNFORMED:
                return "var(--bs-primary)"
            case OrderStatus.GOT_PAYMENT:
                return "var(--bs-warning)"
            case OrderStatus.SHIPPED:
                return "var(--bs-success)"
            case OrderStatus.CANCELLED:
                return "var(--bs-danger)"

        raise ValueError(f"{val} is not allowed as order status")


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


@dataclass
class ReportType:
    id: int
    name: str
    params: list[
        tuple[str, str]
    ]  # Список кортежей типа (Название параметра; Тип параметра)
    values: list[str]
    procedure_name: str
    get_sql: str
