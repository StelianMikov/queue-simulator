"""Експериментите от курсовата работа. Стартиране: python experiments.py

Навсякъде обслужването е средно 2,5 мин, а работният ден е 480 минути.
Таблиците се отпечатват, графиките се записват в results/.
"""

import json
import os

from app.models.analysis import (average_over_runs, compare_cashiers, statistics,
                                 theoretical_wait)
from app.models.simulation import COMMON, MODE_NAMES, simulate
from app.views import charts

SERVICE = 2.5
RATE = 120
RUNS = 200
FOLDER = "results"


def experiment_cashiers():
    rows, recommended = compare_cashiers(RATE, SERVICE, max_cashiers=10, target_wait=1,
                                         runs=RUNS)
    rows = [row for row in rows if not row["overloaded"]]

    print("\n1. Средно чакане (мин) според броя каси")
    print("каси | " + " | ".join(MODE_NAMES.values()) + " | заетост")
    for row in rows:
        waits = [f"{row['results'][mode]['avg_wait']:.2f}" for mode in MODE_NAMES]
        print(row["cashiers"], "|", " | ".join(waits), "|",
              f"{row['results'][COMMON]['utilization']:.0%}")
    print("Каси за средно чакане под 1 мин:", recommended)

    charts.save_png(charts.cashiers_chart(rows, 1), f"{FOLDER}/cashiers.png")
    return {"rows": rows, "recommended": recommended}


def experiment_load():
    cashiers = 6
    rates = [60, 80, 100, 110, 120, 130]
    waits = {mode: [average_over_runs(rate, SERVICE, cashiers, mode, runs=RUNS)["avg_wait"]
                    for rate in rates]
             for mode in MODE_NAMES}

    print("\n2. Средно чакане (мин) според клиентите на час, 6 каси")
    for i, rate in enumerate(rates):
        print(rate, "|", " | ".join(f"{waits[mode][i]:.2f}" for mode in MODE_NAMES))

    charts.save_png(charts.load_chart(rates, waits, cashiers), f"{FOLDER}/load.png")
    return {"rates": rates, "waits": waits}


def experiment_theory():
    print("\n3. Симулация срещу формулата на Ерланг C (обща опашка)")
    rows = []
    for cashiers in range(6, 11):
        simulated = average_over_runs(RATE, SERVICE, cashiers, COMMON, runs=RUNS)["avg_wait"]
        theory = theoretical_wait(RATE, SERVICE, cashiers)
        rows.append({"cashiers": cashiers, "simulated": simulated, "theory": theory})
        print(cashiers, f"| симулация {simulated:.3f} | теория {theory:.3f}")
    return rows


def experiment_repetitions():
    print("\n4. Средно чакане в 10 отделни дни (6 каси, обща опашка)")
    days = []
    for seed in range(10):
        customers = simulate(RATE, SERVICE, 6, COMMON, seed=seed)
        days.append(statistics(customers, 6, 480)["avg_wait"])
    print(" ".join(f"{day:.2f}" for day in days))

    averages = {runs: average_over_runs(RATE, SERVICE, 6, COMMON, runs=runs)["avg_wait"]
                for runs in (5, 20, 50, 200)}
    print("Средно от повече дни:", {runs: round(value, 2) for runs, value in averages.items()})
    return {"days": days, "averages": averages}


if __name__ == "__main__":
    os.makedirs(FOLDER, exist_ok=True)
    results = {
        "cashiers": experiment_cashiers(),
        "load": experiment_load(),
        "theory": experiment_theory(),
        "repetitions": experiment_repetitions(),
    }
    with open(f"{FOLDER}/results.json", "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
