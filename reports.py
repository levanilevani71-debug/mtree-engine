from typing import Dict, List

from models import Household, Business, Government


def describe_household(h: Household) -> str:
    roles = [p.role for p in h.members]
    num_fathers = roles.count("father")
    num_mothers = roles.count("mother")
    num_children = roles.count("child")
    num_singles = roles.count("single")

    if num_singles == 1 and len(h.members) == 1:
        # single adult household
        p = h.members[0]
        return f"single {p.gender} adult ({p.id})"
    else:
        parts = []
        parents = num_fathers + num_mothers
        if parents:
            parts.append(f"{parents} parent(s)")
        if num_children:
            parts.append(f"{num_children} child(ren)")
        if num_singles:
            parts.append(f"{num_singles} single(s)")
        return ", ".join(parts) if parts else "empty"


def print_report(
    month: int,
    households: List[Household],
    businesses: Dict[str, Business],
    government: Government,
) -> None:
    total_people = sum(len(h.members) for h in households)
    total_money = sum(h.balance for h in households)

    avg_money_per_person = total_money / total_people if total_people > 0 else 0.0
    avg_money_per_household = total_money / len(households) if households else 0.0

    min_balance = min(h.balance for h in households) if households else 0.0
    max_balance = max(h.balance for h in households) if households else 0.0

    print(f"=== End of Month {month} ===")
    print(f"Total households: {len(households)}")
    print(f"Total people: {total_people}")
    print(f"Total money in economy: {total_money:.2f}")
    print(f"Average money per person: {avg_money_per_person:.2f}")
    print(f"Average money per household: {avg_money_per_household:.2f}")
    print(f"Min household balance: {min_balance:.2f}")
    print(f"Max household balance: {max_balance:.2f}")
    print(f"Government tax collected total: {government.tax_collected:.2f}")
    print()

    print("Household balances:")
    for h in sorted(households, key=lambda x: x.id):
        desc = describe_household(h)
        print(
            f"  Household {h.id:>3}: {desc:<30} "
            f"-> {h.balance:.2f} $ (salary = {h.salary_this_month:.2f} $)"
        )
    print()

    for b in businesses.values():
        print(f"Business: {b.id}")
        print(f"  Type: {b.btype}")
        print(f"  Employees (slots): {b.employees}")
        print(f"  Revenue: {b.revenue:.2f}")
        print(f"  Tax: {b.tax_collected:.2f}")
        print(f"  Salary pool: {b.salary_pool:.2f}")
        print(f"  Profit: {b.profit:.2f}")
        print(f"  Cost (materials): {b.cost:.2f}")
        print()
    print("-" * 40)