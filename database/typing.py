from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, date, time


@dataclass
class User:
    user_id: int
    login: str
    password: str
    role: str


@dataclass
class Hall:
    id: int
    name: str
    total_seats: int


@dataclass
class HallSchema:
    id: int
    hall: Hall 
    row_num: int
    start_seat: int
    end_seat: int
    base_price: Decimal = Decimal("0.00")


@dataclass
class Film:
    film_id: int
    title: str
    country: str
    year: int
    director: str
    studio: str | None
    duration: int
    description: str | None

@dataclass
class Session:
    session_id: int
    film_id: int
    hall_id: int
    session_date: date = field(default_factory=date.today)
    session_time: time = field(default_factory=lambda: time(0, 0))
    price_coef: Decimal = Decimal("1.00")

@dataclass
class Ticket:
    ticket_id: int 
    session_id: int 
    row_num: int 
    seat_number: int 
    price: Decimal = Decimal("0.00")
    is_sold: bool = False
    sold_datetime: datetime | None = None
