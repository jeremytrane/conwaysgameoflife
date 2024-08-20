import pygame
import numpy as np

# Set up the constants
CELL_SIZE = 10
GRID_WIDTH = 800
GRID_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Calculate the number of cells in the grid
cols = GRID_WIDTH // CELL_SIZE
rows = GRID_HEIGHT // CELL_SIZE

# Initialize the grid with all dead cells
grid = np.zeros((rows, cols), dtype=int)

# Button class to handle drawing and interaction
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
    grid[row, col] = state

def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT + 50))
    pygame.display.set_caption('Conway\'s Game of Life')
    clock = pygame.time.Clock()

    start_button = Button("Start", 10, GRID_HEIGHT + 10, 100, 30, GREEN, WHITE)
    pause_button = Button("Pause", 120, GRID_HEIGHT + 10, 100, 30, BLUE, WHITE)
    stop_button = Button("Stop", 230, GRID_HEIGHT + 10, 100, 30, RED, WHITE)
    
    running = True
    game_started = False
    game_paused = False
    left_mouse_held = False
    right_mouse_held = False
    iteration_count = 0
    global grid

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button pressed
                    left_mouse_held = True
                    if start_button.is_clicked(event.pos):
                        game_started = True
                        game_paused = False
                    elif pause_button.is_clicked(event.pos) and game_started:
                        game_paused = not game_paused
                    elif stop_button.is_clicked(event.pos):
                        game_started = False
                        game_paused = False
                        iteration_count = 0
                        grid = np.zeros((rows, cols), dtype=int)
                    elif not game_started:
                        modify_cell(grid, pygame.mouse.get_pos(), 1)  # Draw cell
                elif event.button == 3:  # Right mouse button pressed
                    right_mouse_held = True
                    if not game_started:
                        modify_cell(grid, pygame.mouse.get_pos(), 0)  # Erase cell
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    left_mouse_held = False
                elif event.button == 3:  # Right mouse button released
                    right_mouse_held = False

        if left_mouse_held and not game_started:
            modify_cell(grid, pygame.mouse.get_pos(), 1)  # Draw cell

        if right_mouse_held and not game_started:
            modify_cell(grid, pygame.mouse.get_pos(), 0)  # Erase cell

        if game_started and not game_paused:
            grid = update_grid(grid)
            iteration_count += 1

        screen.fill(WHITE)
        draw_grid(screen, grid)
        start_button.draw(screen)
        pause_button.draw(screen)
        stop_button.draw(screen)

        # Display the iteration count
        font = pygame.font.Font(None, 36)
        iteration_text = font.render(f"Iterations: {iteration_count}", True, BLACK)
        screen.blit(iteration_text, (350, GRID_HEIGHT + 10))

        pygame.display.flip()
        clock.tick(10)  # 10 frames per second

    pygame.quit()

if __name__ == '__main__':
    main()
