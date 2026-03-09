import pytest

from blackjack.round import BlackJackRound
from cards import Deck
from blackjack_des.state import State
from blackjack_des.events import deal_card
from blackjack_des.handlers import handle_deal_card
from blackjack_des.engine.core import Event


class TestDealCard:
    @pytest.fixture
    def default_state(self):
        deck = Deck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=State.RoundState.DEALING)

        return state

    @pytest.mark.parametrize(
        "round_state",
        [
            State.RoundState.READY,
            State.RoundState.DONE,
            State.RoundState.RESOLVING
        ]
    )
    def test_raises_value_error_if_state_is_not_correct(self, round_state):
        deck = Deck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=round_state)
        
        with pytest.raises(ValueError):
            handle_deal_card(state, None, 0)


    def test_raises_value_error_if_event_data_target_is_not_supplied(self, default_state):
        event = Event(time=0, type="DEAL_CARD", data={})

        with pytest.raises(ValueError):
            handle_deal_card(default_state, event, 0)


    @pytest.mark.parametrize(
        "target",
        [
            123,
            ["player"],
            True
        ]
    )
    def test_raises_value_error_if_event_data_target_is_not_string(self, default_state, target):
        event = Event(time=0, type="DEAL_CARD", data={"target": target})

        with pytest.raises(ValueError):
            handle_deal_card(default_state, event, 0)


    @pytest.mark.parametrize(
        "target",
        [
            "jugador",
            "first",
            "Second"
        ]
    )
    def test_raises_value_error_if_event_data_target_is_not_player_or_dealer(self, default_state, target):
        event = Event(time=0, type="DEAL_CARD", data={"target": target})

        with pytest.raises(ValueError):
            handle_deal_card(default_state, event, 0)


    def test_raises_value_error_if_event_data_target_is_dealer_and_hand_index_supplied(self, default_state):
        event = Event(time=0, type="DEAL_CARD", data={"target": "dealer", "hand_index": 0})

        with pytest.raises(ValueError):
            handle_deal_card(default_state, event, 0)


    def test_raises_value_error_if_event_data_target_is_player_and_hand_index_not_supplied(self, default_state):
        event = Event(time=0, type="DEAL_CARD", data={"target": "player"})

        with pytest.raises(ValueError):
            handle_deal_card(default_state, event, 0)


    @pytest.mark.parametrize(
        "hand_index",
        [
            "0",
            1.0,
            True,
        ]
    )
    def test_raises_value_error_if_event_data_target_is_player_and_hand_index_supplied_but_not_int(self, default_state, hand_index):
        event = Event(time=0, type="DEAL_CARD", data={"target": "player", "hand_index": hand_index})

        with pytest.raises(ValueError):
            handle_deal_card(default_state, event, 0)

    
    @pytest.mark.parametrize(
        "hand_index",
        [
            -1,
            1,
            123,
        ]
    )
    def test_raises_value_error_if_event_data_target_is_player_and_hand_index_supplied_but_invalid(self, default_state, hand_index):
        event = Event(time=0, type="DEAL_CARD", data={"target": "player", "hand_index": hand_index})

        with pytest.raises(ValueError):
            handle_deal_card(default_state, event, 0)


    def test_round_state_does_not_change(self, default_state):
        event = Event(time=0, type="DEAL_CARD", data={"target": "player", "hand_index": 0})
        initial_state = default_state.round_state
        handle_deal_card(default_state, event, 0)
        final_state = default_state.round_state

        assert initial_state == final_state


    def test_round_state_returns_empty_list(self, default_state):
        event = Event(time=0, type="DEAL_CARD", data={"target": "player", "hand_index": 0})
        event_list = handle_deal_card(default_state, event, 0)

        assert len(event_list) == 0


    def test_number_of_cards_in_list_increases_by_one(self, default_state):
        event = Event(time=0, type="DEAL_CARD", data={"target": "player", "hand_index": 0})
        initial_cards = len(default_state.round.player_hands[0]["hand"])
        handle_deal_card(default_state, event, 0)
        final_cards = len(default_state.round.player_hands[0]["hand"])

        assert final_cards == initial_cards + 1


    def test_card_added_to_correct_target_other_target_not_affected(self, default_state):
        event = Event(time=0, type="DEAL_CARD", data={"target": "player", "hand_index": 0})
        initial_dealer_cards = len(default_state.round.dealer_hand)
        handle_deal_card(default_state, event, 0)
        final_dealer_cards = len(default_state.round.dealer_hand)

        assert final_dealer_cards == initial_dealer_cards

