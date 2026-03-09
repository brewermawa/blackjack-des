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


def handle_deal_card(state, event, now):
    allowed_states = {
        State.RoundState.DEALING,
        State.RoundState.PLAYER_ACTING,
        State.RoundState.DEALER_ACTING,
    }
    if state.round_state not in allowed_states:
        raise ValueError(f"DEAL_CARD not permitted in state: {state.round_state}")
    
    if "target" not in event.data:
        raise ValueError("DEAL_CARD requires data['target']")
    
    target = event.data["target"]
    if isinstance(target, str):
        target = target.strip().lower()
    else:
        raise ValueError("data['target'] must be a string")
    
    if target not in {"player", "dealer"}:
        raise ValueError("DEAL_CARD data['target'] must be 'player' or 'dealer'")
    
    hand_index = event.data.get("hand_index", None)
    
    if target == "dealer":
        if hand_index is not None:
            raise ValueError("DEAL_CARD to DEALER must not include hand_index")
        
        card = state.round.deck.draw(1)[0]
        state.round.dealer_hand.add_card(card)

    else:
        if hand_index is None:
            raise ValueError("DEAL_CARD to PLAYER requires hand_index")
        
        if not isinstance(hand_index, int) or isinstance(hand_index, bool):
            raise ValueError("DEAL_CARD data['hand_index'] must be an int")
        
        if hand_index < 0 or hand_index >= len(state.round.player_hands):
            raise ValueError(f"DEAL_CARD invalid hand_index: {hand_index}")
        
        card = state.round.deck.draw(1)[0]
        state.round.player_hands[hand_index]["hand"].add_card(card)
        
    return []


def handle_early_exit_check(state, event, now):
    if state.round_state != State.RoundState.DEALING:
        raise ValueError("EARLY_EXIT_CHECK is only valid in DEALING state")
    
    player_bj = BlackJackEval.blackjack(state.round.player_hands[0]["hand"])
    dealer_bj = BlackJackEval.blackjack(state.round.dealer_hand)

    if player_bj or dealer_bj:
        return [resolve_round(time=now+1)]
    else:
        return [player_turn(time=now+1, hand_index=0)]
    

def handle_player_turn(state, event, now):
    allowed_states = {
        State.RoundState.DEALING,
        State.RoundState.PLAYER_ACTING,
    }
    if state.round_state not in allowed_states:
        raise ValueError(f"PLAYER_ACTING not permitted in state: {state.round_state}")
    
    
    hand_index = event.data.get("hand_index", None)

    if hand_index is None:
        raise ValueError("player_turn requires hand_index")
    
    if not isinstance(hand_index, int) or isinstance(hand_index, bool):
        raise ValueError("player_turn data['hand_index'] must be an int")
    
    if hand_index < 0 or hand_index >= len(state.round.player_hands):
        raise ValueError(f"player_turn invalid hand_index: {hand_index}")