from enum import IntEnum


class Schedule(IntEnum):
    StartUp = 1
    UpdateHighPriority = 2
    Update = 3
