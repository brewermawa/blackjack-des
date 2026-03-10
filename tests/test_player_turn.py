import pytest

from blackjack.round import BlackJackRound
from blackjack.fixed_deck import FixedDeck
from cards import Deck, Hand
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
    def test_next_event_is_player_turn_completed_after_pĺayer_stand(self, default_state):
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


    def test_next_event_is_player_turn_after_pĺayer_stand_and_player_has_more_then_one_hand_after_split(self, default_state):
        default_state.round.deck.deck_for_player_split_then_stand() #["8", "10", "8", "6", "9", "J"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        player_hand_0 = default_state.round.player_hands[0]["hand"]
        player_hand_1 = Hand()
        player_hand_1.add_card(player_hand_0.remove_last_card())

        player_hand_0.add_card(default_state.round.deck.draw(1)[0]) #8, 9
        player_hand_1.add_card(default_state.round.deck.draw(1)[0]) #8, J

        default_state.round.player_hands.append({"hand": player_hand_1, "doubled": False, "surrendered": False})

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "PLAYER_TURN"
        assert next_events[0].data["hand_index"] == 1

    
    #SURRENDER
    def test_next_event_is_player_turn_completed_after_pĺayer_surrender(self, default_state):
        default_state.round.deck.deck_for_surrender()

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


    def test_next_event_is_player_turn_when_strategy_returns_surrender_but_hand_was_split(self, default_state):
        default_state.round.deck.deck_for_player_split_then_surrender()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        player_hand_0 = default_state.round.player_hands[0]["hand"]
        player_hand_1 = Hand()
        player_hand_1.add_card(player_hand_0.remove_last_card())

        player_hand_0.add_card(default_state.round.deck.draw(1)[0]) #8, 7
        player_hand_1.add_card(default_state.round.deck.draw(1)[0]) #8, 7

        default_state.round.player_hands.append({"hand": player_hand_1, "doubled": False, "surrendered": False})

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["hand_index"] == 0
        assert next_events[1].type == "PLAYER_TURN"
        assert next_events[1].data["hand_index"] == 0


    #DOUBLE
    def test_next_event_is_player_turn_completed_after_pĺayer_double(self, default_state):
        default_state.round.deck.deck_for_double_win()

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

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["hand_index"] == 0
        assert next_events[1].type == "PLAYER_TURN_COMPLETED"
        assert default_state.round.player_hands[0]["doubled"] is True


    def test_next_event_is_player_turn_with_hand_index_1_after_pĺayer_double_after_split(self, default_state):
        default_state.round.deck.deck_for_split_then_double_both_hands_win() #["6", "5", "6", "10", "5", "10", "5", "J", "9"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        player_hand_0 = default_state.round.player_hands[0]["hand"]
        player_hand_1 = Hand()
        player_hand_1.add_card(player_hand_0.remove_last_card())

        player_hand_0.add_card(default_state.round.deck.draw(1)[0])
        player_hand_1.add_card(default_state.round.deck.draw(1)[0])

        default_state.round.player_hands.append({"hand": player_hand_1, "doubled": False, "surrendered": False})

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["hand_index"] == 0
        assert next_events[1].type == "PLAYER_TURN"
        assert next_events[1].data["hand_index"] == 1


    #HIT
    def test_next_event_is_deal_card_and_player_turn_after_pĺayer_hit(self, default_state):
        default_state.round.deck.deck_for_win_with_hit()

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

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["hand_index"] == 0
        assert next_events[1].type == "PLAYER_TURN"
        assert next_events[1].data["hand_index"] == 0


    #BUST
    def test_next_event_is_player_turn_completed_when_player_busted(self, default_state):
        default_state.round.deck.deck_for_bust_after_hit() #["9", "8", "6", "9", "Q"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "PLAYER_TURN_COMPLETED"


    def test_next_event_is_player_turn_with_hand_index_1_after_split_and_bust_on_hand_0(self, default_state):
        default_state.round.deck.deck_for_split_bust_first_hand() #["8", "9", "8", "9", "6", "K", "J"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        player_hand_0 = default_state.round.player_hands[0]["hand"]
        player_hand_1 = Hand()
        player_hand_1.add_card(player_hand_0.remove_last_card())

        player_hand_0.add_card(default_state.round.deck.draw(1)[0])
        player_hand_0.add_card(default_state.round.deck.draw(1)[0])
        player_hand_1.add_card(default_state.round.deck.draw(1)[0])
        

        default_state.round.player_hands.append({"hand": player_hand_1, "doubled": False, "surrendered": False})

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "PLAYER_TURN"
        assert next_events[0].data["hand_index"] == 1


    #21 no blackjack
    def test_next_event_is_player_turn_completed_when_player_hand_is_21(self, default_state):
        default_state.round.deck.deck_for_soft_21() #["8", "10", "8", "6", "7", "6"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "PLAYER_TURN_COMPLETED"


    def test_next_event_is_player_turn_with_hand_index_1_after_split_and_player_hand_21_on_hand_0(self, default_state):
        default_state.round.deck.deck_for_player_split_then_21() #["8", "10", "8", "6", "7", "6"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        player_hand_0 = default_state.round.player_hands[0]["hand"]
        player_hand_1 = Hand()
        player_hand_1.add_card(player_hand_0.remove_last_card())

        player_hand_0.add_card(default_state.round.deck.draw(1)[0])
        player_hand_0.add_card(default_state.round.deck.draw(1)[0])
        player_hand_1.add_card(default_state.round.deck.draw(1)[0])
        

        default_state.round.player_hands.append({"hand": player_hand_1, "doubled": False, "surrendered": False})

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "PLAYER_TURN"
        assert next_events[0].data["hand_index"] == 1


    def test_next_event_is_player_turn_when_split(self, default_state):
        default_state.round.deck.deck_for_split_win_both()

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

        assert next_events[0].type == "PLAYER_TURN"
        assert next_events[0].data["hand_index"] == 0


    def test_len_player_hands_is_two_when_one_split(self, default_state):
        default_state.round.deck.deck_for_split_win_both() # ["8", "6", "8", "10", "K", "Q"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        handle_player_turn(default_state, event, 0)

        assert len(default_state.round.player_hands) == 2


    def test_first_card_of_both_hands_are_equal_in_rank(self, default_state):
        default_state.round.deck.deck_for_split_win_both() # ["8", "6", "8", "10", "K", "Q"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        handle_player_turn(default_state, event, 0)

        player_hand_0 = default_state.round.player_hands[0]["hand"]
        player_hand_1 = default_state.round.player_hands[1]["hand"]

        assert player_hand_0.cards[0].rank == player_hand_1.cards[0].rank


    def test_next_events_are_deal_card_and_player_turn_when_trying_to_split_3_times(self, default_state):
        default_state.round.deck.deck_for_player_split_three_times() # ["8", "10", "8", "6", "8", "8"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        player_hand_0 = default_state.round.player_hands[0]["hand"]
        player_hand_1 = Hand()
        player_hand_1.add_card(player_hand_0.remove_last_card())
        default_state.round.player_hands.append({"hand": player_hand_1, "doubled": False, "surrendered": False})

        player_hand_0.add_card(default_state.round.deck.draw(1)[0])

        player_hand_2 = Hand()
        player_hand_2.add_card(player_hand_0.remove_last_card())
        default_state.round.player_hands.append({"hand": player_hand_2, "doubled": False, "surrendered": False})

        player_hand_0.add_card(default_state.round.deck.draw(1)[0])

        #player_hand_0: [8♣, 8♦]
        #player_hand_1: [8♥]
        #player_hand_2: [8♠]

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["hand_index"] == 0
        assert next_events[1].type == "PLAYER_TURN"
        assert next_events[1].data["hand_index"] == 0


    def test_next_events_are_deal_card_and_player_turn_when_hand_only_has_one_card_aftger_split(self, default_state):
        default_state.round.deck.deck_for_split_win_both()
        
        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        player_hand_0 = default_state.round.player_hands[0]["hand"]
        player_hand_1 = Hand()
        player_hand_1.add_card(player_hand_0.remove_last_card())
        default_state.round.player_hands.append({"hand": player_hand_1, "doubled": False, "surrendered": False})

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["hand_index"] == 0
        assert next_events[1].type == "PLAYER_TURN"
        assert next_events[1].data["hand_index"] == 0


    def test_next_events_are_2_deal_card_and_player_turn_completed_when_spliting_aces(self, default_state):
        default_state.round.deck.deck_for_split_AA_only_one_extra_card_per_hand() # ["A", "8", "A", "9", "5", "4"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        #player_hand_0 = default_state.round.player_hands[0]["hand"]
        #player_hand_1 = Hand()
        #player_hand_1.add_card(player_hand_0.remove_last_card())
        #default_state.round.player_hands.append({"hand": player_hand_1, "doubled": False, "surrendered": False})

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["hand_index"] == 0
        assert next_events[1].type == "DEAL_CARD"
        assert next_events[1].data["hand_index"] == 1
        assert next_events[2].type == "PLAYER_TURN_COMPLETED"







































"""
    def test_next_moves_are_deal_card_and_player_turn_when_hand_has_one_card(self, default_state):
        default_state.round.deck.deck_for_split_win_both()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        default_state.round.player_hands[0]["hand"].remove_last_card()

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        next_events = handle_player_turn(default_state, event, 0)

        assert next_events[0].type == "DEAL_CARD"
        assert next_events[0].data["hand_index"] == 0
        assert next_events[1].type == "PLAYER_TURN"
        assert next_events[1].data["hand_index"] == 0



    def test_len_player_hands_is_3_when_two_splits(self, default_state):
        default_state.round.deck.deck_for_player_split_twice() # ["8", "10", "8", "6", "8", "7"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        handle_player_turn(default_state, event, 0)

        assert len(default_state.round.player_hands) == 3


    def test_len_player_hands_is_3_when_two_splits_and_a_possible_third_split_that_is_turned_to_hit(self, default_state):
        default_state.round.deck.deck_for_player_split_three_times() # ["8", "10", "8", "6", "8", "8", "7"]

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        event = Event(time=0, type="PLAYER_TURN", data={"hand_index": 0})
        handle_player_turn(default_state, event, 0)

        assert len(default_state.round.player_hands) == 3


    

"""


