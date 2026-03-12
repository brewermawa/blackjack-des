from blackjack_des.engine.core import Event

def round_started(*, time: int) -> Event:
    return Event(
        time=time,
        type="ROUND_STARTED",
        data={}
    )

def deal_card(*, time: int, target: str, hand_index: int | None = None) -> Event:
    return Event(
        time=time,
        type="DEAL_CARD",
        data={
            "target": target,
            "hand_index": hand_index,
        }
    )

def dealing_completed(*, time: int) -> Event:
    return Event(
        time=time,
        type="DEALING_COMPLETED",
        data={}
    )


def early_exit_check(*, time: int) -> Event:
    return Event(
        time=time,
        type="EARLY_EXIT_CHECK",
        data={}
    )


def player_turn(*, time: int, hand_index: int) -> Event:
    return Event(
        time=time,
        type="PLAYER_TURN",
        data={
            "hand_index": hand_index,
        }
    )


def post_player_card(*, time: int, hand_index: int) -> Event:
    return Event(
        time=time,
        type="POST_PLAYER_CARD",
        data={
            "hand_index": hand_index,
        }
    )


def player_turn_completed(*, time: int) -> Event:
    return Event(
        time=time,
        type="PLAYER_TURN_COMPLETED",
        data={}
    )


def dealer_turn(*, time: int) -> Event:
    return Event(
        time=time,
        type="DEALER_TURN",
        data={}
    )


def dealer_turn_completed(*, time: int) -> Event:
    return Event(
        time=time,
        type="DEALER_TURN_COMPLETED",
        data={}
    )


def resolve_round(*, time: int) -> Event:
    return Event(
        time=time,
        type="RESOLVE_ROUND",
        data={}
    )




