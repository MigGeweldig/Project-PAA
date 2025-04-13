import pygame
import random
import tkinter as tk
from tkinter import filedialog
import math
import heapq

# Inisialisasi Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
CELL_SIZE = 4
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Courier Simulation")

# Warna
GRAY_RANGE = [(90, 90, 90), (150, 150, 150)]
WHITE, BLACK, YELLOW, RED, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (255, 255, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)

# Utilitas
def is_gray(color):
    r, g, b = color
    return all(GRAY_RANGE[0][i] <= c <= GRAY_RANGE[1][i] for i, c in enumerate((r, g, b)))

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Tombol
class Button:
    def __init__(self, rect, color, text, font_size=30):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, font_size)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = self.font.render(self.text, True, BLACK)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Map dan Grid
class Map:
    def __init__(self):
        self.image = None
        self.grid = []
        self.loaded = False

    def load(self):
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(filetypes=[("Images", ".png;.jpg;*.bmp")])
        if not path: return

        img = pygame.image.load(path)
        w, h = img.get_width(), img.get_height()
        if not (1000 <= w <= 1500 and 700 <= h <= 1000):
            print(f"Gambar {w}x{h} tidak valid.")
            return

        self.image = pygame.transform.scale(img, (WIDTH, HEIGHT))
        self.loaded = True
        self.build_grid()

    def build_grid(self):
        self.grid = []
        for y in range(0, HEIGHT, CELL_SIZE):
            row = []
            for x in range(0, WIDTH, CELL_SIZE):
                color = self.image.get_at((x, y))[:3]
                row.append(is_gray(color))
            self.grid.append(row)

    def draw(self):
        if self.loaded:
            screen.blit(self.image, (0, 0))

    def get_random_gray(self):
        for _ in range(1000):
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 100)
            if is_gray(self.image.get_at((x, y))[:3]):
                # Snap ke tengah sel grid
                gx = (x // CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2
                gy = (y // CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2
                return (gx, gy)
        # Default fallback
        return (WIDTH // 2, HEIGHT // 2)


# A* Pathfinder
class Pathfinder:
    def __init__(self, grid):
        self.grid = grid

    def find(self, start, goal):
        start = (start[1] // CELL_SIZE, start[0] // CELL_SIZE)
        goal = (goal[1] // CELL_SIZE, goal[0] // CELL_SIZE)

        if not self.grid[start[0]][start[1]] or not self.grid[goal[0]][goal[1]]:
            return []

        open_set = [(0, start)]
        came_from, g_score = {}, {start: 0}
        f_score = {start: heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) for y, x in path]

            for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                ny, nx = current[0] + dy, current[1] + dx
                neighbor = (ny, nx)
                if 0 <= ny < len(self.grid) and 0 <= nx < len(self.grid[0]) and self.grid[ny][nx]:
                    tentative_g = g_score[current] + 1
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

# Kurir
class Courier:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.path = []
        self.target_index = 0
        self.speed = 2
        self.angle = 0
        self.image = self.create_image()

    def create_image(self):
        surface = pygame.Surface((50, 30), pygame.SRCALPHA)
        pygame.draw.rect(surface, (60, 60, 60), (0, 5, 35, 20), border_radius=8)
        pygame.draw.polygon(surface, RED, [(40, 15), (30, 5), (30, 25)])
        return surface

    def set_path(self, path):
        self.path = path
        self.target_index = 0

    def update(self):
        if self.target_index >= len(self.path): return
        tx, ty = self.path[self.target_index]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 2:
            self.target_index += 1
            return
        self.x += dx / dist * self.speed
        self.y += dy / dist * self.speed
        self.angle = math.degrees(math.atan2(dy, dx))

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

# Inisialisasi elemen
map_obj = Map()
courier = Courier(0, 0)
source = destination = (0, 0)
path = []
running_sim = False

buttons = {
    "load": Button((50, 50, 150, 50), GREEN, "Load Map"),
    "random": Button((50, 120, 150, 50), BLUE, "Acak"),
    "start": Button((50, 190, 150, 50), GREEN, "Start"),
    "stop": Button((50, 260, 150, 50), RED, "Stop"),
}

# Main Loop
def game_loop():
    global courier, source, destination, path, running_sim
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BLACK)
        map_obj.draw()

        if map_obj.loaded:
            pygame.draw.circle(screen, YELLOW, source, 10)
            pygame.draw.circle(screen, RED, destination, 10)
            if running_sim:
                courier.update()
            courier.draw(screen)

        for btn in buttons.values():
            btn.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if buttons["load"].is_clicked(pos):
                    map_obj.load()
                    running_sim = False
                elif buttons["random"].is_clicked(pos) and map_obj.loaded:
                    source = map_obj.get_random_gray()
                    destination = map_obj.get_random_gray()
                    courier = Courier(*source)
                    pathfinder = Pathfinder(map_obj.grid)
                    path = pathfinder.find(source, destination)
                    courier.set_path([])
                    running_sim = False
                elif buttons["start"].is_clicked(pos) and map_obj.loaded:
                    current_pos = (int(courier.x), int(courier.y))
                    pathfinder = Pathfinder(map_obj.grid)
                    new_path = pathfinder.find(current_pos, destination)
                    if path:
                        courier.set_path(new_path)
                        running_sim = True
                elif buttons["stop"].is_clicked(pos):
                    running_sim = False

        clock.tick(60)

    pygame.quit()   

game_loop()
