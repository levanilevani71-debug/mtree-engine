from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Person:
    id: int
    gender: str          # "M" or "F"
    age_group: str       # "adult" or "child"
    role: str            # "father", "mother", "child", "single"
    family_id: Optional[int] = None  # None for singles


@dataclass
class Household:
    id: str                      # e.g. "F1" for family 1, "S26" for single person 26
    members: List[Person]
    balance: float = 0.0         # shared money for the whole household
    salary_this_month: float = 0.0  # total salary received this month


@dataclass
class Business:
    id: str
    btype: str  # "local" (city spending) or "external" (earns from outside)
    employees: int

    # Config values
    spending_per_person: float = 0.0          # for local businesses (per month)
    external_revenue_per_month: float = 0.0   # for external businesses
    priority: Optional[int] = None            # for local spending order

    tax_rate: float = 0.0
    salary_rate: float = 0.0
    profit_rate: float = 0.0
    cost_rate: float = 0.0

    # Runtime stats (reset each month)
    revenue: float = 0.0
    tax_collected: float = 0.0
    salary_pool: float = 0.0
    profit: float = 0.0
    cost: float = 0.0

    def reset_month(self) -> None:
        self.revenue = 0.0
        self.tax_collected = 0.0
        self.salary_pool = 0.0
        self.profit = 0.0
        self.cost = 0.0


@dataclass
class Government:
    tax_collected: float = 0.0