from collections import OrderedDict
import random
import re
from pygame import Rect
import pygame
import numpy as np

WINDOW_WIDTH, WINDOW_HEIGHT = 500, 601
GRID_WIDTH, GRID_HEIGHT = 300, 600
TILE_SIZE = 30
LEVEL_SPEEDS = [800, 600, 450, 300, 200]  # Speeds for each level
LINES_PER_LEVEL = 10

class BottomReached(Exception):
    """Exception raised when a block reaches the bottom."""
    pass

class TopReached(Exception):
    """Exception raised when a block reaches the top."""
    pass

class Block(pygame.sprite.Sprite):
    """
    Base class for different types of blocks in Tetris.
    """

    COLORS = {
        "SquareBlock": (255, 255, 0),  # Yellow
        "TBlock": (128, 0, 128),       # Purple 
        "LineBlock": (0, 255, 255),    # Cyan
        "LBlock": (255, 127, 0),       # Orange
        "ZBlock": (255, 0, 0),         # Red
        "ReverseLBlock": (0, 0, 255),  # Blue
        "ReverseZBlock": (0, 255, 0)   # Green
    }

    @staticmethod
    def collide(block, group):
        """
        Check if the specified block collides with some other block
        in the group.
        """
        for other_block in group:
            # Ignore the current block which will always collide with itself.
            if block == other_block:
                continue
            if pygame.sprite.collide_mask(block, other_block) is not None:
                return True
        return False

    def __init__(self):
        """
        Initialize a block with a random rotation and flip.
        """
        super().__init__()
        self.current = True
        self.struct = np.array(self.struct)

        # Get the color associated with the block type
        class_name = re.search(r"<class '__main__\.([^']+)'>", str(type(self))).group(1)
        self.color = Block.COLORS[class_name]

        # Initial random rotation and flip.
        if random.randint(0, 1):
            self.struct = np.rot90(self.struct)
        if random.randint(0, 1):
            # Flip in the X axis.
            self.struct = np.flip(self.struct, 0)
        self._draw()

    def _draw(self, x=4, y=0):
        """
        Draw the block's structure on the image surface.
        """
        # Calculate the width and height based on the structure
        width = len(self.struct[0]) * TILE_SIZE
        height = len(self.struct) * TILE_SIZE

        # Create a new surface for the image
        self.image = pygame.surface.Surface([width, height])
        self.image.set_colorkey((0, 0, 0))

        # Set the position and size
        self.rect = self._create_rect(0, 0, width, height)
        self.x = x
        self.y = y

        # Draw the structure on the image
        for y, row in enumerate(self.struct):
            for x, col in enumerate(row):
                if col:
                    rect = self._create_rect(x*TILE_SIZE + 1, y*TILE_SIZE + 1,
                                            TILE_SIZE - 2, TILE_SIZE - 2)
                    pygame.draw.rect(self.image, self.color, rect)

        # Create a mask for the image
        self._create_mask()

    def _create_rect(self, x, y, width, height):
        return Rect(x, y, width, height)

    def redraw(self):
        """
        Redraw the block at its current position.
        """
        self._draw(self.x, self.y)

    def _create_mask(self):
        """
        Create the mask attribute from the main surface.
        The mask is required to check collisions. This should be called
        after the surface is created or updated.
        """
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def group(self):
        """
        Get the sprite group to which the block belongs.
        """
        return self.groups()[0]

    @property
    def x(self):
        """
        Get the x-coordinate of the block.
        """
        return self._x

    @x.setter
    def x(self, value):
        """
        Set the x-coordinate of the block and update the rect's left attribute.
        """
        self._x = value
        self.rect.left = value*TILE_SIZE

    @property
    def y(self):
        """
        Get the y-coordinate of the block.
        """
        return self._y

    @y.setter
    def y(self, value):
        """
        Set the y-coordinate of the block and update the rect's top attribute.
        """
        self._y = value
        self.rect.top = value*TILE_SIZE

    def move(self, dx, dy, group):
        """
        Move the block by the specified increments (dx, dy) and check for collisions.
        """
        self.x += dx
        self.y += dy
        if self._is_collision(group) or self._is_out_of_bounds():
            self.x -= dx
            self.y -= dy
            if dy > 0:  # Moving down
                self.current = False
                raise BottomReached

    def _is_collision(self, group):
        """
        Check if the block collides with another block in the group.
        """
        return Block.collide(self, group)

    def _is_out_of_bounds(self):
        """
        Check if the block is out of bounds.
        """
        return (self.rect.right > GRID_WIDTH or 
                self.rect.left < 0 or 
                self.rect.bottom > GRID_HEIGHT)

    def rotate(self, group):
        """
        Rotate the block and adjust its position to avoid collisions and stay within bounds.
        """
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()
        self._create_mask()
        while self._is_out_of_bounds() or self._is_collision(group):
            if self.rect.right > GRID_WIDTH:
                self.x -= 1
            elif self.rect.left < 0:
                self.x += 1
            elif self.rect.bottom > GRID_HEIGHT:
                self.y -= 1
        self.struct = np.rot90(self.struct)

    def move_left(self, group):
        """
        Move the block to the left within the group.
        """
        self.move(-1, 0, group)

    def move_right(self, group):
        """
        Move the block to the right within the group.
        """
        self.move(1, 0, group)

    def move_down(self, group):
        """
        Move the block downward within the group.
        """
        self.move(0, 1, group)

    def update(self):
        """
        Update the block's position if it is the current block.
        """
        if self.current:
            self.move_down()

class SquareBlock(Block):
    """
    Class for the square-shaped block in Tetris.
    """
    struct = (
        (1, 1),
        (1, 1)
    )

class TBlock(Block):
    """
    Class for the T-shaped block in Tetris.
    """
    struct = (
        (1, 1, 1),
        (0, 1, 0)
    )

class LineBlock(Block):
    """
    Class for the line-shaped block in Tetris.
    """
    struct = (
        (1,),
        (1,),
        (1,),
        (1,)
    )

class LBlock(Block):
    """
    Class for the L-shaped block in Tetris.
    """
    struct = (
        (1, 1),
        (1, 0),
        (1, 0),
    )

class ZBlock(Block):
    """
    Class for the Z-shaped block in Tetris.
    """
    struct = (
        (0, 1),
        (1, 1),
        (1, 0),
    )

class ReverseLBlock(Block):
    """
    Class for the reverse L-shaped block in Tetris.
    """
    struct = (
        (1, 1),
        (0, 1),
        (0, 1),
    )

class ReverseZBlock(Block):
    """
    Class for the reverse Z-shaped block in Tetris.
    """
    struct = (
        (1, 0),
        (1, 1),
        (0, 1),
    )

class BlocksGroup(pygame.sprite.OrderedUpdates):
    """
    Class representing a group of blocks in Tetris.
    """

    @staticmethod
    def get_random_block():
        """
        Get a randomly chosen block type.
        """
        return random.choice(
            (SquareBlock, TBlock, LineBlock, LBlock, ZBlock, ReverseLBlock, ReverseZBlock))()

    def __init__(self, *args, **kwargs):
        """
        Initialize the BlocksGroup with grid setup and initial block creation.
        """
        super().__init__(*args, **kwargs)
        self._reset_grid()
        self._ignore_next_stop = False
        self.score = 0
        self.next_block = None
        self.level = 1
        self.lines_completed = 0
        self.speed = LEVEL_SPEEDS[self.level - 1]
        pygame.time.set_timer(pygame.USEREVENT + 1, self.speed)
        self._current_block_movement_heading = None
        self._create_new_block()

    def _check_line_completion(self):
        """
        Check each line of the grid and remove the ones that
        are complete.
        """
        # Start checking from the bottom.
        for i, row in enumerate(self.grid[::-1]):
            if all(row):
                self.score += 5
                # Increment the lines completed counter
                self.lines_completed += 1

                # Get the blocks affected by the line deletion and
                # remove duplicates.
                affected_blocks = list(OrderedDict.fromkeys(self.grid[-1 - i]))

                for block, y_offset in affected_blocks:
                    # Remove the block tiles which belong to the
                    # completed line.
                    block.struct = np.delete(block.struct, y_offset, 0)
                    if block.struct.any():
                        # Once removed, check if we have empty columns
                        # since they need to be dropped.
                        block.struct, x_offset = del_empty_columns(block.struct)
                        # Compensate the space gone with the columns to
                        # keep the block's original position.
                        block.x += x_offset
                        # Force update.
                        block.redraw()
                    else:
                        # If the struct is empty then the block is gone.
                        self.remove(block)

                # Check if enough lines have been completed to change the level
                if self.lines_completed >= LINES_PER_LEVEL:
                    self.lines_completed = 0
                    self.level += 1
                    self.speed = LEVEL_SPEEDS[self.level - 1]
                    pygame.time.set_timer(pygame.USEREVENT + 1, self.speed)
                    print(f"Level {self.level}")

                # Instead of checking which blocks need to be moved
                # once a line was completed, just try to move all of
                # them.
                for block in self:
                    # Except the current block.
                    if block.current:
                        continue
                    # Pull down each block until it reaches the
                    # bottom or collides with another block.
                    while True:
                        try:
                            block.move_down(self)
                        except BottomReached:
                            break

                self.update_grid()
                # Since we've updated the grid, now the i counter
                # is no longer valid, so call the function again
                # to check if there're other completed lines in the
                # new grid.
                self._check_line_completion()
                break

    def _reset_grid(self):
        """
        Reset the grid to an empty state.
        """
        self.grid = [[0 for _ in range(10)] for _ in range(20)]

    def _create_new_block(self):
        """
        Create a new block and add it to the group.
        """
        new_block = self.next_block or BlocksGroup.get_random_block()
        if Block.collide(new_block, self):
            raise TopReached
        self.add(new_block)
        self.next_block = BlocksGroup.get_random_block()
        self.update_grid()
        self._check_line_completion()
        self.speed = LEVEL_SPEEDS[self.level - 1]
        pygame.time.set_timer(pygame.USEREVENT + 1, self.speed)

    def update_grid(self):
        """
        Update the grid representation based on the blocks in the group.
        """
        self._reset_grid()
        for block in self:
            for y_offset, row in enumerate(block.struct):
                for x_offset, digit in enumerate(row):
                    # Prevent replacing previous blocks.
                    if digit == 0:
                        continue
                    rowid = block.y + y_offset
                    colid = block.x + x_offset
                    self.grid[rowid][colid] = (block, y_offset)

    @property
    def current_block(self):
        """
        Get the current block in the group.
        """
        return self.sprites()[-1]

    def update_current_block(self):
        """
        Update the position of the current block.
        """
        try:
            self.current_block.move_down(self)
        except BottomReached:
            self.stop_moving_current_block()
            self._create_new_block()
        else:
            self.update_grid()

    def move_current_block(self):
        """Move the current block based on the user's input."""
        if self._current_block_movement_heading is None:
            return
        action = {
            pygame.K_DOWN: self.current_block.move_down,
            pygame.K_LEFT: self.current_block.move_left,
            pygame.K_RIGHT: self.current_block.move_right
        }
        try:
            action[self._current_block_movement_heading](self)
        except BottomReached:
            self.stop_moving_current_block()
            self._create_new_block()
        else:
            self.update_grid()

    def start_moving_current_block(self, key):
        """Start moving the current block in the specified direction."""
        if self._current_block_movement_heading is not None:
            self._ignore_next_stop = True
        self._current_block_movement_heading = key

    def stop_moving_current_block(self):
        """Stop the movement of the current block."""
        if self._ignore_next_stop:
            self._ignore_next_stop = False
        else:
            self._current_block_movement_heading = None

    def rotate_current_block(self):
        """Rotate the current block if it is not a SquareBlock."""
        if not isinstance(self.current_block, SquareBlock):
            self.current_block.rotate(self)
            self.update_grid()

def del_empty_columns(arr, _x_offset=0, _keep_counting=True):
    """
    Remove empty columns from arr (i.e. those filled with zeros).
    The return value is (new_arr, x_offset), where x_offset is how
    much the x coordinate needs to be increased to maintain
    the block's original position.
    """
    for colid, col in enumerate(arr.T):
        if col.max() == 0:
            if _keep_counting:
                _x_offset += 1
            # Remove the current column and try again.
            arr, _x_offset = del_empty_columns(
                np.delete(arr, colid, 1), _x_offset, _keep_counting)
            break
        else:
            _keep_counting = False
    return arr, _x_offset

def draw_grid(background):
    """Draw the background grid on the given surface."""
    grid_color = 50, 50, 50
    for i in range(11):
        x = TILE_SIZE * i
        pygame.draw.line(
            background, grid_color, (x, 0), (x, GRID_HEIGHT)
        )
    for i in range(21):
        y = TILE_SIZE * i
        pygame.draw.line(
            background, grid_color, (0, y), (GRID_WIDTH, y)
        )

def draw_centered_surface(screen, surface, y):
    """Draw a surface centered on the screen at the specified y-coordinate."""
    screen.blit(surface, (400 - surface.get_width() / 2, y))

def main():
    """Initialize and run the Tetris game."""
    pygame.init()
    pygame.display.set_caption("Tetris by Cnel")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    run = True
    paused = False
    game_over = False

    background = pygame.Surface(screen.get_size())
    bgcolor = (0, 0, 0)
    background.fill(bgcolor)
    draw_grid(background)
    background = background.convert()

    def render_text(font, text, color, bgcolor):
        """Render text with the specified font, text, color, and background color."""
        return font.render(text, True, color, bgcolor)

    try:
        font = pygame.font.Font("Roboto-Regular.ttf", 20)
    except OSError:
        font = pygame.font.Font(None, 20)

    next_block_text = render_text(font, "Next block:", (255, 255, 255), bgcolor)
    score_msg_text = render_text(font, "Score:", (255, 255, 255), bgcolor)
    game_over_text = render_text(font, "Game over!", (255, 220, 0), bgcolor)

    MOVEMENT_KEYS = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN
    EVENT_UPDATE_CURRENT_BLOCK = pygame.USEREVENT + 1
    EVENT_MOVE_CURRENT_BLOCK = pygame.USEREVENT + 2
    pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, LEVEL_SPEEDS[0])
    pygame.time.set_timer(EVENT_MOVE_CURRENT_BLOCK, 100)

    blocks = BlocksGroup()

    def handle_event(event, blocks, game_over, paused):
        """Handle the various events during the game."""
        if event.type == pygame.QUIT:
            return False, game_over, paused

        if event.type == pygame.KEYUP:
            handle_keyup_event(event, blocks, game_over, paused)
        elif event.type == pygame.KEYDOWN and not (game_over or paused):
            handle_keydown_event(event, blocks)
        elif event.type == pygame.USEREVENT + 1:
            blocks.update_current_block()

        try:
            handle_block_events(event, blocks)
        except TopReached:
            game_over = True

        return True, game_over, paused

    def handle_keyup_event(event, blocks, game_over, paused):
        """Handle the KEYUP event during the game."""
        if not paused and not game_over:
            if event.key in MOVEMENT_KEYS:
                blocks.stop_moving_current_block()
            elif event.key == pygame.K_UP:
                blocks.rotate_current_block()

        if event.key == pygame.K_p:
            paused = not paused

    def handle_keydown_event(event, blocks):
        """Handle the KEYDOWN event during the game."""
        if event.key in MOVEMENT_KEYS:
            blocks.start_moving_current_block(event.key)

    def handle_block_events(event, blocks):
        """Handle events related to the game blocks."""
        if event.type == EVENT_UPDATE_CURRENT_BLOCK:
            blocks.update_current_block()
        elif event.type == EVENT_MOVE_CURRENT_BLOCK:
            blocks.move_current_block()

    def draw_screen(screen, background, blocks, next_block_text, score_msg_text, game_over_text, font, bgcolor, game_over):
        """Draw the game screen with relevant information."""
        screen.blit(background, (0, 0))
        blocks.draw(screen)
        draw_centered_surface(screen, next_block_text, 50)
        draw_centered_surface(screen, blocks.next_block.image, 100)
        draw_centered_surface(screen, score_msg_text, 240)
        score_text = font.render(f"Score: {blocks.score}", True, (255, 255, 255), bgcolor)
        draw_centered_surface(screen, score_text, 270)
        level_text = font.render(f"Level: {blocks.level}", True, (255, 255, 255), bgcolor)
        draw_centered_surface(screen, level_text, 300)
        if game_over:
            draw_centered_surface(screen, game_over_text, 360)
        pygame.display.flip()

    while run:
        for event in pygame.event.get():
            run, game_over, paused = handle_event(event, blocks, game_over, paused)
            if not run:
                break
        if run:
            draw_screen(screen, background, blocks, next_block_text, score_msg_text, game_over_text, font, bgcolor, game_over)
    pygame.quit()

if __name__ == "__main__":
    main()
