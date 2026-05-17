import pygame

from typing import get_type_hints, get_origin, get_args
from collections.abc import Callable
from dungeon.ecs.plugin import Plugin
from dungeon.ecs.query import Query
from dungeon.ecs.resource import Res
from dungeon.ecs.schedule import Schedule


class App:
    def __init__(self, title: str):
        self._entities: dict[int, dict[type, object]] = {}
        self._next_id = 0
        self._systems: dict[Schedule, list[tuple[Callable, list]]] = {}
        self._systems[Schedule.StartUp] = []
        self._systems[Schedule.UpdateHighPriority] = []
        self._systems[Schedule.Update] = []
        self._resources: dict[type, object] = {}
        self._running = True

        pygame.init()
        pygame.display.set_caption(title)

    def set_should_close(self):
        self._running = False

    def spawn(self, *components: object) -> int:
        eid = self._next_id
        self._next_id += 1
        self._entities[eid] = {type(c): c for c in components}
        return eid

    def insert_resource(self, res: Res):
        self._resources[type(res)] = res

    def add_plugin(self, plugin: Plugin) -> "App":
        plugin.build(self)
        return self

    def add_system(self, schedule: Schedule, system: Callable):
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
        self._run_systems(self._systems[Schedule.StartUp])

        clock = pygame.time.Clock()

        while self._running:
            clock.tick(60)

            self._run_systems(self._systems[Schedule.UpdateHighPriority])
            self._run_systems(self._systems[Schedule.Update])

        pygame.quit()
