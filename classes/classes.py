from dataclasses import dataclass
from datetime import datetime
import enum


class UserRole(enum.Enum):
    CUSTOMER = "customer"
    WORKER = "worker"
    SALES_MANAGER = "sales_manager"
    SUPPLY_MANAGER = "supply_manager"

    @staticmethod
    def to_name(r) -> str:
        r1 = UserRole(r)
        return {
            UserRole.CUSTOMER: "Покупатель",
            UserRole.WORKER: "Работник склада",
            UserRole.SALES_MANAGER: "Менеджер по продажам",
            UserRole.SUPPLY_MANAGER: "Менеджер по закупкам",
        }[r1]


class OrderStatus(enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

    @staticmethod
    def to_color(val: str):
        val1 = OrderStatus(val)
        match val1:
            case OrderStatus.UNPAID:
                return "var(--bs-primary)"
            case OrderStatus.PAID:
                return "var(--bs-warning)"
            case OrderStatus.SHIPPED:
                return "var(--bs-success)"
            case OrderStatus.CANCELLED:
                return "var(--bs-danger)"

    @staticmethod
    def to_name(val: str):
        val1 = OrderStatus(val)
        match val1:
            case OrderStatus.UNPAID:
                return "Не оплачен"
            case OrderStatus.PAID:
                return "Оплачен"
            case OrderStatus.SHIPPED:
                return "Отгружен"
            case OrderStatus.CANCELLED:
                return "Аннулирован"


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
    status: OrderStatus
    lines: list[OrderLine]
    total_price: int
    customer_name: str


@dataclass
class User:
    u_id: int
    password_hash: str
    username: str
    real_name: str
    role: UserRole


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
