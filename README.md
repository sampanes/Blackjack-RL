
# Blackjack-RL


Agent learns to count cards and win at some blackjack games, like those on discord servers


# Blackjack basics


Blackjack is a simple card game where you try to get your hand's total value higher than the dealer but not higher than 21.
Ace is worth 11, or worth 1 depending on if equaling 11 results in value > 21
All other royal cards are worth 10
All numbered cards are worth their actual number
Bust means hand value is above 21, this can happen to the agent or the dealer and results in a loss
Win means agent has higher value than dealer without busting
Push means tie
Loss can be agent busted, or dealer got a higher hand without exceeding 21
Dealer advantage: Dealer waits until player is done, so player can bust before dealer ever tries, meaning dealer wins slight majority of games in most cases


# AGENT ACTIONS


Actions prior to a round of blackjack, based on BET_MIN and BET_INCR, both set in DealerStub.py:
Bet small (BET_MIN)
Bet medium (BET_MIN + BET_INCR)
Bet large (BET_MIN + 2 * BET_INCR)

Actions during a round of blackjack:
Stand: accept the total value of agent hand, let dealer go and then evaluate hands
Hit: draw one card and continue play (unless hand value >= 21)
Double Down: double the initial bet, hit, and end the game. Cards are then evaluated

Dealer advantage: Dealer waits until player is done, so player can bust before dealer ever tries, meaning dealer wins slight majority of games in most cases


# UNIQUE BLACKJACK RULES


The rules that may be unique here are based on ubeleiveaboat's dealer (discord) and are as follows:
*  Dealer hits until their hand is > DEALER_MIN (set in DealerStub.py, default 16)
*  If either dealer or agent is dealt 21 within first two cards, the game ends and the hands are evaluated
*  Agent can bet any amount, but the RL's action space is limited to small bet, medium bet, and large bet (see above)
*  Agent can chose to stand only if their hand exceeds 11 (hard coded in DQN.act)


# USAGE


This code can be used as follows:
Initialize a dealer with number of decks per shoe as a parameter (default 3, like unbeleivaboat's dealer)
Create a directory where weights can be stored and recalled, set WEIGHTS_FILE parameter to string of this path (in DQN.py)
Hyperparameters can be set in the __init__ method of DQN
Optional values inlcude:
*  ADD_CLOSE_TO_21 bool (this helps the AI get some extra reward for getting a hand value that is <= 21 proportional to hand value, reward occurs even in loss/push)
*  BET_MIN
*  BET_INCR
*  BJ_PAYOUT (some servers count blackjack as 1x, 1.5x or even 2x bet)
*  PARTICIPATION_TROPHY (this is for the millenials who eat avacado toast)


# Imports


import random
import numpy as np
from keras import Sequential
from keras.optimizers import Adam
from collections import deque
from keras.layers import Dense
import matplotlib.pyplot as plt
from tqdm import tqdm
import math

