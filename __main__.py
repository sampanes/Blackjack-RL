from Shoe import Shoe
from DealerStub import Dealer
from DQN_agent import *
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from tabulate import tabulate
import numpy as np

EPISODES_PER_HOUR = 25000  # Depending on your machine, you may be able to set agent's learning to run based on time with some accuracy


def drbj(hours=0, episodes=50_000):
    
    if hours:
        ep = int(hours * EPISODES_PER_HOUR)
    else:
        ep = episodes

    loss, epsilon_list, dh, ph = train_dqn_blackjack(ep)

    default_plot_loss(ep, loss, epsilon_list)
    plot_hands_accumulated(dh, ph)
    

def default_plot_loss(ep, loss, epsilon_list):
    
    fig, ax1 = plt.subplots()

    # Plot the rewards over episodes
    color = 'tab:green'
    ax1.set_xlabel('episodes')
    ax1.set_ylabel('reward', color=color)
    ax1.plot([i for i in range(ep)], loss, color)
    ax1.tick_params(axis='y', labelcolor=color)

    # instantiate second axes that is twins with x
    ax2 = ax1.twinx()

    # Plot the epsilon over episodes
    color = 'tab:red'
    ax2.set_ylabel('epsilon')
    ax2.plot([i for i in range(ep)], epsilon_list, color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    plt.show()
    

def plot_hands_accumulated(dh, ph):
    # Plot hands, agent along x and dealer along y
    if len(ph) != len(dh):
        print(len(ph), " != ", len(dh))
    games = len(ph)

    hands_accumulated = np.zeros([27, 31])

    for i in range(games):
        p = ph[i]
        d = dh[i]
        hands_accumulated[d][p] += 1

    min_seen = np.min(hands_accumulated[np.nonzero(hands_accumulated)])

    print(min_seen)
    if min_seen == 1:
        table = tabulate(hands_accumulated, tablefmt="fancy_grid")
        print(table)
    fig, ax = plt.subplots()
    im = ax.imshow(hands_accumulated, vmin=min_seen)

    ax.set_xticks(np.arange(30))
    ax.set_yticks(np.arange(26))

    plt.setp(ax.get_xticklabels(), rotation=90, ha="right",
             rotation_mode="anchor")

    ax.set_title("Frequency of hands after %s games" % games)
    fig.tight_layout()

    # Draw polygons around regions of interest
    win_dbust = [[3.5, 21.5], [21.5, 21.5], [21.5, 26.5], [3.5, 26.5]]
    win_dlose = [[17.5, 16.5], [21.5, 20.5], [21.5, 3.5], [20.5, 3.5], [20.5, 16.5]]

    lose_pbust = [[21.5, 1.5], [21.5, 11.5], [30.5, 11.5], [30.5, 1.5]]
    lose_plose = [[15.5, 16.5], [20.5, 21.5], [3.5, 21.5], [3.5, 16.5]]
    
    # Add polygons
    ax.add_patch(Polygon(win_dbust, closed=True, fill=False, edgecolor='green', lw=3))
    ax.add_patch(Polygon(win_dlose, closed=True, fill=False, edgecolor='green', lw=3))

    ax.add_patch(Polygon(lose_pbust, closed=True, fill=False, edgecolor='red', lw=2))
    ax.add_patch(Polygon(lose_plose, closed=True, fill=False, edgecolor='red', lw=2))

    plt.xlabel("Agent Hand Total")
    plt.ylabel("Dealer Hand Total")
    plt.show()
    
    
if __name__ == '__main__':
    drbj()
