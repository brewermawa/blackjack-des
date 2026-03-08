from blackjack_des.engine.core import Event
from .state import State
from blackjack.blackjack_eval import BlackJackEval
from blackjack.strategy import BlackJackStrategy
from blackjack_des.events import(
    deal_card, dealing_completed, early_exit_check, player_turn,
    player_turn_completed, dealer_turn, dealer_turn_completed, resolve_round,
) 


def handle_round_started(state, event, now):
    if state.round_state != State.RoundState.READY:
        raise ValueError("ROUND_STARTED is only valid in READY state")

    state.round_state = State.RoundState.DEALING

    return [
        deal_card(time=now+1, target="player", hand_index=0),
        deal_card(time=now+2, target="dealer", hand_index=None),
        deal_card(time=now+3, target="player", hand_index=0),
        deal_card(time=now+4, target="dealer", hand_index=None),
        dealing_completed(time=now+5),
    ]


def handle_deal_card(state: State, event: Event, now: int):
    allowed_states = {
        State.RoundState.DEALING,
        State.RoundState.PLAYER_ACTING,
        State.RoundState.DEALER_ACTING,
    }
    if state.round_state not in allowed_states:
        raise ValueError(f"DEAL_CARD not permitted in state: {state.round_state}")

    if not isinstance(event.data, dict):
        raise ValueError("DEAL_CARD event.data must be a dict")

    if "target" not in event.data:
        raise ValueError("DEAL_CARD requires data['target']")
    

    target = event.data["target"]
    if isinstance(target, str):
        target = target.strip().upper()
    else:
        raise ValueError("Target must be a string")

    if target not in {"PLAYER", "DEALER"}:
        raise ValueError("DEAL_CARD data['target'] must be 'PLAYER' or 'DEALER'")

    hand_index = event.data.get("hand_index", None)

    if target == "DEALER":
        if hand_index is not None:
            raise ValueError("DEAL_CARD to DEALER must not include hand_index")

        card = state.round.deck.draw(1)[0]
        state.round.dealer_hand.add_card(card)

        state.trace.append(f"{now}: DEAL_CARD -> DEALER")

        return []

    #PLAYER
    if hand_index is None:
        raise ValueError("DEAL_CARD to PLAYER requires hand_index")

    if not isinstance(hand_index, int):
        raise ValueError("DEAL_CARD data['hand_index'] must be an int")

    if hand_index < 0 or hand_index >= len(state.round.player_hands):
        raise ValueError(f"DEAL_CARD invalid hand_index: {hand_index}")

    card = state.round.deck.draw(1)[0]
    state.round.player_hands[hand_index]["hand"].add_card(card)
    
    state.trace.append(f"{now}: DEAL_CARD -> PLAYER[{hand_index}]")
    return []


def handle_dealing_completed(state: State, event: Event, now: int):
    if state.round_state != State.RoundState.DEALING:
        raise ValueError(f"DEALING COMPLETED not permitted in state: {state.round_state}")
    
    state.round_state = State.RoundState.PLAYER_ACTING
    state.active_hand_index = 0
    state.trace.append(f"{now}: INITIAL_CARDS_DEALT")

    return [early_exit_check(time=now+1)]


def handle_early_exit_check(state: State, event: Event, now: int):
    bj_dealer = BlackJackEval.blackjack(state.round.dealer_hand)
    bj_player = BlackJackEval.blackjack(state.round.player_hands[0]["hand"])

    state.trace.append(f"{now}: EARLY_EXIT_CHECK")

    if not (bj_player or bj_dealer):
        return [player_turn(time=now+1)]
    else:
        state.round_state = State.RoundState.RESOLVING
        return [resolve_round(time=now+1)]


def handle_player_turn(state: State, event: Event, now: int):
    state.trace.append(f"{now}: PLAYER_TURN")

    player_hand = state.round.player_hands[0]["hand"]
    dealer_card = state.round.dealer_hand.cards[0]

    if BlackJackStrategy.strategy(player_hand=player_hand, dealer_card=dealer_card) == BlackJackStrategy.Action.SURRENDER:
        state.round_state = State.RoundState.RESOLVING
        state.round.player_hands[0]["surrendered"] = True
        
        return [resolve_round(time=now+1)]
        
    if BlackJackStrategy.strategy(player_hand=player_hand, dealer_card=dealer_card) == BlackJackStrategy.Action.DOUBLE:
        state.round.player_hands[0]["doubled"] = True

        return [deal_card(time=now+1, target="player", hand_index=0)]
    
    if BlackJackStrategy.strategy(player_hand=player_hand, dealer_card=dealer_card) == BlackJackStrategy.Action.HIT:
        return [
            deal_card(time=now+1, target="player", hand_index=0),
            player_turn(time=now+1)
        ]
    
    return [player_turn_completed(time=now+1)]


def handle_player_turn_completed(state: State, event: Event, now: int):
    if state.round_state != State.RoundState.PLAYER_ACTING:
        raise ValueError(f"PLAYER_TURN_COMPLETED not permitted in state: {state.round_state}")
    
    state.trace.append(f"{now}: PLAYER_TURN_COMPLETED")
    
    state.round_state = State.RoundState.DEALER_ACTING
    state.active_hand_index = None

    return [dealer_turn(time=now+1)]

def handle_dealer_turn(state: State, event: Event, now: int):
    if state.round_state != State.RoundState.DEALER_ACTING:
        raise ValueError(f"DEALER_TURN not permitted in state: {state.round_state}")
    
    state.trace.append(f"{now}: DEALER_TURN")
    
    return [dealer_turn_completed(time=now+1)]



def handle_dealer_turn_completed(state: State, event: Event, now: int):
    if state.round_state != State.RoundState.DEALER_ACTING:
        raise ValueError(f"DEALER_TURN_COMPLETED not permitted in state: {state.round_state}")
    
    state.trace.append(f"{now}: DEALER_TURN_COMPLETED")
    state.round_state = State.RoundState.RESOLVING
    state.active_hand_index = None

    return[resolve_round(time=now+1)]


def handle_resolve_round(state: State, event: Event, now: int):
    if state.round_state != State.RoundState.RESOLVING:
        raise ValueError(f"RESOLVE_ROUND not permitted in state: {state.round_state}")

    state.trace.append(f"{now}: RESOLVE_ROUND")
    state.round_state = State.RoundState.DONE
    state.outcomes = []
