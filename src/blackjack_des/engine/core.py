import heapq
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass(frozen=True, order=True)
class Event:
    time: int
    type: str = field(compare=False)
    data: dict[str, Any] = field(compare=False)
    seq: int = 0


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
    events = []

    seq = 0
    for event in initial_events:
        heapq.heappush(events, Event(time=event.time, seq=seq, type=event.type, data=event.data))
        seq += 1

    if observers is None:
        observers = []

    while len(events) >= 1 and events_processed < max_events:
        event_to_process = heapq.heappop(events)

        if event_to_process.time < now:
            raise ValueError("Event scheduled in the past")
        
        now = event_to_process.time
        trace.append(event_to_process)
        events_processed += 1
        new_events = handlers[event_to_process.type](state, event_to_process, now) or []

        for event in new_events:
            seq += 1
            if event.time < now:
                raise ValueError("Event scheduled in the past")
            
            heapq.heappush(events, Event(time=event.time, seq=seq, type=event.type, data=event.data))
        

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


