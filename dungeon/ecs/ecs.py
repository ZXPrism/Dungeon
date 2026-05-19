import pygame

from enum import IntEnum
from typing import get_type_hints, get_origin, get_args
from collections.abc import Callable
from dungeon.ecs.plugin import Plugin
from dungeon.ecs.query import Query
from dungeon.ecs.resource import Res
from dungeon.ecs.schedule import Schedule


class ActionType(IntEnum):
    SPAWN = 0
    DESPAWN = 1
    ADD_COMPONENT = 2
    REMOVE_COMPONENT = 3
    INSERT_RESOURCE = 4
    REMOVE_RESOURCE = 5


class App:
    def __init__(self, title: str):
        self._entities: dict[int, dict[type, object]] = {}
        self._next_id = 0
        self._systems: dict[Schedule, list[tuple[Callable, list]]] = {}
        self._systems[Schedule.StartUp] = []
        self._systems[Schedule.LogicalUpdateHighPriority] = []
        self._systems[Schedule.LogicalUpdate] = []
        self._systems[Schedule.RenderUpdate] = []
        self._resources: dict[type, object] = {}
        self._deferred_actions = []
        self._running = False

        pygame.init()
        pygame.display.set_caption(title)

    def set_should_close(self):
        self._running = False

    def spawn(self, *components: object) -> int:
        eid = self._next_id
        self._next_id += 1
        self._deferred_actions.append(lambda: self._spawn(eid, *components))
        return eid

    def _spawn(self, entity_id: int, *components: object):
        self._entities[entity_id] = {type(c): c for c in components}
        if len(components) != len(self._entities[entity_id]):
            raise RuntimeError("Detected duplicate components!")

    def despawn(self, entity_id: int):
        self._deferred_actions.append(lambda: self._despawn(entity_id))

    def _despawn(self, entity_id: int):
        if entity_id not in self._entities:
            raise RuntimeError(f"Entity {entity_id} does not exist!")
        self._entities.pop(entity_id)

    def add_component(self, entity_id: int, *components: object):
        self._deferred_actions.append(
            lambda: self._add_component(entity_id, *components)
        )

    def _add_component(self, entity_id: int, *components: object):
        if entity_id not in self._entities:
            raise RuntimeError(f"Entity {entity_id} does not exist!")
        component_dict = self._entities[entity_id]
        for component in components:
            component_type = type(component)
            if component_type in component_dict:
                raise RuntimeError(
                    f"Entity {entity_id} already has component {component_type}!"
                )
            component_dict[component_type] = component

    def remove_component(self, entity_id: int, *component_types: type):
        self._deferred_actions.append(
            lambda: self._remove_component(entity_id, *component_types)
        )

    def _remove_component(self, entity_id: int, *component_types: type):
        # handle: component does not exist
        raise NotImplementedError("")

    def insert_resource(self, res: Res):
        self._deferred_actions.append(lambda: self._insert_resource(res))

    def _insert_resource(self, res: Res):
        self._resources[type(res)] = res

    def remove_resource(self, res_type: type):
        self._deferred_actions.append(lambda: self._remove_resource(res_type))

    def _remove_resource(self, res_type: type):
        # handle: res does not exist
        raise NotImplementedError("")

    def add_plugin(self, plugin: Plugin) -> "App":
        if self._running == True:
            raise RuntimeError("It's forbidden to add plugins when the app is running")
        plugin.build(self)
        return self

    def add_system(self, schedule: Schedule, system: Callable):
        if self._running == True:
            raise RuntimeError("It's forbidden to add plugins when the app is running")

        type_hints = get_type_hints(system)
        queries = []
        query_app = False

        for annotation in type_hints.values():
            origin = get_origin(annotation) or annotation
            component_type = get_args(annotation)

            if origin is Query:
                queries.append(component_type)
            elif origin is Res:
                if len(component_type) != 1:
                    raise RuntimeError(
                        f"Res query should only have one target, but given {component_type}"
                    )
                queries.append(component_type[0])
            elif origin is App:
                if query_app:
                    raise RuntimeError(
                        "System function can only have at most one `App` argument!"
                    )
                query_app = True
            else:
                raise RuntimeError(
                    f"Found invalid type {origin} in system function arguments!"
                )

        self._systems[schedule].append((system, queries))

    def _run_systems(self, systems: list[tuple[Callable, list]]):
        for system, queries in systems:
            type_hints = get_type_hints(system)
            args = []

            idx_compensation = 0
            for idx, annotation in enumerate(type_hints.values()):
                idx += idx_compensation

                origin = get_origin(annotation) or annotation
                if origin is App:
                    args.append(self)
                    idx_compensation = -1
                elif origin is Query:
                    rows = [
                        tuple(components[t] for t in queries[idx])
                        for components in self._entities.values()
                        if all(t in components for t in queries[idx])
                    ]
                    args.append(Query(rows))
                else:  # Res
                    res = queries[idx]
                    if res not in self._resources:
                        raise RuntimeError(
                            f"Resource of type {res} has not been inserted yet!"
                        )
                    args.append(Res(self._resources[queries[idx]]))

            system(*args)

    def run(self):
        self._running = True

        for action in self._deferred_actions:
            action()
        self._deferred_actions.clear()

        self._run_systems(self._systems[Schedule.StartUp])

        clock = pygame.time.Clock()

        while self._running:
            clock.tick(60)

            for action in self._deferred_actions:
                action()
            self._deferred_actions.clear()

            self._run_systems(self._systems[Schedule.LogicalUpdateHighPriority])
            self._run_systems(self._systems[Schedule.LogicalUpdate])
            self._run_systems(self._systems[Schedule.RenderUpdate])

        pygame.quit()
