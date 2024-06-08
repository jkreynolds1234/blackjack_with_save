"""Runs Blackjack program"""

# CHANGES TO MAKE:
    # Update paused game status to saved when ending a paused game

import random
import time
from deck_blackjack import deck, ascii_cards, Card, suit_symbols
from database import GamesDatabase

##################################################### HELPER FUNCTIONS #####################################################

def deal_card(indeck: list[Card], hand: list[Card], hidden: bool) -> int:
    """Adds random card from deck to hand, removes it from the deck,
    and returns the card's value."""
    card = random.choice(indeck)
    card.hidden = hidden
    hand.append(card)
    indeck.remove(card)
    return int(card.card_value)

def upload_cards(player_cards: list[Card], dealer_cards: list[Card]):
    """Loads player's and dealer's cards into the games database"""
    # Create database and add player & dealer's hands
    games_db = GamesDatabase()
    game_num = games_db.gameNum()
    for c in player_cards:
        games_db.addCard("p", game_num, "Player", c)
    for c in dealer_cards:
        games_db.addCard("p", game_num, "Dealer", c)

def download_cards():
    """Downloads cards from chosen paused game in the games database and unpacks them"""
    games_db = GamesDatabase()
    choices = games_db.selectGameStatus()
    select = input(f"Which game do you want to load? {choices} ")
    game_contents = games_db.selectGame(select)
    print(game_contents)
    # Unpack list of dictionaries into player and dealer cards
    player_cards = []
    player_score = 0
    dealer_cards = []
    dealer_score = 0
    for entry in game_contents:
        if entry["player"] == "Player":
            player_cards.append(Card(suit_symbols[entry["suit"]], entry["suit"], entry["face_value"], entry["card_value"], False))
            player_score += entry["card_value"]
        elif entry["player"] == "Dealer":
            dealer_cards.append(Card(suit_symbols[entry["suit"]], entry["suit"], entry["face_value"], entry["card_value"], hidden = len(dealer_cards) == 0))
            dealer_score += entry["card_value"]
    return(player_cards, player_score, dealer_cards, dealer_score)

def print_cards(persons_cards: list[Card], persons_score: int, person: str, display_score: bool):
    """Prints a person's hand and score"""
    print("\n".join(ascii_cards(persons_cards)))
    if display_score is True:
        print(f"{person} total: {persons_score}")
    else:
        print(f"{person} total: ?")
    print()

def flip_dealer_print_both(player_cards: list[Card], player_score: int, dealer_cards: list[Card], dealer_score: int):
    """Flips over the dealer's first card
    and prints the dealer's hand and the player's hand."""
    print()
    # Flip over dealer's first card
    dealer_cards[0].hidden = False
    print_cards(dealer_cards, dealer_score, "Dealer", True)
    print_cards(player_cards, player_score, "Player", True)

def ace_values(persons_cards: list[Card], persons_score: int) -> list:
    """Handles Ace values dynamically"""
    # Search to see if hand includes Aces with values of eleven
    indices_ace_eleven = [i for i, card in enumerate(persons_cards) if card.card_value == 11 and card.value == "A"]
    while persons_score > 21 and indices_ace_eleven:
        persons_cards[indices_ace_eleven.pop()].card_value = 1
        persons_score -= 10
    return indices_ace_eleven

def handle_second_deal(player_cards: list[Card], player_score: int, dealer_cards: list[Card], dealer_score: int):
    """Prints dealer's and player's cards and calls second_deal function"""
    # Padding
    print()
    print()
    # Print both hands, but don't show dealer's score
    print_cards(dealer_cards, dealer_score, "Dealer", False)
    print_cards(player_cards, player_score, "Player", True)
    second_deal(player_cards, player_score, dealer_cards, dealer_score)

def second_deal(player_cards: list[Card], player_score: int, dealer_cards: list[Card], dealer_score: int):
    """Handles player hitting and dealer hitting, 
    calls score comparison function to handle wins"""
    # Ask player if they want to hit
    print("Do you want to hit?")
    print()
    hit = input("Type 'y' for yes, 'n' for no, or 'p' to pause: ")
    # If they hit, deal a card, handle ace values, and score comparison
    while hit.lower() == "y":
        player_score += deal_card(deck, player_cards, False)
        ace_values(player_cards, player_score)
        player_cards, player_score, hit = handle_win_or_bust("Player", player_cards, player_score, dealer_cards, dealer_score, hit)
        # Ask player if they want to hit
        if hit.lower() == "y":
            print("Do you want to hit?")
            print()
            hit = input("Type 'y' for yes, 'n' for no, or 'p' to pause: ")
    # Dealer hits
    if player_score < 21 and hit.lower() != "p" and hit.lower() != "y":
        dealer_did_hit = False
        while dealer_score <= 16:
            dealer_did_hit = True
            print()
            print("Dealer hits")
            time.sleep(1)
            # Flips dealer's card
            dealer_cards[0].hidden = False
            dealer_score += deal_card(deck, dealer_cards, False)
            ace_values(dealer_cards, dealer_score)
            dealer_cards, dealer_score, hit = handle_win_or_bust("Dealer", player_cards, player_score, dealer_cards, dealer_score, hit)
            time.sleep(1)
        if player_score > dealer_score:
            if not dealer_did_hit:
                flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            print("YOU WIN!")
        elif player_score < dealer_score <= 21:
            if not dealer_did_hit:
                flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            print("YOU LOSE :(")
        elif player_score == dealer_score:
            if player_score == 21 and dealer_score == 21 and len(player_cards) != len(dealer_cards):
                if len(player_cards) < len(dealer_cards):
                    if not dealer_did_hit:
                        flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
                    print("YOU WIN!")
                elif len(player_cards) > len(dealer_cards):
                    if not dealer_did_hit:
                        flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
                    print("YOU LOSE :(")
            else:
                if not dealer_did_hit:
                    flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
                print("TIE GAME.")
    elif hit.lower() == "p":
        upload_cards(player_cards, dealer_cards)

def handle_win_or_bust(person: str, player_cards: list[Card], player_score: int, dealer_cards: list[Card], dealer_score: int, hit: str):
    """Handles win or bust on deal"""
    # Which person is calling the function?
    if person == "Player":
        persons_cards = player_cards
        persons_score = player_score
    elif person == "Dealer":
        persons_cards = dealer_cards
        persons_score = dealer_score
    # Handle win or bust & exit while loop with hit=n
    if persons_score > 21:
        if person == "Player":
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            print("You busted.\nYOU LOSE :(")
            hit = "n"
        else:
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            print("The dealer busted.\nYOU WIN!")
            hit = "n"
    elif player_score == 21 and dealer_score != 21:
        flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
        print("YOU WIN!")
        hit = "n"
    else:
        if person == "Player":
            print()
            print_cards(dealer_cards, dealer_score, "Dealer", False)
            print_cards(player_cards, player_score, "Player", True)
        elif person == "Dealer":
            print()
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
    return persons_cards, persons_score, hit

########################################################### MAIN ###########################################################

def blackjack():
    """Classic blackjack game with dealer and one player.
    Dealer will always hit if score is 16 or below."""
    print()
    print()
    print("WELCOME TO BLACKJACK")
    print()
    load = input("Type 'n' to start a new game or 'l' to load a previous game: ")
    if load.lower() == "l":
        player_cards, player_score, dealer_cards, dealer_score = download_cards()
        handle_second_deal(player_cards, player_score, dealer_cards, dealer_score)
    elif load.lower() == "n":
        player_cards = []
        dealer_cards = []
        player_score = 0
        dealer_score = 0

        # First deal
        while len(player_cards) < 2:
            # Dealer hand and score, hides 1st card
            if len(dealer_cards) == 0:
                dealer_score += deal_card(deck, dealer_cards, True)
            else:
                dealer_score += deal_card(deck, dealer_cards, False)
            # Player hand and score
            player_score += deal_card(deck, player_cards, False)

        # Handle Ace values in case someone is dealt 2 Aces
        ace_values(dealer_cards, dealer_score)
        ace_values(player_cards, player_score)

        # Handle win on flip
        if player_score == 21 and dealer_score != 21:
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            print("YOU WIN!")
        elif dealer_score == 21 and player_score != 21:
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            print("YOU LOSE :(")
        elif player_score == dealer_score == 21:
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            print("TIE GAME")

        # Handle second deal
        else:
            handle_second_deal(player_cards, player_score, dealer_cards, dealer_score)

blackjack()

# def second_deal(person, player_cards, player_score, dealer_cards, dealer_score, hit):
    #     """Deals the person's second hand and handles Ace values dynamically.
    #      Handles win or bust on hit."""
    #     if person == "Player":
    #         persons_cards = player_cards
    #         persons_score = player_score
    #     elif person == "Dealer":
    #         persons_cards = dealer_cards
    #         persons_score = dealer_score

    #     # Search to see if hand includes card with a value of 11
    #     indices_ace_eleven = ace_values(persons_cards, persons_score)

    #     if persons_score > 21 and len(indices_ace_eleven) == 0:
    #         if person == "Player":
    #             flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
    #             print("You busted.\nYOU LOSE :(")
    #             hit = "n"
    #         else:
    #             flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
    #             print("The dealer busted.\nYOU WIN!")
    #     elif player_score == 21 and dealer_score != 21:
    #         flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
    #         print("YOU WIN!")
    #         hit = "n"
    #     else:
    #         if person == "Player":
    #             print()
    #             print_cards(dealer_cards, dealer_score, "Dealer", False)
    #             print_cards(player_cards, player_score, "Player", True)
    #             print("Inner hit")
    #             hit = input("Do you want to hit? Type 'y' for yes, 'n' for no, or 'p' to pause: ")
    #         # elif person == "Dealer":
    #         #     print()
    #         #     print_cards(dealer_cards, dealer_score, "Dealer", True)
    #         #     print_cards(player_cards, player_score, "Player", True)
    #     return persons_cards, persons_score, hit

    # def handle_second_deal(player_cards, player_score, dealer_cards, dealer_score):
    #     """Calls second_deal, handles score comparison"""
    #     # Player's hits
    #     print("Do you want to hit?")
    #     print()
    #     hit = input("Type 'y' for yes, 'n' for no, or 'p' to pause: ")
    #     while hit.lower() == "y":
    #         player_score += deal_card(deck, player_cards, False)
    #         player_cards, player_score, hit = second_deal("Player", player_cards, player_score, dealer_cards, dealer_score, hit)
    #     # Dealer's hits
    #     if player_score < 21 and hit.lower() != "p":
    #         while dealer_score <= 16:
    #             print()
    #             print("Dealer hits")
    #             time.sleep(1)
    #             # Flips dealer's card
    #             dealer_cards[0].hidden = False
    #             dealer_score += deal_card(deck, dealer_cards, False)
    #             dealer_cards, dealer_score, hit = second_deal("Dealer", player_cards, player_score, dealer_cards, dealer_score, hit)
    #             time.sleep(1)
    ###         if player_score > dealer_score:
    #             flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
    #             print("YOU WIN!")
    ###         elif player_score < dealer_score <= 21:
    #             flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
    #             print("YOU LOSE :(")
    ###         elif player_score == dealer_score:
    #             flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
    #             print("TIE GAME.")
    #     if hit.lower() == "p":
    #         load_cards(player_cards, dealer_cards)
