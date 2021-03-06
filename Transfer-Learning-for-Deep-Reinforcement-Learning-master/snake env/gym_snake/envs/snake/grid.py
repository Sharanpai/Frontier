import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.distance import euclidean



class Grid():
    """
    This class contains all data related to the grid in which the game is contained.
    The information is stored as a numpy array of pixels.
    The grid is treated as a cartesian [x,y] plane in which [0,0] is located at
    the upper left most pixel and [max_x, max_y] is located at the lower right most pixel.

    Note that it is assumed spaces that can kill a snake have a non-zero value as their 0 channel.
    It is also assumed that HEAD_COLOR has a 255 value as its 0 channel.
    """

    BODY_COLOR = np.array([0, 255, 0], dtype=np.uint8)
    HEAD_COLOR = np.array([0, 0, 255], dtype=np.uint8)
    # FOOD_COLOR = np.array([0,0,255], dtype=np.uint8)
    FOOD_COLORS = np.array([[255, 0, 0], [0, 0, 200], [0, 0, 180]], dtype=np.uint8)
    # FOOD_COLORS = np.array([[255, 128, 0], [255, 128, 128], [255, 128, 255]], dtype=np.uint8)
    FOOD_REWARDS = np.array([1, 2, 3], dtype=np.uint8)
    SPACE_COLOR = np.array([0, 255, 0], dtype=np.uint8)
    WALL_COLOR = np.array([1, 0, 0], dtype=np.uint8)
    WHITE = np.array([255, 255, 255], dtype=np.uint8)

    def __init__(self, grid_size=[30, 30], unit_size=10, unit_gap=1):
        """
        grid_size - tuple, list, or ndarray specifying number of atomic units in
                    both the x and y direction
        unit_size - integer denoting the atomic size of grid units in pixels
        """

        self.unit_size = int(unit_size)
        self.unit_gap = unit_gap
        self.grid_size = np.asarray(grid_size, dtype=np.int)  # size in terms of units
        height = self.grid_size[1] * self.unit_size
        width = self.grid_size[0] * self.unit_size
        channels = 3
        self.gm = (height/2, width/2)
        self.grid = np.zeros((height, width, channels), dtype=np.uint8)
        self.grid[:, :, :] = self.SPACE_COLOR
        self.open_space = grid_size[0] * grid_size[1]
        self.aag = []

    def check_death(self, head_coord):
        """
        Checks the grid to see if argued head_coord has collided with a death space (i.e. snake or wall)

        head_coord - x,y integer coordinates as a tuple, list, or ndarray
        """
        return self.off_grid(head_coord) or self.snake_space(head_coord)

    def color_of(self, coord):
        """
        Returns the color of the specified coordinate

        coord - x,y integer coordinates as a tuple, list, or ndarray
        """

        return self.grid[int(coord[1] * self.unit_size), int(coord[0] * self.unit_size), :]

    def connect(self, coord1, coord2, color=BODY_COLOR):
        """
        Draws connection between two adjacent pieces using the specified color.
        Created to indicate the relative ordering of the snake's body.
        coord1 and coord2 must be adjacent.

        coord1 - x,y integer coordinates as a tuple, list, or ndarray
        coord2 - x,y integer coordinates as a tuple, list, or ndarray
        color - [R,G,B] values as a tuple, list, or ndarray
        """

        # Check for adjacency
        # Next to one another:
        adjacency1 = (np.abs(coord1[0] - coord2[0]) == 1 and np.abs(coord1[1] - coord2[1]) == 0)
        # Stacked on one another:
        adjacency2 = (np.abs(coord1[0] - coord2[0]) == 0 and np.abs(coord1[1] - coord2[1]) == 1)
        assert adjacency1 or adjacency2

        if adjacency1:  # x values differ
            min_x, max_x = sorted([coord1[0], coord2[0]])
            min_x = min_x * self.unit_size + self.unit_size - self.unit_gap
            max_x = max_x * self.unit_size
            self.grid[coord1[1] * self.unit_size, min_x:max_x, :] = color
            self.grid[coord1[1] * self.unit_size + self.unit_size - self.unit_gap - 1, min_x:max_x, :] = color
        else:  # y values differ
            min_y, max_y = sorted([coord1[1], coord2[1]])
            min_y = min_y * self.unit_size + self.unit_size - self.unit_gap
            max_y = max_y * self.unit_size
            self.grid[min_y:max_y, coord1[0] * self.unit_size, :] = color
            self.grid[min_y:max_y, coord1[0] * self.unit_size + self.unit_size - self.unit_gap - 1, :] = color

    def cover(self, coord, color):
        """
        Colors a single space on the grid. Use erase if creating an empty space on the grid.
        This function is used like draw but without affecting the open_space count.

        coord - x,y integer coordinates as a tuple, list, or ndarray
        color - [R,G,B] values as a tuple, list, or ndarray
        """

        if self.off_grid(coord):
            return False
        x = int(coord[0] * self.unit_size)
        end_x = x + self.unit_size - self.unit_gap
        y = int(coord[1] * self.unit_size)
        end_y = y + self.unit_size - self.unit_gap
        self.grid[y:end_y, x:end_x, :] = np.asarray(color, dtype=np.uint8)
        return True

    def draw(self, coord, color):
        """
        Colors a single space on the grid. Use erase if creating an empty space on the grid.
        Affects the open_space count.

        coord - x,y integer coordinates as a tuple, list, or ndarray
        color - [R,G,B] values as a tuple, list, or ndarray
        """

        if self.cover(coord, color):
            self.open_space -= 1
            return True
        else:
            return False

    def draw_snake(self, snake, head_color=HEAD_COLOR):
        """
        Draws a snake with the given head color.

        snake - Snake object
        head_color - [R,G,B] values as a tuple, list, or ndarray
        """

        self.draw(snake.head, head_color)
        prev_coord = None
        for i in range(len(snake.body)):
            coord = snake.body.popleft()
            self.draw(coord, self.BODY_COLOR)
            if prev_coord is not None:
                self.connect(prev_coord, coord, self.BODY_COLOR)
            snake.body.append(coord)
            prev_coord = coord
        self.connect(prev_coord, snake.head, self.BODY_COLOR)

    def erase(self, coord):
        """
        Colors the entire coordinate with SPACE_COLOR to erase potential
        connection lines.

        coord - (x,y) as tuple, list, or ndarray
        """
        if self.off_grid(coord):
            return False
        self.open_space += 1
        x = int(coord[0] * self.unit_size)
        end_x = x + self.unit_size
        y = int(coord[1] * self.unit_size)
        end_y = y + self.unit_size
        self.grid[y:end_y, x:end_x, :] = self.SPACE_COLOR
        return True

    def erase_connections(self, coord):
        """
        Colors the dead space of the given coordinate with SPACE_COLOR to erase potential
        connection lines

        coord - (x,y) as tuple, list, or ndarray
        """

        if self.off_grid(coord):
            return False
        # Erase Horizontal Row Below Coord
        x = int(coord[0] * self.unit_size)
        end_x = x + self.unit_size
        y = int(coord[1] * self.unit_size) + self.unit_size - self.unit_gap
        end_y = y + self.unit_gap
        self.grid[y:end_y, x:end_x, :] = self.SPACE_COLOR

        # Erase the Vertical Column to Right of Coord
        x = int(coord[0] * self.unit_size) + self.unit_size - self.unit_gap
        end_x = x + self.unit_gap
        y = int(coord[1] * self.unit_size)
        end_y = y + self.unit_size
        self.grid[y:end_y, x:end_x, :] = self.SPACE_COLOR

        return True

    def erase_snake_body(self, snake):
        """
        Removes the argued snake's body and head from the grid.

        snake - Snake object
        """

        for i in range(len(snake.body)):
            self.erase(snake.body.popleft())

    def food_space(self, coord):
        """
        Checks if argued coord is snake food

        coord - x,y integer coordinates as a tuple, list, or ndarray
        """

        color = self.color_of(coord)
        if np.array_equal(color, self.WALL_COLOR):
            return -2

        for i in range(len(self.FOOD_COLORS)):
            if np.array_equal(color, self.FOOD_COLORS[i]):
                return i
        return -1

        # return np.array_equal(self.color_of(coord), self.FOOD_COLOR)

    def place_food(self, coord):
        """
        Draws a food at the coord. Ensures the same placement for
        each food at the beginning of a new episode. This is useful for
        experimentation with curiosity driven behaviors.

        num - the integer denoting the
        """
        if self.open_space < 1 or not np.array_equal(self.color_of(coord), self.SPACE_COLOR):
            return False
        self.draw(coord, self.FOOD_COLOR)
        return True

    def init_fire(self):
        coord = (self.grid_size[0] / 2, self.grid_size[1] / 2)
        self.aag.append(coord)
        self.draw(coord, self.FOOD_COLORS[0])

        coord = (self.grid_size[0] / 2 + 1, self.grid_size[1] / 2)
        self.aag.append(coord)
        self.draw(coord, self.FOOD_COLORS[0])

        coord = (self.grid_size[0] / 2 + 1, self.grid_size[1] / 2 + 1)
        self.aag.append(coord)
        self.draw(coord, self.FOOD_COLORS[0])

        coord = (self.grid_size[0] / 2, self.grid_size[1] / 2 + 1)
        self.aag.append(coord)
        self.draw(coord, self.FOOD_COLORS[0])

        coord = (self.grid_size[0] / 2 + 2, self.grid_size[1] / 2 + 1)
        self.aag.append(coord)
        self.draw(coord, self.FOOD_COLORS[0])

        return True

    def new_food(self, i):
        """
        Draws a food on a random, open unit of the grid.
        Returns true if space left. Otherwise returns false.
        """

        # if self.open_space < 1:
        #     return False
        # coord_not_found = True
        # while (coord_not_found):
        #     coord = (np.random.randint(0, self.grid_size[0]), np.random.randint(0, self.grid_size[1]))
        #     if np.array_equal(self.color_of(coord), self.SPACE_COLOR):
        #         coord_not_found = False

        na = list(ConvexHull(self.aag).points)

        distance = euclidean

        self.gm = \
        min(map(lambda p1: (p1, sum(map(lambda p2: distance(p1, p2), na))), na), key=lambda x: x[1])[0]

        coord_not_found = True

        while coord_not_found:
            spi = np.random.randint(0, len(na))
            sp = na[spi]
            dir = [[0, 1], [0, -1], [1, 0], [-1, 0]]

            for _ in range(4):
                diri = np.random.randint(0, len(dir))

                coord = (sp[0] + dir[diri][0], sp[1] + dir[diri][1])
                if not self.off_grid(coord):
                    o, p = self.color_of(coord), self.SPACE_COLOR
                    if np.array_equal(self.color_of(coord), self.SPACE_COLOR):
                        coord_not_found = False
                        self.draw(coord, self.FOOD_COLORS[0])
                        self.aag.append(coord)
                        return True

                dir.remove(dir[diri])
            na.pop(spi)

    def create_wall(self):

        if self.open_space < 1:
            return False
        coord_not_found = True
        while (coord_not_found):
            coord = (np.random.randint(0, self.grid_size[0]), np.random.randint(0, self.grid_size[1]))
            if np.array_equal(self.color_of(coord), self.SPACE_COLOR):
                coord_not_found = False
                self.draw(coord, self.WALL_COLOR)
        return True

        # center_coord = [self.grid_size[0] // 2, self.grid_size[1] // 2]
        # if self.open_space < 1:
        #     return False
        #
        # self.draw(center_coord, self.WALL_COLOR)
        #
        # self.draw(center_coord + np.array([0, 1]), self.WALL_COLOR)
        # self.draw(center_coord + np.array([0, 2]), self.WALL_COLOR)
        #
        # self.draw(center_coord + np.array([0, -1]), self.WALL_COLOR)
        # self.draw(center_coord + np.array([0, -2]), self.WALL_COLOR)
        #
        # self.draw(center_coord + np.array([1, 0]), self.WALL_COLOR)
        # self.draw(center_coord + np.array([2, 0]), self.WALL_COLOR)
        #
        # self.draw(center_coord + np.array([-1, 0]), self.WALL_COLOR)
        # self.draw(center_coord + np.array([-2, 0]), self.WALL_COLOR)
        #
        # return True

    def off_grid(self, coord):
        """
        Checks if argued coord is off of the grid

        coord - x,y integer coordinates as a tuple, list, or ndarray
        """

        r = coord[0] < 0 or coord[0] >= self.grid_size[0] or coord[1] < 0 or coord[1] >= self.grid_size[1]
        return r

    def snake_space(self, coord):
        """
        Checks if argued coord is occupied by a snake

        coord - x,y integer coordinates as a tuple, list, or ndarray
        """

        color = self.color_of(coord)
        return np.array_equal(color, self.HEAD_COLOR)  # or color[0] == self.HEAD_COLOR[0]
