from cards.deck import Deck
from cards.hand import Hand

from blackjack.roundoutcome import RoundOutcome
from blackjack.fixed_deck import FixedDeck
from blackjack.round import BlackJackRound

from blackjack_des.state import State
from blackjack_des.engine.core import run_simulation
from blackjack_des.events import round_started
from blackjack_des.router import handlers
from blackjack_des.events import round_started

blackjacks = 0
win = 0
double_win = 0
push = 0
loss = 0
double_loss = 0
surrender = 0

bet = 15
bank = 10000
total_bets = 0


deck = Deck(6, False)
round = BlackJackRound(deck=deck, hits_soft_17=False)

deck.set_cut_point()

def stop_condition(state, now, events_processed, metrics):
    return state.round_state == State.RoundState.DONE

for i in range(100000):
    total_bets += 15
    state = State(round=round, round_state=State.RoundState.READY)
    state.round.dealer_hand = Hand()
    state.round.player_hands = [{"hand": Hand(), "doubled": False, "surrendered": False}]
    if deck.needs_shuffle:
        deck.shuffle()
        deck.set_cut_point()

    print(i)

    result = run_simulation(
        initial_state=state,
        initial_events=[round_started(time=0)],
        handlers=handlers,
        stop_condition=stop_condition,
        observers=None,
        max_events=100
    )

    for outcome in state.outcomes:
        if outcome == RoundOutcome.BLACKJACK:
            blackjacks += 1
            bank += (bet * 1.5)

        if outcome == RoundOutcome.WIN:
            win += 1
            bank += bet

        if outcome == RoundOutcome.DOUBLE_WIN:
            double_win += 1
            bank += (bet * 2)

        if outcome == RoundOutcome.PUSH:
            push += 1

        if outcome == RoundOutcome.LOSS:
            loss += 1
            bank -= bet


        if outcome == RoundOutcome.DOUBLE_LOSS:
            double_loss += 1
            bank -= (bet * 2)

        if outcome == RoundOutcome.HALF_PAY:
            surrender += 1
            bank -= (bet * .5)

for player_hand in state.round.player_hands:
    print(f"Player: {player_hand["hand"].cards}")

print(f"Dealer: {state.round.dealer_hand.cards}")
print(f"Outcomes: {state.outcomes}")
print(f"Events: {result.events_processed}")
for e in result.trace:
    #print(f"Time {e["time"]} - {e["type"]}")
    print(e)

print(f"Blackjacks: {blackjacks}")
print(f"Win: {win}")
print(f"Double Win: {double_win}")
print(f"Push: {push}")

print(f"Bank: {bank}")

print(f"Total bets: {total_bets}")
