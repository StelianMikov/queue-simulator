import math

from app.models.simulation import MODE_NAMES, simulate


def statistics(customers, cashiers, duration, limit=5.0):
    count = len(customers)
    if count == 0:
        return {"customers": 0, "avg_wait": 0, "max_wait": 0,
                "over_limit_share": 0, "utilization": 0}

    waits = [c.wait for c in customers]
    busy = sum(min(c.end, duration) - c.start for c in customers if c.start < duration)

    return {
        "customers": count,
        "avg_wait": sum(waits) / count,
        "max_wait": max(waits),
        "over_limit_share": sum(w > limit for w in waits) / count,
        "utilization": busy / (cashiers * duration),
    }


def queue_over_time(customers, duration):
    """Брой чакащи във всяка минута от деня."""
    waiting = [0] * (int(duration) + 1)
    for c in customers:
        first = math.ceil(c.arrival)
        last = min(math.ceil(c.start), len(waiting))
        for minute in range(first, last):
            waiting[minute] += 1
    return waiting


def average_over_runs(rate_per_hour, mean_service, cashiers, mode,
                      duration=480, runs=20, limit=5.0, seed=0):
    totals = {"avg_wait": 0.0, "max_wait": 0.0, "over_limit_share": 0.0, "utilization": 0.0}
    for run in range(runs):
        customers = simulate(rate_per_hour, mean_service, cashiers, mode, duration, seed + run)
        stats = statistics(customers, cashiers, duration, limit)
        for key in totals:
            totals[key] += stats[key]
    return {key: value / runs for key, value in totals.items()}


def is_overloaded(rate_per_hour, mean_service, cashiers):
    return rate_per_hour / 60 * mean_service >= cashiers


def compare_cashiers(rate_per_hour, mean_service, max_cashiers, target_wait,
                     duration=480, runs=20, seed=0):
    """Пробва от 1 до max_cashiers каси. Връща таблицата с резултати и за всеки
    вид опашка най-малкия брой каси със средно чакане под target_wait."""
    rows = []
    recommended = {mode: None for mode in MODE_NAMES}

    for cashiers in range(1, max_cashiers + 1):
        results = {}
        for mode in MODE_NAMES:
            results[mode] = average_over_runs(rate_per_hour, mean_service, cashiers, mode,
                                              duration, runs, target_wait, seed)
            if recommended[mode] is None and results[mode]["avg_wait"] <= target_wait:
                recommended[mode] = cashiers
        rows.append({
            "cashiers": cashiers,
            "overloaded": is_overloaded(rate_per_hour, mean_service, cashiers),
            "results": results,
        })

    return rows, recommended


def theoretical_wait(rate_per_hour, mean_service, cashiers):
    """Средно чакане при обща опашка по формулата на Ерланг C."""
    load = rate_per_hour / 60 * mean_service
    if load >= cashiers:
        return math.inf

    total = sum(load ** k / math.factorial(k) for k in range(cashiers))
    last = load ** cashiers / math.factorial(cashiers) * cashiers / (cashiers - load)
    probability_to_wait = last / (total + last)
    return probability_to_wait * mean_service / (cashiers - load)
