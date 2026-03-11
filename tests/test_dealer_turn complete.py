import pytest

from blackjack.round import BlackJackRound
from blackjack.fixed_deck import FixedDeck
from cards import Deck, Hand
from blackjack_des.state import State
from blackjack_des.events import dealer_turn_completed
from blackjack_des.handlers import handle_dealer_turn_completed
from blackjack_des.engine.core import Event


class TestPlayerTurnCompleted:
    @pytest.fixture
    def default_state(self):
        deck = FixedDeck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=State.RoundState.DEALER_ACTING)

        return state
    
    
    @pytest.mark.parametrize(
        "round_state",
        [
            State.RoundState.READY,
            State.RoundState.DEALING,
            State.RoundState.PLAYER_ACTING,
            State.RoundState.DONE,
            State.RoundState.RESOLVING
        ]
    )
    def test_raises_value_error_if_state_is_not_dealer_acting(self, default_state, round_state):
        default_state.round_state = round_state
        
        with pytest.raises(ValueError):
            handle_dealer_turn_completed(default_state, None, 0)


    def test_test_next_event_is_resolve_round(self, default_state):
        event = dealer_turn_completed(time=0)
        next_events = handle_dealer_turn_completed(default_state, event, 0)

        assert next_events[0].type == "RESOLVE_ROUND"

