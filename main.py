import pygame
import random
import button
import csv
import os

pygame.init()

#---setting up program---
#Changes the title of the program
pygame.display.set_caption("game")

#screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #Creates the game window

clock = pygame.time.Clock() #initialises a frame cap
FPS = 60


#defining game variables
GRAVITY = 0.7
ROWS = 16
COLUMN = 120
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 8
start_menu = True
level_scroll = 0
level_scroll_threshold = 400
end_scroll = 0
currentLevel = 1  #this increases as levels are being completed

#defining player's action by variables
moving_left = False
moving_right = False
shooting = False
shootCooldown = 0


#---loading images---
#item/projectile images
bullet_img = pygame.image.load('images/items/bullet.png').convert_alpha()
correctcoin_img = pygame.image.load('images/items/Ccoin.png').convert_alpha()
wrongcoin_img = pygame.image.load('images/items/Wcoin.png').convert_alpha()
spike_img = pygame.image.load('images/items/spike.png').convert_alpha()

#button images
start_img = pygame.image.load('images/button/start_button.png').convert_alpha()
exit_img = pygame.image.load('images/button/exit_button.png').convert_alpha()
restart_img = pygame.image.load('images/button/restart_button.png').convert_alpha()

#images for map render
image_list = []
for x in range(TILE_TYPES):
    image = pygame.image.load(f'images/tiles/{x}.png')
    image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
    image_list.append(image)
    

#defining constant (colour) variables
Background = (135, 201, 236)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
START_SCREEN = (251,233,195)


def drawBackground():
    screen.fill(Background)
    #pygame.draw.line(screen, BLACK, (0, 400), (SCREEN_WIDTH, 400))


#class/template of player/enemy object
class Player(pygame.sprite.Sprite): 
    def __init__(self, character_type, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.health = 100
        self.Maxhealth = self.health
        self.speed = speed
        self.shootCooldown = 0
        self.direction = 1
        self.flip = False
        self.animationList = []
        self.character_type = character_type
        self.jumping = False
        self.in_air = True
        self.vel_y = 0
        self.vel_x = 0
        self.frameIndex = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #ai specific variables as other variables are for both player and enemy
        self.movementCounter = 0
        self.enemyVision = pygame.Rect(0, 0, 100, 50)  #left, right, width, height
        self.idleState = False
        self.idleCounter = 0

        #animations         0       1       2
        animationTypes = ['idle', 'run', 'death']  #different types of actions the player/enemy does
        for type in animationTypes:
            temp = []  #resets list of stored images
            number_of_images = len(os.listdir(f'images/{self.character_type}/{type}'))  #gets info on how many items are in the file
            
            for i in range(number_of_images):  #loads all images and appends into temporary list
                a_img = pygame.image.load(f'images/{self.character_type}/{type}/{i}.png').convert_alpha()
                temp.append(a_img)
            self.animationList.append(temp)
        
        self.image = self.animationList[self.action][self.frameIndex] #brings image from requested file location e.g., from player or from enemy 
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.rect = self.image.get_rect() #creates a rectangle on the image
        self.rect.center = (x, y)
        


    #checks whether player is alive or not
    def update(self):
        self.updateAnimations()
        self.checkAlive()

        #bullet shooting cooldown update
        if self.shootCooldown > 0:
            self.shootCooldown -= 1

    
    #movement of either the player or enemy
    def movement(self, moving_left, moving_right):
        level_scroll = 0
        dx = 0
        dy = 0
        
        
        #left and right motion
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump and double jump states
        if self.jumping == True and self.alive == True:
            self.vel_y = -12
            self.jumping = False
            self.in_air = False

        #gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        
        #check collision with ground/tiles (new)    
        for tile in world.obstacles:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):  #collision check in x axis
                dx = 0
                
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):  #collision check in y axis
                if self.vel_y < 0:  #collision check when jumping off tiles
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                    
                elif self.vel_y > 0 or self.vel_y == 0:  #collision check when falling 
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
                
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):  #collision with exit door
            level_complete = True
            
        collected = False
        if pygame.sprite.spritecollide(player, correctcoin_group, False):  #checks collision between player and coin
            collected = True
            player.health += 5
            self.kill()
            
        #check collision on sides of screen so they won't go offscreen
        if self.character_type == 'player':
            if self.rect.right + dx > SCREEN_WIDTH:  #collision check on right side of screen
                dx =  SCREEN_WIDTH - self.rect.right
        
            elif self.rect.left + dx < 0:  #collision check on left side of screen
                dx = -self.rect.left
                
            elif self.rect.bottom > SCREEN_HEIGHT:  #collision check on bottom side of screen
                self.health = 0


        #updates player's rectangle
        self.rect.x += dx
        self.rect.y += dy
        
        #level scrolling depending on player position
        if self.character_type == 'player':
            #if the player goes far enough to the right, the screen moves towards the left
            if (self.rect.right > SCREEN_WIDTH - level_scroll_threshold and end_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH):  
                self.rect.x -= dx
                level_scroll = -dx
            #if the player goes far enough to the left, the screen moves towards the right
            elif self.rect.left < level_scroll_threshold and end_scroll > dx:
                self.rect.x -= dx
                level_scroll = -dx
                
        return level_scroll, level_complete, collected


    #player shoot
    def shooting(self):
        if self.shootCooldown == 0:
            self.shootCooldown = 40
            bullet = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)  #bullet's rectangle far enough from player's rectangle 
            bullet_group.add(bullet)


    def checkAlive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0
            self.update_action(2)  #death animation
            

    #ai for enemies in game
    def enemy_ai(self):
        dx = 0
        dy = 0

        if self.alive and player.alive: #checks if enemy and player is alive
            if self.idleState == False and random.randint(1, 255) == 1:  #random cycles between two values until 1 is reached
                self.idleState = True
                self.idleCounter = 30  #the enemy will stay stationary for this long
            
            if self.enemyVision.colliderect(player.rect):  #checks if one rectangle collides with player's rectangle
                self.shooting()

            else:
                if self.idleState == False:  #checks if enemy is not idle
                    if self.direction == 1:  #updates image when moving right
                     enemy_ai_moving_right = True
                    else:
                        enemy_ai_moving_right = False  #updates image when moving left
                    enemy_ai_moving_left = not enemy_ai_moving_right

                    self.movement(enemy_ai_moving_left, enemy_ai_moving_right)  #giving enemy movement
                    self.movementCounter += 1
                    
                    if self.movementCounter > TILE_SIZE:  #done to make enemy move at different direction and reset counter
                        self.direction *= -1
                        self.movementCounter *= -1
                    enemy.rect.x += dx  #updates enemy's rect
                    enemy.rect.y += dy

                    self.enemyVision.center = (self.rect.centerx + 70 * self.direction, self.rect.centery)  #places rectangle to center of enemy position

                else:  #enemy is idle
                    self.idleCounter -= 1
                    if self.idleCounter < 0:
                        self.idleState = False

        self.rect.x += level_scroll  #enemy scroll
        
        
    def updateAnimations(self):  #flips to next image in animation list
        cooldown = 50
        self.image = self.animationList[self.action][self.frameIndex]  #updates image on screen depending on the current index
        
        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frameIndex += 1  #goes to next index in animation list
            
            if self.frameIndex >= len(self.animationList[self.action]):  #if index counter is greater than length of list, then reset
                if self.action == 2:  #"death" action
                    self.frameIndex = len(self.animationList[self.action]) - 1
                else:
                    self.frameIndex = 0
    
    
    def update_action(self, new_action):  #updates so animation always start on first index of list after a new action is detected
        if new_action != self.action:
            self.action = new_action
            self.frameIndex = 0
            self.update_time = pygame.time.get_ticks()
        

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)  #loads player  image onto the screen

    #player's health bar
    def drawHealth(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health
        
        healthRatio = self.health / self.Maxhealth

        # "where to draw", "x and y coordinate", "width and height" #
        pygame.draw.rect(screen, RED, (self.x, self.y, 100, 20))  #red bar for total health
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 100 * healthRatio, 20))  #green bar for current health


#class for handling loading images for levels
class Map():
    def __init__(self):
        self.obstacles = []
        
    def process(self, data):  #iterates through list
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile == -1:  #represents empty space in csv file/levels
                    continue
                
                if tile >= 0:
                    image = image_list[tile]
                    image_rect = image.get_rect()
                    image_rect.x = x * TILE_SIZE
                    image_rect.y = y * TILE_SIZE
                    tile_data = (image, image_rect)
                    if tile >= 0 and tile <= 1:  #tiles dedicated for collisions
                        self.obstacles.append(tile_data)
                        
                    elif tile == 2:
                        coin = wrongCoin(image, x * TILE_SIZE, y * TILE_SIZE)
                        wrongcoin_group.add(coin)  #adds "wrongCoin" into group
                    
                    elif tile == 3:
                        exit_door = Exit(image, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit_door)  #adds "exit_door" into group
                    
                    elif tile == 4:
                        player = Player('player', x * TILE_SIZE, y * TILE_SIZE, 7)  #player spawn
                        
                    elif tile == 5:
                        enemy = Player('enemy', x * TILE_SIZE, y * TILE_SIZE, 2)  #enemy spawn
                        enemy_group.add(enemy)  #adds enemies into group
                        
                    elif tile == 6:
                        spike = Spike(image, x * TILE_SIZE, y * TILE_SIZE)
                        spike_group.add(spike)  #adds "spikes" into group
                        
                    elif tile == 7:
                        coin = correctCoin(image, x * TILE_SIZE, y * TILE_SIZE)
                        correctcoin_group.add(coin)  #adds "correctCoin" into group
                    
        return player
    
    def drawMap(self):  #draws the tiles onto the screen
        for tile in self.obstacles:
            tile[1][0] += level_scroll
            screen.blit(tile[0], tile[1])


def restart_level():
    bullet_group.empty()
    enemy_group.empty()
    exit_group.empty()
    correctcoin_group.empty()
    spike_group.empty()
    
    data = []
    for row in range(ROWS):
        r = [-1] * COLUMN
        data.append(r)
        
    return data


#classes for projectiles/items
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 4
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #movement of bullet
        self.rect.x += (self.direction * self.speed) + level_scroll
        #collision check with game window boundary
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:  #for testing, +100 for rect.left and -100 for rect.right
            self.kill()
        
        #collision on sprites
        #player sprite collision
        if pygame.sprite.spritecollide(player, bullet_group, False):  #sprite, other sprite, if item should be deleted or not from group
            if player.alive:
                player.health -= 10
                self.kill()

        #enemy sprite collision
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 20
                    self.kill()

class correctCoin(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += level_scroll

class wrongCoin(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    def update(self):
        self.rect.x += level_scroll
        if pygame.sprite.spritecollide(player, wrongcoin_group, False):  #checks collision between player and coin
            player.health = 0  #this will make the player.alive == False, so the level will reset

class Spike(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    def update(self):
        self.rect.x += level_scroll
        if pygame.sprite.spritecollide(player, spike_group, False):  #collision with spikes
            player.health -= 0.05
               
class Exit(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    def update(self):
        self.rect.x += level_scroll


#groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
correctcoin_group = pygame.sprite.Group()
wrongcoin_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()


#empty tile list
map_data = []
for row in range(ROWS):
    r = [-1] * COLUMN
    map_data.append(r)

#reading data from csv file
with open(f'Levels/level{currentLevel}.csv', newline = '') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            map_data[x][y] = int(tile)
#print(map_data) # - test if it works properly
world = Map()
player = world.process(map_data)


#creating buttons (x, y, image)
start_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 115, start_img)
exit_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 115, exit_img)
restart_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, restart_img)


#game loop
running = True
while running:
    clock.tick(FPS)  #value the game runs/updates at
    
    if start_menu == True:  #before level loads, menu is loaded
        screen.fill(START_SCREEN)
        #buttons added to screen
        if start_button.drawB(screen):
            start_menu = False

        if exit_button.drawB(screen):
            running = False
        
        
    else:
        drawBackground()  #calls function to draw bg
        world.drawMap()
        
        player.drawHealth(10, 10, player.health)
        player.update()
        player.draw()  #calls function to draw images from player class
        
        #update and draw groups
        for enemy in enemy_group:  #every enemy created can now be updated and drawn onto the screen as they're all put into one group
            enemy.enemy_ai()
            enemy.update()
            enemy.draw()
        bullet_group.update()
        bullet_group.draw(screen)
        correctcoin_group.update()
        correctcoin_group.draw(screen)
        wrongcoin_group.update()
        wrongcoin_group.draw(screen)
        exit_group.update()
        exit_group.draw(screen)
        spike_group.update()
        spike_group.draw(screen)


        #player action animation
        if player.alive:
            if moving_left or moving_right:
                player.update_action(1)  #running
            else:
                player.update_action(0)  #idle
            level_scroll, level_complete, collected = player.movement(moving_left, moving_right)  #player can move
            end_scroll -= level_scroll
            if shooting:
                player.shooting

            if level_complete == True or collected == True:  #checks if the player completed the level
                currentLevel += 1
                collected = False
                world_data = restart_level()
                with open(f'Levels/level{currentLevel}.csv', newline = '') as csvfile:
                    reader = csv.reader(csvfile, delimiter = ',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            map_data[x][y] = int(tile)
                world = Map()
                player = world.process(map_data)

            
                
        else:  #if not alive, player can restart the level
            level_scroll = 0
            if restart_button.drawB(screen):
                map_data = restart_level()  #empties list and appends the same items or values
                
                #reading data from csv file
                with open(f'Levels/level{currentLevel}.csv', newline = '') as csvfile:
                    reader = csv.reader(csvfile, delimiter = ',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            map_data[x][y] = int(tile)
                world = Map()
                player = world.process(map_data)
            elif exit_button.drawB(screen):
                running = False


    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:  #quits game
            running = False
            
        #keyboard inputs when pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  #moves player to left
                moving_left = True
                
            if event.key == pygame.K_RIGHT:  #moves player to right
                moving_right = True
                
            if event.key == pygame.K_UP and player.alive:
                player.jumping = True
                
            if event.key == pygame.K_ESCAPE:
                restart_button.drawB(screen)
                exit_button.drawB(screen)
                if restart_button.drawB(screen):
                    map_data = restart_level()  #empties list and appends the same items or values
                
                    #reading data from csv file
                    with open(f'Levels/level{currentLevel}.csv', newline = '') as csvfile:
                        reader = csv.reader(csvfile, delimiter = ',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                map_data[x][y] = int(tile)
                    world = Map()
                    player = world.process(map_data)
                    
                elif exit_button.drawB(screen):
                    running = False
                    
            if event.key == pygame.K_e:
                shooting = True


            #keyboard inputs when released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:  #stops player moving left
                moving_left = False
                
            if event.key == pygame.K_RIGHT:  #stops player moving right
                moving_right = False
                
            if event.key == pygame.K_UP: 
                moving_right = False
                
            if event.key == pygame.K_e:  #stops player from shooting
                shooting = False


    pygame.display.update()  #updates the window all the time

pygame.quit()  #uninitialises all pygame modules, or it stops the program
