import pygame
import numpy as np

# Set up the constants
CELL_SIZE = 10
GRID_WIDTH = 800
GRID_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Calculate the number of cells in the grid
cols = GRID_WIDTH // CELL_SIZE
rows = GRID_HEIGHT // CELL_SIZE

# Initialize the grid with random states
grid = np.random.randint(2, size=(rows, cols))

def update_grid(grid):
    # Create a copy of the grid to hold the new state
    new_grid = grid.copy()
    for row in range(rows):
        for col in range(cols):
            # Count the number of live neighbors
            live_neighbors = np.sum(grid[row-1:row+2, col-1:col+2]) - grid[row, col]
            
            # Apply the rules of the Game of Life
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
            color = WHITE if grid[row, col] == 1 else BLACK
            pygame.draw.rect(screen, color, (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
    pygame.display.set_caption('Conway\'s Game of Life')
    clock = pygame.time.Clock()
    
    running = True
    global grid

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update the grid state
        grid = update_grid(grid)
        
        # Draw the grid
        screen.fill(BLACK)
        draw_grid(screen, grid)
        pygame.display.flip()
        
        # Control the speed of the game
        clock.tick(10)  # 10 frames per second
    
    pygame.quit()

if __name__ == '__main__':
    main()
