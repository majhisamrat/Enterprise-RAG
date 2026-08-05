from typing import Iterable


def batch_iterator( items: list, batch_size: int) -> Iterable[list]:

    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]