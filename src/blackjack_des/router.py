from .handlers import(
    handle_round_started, 
    handle_deal_card,
    handle_dealing_completed,
    handle_early_exit_check,
    handle_player_turn,
    handle_player_turn_completed,
    handle_dealer_turn,
    handle_dealer_turn_completed,
    handle_resolve_round,
)

handlers = {
    "ROUND_STARTED": handle_round_started,
    "DEAL_CARD": handle_deal_card,
    "DEALING_COMPLETED": handle_dealing_completed,
    "EARLY_EXIT_CHECK": handle_early_exit_check,
    "PLAYER_TURN": handle_player_turn,
    "PLAYER_TURN_COMPLETED": handle_player_turn_completed,
    "DEALER_TURN": handle_dealer_turn,
    "DEALER_TURN_COMPLETED": handle_dealer_turn_completed,
    "RESOLVE_ROUND": handle_resolve_round,
}
