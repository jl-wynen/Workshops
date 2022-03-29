# Requires scipp/io/hdf5.py from 1cf68ee23

from io import BytesIO

from scipp.testing import strategies as scst
import scipp as sc

from hypothesis import given


@given(scst.dataarrays())
def test_data_array_hdf5(da):
    f = BytesIO()
    da.to_hdf5(filename=f)
    f.seek(0)
    loaded = sc.io.open_hdf5(filename=f)

    assert sc.utils.isnear(loaded, da, equal_nan=True)
