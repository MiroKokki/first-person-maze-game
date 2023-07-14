#by Miro Kokki ©2023


import pygame
import math
import random

# Start Pygame
pygame.init()

# Define the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 120, 0)
BLUE = (0, 0, 255)

# Set the width and height of the screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

# Set the size of each cell
CELL_SIZE = 40


# Define the dimensions of the maze
num_rows = 29
num_cols = 29

# Create an empty maze
maze = [[1] * num_cols for _ in range(num_rows)]

# Recursive backtracking algorithm to generate the maze (by chat gpt I couldent for the life of me figure this out)
def generate_maze(row, col):
    maze[row][col] = 0  # Mark the current cell as empty

    # Define the four possible neighbors (top, right, bottom, left)
    neighbors = [(row - 2, col), (row, col + 2), (row + 2, col), (row, col - 2)]
    random.shuffle(neighbors)  # Randomize the order of neighbors

    for neighbor_row, neighbor_col in neighbors:
        if (
            neighbor_row >= 0
            and neighbor_row < num_rows
            and neighbor_col >= 0
            and neighbor_col < num_cols
            and maze[neighbor_row][neighbor_col] == 1
        ):
            # Connect the current cell with the neighbor cell
            maze[(row + neighbor_row) // 2][(col + neighbor_col) // 2] = 0
            generate_maze(neighbor_row, neighbor_col)

# Generate the maze starting from the top-left corner
generate_maze(1, 1)

# Calculate the number of rows and columns in the maze
num_rows = len(maze)
num_cols = len(maze[0])

# Calculate the width and height of the maze
maze_width = num_cols * CELL_SIZE
maze_height = num_rows * CELL_SIZE

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("First-Person Maze Game")

clock = pygame.time.Clock()

# Find a valid initial player position inside the maze
valid_positions = []
for row in range(num_rows):
    for col in range(num_cols):
        if maze[row][col] == 0:
            valid_positions.append((col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2))

player_x, player_y = random.choice(valid_positions)
player_angle = -90

# Define the fov
FOV = math.pi / 2.5

# Define the number of rays to cast
NUM_RAYS = 120

# Calculate the angle between each ray
RAY_ANGLE = FOV / NUM_RAYS

# Define the distance between the player and the projection plane
PROJ_PLANE_DIST = (SCREEN_WIDTH / 2) / math.tan(FOV / 2)

# Define the movement speed
MOVE_SPEED = 2.5

# Define the rotation speed
ROTATION_SPEED = 0.04

# Set up the minimap
MAP_SCALE = 5
MAP_WIDTH = num_cols * MAP_SCALE
MAP_HEIGHT = num_rows * MAP_SCALE
map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
map_surface.fill(WHITE)

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset the game and generate a new maze
                maze = [[1] * num_cols for _ in range(num_rows)]
                generate_maze(1, 1)

                # Find a valid initial player position inside the new maze
                valid_positions = []
                for row in range(num_rows):
                    for col in range(num_cols):
                        if maze[row][col] == 0:
                            valid_positions.append((col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2))

                player_x, player_y = random.choice(valid_positions)
                player_angle = -90

    # Handle player movement and rotation
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        new_x = player_x + math.cos(player_angle) * MOVE_SPEED
        new_y = player_y + math.sin(player_angle) * MOVE_SPEED
        if maze[int(new_y / CELL_SIZE)][int(new_x / CELL_SIZE)] != 1:
            player_x = new_x
            player_y = new_y
    if keys[pygame.K_s]:
        new_x = player_x - math.cos(player_angle) * MOVE_SPEED
        new_y = player_y - math.sin(player_angle) * MOVE_SPEED
        if maze[int(new_y / CELL_SIZE)][int(new_x / CELL_SIZE)] != 1:
            player_x = new_x
            player_y = new_y
    if keys[pygame.K_a]:
        player_angle -= ROTATION_SPEED
    if keys[pygame.K_d]:
        player_angle += ROTATION_SPEED

    # Clear the screen
    screen.fill(BLACK)

    # Cast rays and render walls
    for ray in range(NUM_RAYS):
        ray_angle = player_angle - (FOV / 2) + (ray * RAY_ANGLE)
        distance_to_wall = 0
        hit_wall = False

        while not hit_wall and distance_to_wall < maze_width:
            test_x = int(player_x + math.cos(ray_angle) * distance_to_wall)
            test_y = int(player_y + math.sin(ray_angle) * distance_to_wall)

            if (
                test_x < 0
                or test_x >= maze_width
                or test_y < 0
                or test_y >= maze_height
                or maze[int(test_y / CELL_SIZE)][int(test_x / CELL_SIZE)] == 1
            ):
                hit_wall = True
            else:
                distance_to_wall += 1

        # Ensure the distance to the wall is greater than zero
        if distance_to_wall > 0:
            # Calculate the height of the wall
            wall_height = (CELL_SIZE / distance_to_wall) * PROJ_PLANE_DIST

            # Calculate the position and size of the wall slice on the screen
            wall_top = int((SCREEN_HEIGHT - wall_height) / 2)
            wall_bottom = SCREEN_HEIGHT - wall_top

            # Calculate the width of the wall slice
            wall_width = 10

            # Calculate the x-coordinate of the wall slice
            wall_x = ray * (SCREEN_WIDTH / NUM_RAYS)

            # Determine the color of the wall slice
            wall_color = RED if ray % 2 == 0 else ORANGE

            # Draw the wall slice
            pygame.draw.rect(screen, wall_color, (wall_x, wall_top, wall_width, wall_bottom - wall_top))

    # Update the minimap
    map_surface.fill(WHITE)
    for row in range(num_rows):
        for col in range(num_cols):
            if maze[row][col] == 1:
                pygame.draw.rect(map_surface, BLACK, (col * MAP_SCALE, row * MAP_SCALE, MAP_SCALE, MAP_SCALE))

    # Draw the player's position on the minimap
    pygame.draw.circle(
        map_surface,
        GREEN,
        (int(player_x / CELL_SIZE * MAP_SCALE), int(player_y / CELL_SIZE * MAP_SCALE)),
        3,
    )

    # Draw the rays on the minimap
    for ray in range(NUM_RAYS):
        ray_angle = player_angle - (FOV / 2) + (ray * RAY_ANGLE)
        ray_end_x = player_x + math.cos(ray_angle) * (SCREEN_WIDTH / 4)
        ray_end_y = player_y + math.sin(ray_angle) * (SCREEN_WIDTH / 4)
        pygame.draw.line(
            map_surface,
            BLUE,
            (int(player_x / CELL_SIZE * MAP_SCALE), int(player_y / CELL_SIZE * MAP_SCALE)),
            (int(ray_end_x / CELL_SIZE * MAP_SCALE), int(ray_end_y / CELL_SIZE * MAP_SCALE)),
            1,
        )

    # Draw the minimap on the screen
    screen.blit(map_surface, (SCREEN_WIDTH - MAP_WIDTH - 10, 10))

    # Update the screen
    pygame.display.flip()
    clock.tick(60)


pygame.quit()
