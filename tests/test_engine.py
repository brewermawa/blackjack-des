import pytest

from blackjack_des.engine.core import Event, SimulationResult, run_simulation


class CountingObserver:
    """Minimal observer to prove metrics are produced."""
    def __init__(self) -> None:
        self.count = 0

    def on_event(self, state, event, now) -> None:
        self.count += 1

    def finalize(self, state, now):
        return {"events_seen": self.count, "final_now": now}
    

def test_engine_processes_events_in_timestamp_order_and_returns_trace_and_metrics():
    state = {"handled": []}

    def handle_a(state, event, now):
        state["handled"].append(("A", now))
        return []

    def handle_b(state, event, now):
        state["handled"].append(("B", now))
        return []

    def handle_c(state, event, now):
        state["handled"].append(("C", now))
        return []

    handlers = {
        "A": handle_a,
        "B": handle_b,
        "C": handle_c,
    }

    # Intentionally unsorted initial events (engine must order them by time)
    initial_events = [
        Event(time=10, type="A", data={}),
        Event(time=5, type="B", data={}),
        Event(time=5, type="C", data={}),
    ]

    def stop_condition(state, now, events_processed, metrics):
        return events_processed >= 3
    
    observer = CountingObserver()

    result = run_simulation(
        initial_state=state,
        initial_events=initial_events,
        handlers=handlers,
        stop_condition=stop_condition,
        observers=[observer],
        max_events=100
    )

    assert result.events_processed == 3
    assert result.trace is not None
    assert len(result.trace) == 3

    times = [e.time for e in result.trace]
    assert times == sorted(times), "Trace must be non-decreasing by event.time"
    assert result.now == times[-1], "Final now must equal last processed event time"

    handler_times = [t for (_, t) in result.final_state["handled"]]
    assert handler_times == sorted(handler_times), "Handler now must be non-decreasing"

    assert "events_seen" in result.metrics
    assert result.metrics["events_seen"] == 3
    assert result.metrics["final_now"] == result.now


def test_handlers_can_schedule_new_events_and_engine_processes_them_in_order():
    state = {"handled": []}

    def handle_a(state, event, now):
        state["handled"].append(("A", now))
        return [Event(time=now + 2, type="B", data={})]
    
    def handle_b(state, event, now):
        state["handled"].append(("B", now))
        return [Event(time=now + 8, type="C", data={})]
    
    def handle_c(state, event, now):
        state["handled"].append(("C", now))
        return []
    
    handlers = {
        "A": handle_a,
        "B": handle_b,
        "C": handle_c,
    }
    
    initial_events = [
        Event(time=10, type="A", data={}),
    ]

    def stop_condition(state, now, events_processed, metrics):
        return events_processed >= 3
    
    result = run_simulation(
        initial_state=state,
        initial_events=initial_events,
        handlers=handlers,
        stop_condition=stop_condition,
        observers=[],
        max_events=100
    )

    assert result.now == 20
    assert result.events_processed == 3
    assert result.trace is not None
    assert len(result.trace) == 3

    assert state["handled"][0][0] == "A"
    assert state["handled"][1][0] == "B"
    assert state["handled"][2][0] == "C"

    assert state["handled"][0][1] == 10
    assert state["handled"][1][1] == 12
    assert state["handled"][2][1] == 20


def test_simulation_ends_when_event_queue_is_empty():
    state = {"handled": []}

    def handle_a(state, event, now):
        state["handled"].append(("A", now))
        return [Event(time=now + 2, type="B", data={})]
    
    def handle_b(state, event, now):
        state["handled"].append(("B", now))
        return [Event(time=now + 8, type="C", data={})]
    
    def handle_c(state, event, now):
        state["handled"].append(("C", now))
        return []
    
    handlers = {
        "A": handle_a,
        "B": handle_b,
        "C": handle_c,
    }
    
    initial_events = [
        Event(time=10, type="A", data={}),
    ]

    def stop_condition(state, now, events_processed, metrics):
        return False
    
    result = run_simulation(
        initial_state=state,
        initial_events=initial_events,
        handlers=handlers,
        stop_condition=stop_condition,
        observers=[],
        max_events=100
    )

    assert result.events_processed == 3
    assert len(result.trace) == 3
    assert state["handled"] == [("A",10),("B",12),("C",20)]
    assert result.now == 20


def test_observers_are_called_for_each_event_and_finalize_once():
    class SeenObserver:
        def __init__(self) -> None:
            self.count = 0
            self.events_seen = []
            self.finalize_count = 0

        def on_event(self, state, event, now) -> None:
            self.count += 1
            self.events_seen.append(now)

        def finalize(self, state, now):
            self.finalize_count += 1
            return {
                "events_seen": self.events_seen,
                "final_now": now,
                "finalize_count": self.finalize_count
            }

    state = {"handled": []}

    def handle_a(state, event, now):
        state["handled"].append(("A", now))
        return []

    def handle_b(state, event, now):
        state["handled"].append(("B", now))
        return []

    def handle_c(state, event, now):
        state["handled"].append(("C", now))
        return []

    handlers = {
        "A": handle_a,
        "B": handle_b,
        "C": handle_c,
    }

    initial_events = [
        Event(time=10, type="A", data={}),
        Event(time=5, type="B", data={}),
        Event(time=5, type="C", data={}),
    ]

    def stop_condition(state, now, events_processed, metrics):
        return events_processed >= 3
    
    observer = SeenObserver()

    result = run_simulation(
        initial_state=state,
        initial_events=initial_events,
        handlers=handlers,
        stop_condition=stop_condition,
        observers=[observer],
        max_events=100
    )

    assert result.events_processed == 3
    assert result.trace is not None
    assert len(result.trace) == 3

    # --- Assertions: metrics produced ---
    assert "events_seen" in result.metrics
    assert result.metrics["events_seen"] == [5, 5, 10]
    assert result.metrics["final_now"] == result.now
    assert result.metrics["finalize_count"] == 1


def test_engine_raises_valueerror_when_handler_schedules_event_in_the_past():
    state = {"handled": []}

    def handle_a(state, event, now):
        state["handled"].append(("A", now))
        return [Event(time=now - 2, type="B", data={})]
    
    def handle_b(state, event, now):
        state["handled"].append(("B", now))
        return []
    
    
    handlers = {
        "A": handle_a,
        "B": handle_b,
    }
    
    initial_events = [
        Event(time=10, type="A", data={}),
    ]

    def stop_condition(state, now, events_processed, metrics):
        return False
    
    with pytest.raises(ValueError):
        run_simulation(
            initial_state=state,
            initial_events=initial_events,
            handlers=handlers,
            stop_condition=stop_condition,
            observers=[],
            max_events=100
        )

    assert state["handled"] == [("A", 10)]
    