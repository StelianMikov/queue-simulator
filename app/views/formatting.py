def minutes(value):
    if value * 60 < 59.5:
        return f"{value * 60:.0f} сек"
    return f"{value:.1f} мин".replace(".", ",")


def percent(value):
    return f"{value * 100:.0f}%"


def plain_number(value):
    return f"{value:g}"
