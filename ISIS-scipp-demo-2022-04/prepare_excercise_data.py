"""
Convert RHESSI's xray flare event list to a scipp HDF5 file.

Downloads the event list if necessary.
Output is written to data/hessi_flares.h5
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path
import re

import numpy as np
import pooch
import scipp as sc

DATA_DIR = Path(__file__).parent / 'data'


def flare_list_file():
    registry = pooch.create(
        path=DATA_DIR / 'pooch',
        base_url='https://hesperia.gsfc.nasa.gov/hessidata/dbase/',
        registry={
            'hessi_flare_list.txt': 'md5:89392347dbd0d954e21fe06c9c54c0dd'
        }
    )
    return open(registry.fetch('hessi_flare_list.txt'), 'r')


def parse_month(m) -> int:
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(m) + 1


def parse_date(d) -> date:
    day, month, year = d.split('-')
    return date(day=int(day), month=parse_month(month), year=int(year))


def parse_time(t) -> time:
    return time.fromisoformat(t)


def parse_datetime(d, t) -> np.datetime64:
    dt = datetime.combine(parse_date(d), parse_time(t))
    return np.datetime64(int(dt.timestamp()), 's')


def get_quality(flags: list) -> int:
    pattern = re.compile(r'Q(\d)')
    for flag in flags:
        if match := pattern.match(flag):
            return int(match[1])
    return -1


@dataclass
class Entry:
    flare_id: int
    peak_time: np.datetime64
    duration: float
    total_counts: float
    energy_range: list
    x: float
    y: float
    radial: float
    eclipsed: bool
    non_solar: bool
    quality: int
    flags: list

    @classmethod
    def parse(cls, s) -> Entry:
        fields = [c for c in s.strip().split(' ') if c]
        flags = fields[13:]
        eclipsed = 'ED' in flags or 'EE' in flags or 'ES' in flags
        non_solar = 'NS' in flags
        quality = get_quality(flags)

        return cls(
            flare_id=int(fields[0]),
            peak_time=parse_datetime(fields[1], fields[3]),
            duration=float(fields[5]),
            total_counts=float(fields[7]),
            energy_range=list(map(float, fields[8].split('-'))),
            x=float(fields[9]),
            y=float(fields[10]),
            radial=float(fields[11]),
            eclipsed=eclipsed,
            non_solar=non_solar,
            quality=quality,
            flags=flags)


def load_txt_file():
    flare_id = []
    peak_time = []
    duration = []
    total_counts = []
    energy_range = []
    x_pos = []
    y_pos = []
    radial = []
    eclipsed = []
    origin = []
    quality = []

    # Use to remove duplicates.
    # Way faster than searching through flare_id for every line.
    seen = set()

    with flare_list_file() as f:
        for _ in range(7):
            f.readline()

        while line := f.readline().strip():
            entry = Entry.parse(line)
            if entry.quality == -1:
                continue
            if 'PS' in entry.flags:
                # might be non-solar
                continue
            if entry.flare_id in seen:
                continue
            seen.add(entry.flare_id)

            flare_id.append(entry.flare_id)
            peak_time.append(entry.peak_time)
            duration.append(entry.duration)
            total_counts.append(entry.total_counts)
            energy_range.append(entry.energy_range)
            x_pos.append(entry.x)
            y_pos.append(entry.y)
            radial.append(entry.radial)
            eclipsed.append(entry.eclipsed)
            origin.append(1 if entry.non_solar else 0)
            quality.append(entry.quality)

    origin_legend = sc.DataArray(sc.array(dims=['origin'], values=[0, 1], unit=None),
                                 coords={'origin': sc.array(dims=['origin'], values=['solar', 'non_solar'])})
    energy_range = sc.array(dims=['event', 'energy'], values=energy_range, unit='keV')

    return sc.DataArray(
        sc.array(dims=['event'], values=total_counts, unit='count'),
        coords={
            'time': sc.array(dims=['event'], values=peak_time, unit='s'),
            'duration': sc.array(dims=['event'], values=duration, unit='s'),
            'x': sc.array(dims=['event'], values=x_pos, unit='asec'),
            'y': sc.array(dims=['event'], values=y_pos, unit='asec'),
            'radial': sc.array(dims=['event'], values=radial, unit='asec'),
        },
        attrs={
            'min_energy': energy_range['energy', 0],
            'max_energy': energy_range['energy', 1],
            'eclipsed': sc.array(dims=['event'], values=eclipsed),
            'origin': sc.array(dims=['event'], values=origin, unit=None),
            'origin_legend': sc.scalar(origin_legend),
            'quality': sc.array(dims=['event'], values=quality, unit=None),
            'description': sc.scalar(
                'X-ray flares recorded by NASA\'s Reuven Ramaty High Energy Solar'
                ' Spectroscopic Imager (RHESSI) Small Explorer'),
            'url': sc.scalar(
                'https://hesperia.gsfc.nasa.gov/rhessi3/data-access/rhessi-data/flare-list/index.html'),
        }
    )


def main():
    da = load_txt_file()
    da.to_hdf5(DATA_DIR / 'hessi_flares.h5')


if __name__ == '__main__':
    main()
