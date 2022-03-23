import requests


def run_game():
    play = True
    win_count = 0
    while play:
        game_state = "ONGOING"
        while game_state == "ONGOING":
            deck = requests.get('http://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1').json()
            deck_id = deck["deck_id"]
            user_hand = {}
            dealer_hand = {}
            user_score = 0
            dealer_score = 0
            game_state, user_score, dealer_score = \
                opening_hand(user_hand, user_score, dealer_hand, dealer_score, game_state, deck_id)
            while game_state == "ONGOING":
                game_state, user_score, dealer_score = \
                    game_round(user_hand, user_score, dealer_hand, dealer_score, game_state, deck_id)
            if game_state != "ONGOING":
                win_count = \
                    end_of_game(game_state, win_count, user_score, dealer_score)
        play = play_again()
    print("Thank you for playing")


def opening_hand(user_hand, user_score, dealer_hand, dealer_score, game_state, deck_id):
    user_score = draw_cards(2, user_hand, user_score, deck_id)
    dealer_score = draw_cards(2, dealer_hand, dealer_score, deck_id)
    print(f'Your hand is {user_hand} and your current score is {user_score}'
          f'\nThe dealers hand is {dealer_hand} and their current score is {dealer_score}')
    game_state = valid_score_opening(user_score, dealer_score, game_state)
    return game_state, user_score, dealer_score


def draw_cards(count, hand, score, deck_id):
    start_draw = requests.get(f'http://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={count}').json()["cards"]
    for card in start_draw:
        card_value = 0
        if card["value"].isnumeric():
            card_value = int(card["value"])
        elif card["value"] == "ACE":
            if score > 10:
                card_value = 1
            else:
                card_value = 11
        else:
            card_value = 10
        hand_key = str(f"{card['value']} of {card['suit']}")
        hand[hand_key] = card_value
        score += card_value
    return score


def valid_score_opening(user_score, dealer_score, game_state):
    if user_score > 21 or dealer_score == 21:
        game_state = "LOST"
    elif dealer_score > 21 or user_score == 21:
        game_state = "WON"
    return game_state


def valid_score_mid(user_score, dealer_score, game_state):
    if user_score > 21 or dealer_score == 21:
        game_state = "LOST"
    elif dealer_score > 21 or user_score == 21:
        game_state = "WON"
    else:
        game_state = "ONGOING"
    return game_state


def valid_score_end(user_score, dealer_score, game_state):
    if dealer_score < user_score < 22:
        game_state = "WON"
    elif user_score < dealer_score < 22:
        game_state = "LOST"
    elif user_score == dealer_score:
        game_state = "TIED"
    return game_state


def game_round(user_hand, user_score, dealer_hand, dealer_score, game_state, deck_id):
    draw_card = input("Would you like to draw a card?").upper()
    while draw_card == "YES" and game_state == "ONGOING":
        user_score = draw_cards(1, user_hand, user_score, deck_id)
        game_state = valid_score_mid(user_score, dealer_score, game_state)
        print(f'Your hand is {user_hand} and your current score is {user_score}'
              f'\nThe dealers hand is {dealer_hand} and their current score is {dealer_score}')
        if game_state == "ONGOING":
            draw_card = input("Would you like to draw a card?").upper()
    if draw_card != "YES" and game_state == "ONGOING":
        while dealer_score <= user_score and dealer_score < 22:
            dealer_score = draw_cards(1, dealer_hand, dealer_score, deck_id)
            print(f'Your hand is {user_hand} and your current score is {user_score}'
                  f'\nThe dealers hand is {dealer_hand} and their current score is {dealer_score}')
            game_state = valid_score_mid(user_score, dealer_score, game_state)
        game_state = valid_score_end(user_score, dealer_score, game_state)
    return game_state, user_score, dealer_score


def end_of_game(game_state, win_count, user_score, dealer_score):
    if game_state == "WON":
        win_count += 1
        print(f"Congratulations, you win! Your total win count is {win_count}.")
    elif game_state == "LOST":
        if win_count == 0:
            print(f"Brutal, you lost. Your total win count is {win_count}")
        else:
            print(f"I'm sorry, you lost. Your total win count is {win_count}")
    elif game_state == "TIED":
        print(f"Wow, what a close game. You tied. Your total win count is {win_count}.")
    return win_count


def play_again():
    user_input = input(f"Would you like to play again?").upper()
    play = False
    if user_input == "YES":
        play = True
    return play


run_game()