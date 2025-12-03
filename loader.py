import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple

from models import Person, Household, Business


def load_config(path: str) -> Tuple[int, float, int, Dict[str, Business]]:
    """
    Load economy_config.xml and return:
    - population_count
    - initial_money per person
    - days_per_month (not used yet but kept for future logic)
    - businesses (dict id -> Business)
    """
    tree = ET.parse(path)
    root = tree.getroot()

    # Population settings
    pop_cfg = root.find("population")
    population_count = int(pop_cfg.get("count"))
    initial_money = float(pop_cfg.get("initial_money"))
    days_per_month = int(pop_cfg.get("days_per_month"))

    # Global tax
    tax_cfg = root.find("tax")
    if tax_cfg is None:
        raise ValueError("Missing <tax> element in config.")
    global_tax_rate = float(tax_cfg.get("rate"))

    businesses: Dict[str, Business] = {}

    # Businesses
    b_root = root.find("businesses")
    if b_root is None:
        raise ValueError("Missing <businesses> block in config.")

    for bnode in b_root.findall("business"):
        bid = bnode.get("id")
        btype = bnode.get("type")
        employees = int(bnode.get("employees"))

        # Priority (only meaningful for local businesses)
        priority_attr = bnode.get("priority")
        priority = int(priority_attr) if priority_attr is not None else None

        # Defaults
        spending_per_person = 0.0
        external_revenue = 0.0

        spending_node = bnode.find("spending")
        if spending_node is not None:
            spending_per_person = float(spending_node.get("per_person_per_month", "0"))

        ext_node = bnode.find("external_revenue")
        if ext_node is not None:
            external_revenue = float(ext_node.get("per_month", "0"))

        rates_node = bnode.find("rates")
        if rates_node is None:
            raise ValueError(f"Business {bid} missing <rates> block.")

        salary = float(rates_node.get("salary"))
        cost = float(rates_node.get("cost"))

        tax = global_tax_rate
        profit = 1.0 - (tax + salary + cost)

        if profit < -1e-9:
            # Slight negative tolerance for float errors only
            raise ValueError(
                f"Business {bid} has negative profit rate: {profit:.4f}. "
                f"Check tax + salary + cost in config."
            )

        # Clamp tiny negative to zero if it's just float noise
        if profit < 0 and profit > -1e-9:
            profit = 0.0

        businesses[bid] = Business(
            id=bid,
            btype=btype,
            employees=employees,
            spending_per_person=spending_per_person,
            external_revenue_per_month=external_revenue,
            priority=priority,
            tax_rate=tax,
            salary_rate=salary,
            profit_rate=profit,
            cost_rate=cost,
        )

    return population_count, initial_money, days_per_month, businesses


def load_population_census(
    path: str,
    initial_money: float,
    expected_population: int,
) -> Tuple[List[Person], List[Household]]:
    """
    Load population_census.xml and build:
    - persons: list of Person
    - households: list of Household
    Household money = number_of_members * initial_money (shared).
    """
    tree = ET.parse(path)
    root = tree.getroot()

    persons: List[Person] = []

    for node in root.findall("person"):
        pid = int(node.get("id"))
        gender = node.get("gender")
        age_group = node.get("age_group")
        role = node.get("role")
        family_id_attr = node.get("family_id")
        family_id = int(family_id_attr) if family_id_attr is not None else None

        p = Person(
            id=pid,
            gender=gender,
            age_group=age_group,
            role=role,
            family_id=family_id,
        )
        persons.append(p)

    if len(persons) != expected_population:
        raise ValueError(
            f"Population mismatch: config says {expected_population}, "
            f"but census has {len(persons)} persons."
        )

    # Build households:
    # - all persons with same family_id -> one household "F{family_id}"
    # - single adults (family_id is None) -> own household "S{person_id}"
    households_map: Dict[str, Household] = {}

    for p in persons:
        if p.family_id is not None:
            hh_id = f"F{p.family_id}"
        else:
            # single adult
            hh_id = f"S{p.id}"

        if hh_id not in households_map:
            households_map[hh_id] = Household(id=hh_id, members=[], balance=0.0)
        households_map[hh_id].members.append(p)

    households: List[Household] = list(households_map.values())

    # Set starting balances: members_count * initial_money
    for h in households:
        member_count = len(h.members)
        h.balance = member_count * initial_money
        h.salary_this_month = 0.0

    return persons, households