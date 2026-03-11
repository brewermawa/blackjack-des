import pytest

from blackjack.round import BlackJackRound
from blackjack.fixed_deck import FixedDeck
from cards import Deck, Hand
from blackjack_des.state import State
from blackjack_des.events import player_turn_completed
from blackjack_des.handlers import handle_player_turn_completed
from blackjack_des.engine.core import Event


class TestPlayerRound:
    @pytest.fixture
    def default_state(self):
        fixed_deck = FixedDeck()
        round = BlackJackRound(deck=fixed_deck, hits_soft_17=False)
        state = State(round=round, round_state=State.RoundState.DEALING)

        return state
    
    
    @pytest.mark.parametrize(
        "round_state",
        [
            State.RoundState.READY,
            State.RoundState.DEALING,
            State.RoundState.DEALER_ACTING,
            State.RoundState.DONE,
            State.RoundState.RESOLVING
        ]
    )
    def test_raises_value_error_if_state_is_not_dealing_or_player_acting(self, round_state):
        deck = Deck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=round_state)
        
        with pytest.raises(ValueError):
            handle_player_turn_completed(state, None, 0)

