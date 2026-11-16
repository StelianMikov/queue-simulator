import random
from collections import deque
from dataclasses import dataclass

COMMON = "common"
SHORTEST = "shortest"
RANDOM = "random"

MODE_NAMES = {
    COMMON: "Една обща опашка",
    SHORTEST: "Отделни опашки (най-късата)",
    RANDOM: "Отделни опашки (случайна каса)",
}


@dataclass
class Customer:
    arrival: float
    cashier: int
    start: float
    end: float

    @property
    def wait(self):
        return self.start - self.arrival


def generate_arrivals(rate_per_hour, mean_service, duration, rng):
    """Двойки (момент на пристигане, време за обслужване), всичко в минути."""
    rate_per_minute = rate_per_hour / 60
    arrivals = []
    time = rng.expovariate(rate_per_minute)
    while time < duration:
        arrivals.append((time, rng.expovariate(1 / mean_service)))
        time += rng.expovariate(rate_per_minute)
    return arrivals


def people_in_line(line, now):
    while line and line[0] <= now:
        line.popleft()
    return len(line)


def choose_cashier(mode, arrival, free_at, lines, rng):
    cashiers = range(len(free_at))
    if mode == COMMON:
        return min(cashiers, key=lambda i: free_at[i])
    if mode == SHORTEST:
        return min(cashiers, key=lambda i: people_in_line(lines[i], arrival))
    return rng.randrange(len(free_at))


def simulate(rate_per_hour, mean_service, cashiers, mode, duration=480, seed=None):
    rng = random.Random(seed)
    # Клиентите се генерират преди цикъла, за да са едни и същи при трите вида опашка.
    arrivals = generate_arrivals(rate_per_hour, mean_service, duration, rng)

    free_at = [0.0] * cashiers
    lines = [deque() for _ in range(cashiers)]
    customers = []

    for arrival, service in arrivals:
        cashier = choose_cashier(mode, arrival, free_at, lines, rng)
        start = max(arrival, free_at[cashier])
        end = start + service
        free_at[cashier] = end
        lines[cashier].append(end)
        customers.append(Customer(arrival, cashier, start, end))

    return customers
