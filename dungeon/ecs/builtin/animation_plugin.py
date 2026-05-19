from dungeon.ecs.plugin import Plugin
from dungeon.ecs.schedule import Schedule
from dungeon.ecs.resource import Res
from dungeon.ecs.query import Query
from dungeon.ecs.builtin.component import (
    Entity,
    Transform,
    TweenPosition,
    AnimationEasing,
)
from dungeon.ecs.builtin.resource import DeltaTime
from dungeon.ecs.ecs import App


def update(
    app: App,
    query: Query[Entity, Transform, TweenPosition],
    res_delta_time: Res[DeltaTime],
):
    for entity, transform, tween_position in query:
        assert tween_position.easing == AnimationEasing.LINEAR, tween_position.easing

        tween_position.elapsed += res_delta_time.data.value
        t = min(tween_position.elapsed / tween_position.duration, 1.0)
        transform.position = ((1 - t) * tween_position.start) + (t * tween_position.end)

        if tween_position.elapsed >= tween_position.duration:
            app.remove_component(entity.id, TweenPosition)


class AnimationPlugin(Plugin):
    def build(self, app: App):
        app.add_system(Schedule.LogicalUpdate, update)
