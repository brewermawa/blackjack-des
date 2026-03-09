import pytest

from blackjack.round import BlackJackRound
from blackjack.fixed_deck import FixedDeck
from cards import Deck
from blackjack_des.state import State
from blackjack_des.events import player_turn
from blackjack_des.handlers import handle_player_turn
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
            handle_player_turn(state, None, 0)


    def test_raises_value_error_if_event_data_hand_index_not_supplied(self, default_state):
        event = Event(time=0, type="PLAYER_TURN", data={})

        with pytest.raises(ValueError):
            handle_player_turn(default_state, event, 0)


    @pytest.mark.parametrize(
        "hand_index",
        [
            "0",
            1.0,
            True,
        ]
    )
    def test_raises_value_error_if_event_data_hand_index_supplied_but_not_int(self, default_state, hand_index):
        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": hand_index})

        with pytest.raises(ValueError):
            handle_player_turn(default_state, event, 0)


    @pytest.mark.parametrize(
        "hand_index",
        [
            -1,
            123,
        ]
    )
    def test_raises_value_error_if_event_data_target_is_player_and_hand_index_supplied_but_invalid(self, default_state, hand_index):
        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": hand_index})

        with pytest.raises(ValueError):
            handle_player_turn(default_state, event, 0)

    #STAND
    def test_next_event_is_resolve_round_after_pĺayer_stand(self, default_state):
        default_state.round.deck.deck_for_player_stand_two_cards()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "PLAYER_TURN_COMPLETED"


