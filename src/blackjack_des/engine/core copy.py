from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass(frozen=True, order=True)
class Event:
    time: int
    type: str
    seq: int
    data: dict[str, Any]


@dataclass
class SimulationResult:
    final_state: Any
    now: int
    events_processed: int
    metrics: dict[str, Any]
    trace: List[Event]


def run_simulation(
    *,
    initial_state: Any,
    initial_events: List[Event],
    handlers: Dict[str, Callable[[Any, Event, int], List[Event]]],
    stop_condition: Callable[[Any, int, int, dict[str, Any]], bool],
    observers: Optional[List[Any]] = None,
    max_events: int = 1000,
) -> SimulationResult:
    state = initial_state
    now = 0
    events_processed = 0
    trace = []
    metrics = {}
    events = initial_events[:]

    if observers is None:
        observers = []

    while len(events) >= 1 and events_processed < max_events:
        event_to_process = min(events, key=lambda e: e.time)

        if event_to_process.time < now:
            raise ValueError("Event scheduled in the past")
        
        events.remove(event_to_process)
        now = event_to_process.time
        trace.append(event_to_process)
        events_processed += 1
        new_events = handlers[event_to_process.type](state, event_to_process, now) or []

        for event in new_events:
            if event.time < now:
                raise ValueError("Event scheduled in the past")
        events.extend(new_events)

        for observer in observers:
            observer.on_event(state, event_to_process, now)
        
        if stop_condition(state, now, events_processed, metrics):
            break

    for observer in observers:
        metrics.update(observer.finalize(state, now))

    result = SimulationResult(
        final_state=state,
        now=now,
        events_processed=events_processed,
        metrics=metrics,
        trace=trace
    )

    return result
