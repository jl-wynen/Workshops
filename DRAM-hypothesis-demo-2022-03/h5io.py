# Requires scipp/io/hdf5.py from 1cf68ee23

from io import BytesIO

from hypothesis import given, settings
from scipp.testing import strategies as scst
import scipp as sc


@given(scst.dataarrays())
@settings(max_examples=300)
def test_data_array_hdf5(da):
    f = BytesIO()
    da.to_hdf5(filename=f)
    f.seek(0)
    loaded = sc.io.open_hdf5(filename=f)

    assert sc.utils.isnear(loaded, da, equal_nan=True)
