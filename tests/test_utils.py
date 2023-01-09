from gfe_devices_grabber.utils import split_list


def test_split():
    records = list(range(1, 11))
    assert split_list(records, 3) == [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]
