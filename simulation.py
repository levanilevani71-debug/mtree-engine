from typing import Dict, List

from models import Household, Business, Government


def simulate_one_month(
    households: List[Household],
    businesses: Dict[str, Business],
    government: Government,
) -> None:
    """
    One month tick (household-based):
    1) Reset salaries + business monthly stats
    2) Households spend at local businesses in priority order (bakery, market, shop)
       - No negative money: they spend only what they have
       - Spending is per person, but taken from shared household balance
    3) External businesses (factory) get external revenue
    4) Split revenue into tax / salary / profit / cost
    5) Pay salaries to households (round-robin placeholder for now)
    """

    # Reset monthly salary info
    for h in households:
        h.salary_this_month = 0.0

    # 0) Reset monthly stats on businesses
    for b in businesses.values():
        b.reset_month()

    # Ordered list of local businesses by priority (low number = more important)
    local_businesses: List[Business] = [
        b for b in businesses.values() if b.btype == "local"
    ]
    local_businesses.sort(
        key=lambda x: x.priority if x.priority is not None else 9999
    )

    # 1) HOUSEHOLD SPENDING WITH PRIORITIES & NO NEGATIVE MONEY
    for h in households:
        members_count = len(h.members)
        if members_count == 0:
            continue

        for b in local_businesses:
            per_person_spend = b.spending_per_person
            if per_person_spend <= 0:
                continue

            if h.balance <= 0:
                break  # this household is broke for this month

            planned_spend = per_person_spend * members_count
            spend = min(h.balance, planned_spend)

            h.balance -= spend
            b.revenue += spend

    # 2) EXTERNAL REVENUE (e.g. factory exports)
    for b in businesses.values():
        if b.btype == "external":
            b.revenue += b.external_revenue_per_month

    # 3) SPLIT REVENUE INTO TAX / SALARY / PROFIT / COST
    for b in businesses.values():
        b.tax_collected = b.revenue * b.tax_rate
        b.salary_pool = b.revenue * b.salary_rate
        b.profit = b.revenue * b.profit_rate
        b.cost = b.revenue * b.cost_rate

        government.tax_collected += b.tax_collected

    # 4) PAY SALARIES (round-robin across households for now)
    if households:
        hh_index = 0
        n_households = len(households)

        for b in businesses.values():
            if b.employees > 0 and b.salary_pool > 0:
                salary_per_worker = b.salary_pool / b.employees
                for _ in range(b.employees):
                    hh = households[hh_index % n_households]
                    hh.balance += salary_per_worker
                    hh.salary_this_month += salary_per_worker
                    hh_index += 1