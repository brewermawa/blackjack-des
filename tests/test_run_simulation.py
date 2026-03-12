"""
@pytest.mark.parametrize(
    "deck_method, expected_outcome, doubled, surrendered",
        [
            ("deck_for_bj", [RoundOutcome.BLACKJACK], False, False),
            ("deck_for_surrender", [RoundOutcome.HALF_PAY], False, True),
            ("deck_for_dealer_bust", [RoundOutcome.LOSS], False, False), 
            #("deck_for_win", [RoundOutcome.WIN]),
        ]
    )
    def test_resolve_round_returns_correct_outcome(self, default_state, deck_method, expected_outcome, doubled, surrendered):
        getattr(default_state.round.deck, deck_method)()

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.player_hands[0]["hand"].add_card(card)

        card = default_state.round.deck.draw(1)[0]
        default_state.round.dealer_hand.add_card(card)

        default_state.round.player_hands[0]["doubled"] = doubled
        default_state.round.player_hands[0]["surrendered"] = surrendered

        event = resolve_round(time=0)
        outcome = handle_resolve_round(default_state, event, 0)

        assert outcome == expected_outcome

"""
