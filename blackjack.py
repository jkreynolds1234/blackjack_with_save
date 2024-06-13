"""Runs Blackjack program"""

# CHANGES TO MAKE:
    # Update paused game status to saved when ending a paused game
    # Figure out what to do when someone pauses a game twices

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

def set_cards() -> tuple[list[Card], int, list[Card], int]:
    player_cards = []
    player_score = 0
    dealer_cards = []
    dealer_score = 0
    return (player_cards, player_score, dealer_cards, dealer_score)

def upload_cards(player_cards: list[Card], dealer_cards: list[Card], status: str, game_num: int = 0):
    """Loads player's and dealer's cards into the games database"""
    # Create database and add player & dealer's hands
    games_db = GamesDatabase()
    game_num = games_db.gameNum(game_num)
    for c in player_cards:
        games_db.addCard(status, game_num, "Player", c)
    for c in dealer_cards:
        games_db.addCard(status, game_num, "Dealer", c)

def download_cards() -> tuple[list[Card], int, list[Card], int, int]:
    """Downloads cards from chosen paused game in the games database and unpacks them"""
    games_db = GamesDatabase()
    choices = games_db.selectGameStatus("p")
    if choices:
        print()
        select = input(f"Which game do you want to load? {choices} ")
        game_contents = games_db.selectGame(select)
        # Unpack list of dictionaries into player and dealer cards
        player_cards, player_score, dealer_cards, dealer_score = set_cards()
        for entry in game_contents:
            if entry["player"] == "Player":
                player_cards.append(Card(suit_symbols[entry["suit"]], entry["suit"], entry["face_value"], entry["card_value"], False))
                player_score += entry["card_value"]
            elif entry["player"] == "Dealer":
                dealer_cards.append(Card(suit_symbols[entry["suit"]], entry["suit"], entry["face_value"], entry["card_value"], hidden = len(dealer_cards) == 0))
                dealer_score += entry["card_value"]
    else:
        player_cards, player_score, dealer_cards, dealer_score = set_cards()
        select = 0
    return(player_cards, player_score, dealer_cards, dealer_score, select)

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

def handle_second_deal(player_cards: list[Card], player_score: int, dealer_cards: list[Card], dealer_score: int, game_num: int = 0):
    """Prints dealer's and player's cards and calls second_deal function"""
    # Padding
    print()
    print()
    # Print both hands, but don't show dealer's score
    print_cards(dealer_cards, dealer_score, "Dealer", False)
    print_cards(player_cards, player_score, "Player", True)
    second_deal(player_cards, player_score, dealer_cards, dealer_score, game_num)

def second_deal(player_cards: list[Card], player_score: int, dealer_cards: list[Card], dealer_score: int, game_num: int = 0):
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
        player_cards, player_score, hit = handle_win_or_bust("Player", player_cards, player_score, dealer_cards, dealer_score, hit, game_num)
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
            dealer_cards, dealer_score, hit = handle_win_or_bust("Dealer", player_cards, player_score, dealer_cards, dealer_score, hit, game_num)
            time.sleep(1)
        if player_score > dealer_score:
            if not dealer_did_hit:
                flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            upload_cards(player_cards, dealer_cards, "w", game_num)
            print("YOU WIN!")
        elif player_score < dealer_score <= 21:
            if not dealer_did_hit:
                flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            upload_cards(player_cards, dealer_cards, "l", game_num)
            print("YOU LOSE :(")
        elif player_score == dealer_score:
            if player_score == 21 and dealer_score == 21 and len(player_cards) != len(dealer_cards):
                if len(player_cards) < len(dealer_cards):
                    if not dealer_did_hit:
                        flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
                    upload_cards(player_cards, dealer_cards, "w", game_num)
                    print("YOU WIN!")
                elif len(player_cards) > len(dealer_cards):
                    if not dealer_did_hit:
                        flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
                    upload_cards(player_cards, dealer_cards, "l", game_num)
                    print("YOU LOSE :(")
            else:
                if not dealer_did_hit:
                    flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
                upload_cards(player_cards, dealer_cards, "t", game_num)
                print("TIE GAME.")
    elif hit.lower() == "p":
        upload_cards(player_cards, dealer_cards, "p", game_num)

def handle_win_or_bust(person: str, player_cards: list[Card], player_score: int, dealer_cards: list[Card], dealer_score: int, hit: str, game_num: int):
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
            upload_cards(player_cards, dealer_cards, "l", game_num)
            print("You busted.\nYOU LOSE :(")
            hit = "n"
        else:
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            upload_cards(player_cards, dealer_cards, "w", game_num)
            print("The dealer busted.\nYOU WIN!")
            hit = "n"
    elif player_score == 21 and dealer_score != 21:
        flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
        upload_cards(player_cards, dealer_cards, "w", game_num)
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
    load = input("(1) Type 'n' to start a new game \n(2) Type 'l' to load a paused game \n(3) Type 'r' to view your records \n(4) Type 'x' to reset your records: ")
    games_db = GamesDatabase()
    if load.lower() == "l":
        player_cards, player_score, dealer_cards, dealer_score, game_num = download_cards()
        if game_num != 0:
            handle_second_deal(player_cards, player_score, dealer_cards, dealer_score, game_num)
        else:
            print()
            print("No paused games to load. Please select a different option from the main menu.")
            blackjack()
    elif load.lower() == "r":
        wins, losses, ties = games_db.selectGameStatus("s")
        print()
        print(f"Wins: {wins}")
        print(f"Losses: {losses}")
        print(f"Ties: {ties}")
        blackjack()
    elif load.lower() =="x":
        games_db.clearGamesTable()
        blackjack()
    elif load.lower() == "n":
        player_cards, player_score, dealer_cards, dealer_score = set_cards()

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
            upload_cards(player_cards, dealer_cards, "w")
            print("YOU WIN!")
        elif dealer_score == 21 and player_score != 21:
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            upload_cards(player_cards, dealer_cards, "l")
            print("YOU LOSE :(")
        elif player_score == dealer_score == 21:
            flip_dealer_print_both(player_cards, player_score, dealer_cards, dealer_score)
            upload_cards(player_cards, dealer_cards, "t")
            print("TIE GAME")

        # Handle second deal
        else:
            handle_second_deal(player_cards, player_score, dealer_cards, dealer_score)
    else:
        print("Please enter a valid input.")
        blackjack()

print()
print()
print("WELCOME TO BLACKJACK")
blackjack()
