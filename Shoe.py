# Shoe Class and functions to help it

card_numbers = ['a', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'j', 'q', 'k']
card_symbols = ['C', 'D', 'H', 'S']


def split(word):
    return [char for char in word]


def get_card_value_and_soft(card):
    if "cardback" in card.lower():
        return 0, 0

    if any(x in card for x in ["10", "j", "q", "k"]):
        return 10, False

    card_chars = split(card)
    card_val = card_chars[1]

    if card_val.isdigit():
        return int(card_val), False

    return 11, True


def ret_full_deck_list():
    full_deck = []
    for sym in card_symbols:
        for num in card_numbers:
            full_deck.append(":" + num + sym + ":")
    return full_deck


def ret_full_shoe(NUMBER_OF_DECKS):
    full_deck = []
    for sym in card_symbols:
        for num in card_numbers:
            full_deck.append(":" + num + sym + ":")
    shoeDict = {}
    for card in full_deck:
        shoeDict[card] = NUMBER_OF_DECKS
    return shoeDict


class Shoe:
    '''
    INIT
    '''
    def __init__(self, NUMBER_OF_DECKS=3):
        self.NUMBER_OF_DECKS = NUMBER_OF_DECKS
        self.NUMBER_OF_CARDS_MAX = self.NUMBER_OF_DECKS * 52
        self.numberofcards_unseen = self.NUMBER_OF_CARDS_MAX # OR MAKE THIS ZERO?
        self.numberofcards_remaining_actual = self.NUMBER_OF_CARDS_MAX # OR MAKE THIS ZERO?
        self.unseen_cards_dict = ret_full_shoe(NUMBER_OF_DECKS)
        self.unused_cards_dict = ret_full_shoe(NUMBER_OF_DECKS)

    '''
    RESET THE SHOE
    '''
    def reset(self):
        self.numberofcards_unseen = self.NUMBER_OF_CARDS_MAX
        self.numberofcards_remaining_actual = self.NUMBER_OF_CARDS_MAX
        self.unseen_cards_dict = ret_full_shoe(self.NUMBER_OF_DECKS)
        self.unused_cards_dict = ret_full_shoe(self.NUMBER_OF_DECKS)

    '''
    GET CARDS that haven't been seen
    '''
    def get_cards_unseen(self):
        if all(value == 0 for value in self.unseen_cards_dict.values()):
            return False
        else:
            return self.unseen_cards_dict

    '''
    GET CARDS THAT ARE ACTUALLY LEFT
    '''
    def get_cards_unused(self):
        if all(value == 0 for value in self.unused_cards_dict.values()):
            return False
        else:
            return self.unused_cards_dict

    '''
    GET CARDS LEFT (that haven't been seen) VALUE ARRAY FOR DQN INPUT
    '''
    def get_state(self):
        state   = [  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0]
        c_list  = ['a', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'j', 'q', 'k']
        for key, value in self.unseen_cards_dict.items():
            key = key.replace(':', '')
            key = key.replace('H', '')
            key = key.replace('D', '')
            key = key.replace('S', '')
            key = key.replace('C', '')
            state[c_list.index(key)] += value
        return state

    '''
    SEE CARD, DECREMENT TOTAL OF INPUT CARD, aka the card has been seen by agent and counted
    '''
    def see_card(self, card):
        if "cardback" in card.lower():
            return True
        if card in self.unseen_cards_dict.keys():
            if self.unseen_cards_dict[card] > 0:
                self.unseen_cards_dict[card] -= 1
                self.numberofcards_unseen -= 1
                return True
            else:
                return False  # TODO, there are 0 of those cards
        else:
            return False  # TODO, there is no such card

    '''
    USE CARD, aka the card is actually removed from the shoe
    '''
    def use_card(self, card):
        if "cardback" in card:
            return True
        if card in self.unused_cards_dict.keys():
            if self.unused_cards_dict[card] > 0:
                self.unused_cards_dict[card] -= 1
                return True
            else:
                return False # TODO, there are 0 of those cards
        else:
            return False # TODO, there is no such card
