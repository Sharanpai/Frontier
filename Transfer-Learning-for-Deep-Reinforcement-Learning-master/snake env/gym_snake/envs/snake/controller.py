from gym_snake.envs.snake import Snake
from gym_snake.envs.snake import Grid
import numpy as np
from scipy.spatial.distance import euclidean


class Controller():
    """
    This class combines the Snake, Food, and Grid classes to handle the game logic.
    """

    def __init__(self, grid_size=[30, 30], unit_size=10, unit_gap=1, snake_size=3, n_snakes=1, n_foods=1,
                 random_init=True, wall=False):

        assert n_snakes < grid_size[0] // 3
        assert n_snakes < 25
        assert snake_size < grid_size[1] // 2
        assert unit_gap >= 0 and unit_gap < unit_size

        self.snakes_remaining = n_snakes
        self.grid = Grid(grid_size, unit_size, unit_gap)

        self.empty = []
        self.douse = []
        self.r = [0., 0., 0., 0.]

        self.snakes = []
        self.dead_snakes = []
        for i in range(1, n_snakes + 1):
            start_coord = [i * grid_size[0] // (n_snakes + 1), snake_size + 1]
            self.snakes.append(Snake(start_coord, snake_size))
            color = [self.grid.HEAD_COLOR[0], i * 10, 0]
            color = [0, 0, 255]
            self.snakes[-1].head_color = color
            self.grid.draw_snake(self.snakes[-1], color)
            self.dead_snakes.append(None)

        # if wall:
        #     self.grid.create_wall()
        #     self.grid.create_wall()
        #     self.grid.create_wall()

        # if not random_init:
        #     for i in range(2,n_foods+2):
        #         start_coord = [i*grid_size[0]//(n_foods+3), grid_size[1]-5]
        #         self.grid.place_food(start_coord)
        # else:
        # for i in range(n_foods):
        #     self.grid.new_food(i)

        self.grid.init_fire()

    def move_snake(self, direction, snake_idx):
        """
        Moves the specified snake according to the game's rules dependent on the direction.
        Does not draw head and does not check for reward scenarios. See move_result for these
        functionalities.
        """

        snake = self.snakes[snake_idx]
        if type(snake) == type(None):
            return

        if direction >= 8:
            co = snake.step(snake.head, direction % 4)
            if self.grid.off_grid(co):
                return
            if np.array_equal(self.grid.color_of(co), self.grid.FOOD_COLORS[0]):
                self.grid.draw(co, self.grid.WALL_COLOR)
                self.douse.append(co)
                self.grid.aag.remove(co)
                # self.r[snake_idx] += 1

        elif direction >= 4:
            co = snake.step(snake.head, direction % 4)
            if self.grid.off_grid(co):
                return
            self.grid.draw(co, self.grid.WHITE)
            self.empty.append(co)
            # self.r[snake_idx] += 0.3

        else:
            # x1 = snake.head[0]
            # y1 = snake.head[1]
            # x2 = self.grid.gm[0]
            # y2 = self.grid.gm[1]
            #
            # if np.random.rand()<0.5:
            #     if (x1 < x2):
            #         direction = 1
            #     else:
            #         direction = 3
            # else:
            #     if (y1 < y2):
            #         direction = 2
            #     else:
            #         direction = 0

            co = snake.step(snake.head, direction % 4)
            if self.grid.off_grid(co) or np.array_equal(self.grid.color_of(co), self.grid.FOOD_COLORS[0]):
                return

            # if euclidean(snake.head, self.grid.gm) > euclidean(co, self.grid.gm):
            #     self.r[snake_idx] += 0.1
            # else:
                # self.r[snake_idx] -= 0.1

            # Cover old head position with body
            # if not snake.head in self.empty:
            self.grid.cover(snake.head, self.grid.BODY_COLOR)
            # else:
            #     self.grid.draw(snake.head, self.grid.WHITE)
            # Erase tail without popping so as to redraw if food eaten
            self.grid.erase(snake.body[0])
            # Find and set next head position conditioned on direction
            snake.action(direction)

    def move_result(self, direction, snake_idx=0):
        """
        Checks for food and death collisions after moving snake. Draws head of snake if
        no death scenarios.
        """

        if direction >= 4:
            return

        snake = self.snakes[snake_idx]
        if type(snake) == type(None):
            return 0

        co = snake.step(snake.head, direction)
        if self.grid.off_grid(co) or np.array_equal(self.grid.color_of(co), self.grid.FOOD_COLORS[0]):
            return

        # Check for death of snake
        # if False and self.grid.check_death(snake.head):
        #     self.dead_snakes[snake_idx] = self.snakes[snake_idx]
        #     self.snakes[snake_idx] = None
        #     self.grid.cover(snake.head, snake.head_color)  # Avoid miscount of grid.open_space
        #     if direction < 4:
        #         if len(snake.body)>1:
        #             try:
        #                 self.grid.connect(snake.body.popleft(), snake.body[0], self.grid.SPACE_COLOR)
        #             finally:
        #                 k=0
            # self.r[snake_idx] += -0.9
        # else:
        #     food_item = self.grid.food_space(snake.head)
        #
        #     # Check for wall
        #     if food_item == -2:
        #         self.dead_snakes[snake_idx] = self.snakes[snake_idx]
        #         self.snakes[snake_idx] = None
        #         self.grid.cover(snake.head, snake.head_color)  # Avoid miscount of grid.open_space
        #         self.grid.connect(snake.body.popleft(), snake.body[0], self.grid.SPACE_COLOR)
        #         reward = -1
        #
        #     # Check for reward
        #     elif food_item != -1:
        #         self.grid.draw(snake.body[0], self.grid.BODY_COLOR)  # Redraw tail
        #         self.grid.connect(snake.body[0], snake.body[1], self.grid.BODY_COLOR)
        #         self.grid.cover(snake.head, snake.head_color)  # Avoid miscount of grid.open_space
        #         reward = self.grid.FOOD_REWARDS[food_item]
        #         self.grid.new_food(food_item)

        # else:
        reward = 0
        empty_coord = snake.body.popleft()
        self.grid.connect(empty_coord, snake.body[0], self.grid.SPACE_COLOR)
        self.grid.draw(snake.head, snake.head_color)

        self.grid.connect(snake.body[-1], snake.head, self.grid.BODY_COLOR)

        # return reward

    def kill_snake(self, snake_idx):
        """
        Deletes snake from game and subtracts from the snake_count
        """
        return
        assert self.dead_snakes[snake_idx] is not None
        self.grid.erase(self.dead_snakes[snake_idx].head)
        self.grid.erase_snake_body(self.dead_snakes[snake_idx])
        self.dead_snakes[snake_idx] = None
        self.snakes_remaining -= 1

    def step(self, directions):
        """
        Takes an action for each snake in the specified direction and collects their rewards
        and dones.

        directions - tuple, list, or ndarray of directions corresponding to each snake.
        """

        self.r = [0., 0., 0., 0.]

        # Ensure no more play until reset
        if self.snakes_remaining < 1 or self.grid.open_space < 1:
            if len(directions) is 1:
                return self.grid.grid.copy(), 0, True, {"snakes_remaining": self.snakes_remaining}
            else:
                return self.grid.grid.copy(), [0] * len(directions), True, {"snakes_remaining": self.snakes_remaining}

        # remove when multiple agents

        # directions = int(directions)

        if type(directions) == type(int()):
            directions = [directions]

        for i, direction in enumerate(directions):

            if self.snakes[i] is None and self.dead_snakes[i] is not None:
                self.kill_snake(i)
            self.move_snake(direction, i)
            self.move_result(direction, i)

            snake = self.snakes[i]
            if snake is not None:
                for co in self.empty:
                    if not np.array_equal(snake.head, co):
                        self.grid.draw(co, self.grid.WHITE)

                for co in self.douse:
                    if not np.array_equal(snake.head, co):
                        self.grid.draw(co, self.grid.WALL_COLOR)

                self.grid.draw(snake.head, self.grid.HEAD_COLOR)

        self.grid.new_food(0)

        done = self.snakes_remaining < 1 # or self.grid.open_space < 1
        self.r[0] += -0.2
        # self.r[1] += -0.2
        if len(self.r) is 1:
            return self.grid.grid.copy(), self.r[0], done, {"snakes_remaining": self.snakes_remaining}
        else:
            return self.grid.grid.copy(), self.r, done, {"snakes_remaining": self.snakes_remaining}
