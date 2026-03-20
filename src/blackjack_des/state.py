from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

from blackjack.round import BlackJackRound
from blackjack.roundoutcome import RoundOutcome


@dataclass
class State:
    class RoundState(Enum):
        READY = 1
        DEALING = 2
        PLAYER_ACTING = 3
        DEALER_ACTING = 4
        RESOLVING = 5
        DONE = 6

    round: BlackJackRound
    round_state: RoundState = RoundState.READY
    outcomes: Optional[List[RoundOutcome]] = None
    active_hand_index: Optional[int] = None
    