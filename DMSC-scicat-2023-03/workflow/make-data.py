"""Generate input data for exercises."""
import numpy as np
import plopp as pp
import scipp as sc
from dateutil.parser import parse
from scitacean import Client, Dataset
from scitacean.transfer.ssh import SSHFileTransfer

pp.patch_scipp()

TOKEN = ""

ALL_PEAKS = [
    [(0.41, 0.1, 1.0), (0.65, 0.12, 1.5), (0.89, 0.06, 1.0)],
    [(0.45, 0.2, 1.0), (0.7, 0.05, 1.0), (1.0, 0.08, 1.2)],
    [(0.43, 0.3, 1.0), (0.9, 0.1, 1.3), (1.2, 0.07, 1.0)],
]

BG_SLOPES = [-0.1, -0.09, -0.05]
BG_OFFSETS = [0.2, 0.3, 0.5]
X_RANGES = [(0.3, 1.2, 500), (0.36, 1.4, 550), (0.24, 1.5, 600)]
PROTON_CHARGES = [915.22, 1250.02, 1609.91]


def gaussian(x, mu, sig):
    return sc.exp(-((x - mu) ** 2) / sig**2) / 2 / np.sqrt(2 * np.pi)


def build_data(
    rng,
    peak_list: list[tuple[float, float, float]],
    bg_slope: float,
    bg_offset: float,
    x_range: tuple[float, float, float],
    proton_charge: float,
) -> sc.DataArray:
    x = sc.linspace("wavelength", *x_range, unit="angstrom")

    offset = sc.scalar(bg_offset, unit="counts")
    slope = sc.scalar(bg_slope, unit="counts/angstrom")
    background = offset + slope * x

    peaks = sum(
        gaussian(x, sc.scalar(mu, unit="angstrom"), sc.scalar(sig, unit="angstrom"))
        / norm
        for mu, sig, norm in peak_list
    )
    peaks.unit = background.unit

    noise = sc.array(
        dims=x.dims,
        values=rng.normal(0.0, 0.005, background.shape),
        unit=background.unit,
    )

    lineshape = (background + peaks + noise) * 1000 * proton_charge
    return sc.DataArray(lineshape, coords={"wavelength": x})


def build_dataset(
    i: int,
    x_range: tuple[float, float, float],
    proton_charge: float,
    filename: str,
    total_counts: int,
) -> Dataset:
    ds = Dataset(
        type="raw",
        name=f"Wavelength distribution {i} for SciCat workshop 2023",
        description=f"Dataset no. {i} for the SciCat workshop for DMSC in spring 2023.",
        owner="Jan-Lukas Wynen",
        owner_email="jan-lukas.wynen@ess.eu",
        orcid_of_owner="https://orcid.org/0000-0002-3761-3201",
        principal_investigator="Massimiliano Novelli;Jan-Lukas Wynen",
        contact_email="Max.Novelli@ess.eu;jan-lukas.wynen@ess.eu",
        owner_group="ess",
        access_groups=["dmsc"],
        creation_location="ess/dmsc/PeakMeister",
        data_format="scipp-hdf5",
        end_time=parse("2023-03-15T14:10:00Z"),
        license="CC-BY-4.0",
        instrument_id="8e719050-c9b7-4141-b107-12f58c5fb2eb",
        proposal_id="276577",
        sample_id="170f8c5e-6203-4a58-8b5c-8af9460c0250",
        meta={
            "proton_charge": {"value": proton_charge, "unit": "uAh"},
            "wavelength_min": {"value": x_range[0], "unit": "angstrom"},
            "wavelength_max": {"value": x_range[1], "unit": "angstrom"},
            "wavelength_bins": {"value": x_range[2], "unit": ""},
            "total_counts": {"value": total_counts, "unit": "counts"},
        },
    )
    ds.add_local_files(filename, base_path="data")

    return ds


def upload_datasets(datasets: list[Dataset]) -> None:
    client = Client.from_token(
        url="https://staging.scicat.ess.eu/api/v3",
        token=TOKEN,
        file_transfer=SSHFileTransfer(
            host="dmsc",
            source_folder="/mnt/groupdata/scicat/upload/scicat-workshop/20230322/{pid.pid}",
        ),
    )

    for d in datasets:
        print(f"Uploading {d.name}")
        client.upload_new_dataset_now(d)


def main() -> None:
    rng = np.random.default_rng(74712)
    data = {
        str(i): build_data(rng, *args)
        for i, args in enumerate(
            zip(ALL_PEAKS, BG_SLOPES, BG_OFFSETS, X_RANGES, PROTON_CHARGES)
        )
    }
    filenames = {}
    for i, d in data.items():
        label = rng.integers(10000, 100000, 1)[0]
        filenames[i] = f"data/raw_{label}.h5"
        d.to_hdf5(filenames[i])

    dsets = [
        build_dataset(i, *args, filenames[i], int(da.sum().value))
        for (i, da), *args in zip(data.items(), X_RANGES, PROTON_CHARGES)
    ]
    for ds in dsets:
        print(ds)
        print(list(ds.files))
    # upload_datasets(dsets)

    pp.plot(data, ls="-", marker=None)
    pp.show()


if __name__ == "__main__":
    main()
