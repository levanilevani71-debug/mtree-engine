from models import Government
from loader import load_config, load_population_census
from simulation import simulate_one_month
from reports import print_report


def main():
    config_path = "economy_config.xml"
    census_path = "population_census.xml"

    population_count, initial_money, days_per_month, businesses = load_config(config_path)

    # Load census & build households
    persons, households = load_population_census(census_path, initial_money, population_count)
    government = Government()

    # You can change this to simulate more months
    months = 1

    for month in range(1, months + 1):
        simulate_one_month(households, businesses, government)
        print_report(month, households, businesses, government)


if __name__ == "__main__":
    main()