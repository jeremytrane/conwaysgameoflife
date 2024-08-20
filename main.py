import pygame
import numpy as np

# Set up the constants
CELL_SIZE = 10
MIN_CELL_SIZE = 5
MAX_CELL_SIZE = 50
GRID_WIDTH = 800
GRID_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Slider class to adjust speed
class Slider:
    def __init__(self, x, y, width, min_val, max_val, start_val, color):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.color = color
        self.handle_rect = pygame.Rect(x + (start_val - min_val) / (max_val - min_val) * width - 5, y - 5, 10, 30)
        self.dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        pygame.draw.rect(screen, self.color, self.handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
                self.handle_rect.x = new_x - 5
                self.val = self.min_val + (self.handle_rect.x - self.rect.x) / self.rect.width * (self.max_val - self.min_val)

    def get_value(self):
        return self.val

def create_grid(rows, cols):
    return np.zeros((rows, cols), dtype=int)

def calculate_grid_dimensions():
    cols = GRID_WIDTH // CELL_SIZE
    rows = GRID_HEIGHT // CELL_SIZE
    return rows, cols

def resize_grid(old_grid, old_cell_size, new_cell_size):
    old_rows, old_cols = old_grid.shape
    new_rows = GRID_HEIGHT // new_cell_size
    new_cols = GRID_WIDTH // new_cell_size
    new_grid = np.zeros((new_rows, new_cols), dtype=int)

    scale_factor = new_cell_size / old_cell_size

    for row in range(old_rows):
        for col in range(old_cols):
            if old_grid[row, col] == 1:
                new_row = int(row * scale_factor)
                new_col = int(col * scale_factor)
                if new_row < new_rows and new_col < new_cols:
                    new_grid[new_row, new_col] = 1

    return new_grid

rows, cols = calculate_grid_dimensions()
grid = create_grid(rows, cols)

class Button:
    def __init__(self, text, x, y, width, height, color, text_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def update_grid(grid):
    new_grid = grid.copy()
    for row in range(rows):
        for col in range(cols):
            live_neighbors = np.sum(grid[row-1:row+2, col-1:col+2]) - grid[row, col]
            if grid[row, col] == 1:  # Live cell
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[row, col] = 0
            else:  # Dead cell
                if live_neighbors == 3:
                    new_grid[row, col] = 1
    return new_grid

def draw_grid(screen, grid):
    for row in range(rows):
        for col in range(cols):
            color = BLACK if grid[row, col] == 1 else WHITE
            pygame.draw.rect(screen, color, (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, GRAY, (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)  # Draw grid lines

def modify_cell(grid, pos, state):
    col = pos[0] // CELL_SIZE
    row = pos[1] // CELL_SIZE
    if 0 <= row < rows and 0 <= col < cols:  # Ensure we're within the grid boundaries
        grid[row, col] = state

def interpolate_cells(grid, start_pos, end_pos, state):
    x1, y1 = start_pos[0] // CELL_SIZE, start_pos[1] // CELL_SIZE
    x2, y2 = end_pos[0] // CELL_SIZE, end_pos[1] // CELL_SIZE
    if x1 == x2 and y1 == y2:
        modify_cell(grid, end_pos, state)
    else:
        steps = max(abs(x2 - x1), abs(y2 - y1))
        for i in range(steps + 1):
            x = x1 + (x2 - x1) * i // steps
            y = y1 + (y2 - y1) * i // steps
            modify_cell(grid, (x * CELL_SIZE, y * CELL_SIZE), state)

def main():
    global CELL_SIZE, rows, cols, grid

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT + 100))
    pygame.display.set_caption('Conway\'s Game of Life')
    clock = pygame.time.Clock()

    start_button = Button("Start", 10, GRID_HEIGHT + 10, 100, 30, GREEN, WHITE)
    pause_button = Button("Pause", 120, GRID_HEIGHT + 10, 100, 30, BLUE, WHITE)
    stop_button = Button("Stop", 230, GRID_HEIGHT + 10, 100, 30, RED, WHITE)
    
    # Slider for speed adjustment
    speed_slider = Slider(350, GRID_HEIGHT + 10, 200, 1, 30, 10, BLACK)
    
    running = True
    game_started = False
    game_paused = False
    left_mouse_held = False
    right_mouse_held = False
    last_mouse_pos = None
    iteration_count = 0

    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button pressed
                    left_mouse_held = True
                    last_mouse_pos = mouse_pos
                    if start_button.is_clicked(event.pos):
                        game_started = True
                        game_paused = False
                    elif pause_button.is_clicked(event.pos) and game_started:
                        game_paused = not game_paused
                    elif stop_button.is_clicked(event.pos):
                        game_started = False
                        game_paused = False
                        iteration_count = 0
                        grid = create_grid(rows, cols)
                    elif not game_started:
                        modify_cell(grid, mouse_pos, 1)  # Draw cell
                elif event.button == 3:  # Right mouse button pressed
                    right_mouse_held = True
                    last_mouse_pos = mouse_pos
                    if not game_started:
                        modify_cell(grid, mouse_pos, 0)  # Erase cell
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    left_mouse_held = False
                elif event.button == 3:  # Right mouse button released
                    right_mouse_held = False

            # Handle the slider event
            speed_slider.handle_event(event)

        if left_mouse_held and not game_started:
            interpolate_cells(grid, last_mouse_pos, mouse_pos, 1)  # Draw cells
            last_mouse_pos = mouse_pos

        if right_mouse_held and not game_started:
            interpolate_cells(grid, last_mouse_pos, mouse_pos, 0)  # Erase cells
            last_mouse_pos = mouse_pos

        if game_started and not game_paused:
            grid = update_grid(grid)
            iteration_count += 1

        screen.fill(WHITE)
        draw_grid(screen, grid)
        start_button.draw(screen)
        pause_button.draw(screen)
        stop_button.draw(screen)
        speed_slider.draw(screen)

        # Display the iteration count
        font = pygame.font.Font(None, 36)
        iteration_text = font.render(f"Iterations: {iteration_count}", True, BLACK)
        screen.blit(iteration_text, (600, GRID_HEIGHT + 10))

        pygame.display.flip()
        clock.tick(speed_slider.get_value())  # Use the slider value to adjust the speed

    pygame.quit()

if __name__ == '__main__':
    main()
