import random
from Shoe import Shoe
from Shoe import split, get_card_value_and_soft
from Shoe import ret_full_shoe

ADD_CLOSE_TO_21 = True
DEALER_MIN = 16
BJ_PAYOUT = 1.5  # blackjack multiplier

BET_MIN = 1     # bet 1 unit at minimum
BET_INCR = 2    # bet MIN + INCR * {0:2}
PARTICIPATION_TROPHY = 0.00  # used to reward AI when it plays even if nothing happens


def get_total_and_ongoing_from_hand(hand):
    total = 0
    ongoing = True
    soft_list = []

    for card in hand:
        value, soft_bool = get_card_value_and_soft(card)
        if soft_bool:
            soft_list.append(True)
        total += value
        if soft_list and total > 21:
            total -= 10
            soft_list.pop()

    if total > 21:
        ongoing = False

    return total, ongoing


def get_total_and_soft_from_hand(hand):
    if not hand:
        return 0, 0
    total = 0
    soft_list = []

    for card in hand:
        value, soft_bool = get_card_value_and_soft(card)
        if soft_bool:
            soft_list.append(True)
        total += value
        if soft_list and total > 21:
            total -= 10
            soft_list.pop()

    return total, soft_bool


class Dealer:
    def __init__(self, NUMBER_OF_DECKS=3):
        self.NUMBER_OF_DECKS = NUMBER_OF_DECKS
        self.shoe = Shoe(self.NUMBER_OF_DECKS)
        self.bet = 0
        self.doubled_bet = False
        self.dealer_hand = []
        self.dealer_hand_value = 0
        self.dealer_hand_hidden = []
        self.dealer_hand_hidden_value = 0
        self.agent_hand = []
        self.agent_hand_value = 0
        self.agent_hand_is_soft = False
        self.game_over = True
        self.reshuffled_bool = False

    def draw_rand_card(self):
        deck_dict = self.shoe.get_cards_unused()
        if self.shoe.numberofcards_remaining_actual > 0:
            pulled_card = random.choice(list(deck_dict))
            while deck_dict[pulled_card] == 0:
                pulled_card = random.choice(list(deck_dict))
            self.shoe.use_card(pulled_card)
            self.shoe.numberofcards_remaining_actual -= 1
            return pulled_card
        else:
            self.shoe = Shoe(self.NUMBER_OF_DECKS)
            self.reshuffled_bool = True
            return self.draw_rand_card()

    def deal_cards(self, bet):
        self.bet = bet
        self.game_over = False
        self.doubled_bet = False
        pull_list = []
        while len(pull_list) < 4:
            card = self.draw_rand_card()
            if card:
                pull_list.append(card)
            else:
                return False, False
        self.dealer_hand = [pull_list[0], pull_list[2]]
        self.dealer_hand_hidden = self.dealer_hand[:]
        self.dealer_hand_hidden[1] = ":cardBack:"
        self.agent_hand = [pull_list[1], pull_list[3]]

        self.agent_hand_value, self.agent_hand_is_soft = get_total_and_soft_from_hand(self.agent_hand)
        self.dealer_hand_value, dealer_soft = get_total_and_soft_from_hand(self.dealer_hand)
        self.dealer_hand_hidden_value, _ = get_total_and_soft_from_hand(self.dealer_hand_hidden)

        if self.agent_hand_value == 21 and self.dealer_hand_value == 21:
            self.game_over = True
            return self.agent_hand, self.dealer_hand, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, "Push, money back", 0]

        elif self.agent_hand_value == 21:
            self.game_over = True
            return self.agent_hand, self.dealer_hand, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, "Win", self.bet * BJ_PAYOUT]

        elif self.dealer_hand_value == 21:
            self.game_over = True
            return self.agent_hand, self.dealer_hand, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, "Loss", self.bet * -1]

        return self.agent_hand, self.dealer_hand_hidden, \
               self.shoe.numberofcards_remaining_actual, \
               [self.game_over, False, False]

    '''****************************************************************************************
                Hit (can continue or agent bust)
    ****************************************************************************************'''

    def hit(self):
        new_card = self.draw_rand_card()
        self.agent_hand.append(new_card)
        self.agent_hand_value, self.agent_hand_is_soft = get_total_and_soft_from_hand(self.agent_hand)
        if self.agent_hand_value < 21:
            return self.agent_hand, self.dealer_hand_hidden, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, False, False]
        else:
            return self.stand()

    '''****************************************************************************************
                Stand (ends game)
    ****************************************************************************************'''

    def stand(self):
        ##
        #   Agent Cannot Win, so it busted
        ##
        if self.agent_hand_value > 21:
            self.game_over = True
            return self.agent_hand, self.dealer_hand_hidden, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, "Bust", self.bet * -1]

        while self.dealer_hand_value <= DEALER_MIN:
            self.dealer_hand.append(self.draw_rand_card())
            self.dealer_hand_value, dealer_can_win = get_total_and_ongoing_from_hand(self.dealer_hand)
            
        ##
        #   game ended, decide who won/result
        ##
        self.game_over = True
        
        ##
        #   Dealer Cannot Win, so they busted
        ##
        if self.dealer_hand_value > 21:
            return self.agent_hand, self.dealer_hand, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, "Dealer bust", self.bet + (self.bet * self.doubled_bet)]

        ##
        #   Scores are Equal, push
        ##
        if self.agent_hand_value == self.dealer_hand_value:
            return self.agent_hand, self.dealer_hand, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, "Push, money back", 0]

        ##
        #   Dealer score is greater, Agent loss
        ##
        if self.dealer_hand_value > self.agent_hand_value:
            return self.agent_hand, self.dealer_hand, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, "Loss", self.bet * -1 - (self.bet * self.doubled_bet)]
        ##
        #   Agent score is greater, Agent win
        ##
        else:
            return self.agent_hand, self.dealer_hand, \
                   self.shoe.numberofcards_remaining_actual, \
                   [self.game_over, "Win", self.bet + (self.bet * self.doubled_bet)]

    '''****************************************************************************************
                Double Down (one hit then stand)
    ****************************************************************************************'''

    def double_down(self):
        self.doubled_bet = True
        self.hit()
        return self.stand()

    '''****************************************************************************************
                AI METHODS
    ****************************************************************************************'''

    def see_cards_hands(self):
        if self.reshuffled_bool:
            self.reshuffled_bool = False
        else:
            add_list = self.dealer_hand if self.agent_hand_value < 21 else self.dealer_hand_hidden
            add_list += self.agent_hand
            for card in add_list:
                ok = self.shoe.see_card(card)
                if not ok:
                    print("There was a card to see that is not in list, already been seen?!")
                    print(card)
                    exit(1)

    def reset(self):
        self.bet = 0
        self.dealer_hand = []
        self.dealer_hand_value = 0
        self.dealer_hand_hidden = []
        self.dealer_hand_hidden_value = 0
        self.agent_hand = []
        self.agent_hand_value = 0
        self.agent_hand_is_soft = False
        self.game_over = True
        return self.get_state()

    def get_state(self):
        p_tot = self.agent_hand_value
        p_soft = self.agent_hand_is_soft
        d_tot = self.dealer_hand_value if (self.game_over and p_tot <= 21) else self.dealer_hand_hidden_value

        state = self.shoe.get_state()  # 13 cards and quants
        state.append(self.shoe.numberofcards_remaining_actual)  # cards actual
        state.append(p_tot)  # agent total
        state.append(p_soft)  # agent soft bool
        state.append(d_tot)  # dealer total

        return state

    def step(self, action):
        if action == 0:
            p_hand, d_hand, cards_remain, result_list = self.stand()

        elif action == 1:
            p_hand, d_hand, cards_remain, result_list = self.hit()

        elif action == 2:
            p_hand, d_hand, cards_remain, result_list = self.double_down()

        elif self.game_over and action >= 3:
            p_hand, d_hand, cards_remain, result_list = self.deal_cards(BET_MIN + (action - 3) * BET_INCR)

        else:
            print("DealerStub > step: IMPOSSIBLE CHOICE, quitting immediately")
            exit(1)

        finished = result_list[0]

        reward = result_list[2] + PARTICIPATION_TROPHY  # for millenials who eat avacado toast

        if ADD_CLOSE_TO_21 and (16 < self.agent_hand_value < 22):
            bonus = (self.agent_hand_value - 16) * (1 + finished)/16 * self.bet  # was 16 @ 09:37 4/10/2022
            reward += bonus
        state = self.get_state()

        return reward, state, finished
