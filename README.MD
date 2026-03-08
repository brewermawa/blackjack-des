# DES
 A minimal discrete-event simulation kernel. It advances a simulated clock by processing a time-ordered event queue and dispatching events to domain-provided handlers.
 
 ## Core idea
 - The engine does not know the domain.
 - The domain provides handlers for each event.type.
 - Handlers may schedule new events.
 - The engine never decides what happens next; the domain does.
 
 ## Inputs
 - initial_state: mutable domain state owned by the simulation
 - initial_events: list of events scheduled at simulation start
 - handlers: mapping event.type → handler(state, event, now)
 - stop_condition: predicate evaluated after each event

 ## Outputs
 - final_state: domain state after simulation ends
 - now: final simulated time
 - events_processed: total number of processed events
 - metrics: aggregated metrics produced by observers
 - trace: ordered list of processed events
 
 ## Guarantees
 - Events are processed in non-decreasing timestamp order
 - The simulated clock only moves forward
 - Each event is dispatched to exactly one handler
 - The engine never mutates domain state directly