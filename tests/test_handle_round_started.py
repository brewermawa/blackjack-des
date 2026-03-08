import pytest

from blackjack.round import BlackJackRound
from cards import Deck
from blackjack_des.state import State
from blackjack_des.events import round_started
from blackjack_des.handlers import handle_round_started
from blackjack_des.engine.core import Event


class TestRoundStarted:
    @pytest.fixture
    def defaut_state(self):
        deck = Deck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round)

        return state

    @pytest.mark.parametrize(
        "round_state",
        [
            State.RoundState.DEALING,
            State.RoundState.PLAYER_ACTING,
            State.RoundState.DEALER_ACTING,
            State.RoundState.DONE,
            State.RoundState.RESOLVING
        ]
    )
    def test_raises_value_error_if_state_is_not_ready(self, round_state):
        deck = Deck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=round_state)
        
        with pytest.raises(ValueError):
            handle_round_started(state, None, 0)

    
    def test_leaves_round_state_in_round_state_dealing(self, defaut_state):
        handle_round_started(defaut_state, None, 0)
        assert defaut_state.round_state == State.RoundState.DEALING


    def test_round_started_returns_list_with_5_elements(self, defaut_state):
        events = handle_round_started(defaut_state, None, 0)
        assert len(events) == 5


    def test_round_started_return_list_elements_are_instance_of_event(self, defaut_state):
        events = handle_round_started(defaut_state, None, 0)
        
        for event in events:
            assert isinstance(event, Event) is True


    def test_round_started_return_list_in_with_correct_target_and_in_correct_order(self, defaut_state):
        events = handle_round_started(defaut_state, None, 0)

        assert events[0].type == "DEAL_CARD"
        assert events[0].data["target"] == "player"
        assert events[0].data["hand_index"] == 0

        assert events[1].type == "DEAL_CARD"
        assert events[1].data["target"] == "dealer"

        assert events[2].type == "DEAL_CARD"
        assert events[2].data["target"] == "player"
        assert events[2].data["hand_index"] == 0

        assert events[3].type == "DEAL_CARD"
        assert events[3].data["target"] == "dealer"

        assert events[4].type == "DEALING_COMPLETED"
