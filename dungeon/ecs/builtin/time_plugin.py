import time

from dungeon.ecs.plugin import Plugin
from dungeon.ecs.schedule import Schedule
from dungeon.ecs.query import Query
from dungeon.ecs.resource import Res
from dungeon.ecs.builtin.resource import DeltaTime
from dungeon.ecs.ecs import App


def update_time(res_delta_time: Res[DeltaTime]):
    timepoint = time.perf_counter()
    delta_time_state = res_delta_time.data
    if delta_time_state._last_timepoint is None:
        delta_time_state._last_timepoint = timepoint
    delta_time_state.value = timepoint - delta_time_state._last_timepoint
    delta_time_state._last_timepoint = timepoint


class TimePlugin(Plugin):
    def build(self, app: App):
        app.add_system(Schedule.UpdateHighPriority, update_time)
        app.insert_resource(DeltaTime())
