from typing import Iterator


class Query[*Ts]:
    def __init__(self, rows: list[tuple[*Ts]]):
        self._rows = rows

    def __iter__(self) -> Iterator[tuple[*Ts]]:
        return iter(self._rows)

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, index: int) -> tuple[*Ts]:
        return self._rows[index]
