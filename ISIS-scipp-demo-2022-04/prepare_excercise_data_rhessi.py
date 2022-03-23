"""
Convert RHESSI's xray flare event list to a scipp HDF5 file.

Downloads the event list if necessary.
Output is written to data/hessi_flares.h5
"""

from __future__ import annotations
from pathlib import Path
import re

import pooch
import scipp as sc

from common import parse_datetimes

DATA_DIR = Path(__file__).parent / "data"


def flare_list_file():
    registry = pooch.create(
        path=DATA_DIR / "pooch",
        base_url="https://hesperia.gsfc.nasa.gov/hessidata/dbase/",
        registry={"hessi_flare_list.txt": "md5:89392347dbd0d954e21fe06c9c54c0dd"},
    )
    return open(registry.fetch("hessi_flare_list.txt"), "r")


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


def get_quality(flags: list) -> int:
    pattern = re.compile(r"Q(\d)")
    for flag in flags:
        if match := pattern.match(flag):
            return int(match[1])
    return -1


FLAGS = (
    "a0",
    "a1",
    "a2",
    "a3",
    "An",
    "DF",
    "DR",
    "ED",
    "EE",
    "ES",
    "FE",
    "FR",
    "FS",
    "GD",
    "GE",
    "GS",
    "MR",
    "NS",
    "PE",
    "PS",
    "Pn",
    "Qn",
    "SD",
    "SE",
    "SS",
)


def parse_line(line):
    fields = [c for c in line.split(" ") if c]
    flags = fields[13:]
    eclipsed = "ED" in flags or "EE" in flags or "ES" in flags
    non_solar = "NS" in flags
    quality = get_quality(flags)

    return {
        "flare_id": int(fields[0]),
        "peak_time": parse_datetimes(*fields[1:5])[0],
        "duration": float(fields[5]),
        "total_counts": float(fields[7]),
        "energy_range": list(map(float, fields[8].split("-"))),
        "x": float(fields[9]),
        "y": float(fields[10]),
        "radial": float(fields[11]),
        "eclipsed": eclipsed,
        "non_solar": non_solar,
        "quality": quality,
        **{name: name in flags for name in FLAGS},
    }


def load_txt_file():
    values = {}

    # Use to remove duplicates.
    # Way faster than searching through flare_id list for every line.
    seen = set()

    with flare_list_file() as f:
        for _ in range(7):
            f.readline()

        while line := f.readline().strip():
            entry = parse_line(line)
            if entry["flare_id"] in seen:
                continue
            seen.add(entry["flare_id"])

            for key, val in entry.items():
                values.setdefault(key, []).append(val)

    energy_range = sc.array(
        dims=["event", "energy"], values=values.pop("energy_range"), unit="keV"
    )

    def event_array(name, unit):
        return sc.array(dims=["event"], values=values.pop(name), unit=unit)

    return sc.DataArray(
        event_array("total_counts", "count"),
        coords={
            "time": event_array("peak_time", "s"),
            "duration": event_array("duration", "s"),
            "x": event_array("x", "asec"),
            "y": event_array("y", "asec"),
            "radial": event_array("radial", "asec"),
        },
        attrs={
            "min_energy": energy_range["energy", 0],
            "max_energy": energy_range["energy", 1],
            "quality": event_array("quality", None),
            **{key: event_array(key, None) for key in list(values)},
            "description": sc.scalar(
                "X-ray flares recorded by NASA's Reuven Ramaty High Energy Solar"
                " Spectroscopic Imager (RHESSI) Small Explorer"
            ),
            "url": sc.scalar(
                "https://hesperia.gsfc.nasa.gov/rhessi3/data-access/rhessi-data/flare-list/index.html"
            ),
            "citation": sc.scalar("https://doi.org/10.1023/A:1022428818870"),
        },
    )


def prefilter(da):
    da = da.copy()
    del da.attrs["flare_id"]
    da = da[~da.attrs.pop("eclipsed")]
    # no quality flag
    da = da[da.attrs["quality"] >= sc.index(0)]
    # PS - Possible Solar Flare; in front detectors, but no position
    da = da[~da.attrs.pop("PS")]

    for flag in FLAGS:
        try:
            del da.attrs[flag]
        except KeyError:
            pass
    return da


def main():
    da = load_txt_file()
    da = prefilter(da)
    da.to_hdf5(DATA_DIR / "hessi_flares.h5")


if __name__ == "__main__":
    main()
