from scipp.testing import strategies as scst
import scipp as sc

from hypothesis import given


@given(scst.variables())
def test_show_var(var):
    print(var)
