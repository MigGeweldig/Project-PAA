import pygame
import random
import cv2
import numpy as np
import math

pygame.init()

WIDTH, HEIGHT = 1200, 800

GRAY_RANGE = [(90, 90, 90), (150, 150, 150)]
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Courier Simulation")

map_image = None  
map_loaded = False
map_files = ["map1.png", "map2.png", "map3.png", "map4.png"]
last_map = None

def load_map():
    global map_image, map_loaded, last_map
    
    if len(map_files) == 0:
        print("Tidak ada peta tersedia!")
        return

    available_maps = [m for m in map_files if m != last_map]
    if not available_maps:
        available_maps = map_files

    image_path = random.choice(available_maps)
    
    try:
        map_image = pygame.image.load(image_path)
        map_image = pygame.transform.scale(map_image, (WIDTH, HEIGHT))
        map_loaded = True  
        last_map = image_path
        print(f"Peta {image_path} dimuat!")

    except:
        print(f"Error: Tidak bisa memuat {image_path}")

class Courier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  
        self.speed = 2  
        self.dx = 0
        self.dy = 0
        self.moving = False  

        self.image = pygame.Surface((30, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLACK, [(0, 20), (30, 10), (0, 0)])
        
    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated_image.get_rect(center=(self.x, self.y))
        surface.blit(rotated_image, rect.topleft)
        
    def move_towards(self, target_x, target_y):
        """Gerakkan kurir menuju tujuan"""
        if not self.moving:
            return
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < 5:
            self.moving = False
            return

        self.dx = (dx / distance) * self.speed
        self.dy = (dy / distance) * self.speed

        self.x += self.dx
        self.y += self.dy
        
        self.angle = math.degrees(math.atan2(-self.dy, self.dx))

def randomize_positions():
    global source, destination, courier, running_simulation
    source = (random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100))
    destination = (random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100))
    courier = Courier(*source)  
    running_simulation = False  
    print(f"Posisi diacak! Start: {source}, Finish: {destination}")

source = (0, 0)
destination = (0, 0)
courier = Courier(*source)

load_map_button = pygame.Rect(50, 50, 150, 50)
random_button = pygame.Rect(250, 50, 150, 50)
start_button = pygame.Rect(450, 50, 150, 50)
stop_button = pygame.Rect(650, 50, 150, 50)
running_simulation = False

def game_loop():
    global running_simulation
    running = True
    while running:
        screen.fill(BLACK)

        if map_loaded and map_image:
            screen.blit(map_image, (0, 0))

            pygame.draw.circle(screen, YELLOW, source, 10)
            pygame.draw.circle(screen, RED, destination, 10)

            if running_simulation:
                courier.move_towards(*destination)

            courier.draw(screen)

        pygame.draw.rect(screen, GREEN, load_map_button)
        pygame.draw.rect(screen, BLUE, random_button)
        pygame.draw.rect(screen, GREEN, start_button)
        pygame.draw.rect(screen, RED, stop_button)
        
        font = pygame.font.Font(None, 36)
        load_text = font.render("Load Map", True, BLACK)
        random_text = font.render("Acak", True, WHITE)
        start_text = font.render("Start", True, BLACK)
        stop_text = font.render("Stop", True, BLACK)
        
        screen.blit(load_text, (load_map_button.x + 30, load_map_button.y + 10))
        screen.blit(random_text, (random_button.x + 50, random_button.y + 10))
        screen.blit(start_text, (start_button.x + 50, start_button.y + 10))
        screen.blit(stop_text, (stop_button.x + 50, stop_button.y + 10))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if load_map_button.collidepoint(event.pos):
                    load_map()
                elif random_button.collidepoint(event.pos) and map_loaded:
                    randomize_positions()
                elif start_button.collidepoint(event.pos) and map_loaded:
                    running_simulation = True
                    courier.moving = True
                elif stop_button.collidepoint(event.pos) and map_loaded:
                    running_simulation = False
                    courier.moving = False
    
    pygame.quit()

game_loop()