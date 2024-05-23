"""Creates a 52 card deck and prints ASCII versions of the cards."""
# Card class definition and creation when called
class Card:
    """Creates a 52 card deck."""
    # Setting parameter equal to something makes that the default value if nothing is passed in
    def __init__(self, suit, suit_name, value, card_value, hidden = True):
        self.suit = suit
        self.suit_name = suit_name
        self.value = value
        self.card_value = card_value
        self.hidden = hidden

    def __str__(self):
        return f"{self.value} of {self.suit}"

# Card deck without jokers

# Suit images
suit_symbols = {"Spades":"♠", "Hearts":"♥", "Clubs": "♣", "Diamonds": "♦"}

# Cards and values
cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Ace defaulted to 11 unless the combination of cards the player draws will add up to over 21, then it has a value of 1
card_values = {"A": 11, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}

# Generate a deck of cards:
deck = [Card(suit_symbols[s], s, c, card_values[c], hidden = True) for s in suit_symbols for c in cards]
# ---------------------------------------------------------------------------------------------------------------------------------

# ASCII ART for cards
def ascii_cards(cards_list: list[Card]):
    """Creates ascii art of a card with the input of the suit and card value"""
    lines = [[] for i in range(9)]
    for chosen_card in cards_list:
        if chosen_card.hidden is False:
            value = chosen_card.value
            # 10 is the only value with 2 chars
            if value == "10":
                space = ""
            else:
                space = " "
            suit_symbol = chosen_card.suit
            # Generating the card
            lines[0].append('┌─────────┐')
            lines[1].append('│ {}{}      │'.format(value, space))
            lines[2].append('│         │')
            lines[3].append('│         │')
            lines[4].append('│    {}    │'.format(suit_symbol))
            lines[5].append('│         │')
            lines[6].append('│         │')
            lines[7].append('│      {}{} │'.format(space, value))
            lines[8].append('└─────────┘')
        else:
            lines[0].append('┌─────────┐')
            lines[1].append('│░░░░░░░░░│')
            lines[2].append('│░░░░░░░░░│')
            lines[3].append('│░░░░░░░░░│')
            lines[4].append('│░░░░░░░░░│')
            lines[5].append('│░░░░░░░░░│')
            lines[6].append('│░░░░░░░░░│')
            lines[7].append('│░░░░░░░░░│')
            lines[8].append('└─────────┘')
    result = ["  ".join(line) for line in lines]
    return result

# test_card1 = Card(suit_symbols["Spades"], "Spades", "6", "6", False)
# test_card2 = Card(suit_symbols["Diamonds"], "Diamonds", "4", "4")
# list_of_cards = [test_card1, test_card2]
# print("\n".join(ascii_cards(list_of_cards)))
