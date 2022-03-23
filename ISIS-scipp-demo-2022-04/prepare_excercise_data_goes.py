"""
Convert GOES's xray flare event list to a scipp HDF5 file.

Downloads the event list if necessary.
Output is written to data/goes_flares.h5
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pooch
import scipp as sc

from common import parse_datetimes

DATA_DIR = Path(__file__).parent / "data"


def flare_list_files():
    registry = pooch.create(
        path=DATA_DIR / "pooch",
        base_url="https://hesperia.gsfc.nasa.gov/goes/goes_event_listings/",
        registry={
            "goes_xray_event_list_1975.txt": "md5:3b86a114ff8b89f022099e48a45490f1",
            "goes_xray_event_list_1976.txt": "md5:686996b33fa10843349511534cede792",
            "goes_xray_event_list_1977.txt": "md5:59af12be270031c75061f05f61e439cd",
            "goes_xray_event_list_1978.txt": "md5:0f54db2c616667f8f098b77ff94c2dc7",
            "goes_xray_event_list_1979.txt": "md5:f1fc69b5184298b0d161f0e2db517393",
            "goes_xray_event_list_1980.txt": "md5:a0b1989cb085765fb7e05d661e5872ce",
            "goes_xray_event_list_1981.txt": "md5:1d803bf83d34c8e98ec0c54e0aa7306f",
            "goes_xray_event_list_1982.txt": "md5:e15b06083fade2699394836b690a7950",
            "goes_xray_event_list_1983.txt": "md5:61c3456bf89aafe48cd33b4339c3908a",
            "goes_xray_event_list_1984.txt": "md5:674ad932b5c4d404d32332617b1b4def",
            "goes_xray_event_list_1985.txt": "md5:5bbdf63229e44e4aed03b21a90bb5058",
            "goes_xray_event_list_1986.txt": "md5:198387ed43bc3564ca6f9387e6874591",
            "goes_xray_event_list_1987.txt": "md5:d20e16b27eff7e7afb8e3e045a05a32d",
            "goes_xray_event_list_1988.txt": "md5:990e8c2b2ddc9c41ca458ce75d115323",
            "goes_xray_event_list_1989.txt": "md5:d1b36a802c9f4213b9e7862b4e0a7d70",
            "goes_xray_event_list_1990.txt": "md5:fb73a5462c172cee115927901be45bf1",
            "goes_xray_event_list_1991.txt": "md5:1b858943914240e13815a7d0fdeba25e",
            "goes_xray_event_list_1992.txt": "md5:eb1702f6494e917a586379884e821cab",
            "goes_xray_event_list_1993.txt": "md5:bb56c16c3d4112647af913907405982c",
            "goes_xray_event_list_1994.txt": "md5:b30d744720cf03faa10c4c517bfe9b1f",
            "goes_xray_event_list_1995.txt": "md5:a52e6dacdf7daebd587affaf50e34262",
            "goes_xray_event_list_1996.txt": "md5:072d8fbb1e904528b9794dd54f703eba",
            "goes_xray_event_list_1997.txt": "md5:9ab0b933143569b221b2b880c2ad0934",
            "goes_xray_event_list_1998.txt": "md5:1823f627ada9d74e099dd0e4eecd8be9",
            "goes_xray_event_list_1999.txt": "md5:6eb71345ef67e88e9cda3a0f3f846f18",
            "goes_xray_event_list_2000.txt": "md5:06a7bb098139afdc8b98cce169e0ff13",
            "goes_xray_event_list_2001.txt": "md5:f0468af28f06b0697ea72bcc9ad58115",
            "goes_xray_event_list_2002.txt": "md5:a7cbface94c9b579774abe04b37e404d",
            "goes_xray_event_list_2003.txt": "md5:e23c6ed9c83ad338bb214b059f484294",
            "goes_xray_event_list_2004.txt": "md5:05a35e02e8263a6074f67e3bfad33f4a",
            "goes_xray_event_list_2005.txt": "md5:a905049364b0d74b9653b6c02117f967",
            "goes_xray_event_list_2006.txt": "md5:15dea113fa50c27691ddb3146bb67fde",
            "goes_xray_event_list_2007.txt": "md5:f4dc9b1582d37b0b234444c2c7d0a250",
            "goes_xray_event_list_2008.txt": "md5:52d7be510eeb98e54289b4c394a6bd86",
            "goes_xray_event_list_2009.txt": "md5:433ae27934de04872b309384861e4715",
            "goes_xray_event_list_2010.txt": "md5:fd36e382b14cf83782039ea8e5dab48f",
            "goes_xray_event_list_2011.txt": "md5:ccaff65573afd1bf79d4ee69fa522d34",
            "goes_xray_event_list_2012.txt": "md5:863df2313cd108fb12cc32e80c7c1f7a",
            "goes_xray_event_list_2013.txt": "md5:719d8a73de96295cf123fcc80020d7ad",
            "goes_xray_event_list_2014.txt": "md5:e2ffcf5386a702eeadd6519cd7ac28b2",
            "goes_xray_event_list_2015.txt": "md5:fcbfd4aa81cf8e6fb72b6eddcab15d4d",
            "goes_xray_event_list_2016.txt": "md5:8104041d10d3a2e6db74de0daecdc8ab",
            "goes_xray_event_list_2017.txt": "md5:7e560e6e106d26cba50592bcc1eb8080",
            "goes_xray_event_list_2018.txt": "md5:2f1e7ef54202ac8948de38151c9a7e60",
            "goes_xray_event_list_2019.txt": "md5:33433e75f48f080f70c8268a58b3b44a",
            "goes_xray_event_list_2020.txt": "md5:b6364df2b0fd837fe07100999b1dd1da",
            "goes_xray_event_list_2021.txt": "md5:4fe373bc7896457f300955d687c107a7",
        },
    )
    return [registry.fetch(name) for name in registry.registry]


def parse_position(s) -> Tuple[float, float]:
    y_sign = +1 if s[0] == "N" else -1
    x_sign = +1 if s[3] == "E" else -1
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
        fields = [c for c in s.strip().split(" ") if c]
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
            region=int(fields[6]),
        )


def load_txt_file(fname):
    peak_time = []
    duration = []
    class_ = []
    x_pos = []
    y_pos = []
    region = []

    with open(fname, "r") as f:
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
        sc.ones(sizes={"event": len(peak_time)}, unit="count"),
        coords={
            "time": sc.array(dims=["event"], values=peak_time, unit="s"),
            "duration": sc.array(dims=["event"], values=duration, unit="s"),
            "x": sc.array(dims=["event"], values=x_pos, unit="asec"),
            "y": sc.array(dims=["event"], values=y_pos, unit="asec"),
        },
        attrs={
            "class": sc.array(dims=["event"], values=class_),
            "region": sc.array(dims=["event"], values=region),
        },
    )


def main():
    data = [load_txt_file(fname) for fname in flare_list_files()]
    full = sc.concat(data, dim="event")
    full.to_hdf5(DATA_DIR / "goes_flares.h5")


if __name__ == "__main__":
    main()
