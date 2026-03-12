from blackjack_des.state import State
from blackjack_des.engine.core import Event
from cards import Hand
from blackjack.blackjack_eval import BlackJackEval
from blackjack.strategy import BlackJackStrategy
from blackjack.round import BlackJackRound
from blackjack.fixed_deck import FixedDeck
from blackjack.roundoutcome import RoundOutcome
from blackjack_des.events import(
    deal_card, dealing_completed, early_exit_check, player_turn,
    player_turn_completed, dealer_turn, dealer_turn_completed, resolve_round,
)



def handle_round_started(state, event, now):
    if state.round_state != State.RoundState.READY:
        raise ValueError("ROUND_STARTED is only valid in READY state")

    state.round_state = State.RoundState.DEALING

    return [
        deal_card(time=now+1, target="player", hand_index=0),
        deal_card(time=now+2, target="dealer", hand_index=None),
        deal_card(time=now+3, target="player", hand_index=0),
        deal_card(time=now+4, target="dealer", hand_index=None),
        dealing_completed(time=now+5),
    ]


def handle_deal_card(state, event, now):
    allowed_states = {
        State.RoundState.DEALING,
        State.RoundState.PLAYER_ACTING,
        State.RoundState.DEALER_ACTING,
    }
    if state.round_state not in allowed_states:
        raise ValueError(f"DEAL_CARD not permitted in state: {state.round_state}")
    
    if "target" not in event.data:
        raise ValueError("DEAL_CARD requires data['target']")
    
    target = event.data["target"]
    if isinstance(target, str):
        target = target.strip().lower()
    else:
        raise ValueError("data['target'] must be a string")
    
    if target not in {"player", "dealer"}:
        raise ValueError("DEAL_CARD data['target'] must be 'player' or 'dealer'")
    
    hand_index = event.data.get("hand_index", None)
    
    if target == "dealer":
        if hand_index is not None:
            raise ValueError("DEAL_CARD to DEALER must not include hand_index")
        
        card = state.round.deck.draw(1)[0]
        state.round.dealer_hand.add_card(card)

    else:
        if hand_index is None:
            raise ValueError("DEAL_CARD to PLAYER requires hand_index")
        
        if not isinstance(hand_index, int) or isinstance(hand_index, bool):
            raise ValueError("DEAL_CARD data['hand_index'] must be an int")
        
        if hand_index < 0 or hand_index >= len(state.round.player_hands):
            raise ValueError(f"DEAL_CARD invalid hand_index: {hand_index}")
        
        card = state.round.deck.draw(1)[0]
        state.round.player_hands[hand_index]["hand"].add_card(card)
        
    return []


def handle_early_exit_check(state, event, now):
    if state.round_state != State.RoundState.DEALING:
        raise ValueError("EARLY_EXIT_CHECK is only valid in DEALING state")
    
    player_bj = BlackJackEval.blackjack(state.round.player_hands[0]["hand"])
    dealer_bj = BlackJackEval.blackjack(state.round.dealer_hand)

    if player_bj or dealer_bj:
        return [resolve_round(time=now+1)]
    else:
        return [player_turn(time=now+1, hand_index=0)]
    

def _next_hand_or_completed(hand_index, number_of_hands, now):
    if hand_index < number_of_hands - 1:
        return [player_turn(time=now+1, hand_index=hand_index+1)]
    return [player_turn_completed(time=now+1)]


def handle_player_turn(state, event, now):
    allowed_states = {
        State.RoundState.DEALING,
        State.RoundState.PLAYER_ACTING,
    }
    if state.round_state not in allowed_states:
        raise ValueError(f"PLAYER_ACTING not permitted in state: {state.round_state}")
    
    hand_index = event.data.get("hand_index", None)

    if hand_index is None:
        raise ValueError("player_turn requires hand_index")
    
    if not isinstance(hand_index, int) or isinstance(hand_index, bool):
        raise ValueError("player_turn data['hand_index'] must be an int")
    
    if hand_index < 0 or hand_index >= len(state.round.player_hands):
        raise ValueError(f"player_turn invalid hand_index: {hand_index}")
    
    number_of_player_hands = len(state.round.player_hands)
    state.round_state = State.RoundState.PLAYER_ACTING
    player_hand = state.round.player_hands[hand_index]["hand"]
    dealer_hand = state.round.dealer_hand
    dealer_card = dealer_hand.cards[0]

    if len(player_hand) == 1:
        return [
            deal_card(time=now+1, target="player", hand_index=hand_index),
            player_turn(time=now+2, hand_index=hand_index)
        ]

    if BlackJackEval.bust(player_hand) or BlackJackEval.value(player_hand) >= 21:
        return _next_hand_or_completed(hand_index, number_of_player_hands, now)

    correct_move = BlackJackStrategy.strategy(player_hand, dealer_card)

    if correct_move == BlackJackStrategy.Action.SURRENDER:
        if number_of_player_hands > 1:
            return [
                deal_card(time=now+1, target="player", hand_index=hand_index),
                player_turn(time=now+2, hand_index=hand_index)
            ]
        else:
            state.round.player_hands[hand_index]["surrendered"] = True
            return _next_hand_or_completed(hand_index, number_of_player_hands, now)
        
    if correct_move == BlackJackStrategy.Action.SPLIT:
        if number_of_player_hands == 3:
            return [
                deal_card(time=now+1, target="player", hand_index=hand_index),
                player_turn(time=now+2, hand_index=hand_index)
            ]

        new_player_hand = Hand()
        new_player_hand.add_card(player_hand.remove_last_card())
        state.round.player_hands.append({"hand": new_player_hand, "doubled": False, "surrendered": False})

        #split aces
        if player_hand.cards[0].rank == "A":
            return [
                deal_card(time=now+1, target="player", hand_index=hand_index),
                deal_card(time=now+2, target="player", hand_index=hand_index+1),
                player_turn_completed(time=now+3)
            ]

        return [player_turn(time=now+2, hand_index=hand_index)]
        
    if correct_move == BlackJackStrategy.Action.DOUBLE:
        state.round.player_hands[hand_index]["doubled"] = True
        return [deal_card(time=now+1, target="player", hand_index=hand_index)] + (_next_hand_or_completed(hand_index, number_of_player_hands, now))
    
    if correct_move == BlackJackStrategy.Action.HIT:
        return [
            deal_card(time=now+1, target="player", hand_index=hand_index),
            player_turn(time=now+2, hand_index=hand_index)
        ]

    if correct_move == BlackJackStrategy.Action.STAND:
        return _next_hand_or_completed(hand_index, number_of_player_hands, now)
    

def handle_player_turn_completed(state, event, now):
    if state.round_state != State.RoundState.PLAYER_ACTING:
        raise ValueError(f"player_turn_completed not permitted in state: {state.round_state}")
    
    return [dealer_turn(time=now+1)]


def handle_dealer_turn(state, event, now):
    if state.round_state != State.RoundState.PLAYER_ACTING:
        raise ValueError(f"player_turn_completed not permitted in state: {state.round_state}")
    
    state.round_state = State.RoundState.DEALER_ACTING
    dealer_hand = state.round.dealer_hand
    hits_soft_17 = state.round.hits_soft_17
    soft_17 = BlackJackEval.soft(dealer_hand) and BlackJackEval.value(dealer_hand) == 17

    if (soft_17 and hits_soft_17) or (BlackJackEval.value(dealer_hand) < 17):
        return [
            deal_card(time=now+1, target="dealer"),
            dealer_turn(time=now+2)
        ]

    return [dealer_turn_completed(time=now+1)]
    

def handle_dealer_turn_completed(state, event, now):
    if state.round_state != State.RoundState.DEALER_ACTING:
        raise ValueError(f"dealer_turn_completed not permitted in state: {state.round_state}")
    
    return [resolve_round(time=now+1)]


def handle_resolve_round(state, event, now):
    if state.round_state not in [State.RoundState.DEALER_ACTING, State.RoundState.DEALING]:
        raise ValueError(f"handle_resolve_round not permitted in state: {state.round_state}")

    state.outcomes = []
    player_hands = state.round.player_hands
    dealer_hand = state.round.dealer_hand

    for player_hand in player_hands:
        hand = player_hand["hand"]

        print(hand.cards)
        print(dealer_hand.cards)



        player_bj = BlackJackEval.blackjack(hand)
        dealer_bj = BlackJackEval.blackjack(dealer_hand)

        if player_bj and not dealer_bj:
            outcome = RoundOutcome.BLACKJACK
        elif not player_bj and dealer_bj:
            outcome = RoundOutcome.LOSS
        elif player_bj and dealer_bj:
            outcome = RoundOutcome.PUSH

        elif player_hand["surrendered"]:
            outcome = RoundOutcome.HALF_PAY

        elif BlackJackEval.bust(hand):
            outcome = RoundOutcome.LOSS

        elif BlackJackEval.bust(dealer_hand):
            outcome = (RoundOutcome.DOUBLE_WIN if player_hand["doubled"] else RoundOutcome.WIN)

        else:
            player_value = BlackJackEval.value(hand)
            dealer_value = BlackJackEval.value(dealer_hand)

            if player_value > dealer_value:
                outcome = (RoundOutcome.DOUBLE_WIN if player_hand["doubled"] else RoundOutcome.WIN)
            elif player_value < dealer_value:
                outcome = (RoundOutcome.DOUBLE_LOSS if player_hand["doubled"] else RoundOutcome.LOSS)
            else:
                outcome = RoundOutcome.PUSH

        state.outcomes.append(outcome)

    state.round_state = State.RoundState.DONE
    return []



if __name__ == "__main__":
    fixed_deck = FixedDeck()
    fixed_deck.deck_for_bj()
    round = BlackJackRound(deck=fixed_deck, hits_soft_17=False)
    state = State(round=round, round_state=State.RoundState.DEALER_ACTING)

    card = state.round.deck.draw(1)[0]
    state.round.player_hands[0]["hand"].add_card(card)

    card = state.round.deck.draw(1)[0]
    state.round.dealer_hand.add_card(card)

    card = state.round.deck.draw(1)[0]
    state.round.player_hands[0]["hand"].add_card(card)

    card = state.round.deck.draw(1)[0]
    state.round.dealer_hand.add_card(card)


    event = Event(time=0, type="RESOLVE_ROUND", data={})
    outcomes = handle_resolve_round(state, event, 0)

    print(outcomes)
