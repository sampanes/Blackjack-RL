from DealerStub import Dealer

import random
import numpy as np
from keras import Sequential
from collections import deque
from keras.layers import Dense
from keras.optimizers import Adam
import matplotlib.pyplot as plt
from tqdm import tqdm
import math

env = Dealer()
np.random.seed(0)

PRINT_AMOUNT = 100  # how many times to interrupt progress bar and view loss and epsilon in real time, 0 or False just prints progress bar

WEIGHTS_FILE = "YOUR_FOLDER/YOUR_WEIGHTS"  # You should add your own folder to save weight files


class DQN:
    """ Implementation of deep q learning algorithm """

    def __init__(self, action_space, state_space, weights_filepath='', expect_partial=False):

        self.action_space = action_space
        self.state_space = state_space
        self.epsilon = 1  # Exploration rate, randomly decide an action rather than prediction
        self.gamma = .94  # Decay or discount rate
        self.batch_size = 256  # some set this to 64
        self.epsilon_min = .05 # some set this to 0.01
        self.epsilon_decay = .99999  # Decrease the number of explorations as skill increases, .99 is typically enough unless running 750k+ episodes
        self.learning_rate = .0005  # Determines how much the neural network learns in each iteration, typically .001
        self.memory = deque(maxlen=100000)
        self.model = self.build_model()
        if weights_filepath:
            if not expect_partial:
                self.model.load_weights(weights_filepath)
            else:
                self.model.load_weights(weights_filepath).expect_partial()

    def build_model(self):

        model = Sequential()
        model.add(Dense(34, input_shape=(self.state_space,), activation='relu'))
        model.add(Dense(68, activation='relu'))
        model.add(Dense(136, activation='relu'))
        model.add(Dense(92, activation='relu'))
        model.add(Dense(48, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(12, activation='relu'))
        model.add(Dense(self.action_space, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        model.trainable = True
        return model

    def remember(self, state, action, reward, next_state, done):
      
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        # Action that DQN agent takes depends on if game is ongoing or not, and if agent's hand is less than 12
        # Actions:
        #   Ongoing round
        #       0 : Stand
        #       1 : Hit
        #       2 : Double Down
        #   Start New Round
        #       3 : Bet Small
        #       4 : Bet Medium
        #       5 : Bet Large
        
        game_over = env.game_over                               # check if round is over
        sr = 0 if state[0][-3] > 11 else 1                      # action 0 (stand) is only allowed if hand > 11
        start_range = 3 if game_over else sr                    # actions can be 3 through 5 if round is complete, otherwise (0 or 1) through 2
        stop_range = self.action_space if game_over else 3      # use ternary expressions to set start and stop range for action choice

        if np.random.rand() <= self.epsilon:                    # if dice roll is higher than exploration value, return random action from range
            return random.randrange(start_range, stop_range)

        act_values = self.model.predict(state)                          # get values of actions based on state
        act_values_allowed = act_values[0][start_range: stop_range]     # actions allowed var, only 0-2 are allowed during game, else 3-5, as described above
        ret = np.argmax(act_values_allowed) + start_range               # get action within allowed range that has maximum expected return
        return ret

    def replay(self):

        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states = np.array([i[0] for i in minibatch])
        actions = np.array([i[1] for i in minibatch])
        rewards = np.array([i[2] for i in minibatch])
        next_states = np.array([i[3] for i in minibatch])
        dones = np.array([i[4] for i in minibatch])

        states = np.squeeze(states)
        next_states = np.squeeze(next_states)

        targets = rewards + self.gamma * (np.amax(self.model.predict_on_batch(next_states), axis=1)) * (1 - dones)
        targets_full = self.model.predict_on_batch(states)

        ind = np.array([i for i in range(self.batch_size)])
        targets_full[[ind], [actions]] = targets

        self.model.fit(states, targets_full, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model_to_file(self, filepath):
      
        self.model.save(filepath)

    def save_weights_to_file(self, filepath=''):
      
        if not filepath:
            return
        self.model.save_weights(filepath)


def train_dqn_blackjack(episode):
    
    loss = []
    
    # Set action space as Stand + Hit + Double Down + Small  + Medium + Large bets
    action_space = 6
    
    # Set state space as 13 cards (each with 0 to 12 quantities) + agent hand value (int) + agent hand soft (bool) + dealer hand (int)
    state_space = 13 + 1 + 2 + 1
    
    max_steps = 12  # edge case where if agent continually hits and gets all 2s, 11 times is bust

    agent = DQN(action_space, state_space, WEIGHTS_FILE)
    
    score = 0  # score = 0 can be moved into the main loop to reset each round, not recommended for 750k+ rounds as no trends are immediately obvious

    # These track hands and epsilon values for print out at end of episodes
    dh = []
    ph = []
    epsilon_list = []

    for e in tqdm(range(episode), colour='green'): # TDQM prints a pretty progress bar, not needed
        
        state = env.reset()
        state = np.reshape(state, (1, state_space))
        
        for i in range(max_steps):
            
            action = agent.act(state)
            reward, next_state, done = env.step(action)
            score += reward
            next_state = np.reshape(next_state, (1, state_space))
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            agent.replay()

            if done:
                dh.append(next_state[0][-1])
                ph.append(next_state[0][-3])

                if PRINT_AMOUNT and (e % math.floor(episode / PRINT_AMOUNT) == 0):
                    print("episode: {:,}/{:,}\tscore: {:,.2f}\tepsilon: {:.6f}".format(e, episode, score, agent.epsilon))
                break
            
        env.see_cards_hands()
        loss.append(score)
        epsilon_list.append(agent.epsilon)
        
    agent.save_weights_to_file(WEIGHTS_FILE)
    return loss, epsilon_list, dh, ph
