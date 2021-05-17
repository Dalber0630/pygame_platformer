# Imports
import pygame
import random
vec = pygame.math.Vector2

# Window settings
GRID_SIZE = 64
WIDTH = 30 * GRID_SIZE
HEIGHT = 16 * GRID_SIZE
TITLE = "FRICTION"
FPS = 60


# Create window
pygame.init()
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (0, 150, 255)

# Stages
START = 0
PLAYING = 1
LOSE = 2


# Load fonts
font_xl = pygame.font.Font("assets/fonts/Dinomouse-Regular.otf", 96)
font_lg = pygame.font.Font("assets/fonts/Dinomouse-Regular.otf", 64)
font_md = pygame.font.Font("assets/fonts/Dinomouse-Regular.otf", 32)
font_sm  = pygame.font.Font("assets/fonts/Dinomouse-Regular.otf", 24)

# Load images
enemy_img = pygame.image.load('assets/images/characters/enemy1a.png').convert_alpha()
hero_img = pygame.image.load('assets/images/characters/player_idle.png').convert_alpha()
grass_dirt_img = pygame.image.load('assets/images/tiles/grass_dirt.png').convert_alpha()
platform_img = pygame.image.load('assets/images/tiles/block.png').convert_alpha()
gem_img = pygame.image.load('assets/images/items/gem.png').convert_alpha()
heart_img = pygame.image.load('assets/images/items/heart.png').convert_alpha()

# Load sounds

#settings
gravity = 0.75
terminal_velocity = 35
max_speed = 15
max_mass = 30
friction = -0.15
accel = 2.15


# Game classes

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x * GRID_SIZE + GRID_SIZE // 2
        self.rect.centery = y * GRID_SIZE + GRID_SIZE // 2
        self.vx = 0
        self.vy = 0
    def apply_gravity(self):
        self.vy += gravity
        
        if self.vy > terminal_velocity:
            self.vy = terminal_velocity
            
class Hero(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.mass = 0
        self.speed = 7.5
        self.jump_power = 19
        self.gems = 0
        self.jump_cnt = 0
        self.hurt_timer = 0 
        self.hearts = 3
        self.score = 0
        
        self.pos = vec(self.rect.centerx, self.rect.centery)
        self.vel = vec(0,0)
        self.acc = vec(0,0)


    def apply_mass(self):
        pass
##    def move_right(self):
##        #self.vx = self.speed
##    	self.acc.x = -accel
##    def move_left(self):
##    	#self.vx = -self.speed
##    	self.acc.x = accel

    def stop(self):
        self.vx = 0 
    
    def jump(self):
        if self.jump_cnt < 2:
            self.jump_cnt += 1 
            self.rect.y += 2
            hits = pygame.sprite.spritecollide(self, platforms, False)
            self.rect.y -= 2
            
            if len(hits) > 0:
                self.jump_cnt = 0
                self.vel.y = -self.jump_power

            if self.jump_cnt < 2 and len(hits) < 1:
                self.rect.y += 2                
                self.rect.y -= 2
                self.vel.y = -self.jump_power
                self.jump_cnt += 1
                    


    def move_and_check_blocks(self):
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for hit in hits:
            if self.vx > 0:
                self.rect.right = hit.rect.left
            elif self.vx < 0:
                self.rect.left = hit.rect.right

        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for hit in hits:
            if self.vel.y > 0:
                hero.jump_cnt = 0
                self.pos.y = hit.rect.top
                self.vel.y = 0
            elif self.vy < 0:
                hero.jump_cnt = 0
                self.rect.top = hit.rect.bottom

            self.vy = 0

        pickups = pygame.sprite.spritecollide(self, gems, True)

        for pick in pickups:
            pick.apply(self)

    def check_enemies(self):
        hits = pygame.sprite.spritecollide(self, enemies, False)

        for enemy in hits:
            if self.hurt_timer == 0:
                self.hearts -=1
                print(self.hearts)
                print("Oof!") #playsoundhere
                self.hurt_timer = 0.35 * FPS
            else:
                self.hurt_timer -= 1

                if self.hurt_timer < 0:
                    self.hurt_timer = 0
            if self.hearts < 1:
                self.kill()
                print("DEAD")
            if self.rect.x < enemy.rect.x:
                self.vx -= self.speed
            elif self.rect.x > enemy.rect.x:
                self.vx = self.speed
                
            if self.rect.y < enemy.rect.y:
                self.vy = -5
                enemy.kill()
            elif self.rect.y > enemy.rect.y:
                self.vy = 5
                

    def check_world_edges(self):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = -HEIGHT
            #self.vy = -self.jump_power

    def update(self):
        self.apply_gravity()
        self.check_world_edges()
        self.check_enemies()
        self.acc = vec(0, gravity)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -accel
        if keys[pygame.K_RIGHT]:
            self.acc.x = accel
        # apply friction
        self.acc.x += self.vel.x * friction
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos
        self.move_and_check_blocks()


class Enemy(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.vx = -2 
        self.vy = 0

    def reverse(self):
        self.vx *= -1
        
    def move_and_check_blocks(self):
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for hit in hits:
            if self.vx > 0:
                self.rect.right = hit.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = hit.rect.right
                self.reverse()

        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for hit in hits:
            if self.vy > 0:
                self.rect.bottom = hit.rect.top
            elif self.vy < 0:
                self.rect.top = hit.rect.bottom

            self.vy = 0
         
    def check_world_edges(self):
        if self.rect.left < 0:
            self.reverse()
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.reverse()

    def check_platform_edges(self):
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 2

        must_reverse = True

        for platform in hits:
            if self.vx < 0 and platform.rect.left <= self.rect.left:
                must_reverse = False
            elif self.vx > 0 and platform.rect.right >= self.rect.right:
                must_reverse = False

        if must_reverse:
            self.reverse()
    
    def update(self):
        self.move_and_check_blocks()
        self.check_world_edges()
        self.apply_gravity()
        self.check_platform_edges()
    	
    	 
class Platforms(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Gem(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, hero):
        if hero.speed != max_speed:
            hero.speed += 2
        else:
            hero.speed = max_speed

        hero.gems += 1
        hero.mass += 1
        hero.score += 1

# Helper Functions
def show_start_screen():
    text = font_xl.render(TITLE, True, WHITE)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2 + 8
    screen.blit(text, rect)

    text = font_sm.render("Press any key to start.", True, WHITE)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, HEIGHT // 2 + 8
    screen.blit(text, rect)

def show_lose_screen():
    text = font_lg.render("Game Over", True, WHITE)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2 + 8
    screen.blit(text, rect)

    text = font_sm.render("Press 'r' to play again.", True, WHITE)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, HEIGHT // 2 + 8
    screen.blit(text, rect)

def show_hud():
    text = font_md.render(str(hero.score), True, WHITE)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, 16
    screen.blit(text, rect)

    screen.blit(gem_img, [WIDTH - 120, 0])
    text = font_sm.render("x" + str(hero.gems), True, WHITE)
    rect = text.get_rect()
    rect.topleft = WIDTH - 60, 16
    screen.blit(text, rect)

    for i in range(hero.hearts):
        x = i * 36 + 16
        y = 16
        screen.blit(heart_img, [x, y])

# Setup
def setup():
    global stage, platforms, enemies, player, gems, hero
    
    enemies = pygame.sprite.Group()
    player = pygame.sprite.GroupSingle()
    platforms = pygame.sprite.Group()
    gems = pygame.sprite.Group()


    start = (3, 7)

    enemy_locs = [(11, 7)]

    for loc in enemy_locs:
        x = loc[0]
        y = loc[1]
        e = Enemy(x, y, enemy_img)
        enemies.add(e)

    hero = Hero(start[0], start[1], hero_img)
    player.add(hero)

    gem_locs = [(7,2), (12, 7)]

    for loc in gem_locs:
        x = loc[0]
        y = loc[1]
        g = Gem(x, y, gem_img)
        gems.add(g)

    grass_locs = [[0,8], [1,8], [2,8], [3,8], [4,8],
                  [5,8], [6,8], [7,8], [8,8], [9,8],
                  [10,8], [11,8], [12,8],[13,8], [14,8],
                  [15,8], [16,8], [17,8], [18,8],[19,8], [20,8],
                  [21,8], [22,8], [23,8], [24,8],[25,8], [26,8],
                  [27,8],[28,8],[29,8], [30,8],
                  [31,8]]

    for loc in grass_locs:
        x = loc[0]
        y = loc[1]
        p = Platforms(x, y, grass_dirt_img)
        platforms.add(p)

    platform_locs = [[7,5], [8,5], [9,5], [13,2], [14,2], [15,2]]

    for loc in platform_locs:
        x = loc[0]
        y = loc[1]
        p = Platforms(x, y, platform_img)
        platforms.add(p)


    stage = START

# Game loop
clock = pygame.time.Clock()
timer = 0
dt = 0
running = True
setup()

while running:
    # Input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if stage == START:
                stage = PLAYING
            elif stage == PLAYING:
                if event.key == pygame.K_SPACE:
                    hero.jump()
                    
            elif stage == LOSE:
                if event.key == pygame.K_r:
                    setup()

    # Game logic
    if stage == PLAYING:
        player.update()
        enemies.update()

        if hero.hearts == 0:
            stage = LOSE
    
    # Drawing code
    screen.fill(SKY_BLUE)
    player.draw(screen)
    enemies.draw(screen)
    platforms.draw(screen)
    gems.draw(screen)
    show_hud()

    if stage == START:
        show_start_screen()
    elif stage == LOSE:
        show_lose_screen()
        
    # Update screen
    pygame.display.update()


    # Limit refresh rate of game loop 
    clock.tick(FPS)


# Close window and quit
pygame.quit()

