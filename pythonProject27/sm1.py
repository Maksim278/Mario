import pygame
import json
pygame.init()

with open('lvl/lvl1.json', 'r') as file:
    world_data = json.load(file)

height = 800
width = 800
clock = pygame.time.Clock()
fps = 60
tile_size = 40
game_over = 0

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Platformer')
bg_image = pygame.image.load('image/bg5.png')
bg_rect = bg_image.get_rect()

run = True

class World:
    def __init__(self, data):
        dirt_img = pygame.image.load('image/dirt.png')
        grass_img = pygame.image.load('image/grass.png')
        self.tile_list = []
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1 or tile == 2:
                    images = {1: dirt_img, 2: grass_img}
                    img = pygame.transform.scale(images[tile], (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                elif tile == 3:
                    lava = Lava(col_count * tile_size,
                                row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Button:
    def __init__(self, x, y, image):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        action = False
        if self.rect.colliderect(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image,self.rect)
        return action


class Player:
    def __init__(self):
        self.image = pygame.image.load('image/player1.png')
        self.image = pygame.transform.scale(self.image, (35, 70))
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = 690
        self.gravity = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.jump = False
        self.image_right = []
        self.image_left = []
        self.index = 0
        self.counter = 0
        self.direction = 0
        self.alive = True
        self.death_image = pygame.image.load('image/ghost.png')
        self.death_image = pygame.transform.scale(self.death_image, (35, 70))

        for num in range(1, 3):
            img_right = pygame.image.load(f'image/player{num}.png')
            img_right = pygame.transform.scale(img_right, (35, 70))
            img_left = pygame.transform.flip(img_right, True, False)
            self.image_right.append(img_right)
            self.image_left.append(img_left)

        self.image = self.image_right[self.index]

    def update(self):
        global game_over
        x = 0
        y = 0
        walk_speed = 10

        if self.alive:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and  self.jump == False:
                self.gravity = -15
                self.jump = True
            if key[pygame.K_LEFT]:
                x -= 5
                self.direction = -1
                self.counter += 1
            if key[pygame.K_RIGHT]:
                x += 5
                self.direction = 1
                self.counter += 1
            if self.counter > walk_speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.image_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.image_right[self.index]
                else:
                    self.image = self.image_left[self.index]

            self.rect.x += x
            self.rect.y += y
            self.gravity += 1
            if self.gravity > 10:
                self.gravity = 10
            y += self.gravity
            if self.rect.bottom > height:
                self.rect.bottom = height

            if pygame.sprite.spritecollide(self, lava_group, False):
                self.alive = False
                game_over = -1

            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):

                    x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + y, self.width, self.height):

                    if self.gravity < 0:
                        y = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    elif self.gravity >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.gravity = 0
                        self.jump = False

        else:
            self.image = self.death_image

        screen.blit(self.image, self.rect)

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load('image/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size/ 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
lava_group = pygame.sprite.Group()


start = Button
exit = Button
restart_button = Button(width // 2, height // 2, 'image/restart.png')
world = World(world_data)
player = Player()
while run:
    clock.tick(fps)
    screen.blit(bg_image, bg_rect)
    world.draw()

    if game_over == -1:
        if restart_button.draw():
            player = Player()
            world = World(world_data)
            game_over = 0

    lava_group.draw(screen)
    lava_group.update()
    player.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()