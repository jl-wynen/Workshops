"""
Convert GOES's xray flare event list to a scipp HDF5 file.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
import subprocess
from typing import Optional, Tuple

import numpy as np
import scipp as sc

DATA_DIR = Path(__file__).parent / 'data'


def download():
    url = 'https://hesperia.gsfc.nasa.gov/goes/goes_event_listings/'
    name_pat = 'goes_xray_event_list_{year}.txt'
    for year in range(1975, 2021):
        print('downloading ', year)
        name = name_pat.format(year=year)
        subprocess.check_call(
            ['curl', url + name, '--output', f'data/{name}'])


def parse_month(m) -> int:
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(m) + 1


def parse_date(d) -> date:
    day, month, year = d.split('-')
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

    return (np.datetime64(int(peak_datetime.timestamp()), 's'),
            int((end_datetime - start_datetime).total_seconds()))


def parse_position(s) -> Tuple[float, float]:
    y_sign = +1 if s[0] == 'N' else -1
    x_sign = +1 if s[3] == 'E' else -1
    y = y_sign * float(s[1:3])
    x = x_sign * float(s[4:6])
    return x, y


@dataclass
class Entry:
    peak_time: np.datetime64
    duration: int
    class_: str
    x: float
    y: float
    region: int

    @classmethod
    def parse(cls, s) -> Optional[Entry]:
        fields = [c for c in s.strip().split(' ') if c]
        if len(fields) != 7:
            return None
        dat, dur = parse_datetimes(*fields[0:4])
        pos = parse_position(fields[5])

        return cls(
            peak_time=dat,
            duration=dur,
            class_=fields[4],
            x=pos[0],
            y=pos[1],
            region=int(fields[6]))


def load_txt_file(fname):
    peak_time = []
    duration = []
    class_ = []
    x_pos = []
    y_pos = []
    region = []

    with open(fname, 'r') as f:
        for _ in range(6):
            f.readline()

        while line := f.readline().strip():
            if (entry := Entry.parse(line)) is None:
                continue
            peak_time.append(entry.peak_time)
            duration.append(entry.duration)
            class_.append(entry.class_)
            x_pos.append(entry.x)
            y_pos.append(entry.y)
            region.append(entry.region)

    return sc.DataArray(
        sc.ones(sizes={'event': len(peak_time)}, unit='count'),
        coords={
            'time': sc.array(dims=['event'], values=peak_time, unit='s'),
            'duration': sc.array(dims=['event'], values=duration, unit='s'),
            'x': sc.array(dims=['event'], values=x_pos, unit='asec'),
            'y': sc.array(dims=['event'], values=y_pos, unit='asec'),
        },
        attrs={
            'class': sc.array(dims=['event'], values=class_),
            'region': sc.array(dims=['event'], values=region)
        }
    )


def main():
    data = [load_txt_file(f'data/goes_xray_event_list_{year}.txt')
            for year in range(1975, 2021)]
    full = sc.concat(data, dim='event')
    full.to_hdf5(DATA_DIR / 'goes_flares.h5')


if __name__ == '__main__':
    main()
