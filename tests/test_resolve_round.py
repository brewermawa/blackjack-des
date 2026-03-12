import pytest

from blackjack.round import BlackJackRound
from blackjack.fixed_deck import FixedDeck
from blackjack.roundoutcome import RoundOutcome
from blackjack_des.state import State
from blackjack_des.events import resolve_round
from blackjack_des.handlers import handle_resolve_round


class TestResolveRound:
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
            State.RoundState.PLAYER_ACTING,
            State.RoundState.DONE,
            State.RoundState.RESOLVING,
        ]
    )
    def test_raises_value_error_if_state_is_not_dealer_acting(self, default_state, round_state):
        default_state.round_state = round_state

        with pytest.raises(ValueError):
            handle_resolve_round(default_state, None, 0)


    def test_state_on_exit_is_done(self, default_state):
        default_state.round.deck.deck_for_bj()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = resolve_round(time=0)
        handle_resolve_round(default_state, event, 0)

        assert default_state.round_state == State.RoundState.DONE


    def test_resolve_round_returns_empty_event_list(self, default_state):
        default_state.round.deck.deck_for_bj()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = resolve_round(time=0)
        next_events = handle_resolve_round(default_state, event, 0)

        assert next_events == []


    def test_resolve_round_adds_outcomes_to_round_outcomes(self, default_state):
        default_state.round.deck.deck_for_bj()
        
        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = resolve_round(time=0)
        handle_resolve_round(default_state, event, 0)

        assert isinstance(default_state.outcomes, list)
        assert len(default_state.outcomes) > 0
        assert all(isinstance(outcome, RoundOutcome) for outcome in default_state.outcomes)


    @pytest.mark.parametrize(
    "deck_method, expected_outcome",
        [
            ("deck_for_bj", [RoundOutcome.BLACKJACK]),
            ("deck_for_win", [RoundOutcome.WIN]),
            ("deck_for_loss", [RoundOutcome.LOSS]),
            ("deck_for_push", [RoundOutcome.PUSH])
            
        ]
    )
    def test_resolve_round_returns_correct_outcome(self, default_state, deck_method, expected_outcome):
        getattr(default_state.round.deck, deck_method)()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = resolve_round(time=0)
        handle_resolve_round(default_state, event, 0)

        assert default_state.outcomes == expected_outcome


    
