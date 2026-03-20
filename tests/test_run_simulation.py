import pytest

from blackjack.roundoutcome import RoundOutcome
from blackjack.fixed_deck import FixedDeck
from blackjack.round import BlackJackRound

from blackjack_des.state import State
from blackjack_des.engine.core import run_simulation
from blackjack_des.events import round_started
from blackjack_des.router import handlers
from blackjack_des.events import round_started


class TestSmulation:
    @pytest.mark.parametrize(
    "deck_method, expected_outcomes",
        [
            ("deck_for_win", [RoundOutcome.WIN]),
            ("deck_for_bj", [RoundOutcome.BLACKJACK]),
            ("deck_for_win_with_hit", [RoundOutcome.WIN]),
            ("deck_for_loss", [RoundOutcome.LOSS]),
            ("deck_for_bust_after_hit", [RoundOutcome.LOSS]),
            ("deck_for_push", [RoundOutcome.PUSH]),
            ("deck_for_double_win", [RoundOutcome.DOUBLE_WIN]),
            ("deck_for_double_loss", [RoundOutcome.DOUBLE_LOSS]),
            ("deck_for_double_push", [RoundOutcome.PUSH]),
            ("deck_for_surrender", [RoundOutcome.HALF_PAY]),
            ("deck_for_dealer_bust", [RoundOutcome.WIN]),
            ("deck_for_dealer_bj", [RoundOutcome.LOSS]),
            ("deck_for_bj_push", [RoundOutcome.PUSH]),
            ("deck_for_soft_hits_17_false_push", [RoundOutcome.PUSH]),
            ("deck_for_player_bust", [RoundOutcome.LOSS]),
            ("deck_for_player_double_loss", [RoundOutcome.DOUBLE_LOSS]),
            ("deck_for_win_with_two_hits", [RoundOutcome.WIN]),
            ("deck_for_loss_with_two_hits", [RoundOutcome.LOSS]),
            ("deck_for_split_win_one_loss_one", [RoundOutcome.WIN, RoundOutcome.LOSS]),
            ("deck_for_split_push", [RoundOutcome.PUSH, RoundOutcome.PUSH]),
            ("deck_for_split_win_both", [RoundOutcome.WIN, RoundOutcome.WIN]),
            ("deck_for_split_AA_win_win", [RoundOutcome.WIN, RoundOutcome.WIN]),
            ("deck_for_split_AA_only_one_extra_card_per_hand", [RoundOutcome.LOSS, RoundOutcome.LOSS]),
            ("deck_for_split_AA_then_KK_dealer_21", [RoundOutcome.PUSH, RoundOutcome.PUSH]),
            ("deck_for_split_then_double_both_hands_win", [RoundOutcome.DOUBLE_WIN, RoundOutcome.DOUBLE_WIN]),
            ("deck_for_split_then_double_both_hands_lose", [RoundOutcome.DOUBLE_LOSS, RoundOutcome.DOUBLE_LOSS]),
            ("deck_for_split_then_double_one_wins_one_lose", [RoundOutcome.DOUBLE_WIN, RoundOutcome.DOUBLE_LOSS]),
            #("deck_for_split_first_hand_normal_push_second_hand_double_lose", [RoundOutcome]),
            #("deck_for_split_then_resplit", [RoundOutcome]),
            #("deck_for_split_no_surrender", [RoundOutcome]),
            #("deck_for_split_resplit_fallback_stand", [RoundOutcome]),
            #("deck_for_surrender_to_hit_when_more_than_2_cards", [RoundOutcome]),
            #("deck_for_soft_21", [RoundOutcome]),
            #("deck_for_both_bj", [RoundOutcome]),
            #("deck_for_player_stand_two_cards", [RoundOutcome]),
            #("deck_for_player_split_then_stand", [RoundOutcome]),
            #("deck_for_player_split_then_surrender", [RoundOutcome]),
            #("deck_for_split_bust_first_hand", [RoundOutcome]),
            #("deck_for_player_split_then_21", [RoundOutcome]),
            #("deck_for_player_split_twice", [RoundOutcome]),
            #("deck_for_player_split_three_times", [RoundOutcome]),
            #("deck_for_dealer_less_than_17", [RoundOutcome]),
            #("deck_for_dealer_soft_17", [RoundOutcome]),
            #("deck_for_dealer_more_than_or_equal_to_17", [RoundOutcome]),
            
        ]
    )
    def test_resolve_round_returns_correct_outcome(self, deck_method, expected_outcomes):
        deck = FixedDeck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=State.RoundState.READY)
        getattr(state.round.deck, deck_method)()

        def stop_condition(state, now, events_processed, metrics):
            return state.round_state == State.RoundState.DONE

        run_simulation(
            initial_state=state,
            initial_events=[round_started(time=0)],
            handlers=handlers,
            stop_condition=stop_condition,
            observers=None,
            max_events=100
        )
        
        assert state.outcomes == expected_outcomes

"""
    @pytest.mark.parametrize(
    "deck_method, expected_outcomes",
        [
           ("deck_for_soft_hits_17_true_player_wins", [RoundOutcome.WIN]),
           ("deck_for_soft_hits_17_true_player_loss", [RoundOutcome.LOSS]),
           ("deck_for_soft_hits_17_true_push", [RoundOutcome.PUSH]),
        ]
    )
    def test_resolve_round_returns_correct_outcome_hits_soft_17_true(self, deck_method, expected_outcomes):
        deck = FixedDeck()
        round = BlackJackRound(deck=deck, hits_soft_17=False)
        state = State(round=round, round_state=State.RoundState.READY)
        getattr(state.round.deck, deck_method)()

        def stop_condition(state, now, events_processed, metrics):
            return state.round_state == State.RoundState.DONE

        run_simulation(
            initial_state=state,
            initial_events=[round_started(time=0)],
            handlers=handlers,
            stop_condition=stop_condition,
            observers=None,
            max_events=100
        )
        
        assert state.outcomes == expected_outcomes
"""
