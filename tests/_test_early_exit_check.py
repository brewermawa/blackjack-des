import pytest

from blackjack.round import BlackJackRound
from blackjack.fixed_deck import FixedDeck
from cards import Deck
from blackjack_des.state import State
from blackjack_des.events import early_exit_check
from blackjack_des.handlers import handle_early_exit_check
from blackjack_des.engine.core import Event


class TestEarlyExitCheck:
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
            State.RoundState.PLAYER_ACTING,
            State.RoundState.DEALER_ACTING,
            State.RoundState.DONE,
            State.RoundState.RESOLVING
        ]
    )
    def test_raises_value_error_if_state_is_not_dealing(self, round_state):
        deck = Deck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=round_state)
        
        with pytest.raises(ValueError):
            handle_early_exit_check(state, None, 0)


    def test_state_stays_dealing(self, default_state):
        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)
        handle_early_exit_check(default_state, None, 0)

        assert default_state.round_state == State.RoundState.DEALING

    
    def test_next_event_is_resolve_round_after_pĺayer_blackjack(self, default_state):
        default_state.round.deck.deck_for_bj()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        next_events = handle_early_exit_check(default_state, None, 0)

        assert next_events[0].type == "RESOLVE_ROUND"


    def test_next_event_is_resolve_round_after_dealer_blackjack(self, default_state):
        default_state.round.deck.deck_for_dealer_bj()
        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        next_events = handle_early_exit_check(default_state, None, 0)

        assert next_events[0].type == "RESOLVE_ROUND"


    def test_next_event_is_resolve_round_after_player_and_dealer_blackjack(self, default_state):
        default_state.round.deck.deck_for_both_bj()
        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        next_events = handle_early_exit_check(default_state, None, 0)

        assert next_events[0].type == "RESOLVE_ROUND"


    def test_next_event_is_player_turn_if_no_blackjacks(self, default_state):
        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)
        
        next_events = handle_early_exit_check(default_state, None, 0)

        assert next_events[0].type == "PLAYER_TURN"
