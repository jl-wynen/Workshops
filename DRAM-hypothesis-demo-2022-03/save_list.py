from io import StringIO

from hypothesis import given, settings, example
from hypothesis import strategies as st


def save_list(data, f):
    for element in data:
        f.write(element + ',')


def load_list(f):
    # initial:
    # return f.read().split(',')[:-1]
    # improved but still faulty
    return f.read().split(',')[:-1]


# # initial
# def test_roundtrip():
#     data = ['a', 'b ', ' c', 'a\nd']
#     f = StringIO()
#     save_list(data, f)
#     f.seek(0)
#     loaded = load_list(f)
#     assert loaded == data


# w/ hypo
@given(st.lists(st.text()))
def test_roundtrip(data):
    f = StringIO()
    save_list(data, f)
    f.seek(0)
    loaded = load_list(f)
    assert loaded == data


# w/ hypo
# fixed example
@given(st.lists(st.text()))
@example([','])
def test_roundtrip(data):
    f = StringIO()
    save_list(data, f)
    f.seek(0)
    loaded = load_list(f)
    assert loaded == data

