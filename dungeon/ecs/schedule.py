from enum import IntEnum


class Schedule(IntEnum):
    StartUp = 1
    LogicalUpdateHighPriority = 2
    LogicalUpdate = 3
    RenderUpdate = 4
