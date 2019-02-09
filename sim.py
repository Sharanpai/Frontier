from PIL import Image
import numpy as np

import gym
import gym_snake

from skimage.color import rgb2gray
from skimage.transform import resize

from IPython.display import display

from PIL import Image

ENV_NAME = 'snake-v0'  # Environment name


def get_env():
    env = gym.make(ENV_NAME)
    # env.n_foods =
    env.snake_size = 2
    env.n_snakes = 4
    env.grid_size = [30, 30]
    env.unit_size = 5
    env.unit_gap = 1
    # env.random_init = True
    return env


UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

CUT_UP = 0 + 4
CUT_RIGHT = 1 + 4
CUT_DOWN = 2 + 4
CUT_LEFT = 3 + 4

DOUSE_UP = 0 + 8
DOUSE_RIGHT = 1 + 8
DOUSE_DOWN = 2 + 8
DOUSE_LEFT = 3 + 8

env = get_env()
o = env.reset()
img = Image.fromarray(o)
i = 0
img.save('sim' + str(i) + '.png')
display(img)

while True:
    i += 1
    l = []
    l.append(input())
    l.append(input())
    l.append(input())
    l.append(input())

    a = []
    for k in range(4):
        action = 0
        if l[k] == 'w':
            action = UP
        elif l[k] == 'a':
            action = LEFT
        elif l[k] == 's':
            action = DOWN
        elif l[k] == 'd':
            action = RIGHT
        elif l[k] == 'cw':
            action = CUT_UP
        elif l[k] == 'ca':
            action = CUT_LEFT
        elif l[k] == 'cs':
            action = CUT_DOWN
        elif l[k] == 'cd':
            action = CUT_RIGHT
        elif l[k] == 'dw':
            action = DOUSE_UP
        elif l[k] == 'da':
            action = DOUSE_LEFT
        elif l[k] == 'ds':
            action = DOUSE_DOWN
        elif l[k] == 'dd':
            action = DOUSE_RIGHT
        a.append(action)

    o, r, d, _ = env.step(a)
    img = Image.fromarray(o)
    img.save('sim' + str(i) + '.png')
    img.show()
    # env.render()
    print("step")
