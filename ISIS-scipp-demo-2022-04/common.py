from datetime import date, datetime, time, timedelta
from typing import Tuple

import numpy as np


def parse_month(m) -> int:
    return [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ].index(m) + 1


def parse_date(d) -> date:
    day, month, year = d.split("-")
    return date(day=int(day), month=parse_month(month), year=int(year))


def parse_time(t) -> time:
    return time.fromisoformat(t)


def parse_datetimes(d, start, peak, end) -> Tuple[np.datetime64, int]:
    d = parse_date(d)
    start = parse_time(start)
    peak = parse_time(peak)
    end = parse_time(end)

    start_datetime = datetime.combine(d, start)
    peak_date = d + timedelta(days=1) if peak < start else d
    peak_datetime = datetime.combine(peak_date, peak)
    end_date = d + timedelta(days=1) if end < start else d
    end_datetime = datetime.combine(end_date, end)

    return (
        np.datetime64(int(peak_datetime.timestamp()), "s"),
        int((end_datetime - start_datetime).total_seconds()),
    )
