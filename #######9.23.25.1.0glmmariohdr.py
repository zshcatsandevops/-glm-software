import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario 2D World - SMB6 Golden Coins Style")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)

# Game states
INTRO = 0
MAIN_OVERWORLD = 1
WORLD_MAP = 2
LEVEL_START = 3
GAME = 4
BOSS = 5
LEVEL_COMPLETE = 6
GAME_OVER = 7
VICTORY = 8

# Fonts
title_font = pygame.font.SysFont('Arial', 48, bold=True)
subtitle_font = pygame.font.SysFont('Arial', 36)
normal_font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)

# Player class with SMBX-style powerups
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT - 150
        self.vel_y = 0
        self.jump_power = 15
        self.gravity = 0.8
        self.is_jumping = False
        self.speed = 5
        self.direction = 1  # 1 for right, -1 for left
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.invincible = 0
        self.powerup = "small"  # small, big, fire
        self.color = RED
        self.animation_frame = 0
        self.run_frame = 0
        
    def jump(self):
        if not self.is_jumping:
            self.vel_y = -self.jump_power
            self.is_jumping = True
    
    def update(self, platforms, enemies):
        # Apply gravity
        self.vel_y += self.gravity
        self.y += self.vel_y
        
        # Update animation
        self.animation_frame = (self.animation_frame + 1) % 60
        
        # Check platform collisions
        self.is_jumping = True
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.is_jumping = False
        
        # Keep player on screen (except for falling)
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
        # Check if player fell off the screen
        if self.y > SCREEN_HEIGHT:
            self.lives -= 1
            self.invincible = 60
            self.reset_position(platforms)
            
        # Update invincibility
        if self.invincible > 0:
            self.invincible -= 1
            
        # Update running animation
        if abs(self.vel_y) > 0 or (pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT]):
            self.run_frame = (self.run_frame + 1) % 20
    
    def reset_position(self, platforms):
        self.x = 100
        # Find the highest platform to spawn on
        spawn_y = SCREEN_HEIGHT - 150
        for platform in platforms:
            if platform.y < spawn_y and platform.y > SCREEN_HEIGHT - 200:
                spawn_y = platform.y - self.height
        self.y = spawn_y
        self.vel_y = 0
        self.is_jumping = False
        
    def draw(self, screen):
        # Flash when invincible
        if self.invincible > 0 and self.invincible % 10 < 5:
            return
            
        # Adjust size based on powerup
        draw_height = self.height
        if self.powerup == "small":
            draw_height = 40
            
        # Body (color changes based on powerup)
        body_color = self.color
        if self.powerup == "fire":
            body_color = ORANGE
            
        pygame.draw.rect(screen, body_color, (self.x, self.y + (self.height - draw_height), self.width, draw_height))
        
        # Hat
        pygame.draw.rect(screen, RED, (self.x-5, self.y + (self.height - draw_height), self.width+10, 15))
        
        # Face
        face_y = self.y + (self.height - draw_height) + 25
        pygame.draw.circle(screen, (255, 200, 150), (self.x+self.width//2, face_y), 12)
        
        # Eyes (blink occasionally)
        if self.animation_frame < 55 or self.animation_frame % 10 < 5:
            pygame.draw.circle(screen, BLACK, (self.x+self.width//2+5*self.direction, face_y-3), 4)
        
        # Mustache
        pygame.draw.rect(screen, BLACK, (self.x+self.width//2-15, face_y+5, 30, 5))
        
        # Running animation - legs
        leg_offset = 0
        if self.run_frame < 10:
            leg_offset = 5
        elif self.run_frame < 20:
            leg_offset = -5
            
        pygame.draw.rect(screen, BLUE, (self.x+5, self.y+draw_height-10, 10, 10+leg_offset))
        pygame.draw.rect(screen, BLUE, (self.x+self.width-15, self.y+draw_height-10, 10, 10-leg_offset))

# Platform class with different types
class Platform:
    def __init__(self, x, y, width, height, platform_type="normal"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = platform_type
        self.color = BROWN
        if platform_type == "brick":
            self.color = (150, 75, 0)
        elif platform_type == "question":
            self.color = YELLOW
        elif platform_type == "pipe":
            self.color = GREEN
            
    def draw(self, screen):
        if self.type == "normal":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Platform top
            pygame.draw.rect(screen, (160, 82, 45), (self.x, self.y, self.width, 5))
        elif self.type == "brick":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Brick pattern
            for i in range(0, self.width, 10):
                pygame.draw.line(screen, (120, 60, 0), (self.x+i, self.y), (self.x+i, self.y+self.height), 1)
            for i in range(0, self.height, 10):
                pygame.draw.line(screen, (120, 60, 0), (self.x, self.y+i), (self.x+self.width, self.y+i), 1)
        elif self.type == "question":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, (200, 150, 0), (self.x+5, self.y+5, self.width-10, self.height-10))
            # Question mark
            text = small_font.render("?", True, BLACK)
            screen.blit(text, (self.x+self.width//2-5, self.y+self.height//2-8))
        elif self.type == "pipe":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Pipe details
            pygame.draw.rect(screen, (0, 100, 0), (self.x+5, self.y, self.width-10, 10))

# Enemy class with more types
class Enemy:
    def __init__(self, x, y, enemy_type="goomba"):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 2
        self.direction = 1
        self.type = enemy_type
        self.is_alive = True
        self.animation = 0
        
    def update(self, platforms):
        if not self.is_alive:
            return
            
        self.animation = (self.animation + 1) % 30
        self.x += self.speed * self.direction
        
        # Change direction at edges
        on_platform = False
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width):
                on_platform = True
                # Check if at edge of platform
                if (self.x <= platform.x and self.direction == -1) or \
                   (self.x + self.width >= platform.x + platform.width and self.direction == 1):
                    self.direction *= -1
                break
                
        if not on_platform:
            self.direction *= -1
    
    def draw(self, screen):
        if not self.is_alive:
            return
            
        if self.type == "goomba":
            # Draw Goomba with animation
            offset = 0
            if self.animation < 15:
                offset = 2
                
            pygame.draw.ellipse(screen, (139, 69, 19), (self.x, self.y+offset, self.width, self.height-offset))
            pygame.draw.ellipse(screen, (100, 40, 0), (self.x, self.y+offset, self.width, (self.height-offset)//2))
            # Eyes
            pygame.draw.circle(screen, BLACK, (self.x+10, self.y+15+offset), 5)
            pygame.draw.circle(screen, BLACK, (self.x+30, self.y+15+offset), 5)
        elif self.type == "koopa":
            # Draw Koopa Troopa
            pygame.draw.ellipse(screen, GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.ellipse(screen, (0, 100, 0), (self.x, self.y, self.width, self.height//2))
            # Shell pattern
            pygame.draw.ellipse(screen, (0, 80, 0), (self.x+5, self.y+5, self.width-10, self.height-10))
        elif self.type == "piranha":
            # Draw Piranha Plant (emerges from pipes)
            pygame.draw.rect(screen, GREEN, (self.x+10, self.y, self.width-20, self.height))
            pygame.draw.ellipse(screen, (0, 150, 0), (self.x, self.y+self.height//2, self.width, self.height//2))
            # Mouth
            pygame.draw.ellipse(screen, RED, (self.x+15, self.y+self.height//2-5, self.width-30, 10))

# Powerup class
class Powerup:
    def __init__(self, x, y, power_type="mushroom"):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = power_type
        self.collected = False
        self.direction = 1
        self.speed = 1
        self.animation = 0
        
    def update(self, platforms):
        if self.collected:
            return
            
        self.animation = (self.animation + 1) % 60
        self.x += self.speed * self.direction
        
        # Simple movement and platform edge detection
        on_platform = False
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 5 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width):
                on_platform = True
                if (self.x <= platform.x and self.direction == -1) or \
                   (self.x + self.width >= platform.x + platform.width and self.direction == 1):
                    self.direction *= -1
                break
                
        if not on_platform:
            self.direction *= -1
            self.y += 5  # Fall if not on platform
    
    def draw(self, screen):
        if self.collected:
            return
            
        offset = math.sin(self.animation * 0.1) * 3
        if self.type == "mushroom":
            # Red mushroom
            pygame.draw.ellipse(screen, RED, (self.x, self.y+offset, self.width, self.height//2))
            pygame.draw.ellipse(screen, WHITE, (self.x, self.y+offset, self.width, self.height))
        elif self.type == "fireflower":
            # Fire flower
            pygame.draw.ellipse(screen, ORANGE, (self.x, self.y+offset, self.width, self.height))
            for i in range(4):
                angle = i * math.pi/2
                pygame.draw.ellipse(screen, RED, 
                                   (self.x + math.cos(angle)*10, 
                                    self.y+offset + math.sin(angle)*10, 
                                    self.width//2, self.height//2))

# Boss class with improved AI
class Boss:
    def __init__(self, boss_type, world):
        self.type = boss_type
        self.world = world
        self.width = 80
        self.height = 80
        self.x = SCREEN_WIDTH - 150
        self.y = SCREEN_HEIGHT - 200
        self.health = 5
        self.speed = 3
        self.direction = -1
        self.attack_timer = 0
        self.projectiles = []
        self.jump_timer = 0
        self.is_jumping = False
        self.jump_power = 10
        
    def update(self, player, platforms):
        # Movement
        if not self.is_jumping:
            self.x += self.speed * self.direction
            
            # Change direction at edges or when player is on other side
            if (self.x <= 50 or self.x >= SCREEN_WIDTH - 150 or 
                (self.direction == -1 and player.x > self.x) or 
                (self.direction == 1 and player.x < self.x)):
                self.direction *= -1
                
            # Jump occasionally
            self.jump_timer += 1
            if self.jump_timer >= 90:  # Jump every 3 seconds
                self.is_jumping = True
                self.jump_timer = 0
        else:
            # Jumping physics
            self.y -= self.jump_power
            self.jump_power -= 0.5
            if self.jump_power <= 0:
                self.is_jumping = False
                self.jump_power = 10
                # Land on a platform if possible
                for platform in platforms:
                    if (self.y + self.height >= platform.y and 
                        self.y + self.height <= platform.y + 10 and
                        self.x + self.width > platform.x and 
                        self.x < platform.x + platform.width):
                        self.y = platform.y - self.height
            
        # Attack periodically
        self.attack_timer += 1
        if self.attack_timer >= 60:  # Attack every 2 seconds
            self.attack(player)
            self.attack_timer = 0
            
        # Update projectiles
        for proj in self.projectiles[:]:
            proj[0] += proj[2] * 5  # Move projectile
            proj[1] += proj[3] * 5 if len(proj) > 3 else 0
            if proj[0] < 0 or proj[0] > SCREEN_WIDTH or proj[1] < 0 or proj[1] > SCREEN_HEIGHT:
                self.projectiles.remove(proj)
                
            # Check collision with player
            if (player.x < proj[0] < player.x + player.width and
                player.y < proj[1] < player.y + player.height and
                player.invincible == 0):
                player.lives -= 1
                player.invincible = 60
                if proj in self.projectiles:
                    self.projectiles.remove(proj)
    
    def attack(self, player):
        if self.type == "kamek":
            # Kamek shoots magic projectiles
            self.projectiles.append([self.x, self.y + self.height//2, -1, 0])
        elif self.type == "king_boo":
            # King Boo shoots ghostly projectiles
            angle = math.atan2(player.y - self.y, player.x - self.x)
            self.projectiles.append([self.x, self.y + self.height//2, math.cos(angle), math.sin(angle)])
        elif self.type == "wiggler":
            # Wiggler charges
            self.speed = 8
            pygame.time.set_timer(pygame.USEREVENT, 1000)  # Reset speed after 1 second
        elif self.type == "bowser_jr":
            # Bowser Jr. shoots fireballs
            self.projectiles.append([self.x, self.y + self.height//2, -1, 0])
            self.projectiles.append([self.x, self.y + self.height//2, -0.7, -0.3])
            self.projectiles.append([self.x, self.y + self.height//2, -1.3, 0.3])
        elif self.type == "dry_bowser":
            # Dry Bowser shoots bone projectiles
            for i in range(3):
                angle = (i - 1) * 0.5
                self.projectiles.append([self.x, self.y + self.height//2, math.cos(angle), math.sin(angle)])
    
    def draw(self, screen):
        if self.type == "kamek":
            # Draw Kamek
            pygame.draw.rect(screen, (200, 0, 200), (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, (150, 0, 150), (self.x+self.width//2, self.y-10), 20)
            # Eyes
            pygame.draw.circle(screen, YELLOW, (self.x+20, self.y+20), 10)
            pygame.draw.circle(screen, YELLOW, (self.x+60, self.y+20), 10)
            pygame.draw.circle(screen, BLACK, (self.x+20, self.y+20), 5)
            pygame.draw.circle(screen, BLACK, (self.x+60, self.y+20), 5)
            # Nose
            pygame.draw.polygon(screen, (255, 150, 150), [(self.x+40, self.y+30), (self.x+30, self.y+50), (self.x+50, self.y+50)])
        elif self.type == "king_boo":
            # Draw King Boo
            pygame.draw.circle(screen, WHITE, (self.x+self.width//2, self.y+self.height//2), self.width//2)
            pygame.draw.circle(screen, (200, 200, 200), (self.x+self.width//2, self.y+self.height//2), self.width//2-5)
            # Crown
            pygame.draw.polygon(screen, YELLOW, [(self.x+20, self.y+10), (self.x+40, self.y-20), (self.x+60, self.y+10)])
            # Eyes
            pygame.draw.ellipse(screen, BLACK, (self.x+20, self.y+20, 20, 30))
            pygame.draw.ellipse(screen, BLACK, (self.x+40, self.y+20, 20, 30))
            # Mouth
            pygame.draw.arc(screen, BLACK, (self.x+20, self.y+40, 40, 20), 0, math.pi, 3)
        elif self.type == "wiggler":
            # Draw Wiggler
            pygame.draw.ellipse(screen, YELLOW, (self.x, self.y, self.width, self.height))
            pygame.draw.ellipse(screen, (200, 200, 0), (self.x, self.y, self.width, self.height//2))
            # Eyes
            pygame.draw.circle(screen, BLACK, (self.x+20, self.y+20), 8)
            pygame.draw.circle(screen, BLACK, (self.x+60, self.y+20), 8)
            # Antennae
            pygame.draw.line(screen, BLACK, (self.x+20, self.y), (self.x+10, self.y-20), 3)
            pygame.draw.line(screen, BLACK, (self.x+60, self.y), (self.x+70, self.y-20), 3)
            pygame.draw.circle(screen, RED, (self.x+10, self.y-20), 5)
            pygame.draw.circle(screen, RED, (self.x+70, self.y-20), 5)
        elif self.type == "bowser_jr":
            # Draw Bowser Jr.
            pygame.draw.ellipse(screen, ORANGE, (self.x, self.y, self.width, self.height))
            pygame.draw.ellipse(screen, (200, 100, 0), (self.x, self.y, self.width, self.height//2))
            # Shell
            pygame.draw.ellipse(screen, RED, (self.x+5, self.y+5, self.width-10, self.height-10))
            # Spikes
            for i in range(5):
                spike_x = self.x + 10 + i * 15
                pygame.draw.polygon(screen, WHITE, [(spike_x-5, self.y+5), (spike_x, self.y-5), (spike_x+5, self.y+5)])
            # Eyes
            pygame.draw.circle(screen, BLACK, (self.x+25, self.y+20), 5)
            pygame.draw.circle(screen, BLACK, (self.x+55, self.y+20), 5)
        elif self.type == "dry_bowser":
            # Draw Dry Bowser
            pygame.draw.ellipse(screen, WHITE, (self.x, self.y, self.width, self.height))
            # Shell
            pygame.draw.ellipse(screen, (200, 200, 200), (self.x+5, self.y+5, self.width-10, self.height-10))
            # Spikes
            for i in range(5):
                spike_x = self.x + 10 + i * 15
                pygame.draw.polygon(screen, BLACK, [(spike_x-5, self.y+5), (spike_x, self.y-5), (spike_x+5, self.y+5)])
            # Eyes
            pygame.draw.circle(screen, RED, (self.x+25, self.y+20), 5)
            pygame.draw.circle(screen, RED, (self.x+55, self.y+20), 5)
            # Mouth
            pygame.draw.arc(screen, BLACK, (self.x+20, self.y+40, 40, 20), 0, math.pi, 3)
        
        # Draw projectiles
        for proj in self.projectiles:
            if self.type == "kamek" or self.type == "bowser_jr":
                pygame.draw.circle(screen, RED, (int(proj[0]), int(proj[1])), 8)
            elif self.type == "king_boo":
                pygame.draw.circle(screen, (200, 200, 255), (int(proj[0]), int(proj[1])), 8)
            elif self.type == "dry_bowser":
                pygame.draw.ellipse(screen, WHITE, (int(proj[0]), int(proj[1]), 15, 8))

# Coin class with better animation
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.collected = False
        self.animation = 0
        
    def update(self):
        self.animation = (self.animation + 0.2) % (2 * math.pi)
        
    def draw(self, screen):
        if not self.collected:
            # Animated coin with spinning effect
            offset = math.sin(self.animation) * 3
            size_mod = abs(math.cos(self.animation)) * 3
            pygame.draw.circle(screen, YELLOW, (int(self.x + self.width//2), int(self.y + self.height//2 + offset)), 
                             self.width//2 + int(size_mod))
            pygame.draw.circle(screen, (255, 200, 0), (int(self.x + self.width//2), int(self.y + self.height//2 + offset)), 
                             self.width//2 + int(size_mod) - 3)

# Flagpole class (end of level)
class Flagpole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 200
        self.flag_raised = False
        
    def draw(self, screen):
        # Pole
        pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height))
        # Flag
        if not self.flag_raised:
            pygame.draw.polygon(screen, RED, [(self.x+self.width, self.y+30), 
                                            (self.x+self.width+40, self.y+30), 
                                            (self.x+self.width+40, self.y+60), 
                                            (self.x+self.width, self.y+60)])

# World Map Node class
class WorldMapNode:
    def __init__(self, x, y, level_num, world_num, completed=False):
        self.x = x
        self.y = y
        self.level_num = level_num
        self.world_num = world_num
        self.completed = completed
        self.width = 40
        self.height = 40
        
    def draw(self, screen):
        color = GREEN if self.completed else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        text = small_font.render(str(self.level_num), True, WHITE)
        screen.blit(text, (self.x + self.width//2 - 5, self.y + self.height//2 - 8))

# Main Overworld World Node class
class OverworldWorldNode:
    def __init__(self, x, y, world_num, name, color, unlocked=True):
        self.x = x
        self.y = y
        self.world_num = world_num
        self.name = name
        self.color = color
        self.unlocked = unlocked
        self.width = 80
        self.height = 80
        self.selected = False
        
    def draw(self, screen):
        # Draw castle/icon for world
        if self.unlocked:
            # Castle base
            pygame.draw.rect(screen, self.color, (self.x, self.y + 40, self.width, 40))
            # Castle towers
            pygame.draw.rect(screen, self.color, (self.x, self.y, 20, 60))
            pygame.draw.rect(screen, self.color, (self.x + 30, self.y, 20, 60))
            pygame.draw.rect(screen, self.color, (self.x + 60, self.y, 20, 60))
            # Castle flags
            pygame.draw.polygon(screen, RED, [(self.x+10, self.y), (self.x+30, self.y+10), (self.x+10, self.y+20)])
            pygame.draw.polygon(screen, RED, [(self.x+40, self.y), (self.x+60, self.y+10), (self.x+40, self.y+20)])
            pygame.draw.polygon(screen, RED, [(self.x+70, self.y), (self.x+90, self.y+10), (self.x+70, self.y+20)])
            
            # Highlight if selected
            if self.selected:
                pygame.draw.rect(screen, YELLOW, (self.x-5, self.y-5, self.width+10, self.height+10), 3)
        else:
            # Locked castle
            pygame.draw.rect(screen, GRAY, (self.x, self.y + 40, self.width, 40))
            pygame.draw.rect(screen, GRAY, (self.x, self.y, 20, 60))
            pygame.draw.rect(screen, GRAY, (self.x + 30, self.y, 20, 60))
            pygame.draw.rect(screen, GRAY, (self.x + 60, self.y, 20, 60))
            # Lock icon
            pygame.draw.rect(screen, BLACK, (self.x + 30, self.y + 30, 20, 15))
            pygame.draw.arc(screen, BLACK, (self.x + 30, self.y + 20, 20, 20), 0, math.pi, 3)
            
        # World name
        text = small_font.render(self.name, True, WHITE)
        screen.blit(text, (self.x + self.width//2 - text.get_width()//2, self.y + self.height + 10))

# Create game objects
player = Player()
platforms = []
enemies = []
coins = []
powerups = []
boss = None
flagpole = None
world_map_nodes = []
overworld_world_nodes = []

# Game state
game_state = INTRO
current_world = 1
current_level = 1
intro_timer = 0
boss_defeated = False
level_complete = False
level_timer = 0
level_start_timer = 0
camera_x = 0
selected_world = 1

# Boss types for each world
boss_types = ["kamek", "king_boo", "wiggler", "bowser_jr", "dry_bowser"]
boss_names = ["Kamek", "King Boo", "Wiggler", "Bowser Jr.", "Dry Bowser"]
world_names = ["Grass Land", "Desert Hills", "Water World", "Sky Kingdom", "Volcano Peak"]
world_colors = [GREEN, ORANGE, BLUE, CYAN, RED]

# Create levels with SMBX-style design
def create_level(world, level):
    global platforms, enemies, coins, powerups, flagpole, boss, camera_x
    
    platforms = []
    enemies = []
    coins = []
    powerups = []
    boss = None
    flagpole = None
    camera_x = 0
    
    # Ground platform (longer for scrolling)
    level_length = 2000 if level < 4 else 1200  # Boss levels are shorter
    platforms.append(Platform(0, SCREEN_HEIGHT - 50, level_length, 50))
    
    # Level design based on world and level
    if level < 4:  # Regular levels
        # Add platforms in a pattern
        platform_patterns = [
            [(200, SCREEN_HEIGHT - 150, 100, 20), (400, SCREEN_HEIGHT - 200, 100, 20), 
             (600, SCREEN_HEIGHT - 150, 100, 20), (800, SCREEN_HEIGHT - 250, 100, 20)],
            [(150, SCREEN_HEIGHT - 180, 80, 20), (350, SCREEN_HEIGHT - 220, 80, 20), 
             (550, SCREEN_HEIGHT - 180, 80, 20), (750, SCREEN_HEIGHT - 280, 80, 20)],
            [(100, SCREEN_HEIGHT - 150, 120, 20), (300, SCREEN_HEIGHT - 200, 120, 20), 
             (500, SCREEN_HEIGHT - 250, 120, 20), (700, SCREEN_HEIGHT - 200, 120, 20)]
        ]
        
        pattern = platform_patterns[(level-1) % 3]
        for p in pattern:
            platforms.append(Platform(p[0], p[1], p[2], p[3], 
                                   random.choice(["normal", "brick", "question"])))
            
        # Add pipes
        for i in range(3):
            pipe_x = 300 + i*400
            platforms.append(Platform(pipe_x, SCREEN_HEIGHT - 150, 60, 100, "pipe"))
            
        # Add enemies based on world theme
        enemy_types = ["goomba", "koopa"]
        if world >= 3:
            enemy_types.append("piranha")
            
        for i in range(5 + level):  # More enemies in later levels
            enemy_x = 200 + i*150
            enemy_y = SCREEN_HEIGHT - 150
            enemies.append(Enemy(enemy_x, enemy_y, random.choice(enemy_types)))
            
        # Add coins in patterns
        for i in range(15):
            coin_x = 100 + i*100
            coin_y = SCREEN_HEIGHT - 200
            # Some coins in air, some on platforms
            if i % 3 == 0:
                coin_y = SCREEN_HEIGHT - 300
            coins.append(Coin(coin_x, coin_y))
            
        # Add powerups
        for i in range(2):
            powerup_x = 300 + i*600
            powerup_y = SCREEN_HEIGHT - 200
            powerups.append(Powerup(powerup_x, powerup_y, 
                                  random.choice(["mushroom", "fireflower"])))
            
        # Add flagpole at the end
        flagpole = Flagpole(level_length - 150, SCREEN_HEIGHT - 250)
        
    else:  # Boss level
        # Create boss
        boss = Boss(boss_types[world-1], world)
        
        # Add platforms for boss battle
        platforms.append(Platform(0, SCREEN_HEIGHT - 150, 200, 20))
        platforms.append(Platform(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150, 200, 20))
        platforms.append(Platform(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 250, 200, 20))
        
        # Boss level has more powerups
        powerups.append(Powerup(100, SCREEN_HEIGHT - 200, "mushroom"))
        powerups.append(Powerup(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 200, "fireflower"))

# Create world map
def create_world_map():
    global world_map_nodes
    world_map_nodes = []
    
    for level in range(1, 5):
        x = 100 + (level-1) * 150
        y = 300
        # Mark completed levels
        completed = (level < current_level)
        world_map_nodes.append(WorldMapNode(x, y, level, current_world, completed))

# Create main overworld
def create_main_overworld():
    global overworld_world_nodes
    overworld_world_nodes = []
    
    # Create 5 world nodes in a pattern
    positions = [
        (150, 200),  # World 1
        (350, 150),  # World 2
        (550, 200),  # World 3
        (350, 300),  # World 4
        (150, 350)   # World 5
    ]
    
    for i in range(5):
        x, y = positions[i]
        unlocked = (i+1 <= current_world)
        node = OverworldWorldNode(x, y, i+1, world_names[i], world_colors[i], unlocked)
        if i+1 == selected_world:
            node.selected = True
        overworld_world_nodes.append(node)

# Initial setup
create_level(current_world, current_level)
create_world_map()
create_main_overworld()

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == INTRO:
                    game_state = MAIN_OVERWORLD
                elif game_state == MAIN_OVERWORLD:
                    # Enter the selected world
                    current_world = selected_world
                    current_level = 1
                    create_level(current_world, current_level)
                    create_world_map()
                    game_state = WORLD_MAP
                elif game_state == WORLD_MAP:
                    game_state = LEVEL_START
                    level_start_timer = 0
                elif game_state == GAME and not level_complete:
                    player.jump()
                elif game_state == BOSS and not boss_defeated:
                    player.jump()
                elif game_state == LEVEL_COMPLETE or game_state == GAME_OVER or game_state == VICTORY:
                    # Return to world map
                    game_state = WORLD_MAP
            elif event.key == pygame.K_r and (game_state == GAME_OVER or game_state == VICTORY):
                # Reset game
                player = Player()
                current_world = 1
                current_level = 1
                selected_world = 1
                create_level(current_world, current_level)
                create_world_map()
                create_main_overworld()
                game_state = MAIN_OVERWORLD
            elif event.key == pygame.K_ESCAPE:
                # Return to previous screen
                if game_state == GAME or game_state == BOSS or game_state == LEVEL_COMPLETE:
                    game_state = WORLD_MAP
                elif game_state == WORLD_MAP:
                    game_state = MAIN_OVERWORLD
            elif event.key == pygame.K_LEFT and game_state == MAIN_OVERWORLD:
                # Navigate left on overworld
                for i in range(len(overworld_world_nodes)):
                    overworld_world_nodes[i].selected = False
                if selected_world > 1:
                    selected_world -= 1
                overworld_world_nodes[selected_world-1].selected = True
            elif event.key == pygame.K_RIGHT and game_state == MAIN_OVERWORLD:
                # Navigate right on overworld
                for i in range(len(overworld_world_nodes)):
                    overworld_world_nodes[i].selected = False
                if selected_world < 5:
                    selected_world += 1
                overworld_world_nodes[selected_world-1].selected = True
            elif event.key == pygame.K_UP and game_state == MAIN_OVERWORLD:
                # Navigate up on overworld
                for i in range(len(overworld_world_nodes)):
                    overworld_world_nodes[i].selected = False
                if selected_world == 3:
                    selected_world = 2
                elif selected_world == 4:
                    selected_world = 3
                elif selected_world == 5:
                    selected_world = 4
                overworld_world_nodes[selected_world-1].selected = True
            elif event.key == pygame.K_DOWN and game_state == MAIN_OVERWORLD:
                # Navigate down on overworld
                for i in range(len(overworld_world_nodes)):
                    overworld_world_nodes[i].selected = False
                if selected_world == 1:
                    selected_world = 4
                elif selected_world == 2:
                    selected_world = 3
                elif selected_world == 3:
                    selected_world = 5
                overworld_world_nodes[selected_world-1].selected = True
    
    # Fill background based on game state
    if game_state == INTRO:
        screen.fill(BLACK)
    elif game_state == MAIN_OVERWORLD:
        # Draw a starry background for the main overworld
        screen.fill((0, 0, 50))
        # Draw stars
        for i in range(100):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 47) % SCREEN_HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)
    elif game_state == WORLD_MAP:
        # Background based on current world
        if current_world == 1:
            screen.fill((135, 206, 235))  # Sky blue for world 1
        elif current_world == 2:
            screen.fill((210, 180, 140))  # Sandy color for world 2
        elif current_world == 3:
            screen.fill((100, 149, 237))  # Cornflower blue for world 3
        elif current_world == 4:
            screen.fill((173, 216, 230))  # Light blue for world 4
        else:
            screen.fill((255, 140, 0))    # Dark orange for world 5
    elif game_state == GAME or game_state == BOSS:
        # Background based on current world
        if current_world == 1:
            screen.fill((135, 206, 235))  # Sky blue for world 1
        elif current_world == 2:
            screen.fill((210, 180, 140))  # Sandy color for world 2
        elif current_world == 3:
            screen.fill((100, 149, 237))  # Cornflower blue for world 3
        elif current_world == 4:
            screen.fill((173, 216, 230))  # Light blue for world 4
        else:
            screen.fill((255, 140, 0))    # Dark orange for world 5
    else:
        screen.fill(BLACK)
    
    # Game state handling
    if game_state == INTRO:
        # Draw intro screens
        intro_timer += 1
        
        if intro_timer < 180:  # SamSoft presents (3 seconds)
            # SamSoft logo (similar to HAL Labs style)
            pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 200))
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 140, SCREEN_HEIGHT//2 - 90, 280, 180))
            
            text = title_font.render("SamSoft", True, BLUE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 70))
            
            text = subtitle_font.render("presents", True, BLUE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
            
        elif intro_timer < 360:  # Nintendo co-presents (3 seconds)
            # Nintendo logo
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 200))
            
            text = title_font.render("Nintendo", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 70))
            
            text = subtitle_font.render("co-presents", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
            
        else:  # Fade to main overworld
            game_state = MAIN_OVERWORLD
            
    elif game_state == MAIN_OVERWORLD:
        # Draw main overworld
        text = title_font.render("SUPER MARIO 2D WORLD", True, YELLOW)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 50))
        
        text = subtitle_font.render("Select a World", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100))
        
        # Draw paths between worlds
        # Path from World 1 to World 2
        pygame.draw.line(screen, GRAY, (230, 240), (350, 190), 3)
        # Path from World 2 to World 3
        pygame.draw.line(screen, GRAY, (430, 190), (550, 240), 3)
        # Path from World 3 to World 4
        pygame.draw.line(screen, GRAY, (550, 280), (430, 340), 3)
        # Path from World 4 to World 5
        pygame.draw.line(screen, GRAY, (350, 340), (230, 390), 3)
        
        # Draw world nodes
        for node in overworld_world_nodes:
            node.draw(screen)
        
        # Draw instructions
        text = normal_font.render("Use Arrow Keys to navigate, SPACE to select", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT - 50))
        
        # Draw player progress
        text = normal_font.render(f"Worlds Completed: {current_world - 1}/5", True, WHITE)
        screen.blit(text, (20, 20))
        
    elif game_state == WORLD_MAP:
        # Draw world map
        text = title_font.render(f"WORLD {current_world}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 30))
        
        text = subtitle_font.render(f"{world_names[current_world-1]}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 80))
        
        # Draw nodes
        for node in world_map_nodes:
            node.draw(screen)
            if node.level_num == current_level:
                # Highlight current level
                pygame.draw.rect(screen, YELLOW, (node.x-5, node.y-5, node.width+10, node.height+10), 3)
        
        # Draw paths between levels
        for i in range(len(world_map_nodes) - 1):
            start_x = world_map_nodes[i].x + world_map_nodes[i].width
            start_y = world_map_nodes[i].y + world_map_nodes[i].height // 2
            end_x = world_map_nodes[i+1].x
            end_y = world_map_nodes[i+1].y + world_map_nodes[i+1].height // 2
            pygame.draw.line(screen, GRAY, (start_x, start_y), (end_x, end_y), 3)
        
        # Draw instructions
        text = normal_font.render("Press SPACE to start level or ESC to return to overworld", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT - 50))
        
    elif game_state == LEVEL_START:
        # Level start screen
        level_start_timer += 1
        
        # Draw level info
        text = title_font.render(f"World {current_world}-{current_level}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        text = subtitle_font.render(f"{world_names[current_world-1]}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2))
        
        if level_start_timer > 90:  # Show for 1.5 seconds
            game_state = GAME
            
    elif game_state == GAME:
        # Handle player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player.speed
            player.direction = -1
            # Scroll camera
            if player.x < camera_x + SCREEN_WIDTH//4 and camera_x > 0:
                camera_x = max(0, camera_x - player.speed)
        if keys[pygame.K_RIGHT]:
            player.x += player.speed
            player.direction = 1
            # Scroll camera
            if player.x > camera_x + SCREEN_WIDTH//2 and camera_x < 2000 - SCREEN_WIDTH:
                camera_x = min(2000 - SCREEN_WIDTH, camera_x + player.speed)
                
        # Update game objects
        player.update(platforms, enemies)
        
        for enemy in enemies:
            enemy.update(platforms)
            
        for coin in coins:
            coin.update()
            
        for powerup in powerups:
            powerup.update(platforms)
            
        # Check coin collection
        for coin in coins:
            if (not coin.collected and 
                player.x < coin.x + coin.width and 
                player.x + player.width > coin.x and
                player.y < coin.y + coin.height and 
                player.y + player.height > coin.y):
                coin.collected = True
                player.coins += 1
                player.score += 100
                if player.coins >= 100:  # 1-up at 100 coins
                    player.coins = 0
                    player.lives += 1
                
        # Check powerup collection
        for powerup in powerups:
            if (not powerup.collected and 
                player.x < powerup.x + powerup.width and 
                player.x + player.width > powerup.x and
                player.y < powerup.y + powerup.height and 
                player.y + player.height > powerup.y):
                powerup.collected = True
                if powerup.type == "mushroom" and player.powerup == "small":
                    player.powerup = "big"
                elif powerup.type == "fireflower":
                    player.powerup = "fire"
                
        # Check enemy collisions
        for enemy in enemies[:]:
            if (enemy.is_alive and
                player.x < enemy.x + enemy.width and 
                player.x + player.width > enemy.x and
                player.y < enemy.y + enemy.height and 
                player.y + player.height > enemy.y):
                
                # Player jumps on enemy
                if player.vel_y > 0 and player.y + player.height < enemy.y + enemy.height/2:
                    enemy.is_alive = False
                    player.vel_y = -10  # Bounce
                    player.score += 200
                # Player gets hit
                elif player.invincible == 0:
                    if player.powerup == "fire":
                        player.powerup = "big"
                    elif player.powerup == "big":
                        player.powerup = "small"
                    else:
                        player.lives -= 1
                    player.invincible = 60
                    
        # Check if player reached flagpole
        if flagpole and not level_complete:
            if (player.x + player.width > flagpole.x and 
                player.x < flagpole.x + flagpole.width):
                level_complete = True
                level_timer = 0
                flagpole.flag_raised = True
                player.score += 1000  # Level completion bonus
                
        # Handle level completion
        if level_complete:
            level_timer += 1
            if level_timer > 120:  # 2 seconds delay
                level_complete = False
                if current_level < 4:
                    current_level += 1
                    game_state = LEVEL_START
                    level_start_timer = 0
                else:
                    current_level = 1
                    current_world += 1
                    if current_world > 5:
                        game_state = VICTORY
                    else:
                        game_state = BOSS
                create_level(current_world, current_level)
                create_world_map()
                
        # Check for game over
        if player.lives <= 0:
            game_state = GAME_OVER
            
        # Draw game objects with camera offset
        for platform in platforms:
            # Only draw platforms in view
            if platform.x + platform.width > camera_x and platform.x < camera_x + SCREEN_WIDTH:
                platform.draw(screen)
            
        for coin in coins:
            if coin.x > camera_x and coin.x < camera_x + SCREEN_WIDTH:
                coin.draw(screen)
            
        for powerup in powerups:
            if powerup.x > camera_x and powerup.x < camera_x + SCREEN_WIDTH:
                powerup.draw(screen)
                
        for enemy in enemies:
            if enemy.x > camera_x and enemy.x < camera_x + SCREEN_WIDTH:
                enemy.draw(screen)
                
        # Draw flagpole if in view
        if flagpole and flagpole.x > camera_x and flagpole.x < camera_x + SCREEN_WIDTH:
            flagpole.draw(screen)
            
        # Draw player (adjust position based on camera)
        player.draw(screen)
        
        # Draw HUD
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 30))
        text = normal_font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(text, (10, 5))
        text = normal_font.render(f"Coins: {player.coins}", True, YELLOW)
        screen.blit(text, (200, 5))
        text = normal_font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(text, (350, 5))
        text = normal_font.render(f"World {current_world}-{current_level}", True, WHITE)
        screen.blit(text, (500, 5))
        
    elif game_state == BOSS:
        # Handle player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= player.speed
            player.direction = -1
        if keys[pygame.K_RIGHT]:
            player.x += player.speed
            player.direction = 1
                
        # Update game objects
        player.update(platforms, enemies)
        
        if boss:
            boss.update(player, platforms)
            
        for coin in coins:
            coin.update()
            
        for powerup in powerups:
            powerup.update(platforms)
            
        # Check coin collection
        for coin in coins:
            if (not coin.collected and 
                player.x < coin.x + coin.width and 
                player.x + player.width > coin.x and
                player.y < coin.y + coin.height and 
                player.y + player.height > coin.y):
                coin.collected = True
                player.coins += 1
                player.score += 100
                if player.coins >= 100:  # 1-up at 100 coins
                    player.coins = 0
                    player.lives += 1
                
        # Check powerup collection
        for powerup in powerups:
            if (not powerup.collected and 
                player.x < powerup.x + powerup.width and 
                player.x + player.width > powerup.x and
                player.y < powerup.y + powerup.height and 
                player.y + player.height > powerup.y):
                powerup.collected = True
                if powerup.type == "mushroom" and player.powerup == "small":
                    player.powerup = "big"
                elif powerup.type == "fireflower":
                    player.powerup = "fire"
                
        # Check boss collision
        if boss and player.invincible == 0:
            if (player.x < boss.x + boss.width and 
                player.x + player.width > boss.x and
                player.y < boss.y + boss.height and 
                player.y + player.height > boss.y):
                
                # Player gets hit
                if player.powerup == "fire":
                    player.powerup = "big"
                elif player.powerup == "big":
                    player.powerup = "small"
                else:
                    player.lives -= 1
                player.invincible = 60
                
            # Check if player jumps on boss (does damage)
            if player.vel_y > 0 and player.y + player.height < boss.y + boss.height/2:
                boss.health -= 1
                player.vel_y = -10  # Bounce
                player.score += 500
                
                # Check if boss is defeated
                if boss.health <= 0:
                    boss_defeated = True
                    level_timer = 0
                    player.score += 5000  # Boss defeat bonus
                    
        # Handle boss defeat
        if boss_defeated:
            level_timer += 1
            if level_timer > 180:  # 3 seconds delay
                boss_defeated = False
                current_world += 1
                current_level = 1
                if current_world > 5:
                    game_state = VICTORY
                else:
                    game_state = MAIN_OVERWORLD
                create_level(current_world, current_level)
                create_world_map()
                create_main_overworld()
                
        # Check for game over
        if player.lives <= 0:
            game_state = GAME_OVER
            
        # Draw game objects
        for platform in platforms:
            platform.draw(screen)
            
        for coin in coins:
            coin.draw(screen)
            
        for powerup in powerups:
            powerup.draw(screen)
                
        if boss:
            boss.draw(screen)
            
        # Draw player
        player.draw(screen)
        
        # Draw HUD
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 30))
        text = normal_font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(text, (10, 5))
        text = normal_font.render(f"Coins: {player.coins}", True, YELLOW)
        screen.blit(text, (200, 5))
        text = normal_font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(text, (350, 5))
        text = normal_font.render(f"Boss: {boss_names[current_world-1]}", True, WHITE)
        screen.blit(text, (500, 5))
        
        # Draw boss health bar
        if boss:
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - 100, 40, 200, 20))
            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - 100, 40, 200 * (boss.health / 5), 20))
            text = small_font.render(f"Health: {boss.health}/5", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 42))
        
    elif game_state == GAME_OVER:
        # Draw game over screen
        text = title_font.render("GAME OVER", True, RED)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        text = subtitle_font.render(f"Final Score: {player.score}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        text = normal_font.render("Press R to restart or ESC to return to overworld", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 80))
        
    elif game_state == VICTORY:
        # Draw victory screen
        text = title_font.render("CONGRATULATIONS!", True, YELLOW)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        
        text = subtitle_font.render("You have completed all worlds!", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 30))
        
        text = subtitle_font.render(f"Final Score: {player.score}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 30))
        
        text = normal_font.render("Press R to play again or ESC to return to overworld", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 100))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
