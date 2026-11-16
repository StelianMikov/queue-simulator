import io

from matplotlib.figure import Figure

from app.models.analysis import queue_over_time
from app.models.simulation import COMMON, MODE_NAMES, RANDOM, SHORTEST

MODE_COLORS = {COMMON: "#2a78d6", SHORTEST: "#eb6834", RANDOM: "#1baf7a"}
MODE_MARKERS = {COMMON: "o", SHORTEST: "s", RANDOM: "^"}

TEXT = "#111111"
MUTED = "#555555"
GRID = "#dddddd"


def new_chart(title, x_label, y_label):
    figure = Figure(figsize=(7, 3.6), facecolor="white")
    axes = figure.add_subplot()
    axes.set_title(title, loc="left", color=TEXT, fontsize=12, fontweight="bold", pad=12)
    axes.set_xlabel(x_label, color=MUTED, fontsize=10)
    axes.set_ylabel(y_label, color=MUTED, fontsize=10)
    axes.grid(axis="y", color=GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    axes.tick_params(colors=MUTED, labelsize=9, length=0)
    for side in ("top", "right", "left"):
        axes.spines[side].set_visible(False)
    axes.spines["bottom"].set_color("#999999")
    return figure, axes


def to_svg(figure):
    buffer = io.StringIO()
    figure.savefig(buffer, format="svg", bbox_inches="tight")
    svg = buffer.getvalue()
    return svg[svg.index("<svg"):]


def save_png(figure, path):
    figure.savefig(path, format="png", dpi=200, bbox_inches="tight")


def wait_histogram(customers):
    waits = [c.wait for c in customers]
    top = max(5, int(max(waits, default=0)) + 1)
    step = max(1, top // 20)
    figure, axes = new_chart("Разпределение на времето за чакане",
                             "Чакане (минути)", "Брой клиенти")
    axes.hist(waits, bins=range(0, top + step, step), color=MODE_COLORS[COMMON], rwidth=0.9)
    return figure


def queue_chart(customers, duration):
    waiting = queue_over_time(customers, duration)
    minutes = range(len(waiting))
    figure, axes = new_chart("Чакащи клиенти през деня",
                             "Минута от работния ден", "Брой чакащи")
    axes.plot(minutes, waiting, color=MODE_COLORS[COMMON], linewidth=1.6)
    axes.fill_between(minutes, waiting, color=MODE_COLORS[COMMON], alpha=0.12)
    axes.set_xlim(0, duration)
    axes.set_ylim(bottom=0)
    return figure


def plot_modes(axes, xs, waits_by_mode):
    for mode, name in MODE_NAMES.items():
        axes.plot(xs, waits_by_mode[mode], color=MODE_COLORS[mode],
                  marker=MODE_MARKERS[mode], markersize=7, linewidth=2, label=name)
    axes.set_xticks(xs)
    axes.set_ylim(bottom=0)


def cashiers_chart(rows, target_wait):
    # Претоварените варианти се пропускат: при тях чакането е стотици минути.
    stable = [row for row in rows if not row["overloaded"]]
    waits = {mode: [row["results"][mode]["avg_wait"] for row in stable]
             for mode in MODE_NAMES}
    figure, axes = new_chart("Средно чакане според броя каси",
                             "Брой каси", "Средно чакане (минути)")
    plot_modes(axes, [row["cashiers"] for row in stable], waits)
    axes.axhline(target_wait, color=MUTED, linewidth=1, linestyle="--",
                 label=f"Цел: {target_wait:g} мин")
    axes.legend(frameon=False, fontsize=9)
    return figure


def load_chart(rates, waits_by_mode, cashiers):
    figure, axes = new_chart(f"Средно чакане според потока от клиенти ({cashiers} каси)",
                             "Клиенти на час", "Средно чакане (минути)")
    plot_modes(axes, rates, waits_by_mode)
    axes.legend(frameon=False, fontsize=9)
    return figure
