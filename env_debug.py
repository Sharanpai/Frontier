from PIL import Image
import numpy as np

import gym
import gym_snake

# from skimage.color import rgb2gray
# from skimage.transform import resize
# from tqdm import tqdm, tqdm_notebook
#
# import random
#
# from IPython.display import display
#
# from PIL import Image


ENV_NAME = 'snake-v0'  # Environment name
FRAME_WIDTH = 84  # Resized frame width
FRAME_HEIGHT = 84  # Resized frame height
INPUT_SHAPE = (FRAME_WIDTH, FRAME_HEIGHT)
WINDOW_LENGTH = 4  # Number of most recent frames to produce the input to the network (WINDOW LENGTH)

NUM_STEPS = 6_000_005

EXPLORATION_STEPS = 4_500_005  # Number of steps over which the initial value # of epsilon is linearly annealed to its final value
INITIAL_EPSILON = 1.0  # Initial value of epsilon in epsilon-greedy
FINAL_EPSILON = 0.1  # Final value of epsilon in epsilon-greedy

OBSERVE = 20_000  # Number of steps to populate the replay memory before training starts
NUM_REPLAY_MEMORY = 400_000  # Number of replay memory the agent uses for training
BATCH_SIZE = 32  # Mini batch size
TARGET_UPDATE_INTERVAL = 10_000  # The frequency with which the target network is updated
TRAIN_INTERVAL = 4  # The agent selects 4 actions between successive updates

LEARNING_RATE = 0.00025  # Learning rate used by optimizer
GAMMA = 0.99  # Discount factor

SAVE_INTERVAL = 200_000  # The frequency with which the network is saved
NO_OP_STEPS = 7  # Maximum number of "do nothing" actions to be performed by the agent at the start of an episode

SAVE_NETWORK_PATH = 'saved_networks/' + ENV_NAME
SAVE_SUMMARY_PATH = 'summary/' + ENV_NAME


def get_env():
    env = gym.make(ENV_NAME)
    # env.n_foods =
    env.snake_size = 2
    env.n_snakes = 4
    env.grid_size = [100, 100]
    env.unit_size = 10
    env.unit_gap = 1
    # env.random_init = True
    return env



env = get_env()
env.reset()
import time
for i in range(100):
    # time.sleep(2)
    print(i)
    o, _, d, _ = env.step([np.random.randint(4, 12), np.random.randint(4, 12), np.random.randint(4, 12), np.random.randint(4, 12)])
    env.render()

input()