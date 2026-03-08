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

