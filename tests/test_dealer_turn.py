import pytest

from blackjack.round import BlackJackRound
from blackjack.fixed_deck import FixedDeck
from blackjack_des.state import State
from blackjack_des.handlers import handle_dealer_turn
from blackjack_des.engine.core import Event


class TestPlayerRound:
    @pytest.fixture
    def default_state(self):
        deck = FixedDeck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=State.RoundState.PLAYER_ACTING)

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
    def test_raises_value_error_if_state_is_not_player_acting(self, default_state, round_state):
        default_state.round_state = round_state
        
        with pytest.raises(ValueError):
            handle_dealer_turn(default_state, None, 0)


    def test_verifies_that_state_on_exit_is_dealer_acting(self, default_state):
        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="DEALER_TURN", data={})
        handle_dealer_turn(default_state, event, 0)

        assert default_state.round_state == State.RoundState.DEALER_ACTING


    def test_next_event_is_deal_card_when_value_dealer_card_is_less_than_17(self, default_state):
        default_state.round.deck.deck_for_dealer_less_than_17()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="DEALER_TURN", data={})
        next_events = handle_dealer_turn(default_state, event, 0)

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["target"] == "dealer"


    def test_next_event_is_deal_card_when_dealer_has_soft_17_and_hits_soft_17_is_True(self):
        deck = FixedDeck()
        round = BlackJackRound(deck=deck, hits_soft_17=True)
        state = State(round=round, round_state=State.RoundState.PLAYER_ACTING)
        deck.deck_for_dealer_soft_17()

        card = state.round.deck.draw(1)[0]
        state.round.player_hands[0]["hand"].add_card(card)

        card = state.round.deck.draw(1)[0]
        state.round.dealer_hand.add_card(card)

        card = state.round.deck.draw(1)[0]
        state.round.player_hands[0]["hand"].add_card(card)

        card = state.round.deck.draw(1)[0]
        state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="DEALER_TURN", data={})
        next_events = handle_dealer_turn(state, event, 0)

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["target"] == "dealer"


    def test_next_event_is_dealer_turn_completed_when_dealer_has_soft_17_and_hits_soft_17_is_False(self, default_state):
        default_state.round.deck.deck_for_dealer_soft_17()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="DEALER_TURN", data={})
        next_events = handle_dealer_turn(default_state, event, 0)

        assert next_events[0].type == "DEALER_TURN_COMPLETED"


    def test_next_event_is_dealer_turn_completed_when_value_dealer_card_is_greater_than_or_equal_to_17(self, default_state):
        default_state.round.deck.deck_for_dealer_more_than_or_equal_to_17()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="DEALER_TURN", data={})
        next_events = handle_dealer_turn(default_state, event, 0)

        assert next_events[0].type == "DEALER_TURN_COMPLETED"

