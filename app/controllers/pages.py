from flask import Blueprint, render_template, request

from app.models.analysis import (compare_cashiers, is_overloaded, statistics,
                                 theoretical_wait)
from app.models.simulation import COMMON, MODE_NAMES, simulate
from app.views import charts

pages = Blueprint("pages", __name__)


def number(name, default, lowest, highest, cast=float):
    try:
        value = cast(request.args.get(name, default))
    except ValueError:
        value = default
    return max(lowest, min(highest, value))


@pages.route("/")
def simulation():
    params = {
        "rate": number("rate", 120, 1, 600),
        "service": number("service", 2.5, 0.5, 30),
        "cashiers": number("cashiers", 6, 1, 12, int),
        "duration": number("duration", 480, 30, 720, int),
        "seed": number("seed", 1, 0, 999999, int),
        "mode": request.args.get("mode", COMMON),
    }
    if params["mode"] not in MODE_NAMES:
        params["mode"] = COMMON

    customers = simulate(params["rate"], params["service"], params["cashiers"],
                         params["mode"], params["duration"], params["seed"])

    animation = {
        "cashiers": params["cashiers"],
        "duration": params["duration"],
        "common": params["mode"] == COMMON,
        "customers": [[round(c.arrival, 2), c.cashier, round(c.start, 2), round(c.end, 2)]
                      for c in customers],
    }

    return render_template(
        "simulation.html",
        params=params,
        modes=MODE_NAMES,
        stats=statistics(customers, params["cashiers"], params["duration"]),
        overloaded=is_overloaded(params["rate"], params["service"], params["cashiers"]),
        animation=animation,
        histogram=charts.to_svg(charts.wait_histogram(customers)),
        queue=charts.to_svg(charts.queue_chart(customers, params["duration"])),
    )


@pages.route("/kasi")
def cashiers():
    params = {
        "rate": number("rate", 120, 1, 600),
        "service": number("service", 2.5, 0.5, 30),
        "max_cashiers": number("max_cashiers", 10, 1, 15, int),
        "target": number("target", 1, 0.1, 60),
        "runs": number("runs", 20, 1, 50, int),
    }
    rows, recommended = compare_cashiers(params["rate"], params["service"],
                                         params["max_cashiers"], params["target"],
                                         runs=params["runs"])
    for row in rows:
        row["theory"] = theoretical_wait(params["rate"], params["service"], row["cashiers"])

    reached = {mode: count for mode, count in recommended.items() if count is not None}
    best_mode = min(reached, key=reached.get) if reached else None

    return render_template(
        "cashiers.html",
        params=params,
        modes=MODE_NAMES,
        rows=rows,
        recommended=recommended,
        best_mode=best_mode,
        chart=charts.to_svg(charts.cashiers_chart(rows, params["target"])),
    )


@pages.route("/model")
def model():
    return render_template("model.html")
