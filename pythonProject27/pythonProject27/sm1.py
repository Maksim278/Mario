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
level = 2
max_level = 2
live = 2
score = 0

def reset_lvl():
    player.rect.x = 100
    player.rect.y = height - 130
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()
    with open(f'lvl/lvl{level}.json', 'r') as file:
        world_data = json.load(file)
    world = World(world_data)
    return world

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Platformer')
bg_image = pygame.image.load('image/bg5.png')
bg_rect = bg_image.get_rect()

pygame.mixer.music.load('sound/funny-bgm-240795.mp3')
pygame.mixer.music.play(-1, 0, 0)
pygame.mixer.music.set_volume(0.3)
coin_sound = pygame.mixer.Sound('sound/coin.wav')
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
                elif tile == 5:
                    exit = Exit(col_count * tile_size,
                                row_count * tile_size + (tile_size // 2))
                    exit_group.add(exit)
                elif tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2),
                                row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
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
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, self.rect)
        return action

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('image/door2.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('image/coin.png')
        self.image = pygame.transform.scale(image, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

def draw_coin(text, color, size, x, y):
    font = pygame.font.SysFont('Arial', size)
    img = font.render(text, True, color)
    screen.blit(img ,(x, y))

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
        global live
        x = 0
        y = 0
        walk_speed = 10

        if self.alive:
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and  self.jump == False:
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

            self.gravity += 1
            if self.gravity > 10:
                self.gravity = 10
            y += self.gravity
            if self.rect.bottom > height:
                self.rect.bottom = height

            if pygame.sprite.spritecollide(self, lava_group, False):
                live -= 1
                self.alive = False
                game_over = -1


            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

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
            self.rect.x += x
            self.rect.y += y

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
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
start_button = Button(width // 2 - 150, height // 2, 'image/start.png')
exit_button = Button(width // 2 + 150, height // 2, 'image/exit.png')
restart_button = Button(width // 2, height // 2, 'image/restart.png')
world = World(world_data)
main_menu = True
player = Player()
while run:
    screen.blit(bg_image, bg_rect)
    clock.tick(fps)
    if main_menu:
        if start_button.draw():
            main_menu = False
            live = 2
            level = 1
            world = reset_lvl()
        if exit_button.draw():
            run = False
    else:
        world.draw()
        player.update()
        exit_group.draw(screen)
        coin_group.draw(screen)
        lava_group.draw(screen)
        lava_group.update()
        draw_coin(str(score), (255, 255, 255), 30, 10, 10)

        if pygame.sprite.spritecollide(player, coin_group, True):
            score += 1
            coin_sound.play()
            print(score)

        if game_over == -1:
            if restart_button.draw():
                player = Player()
                #world = World(world_data)
                world = reset_lvl()
                game_over = 0
            if live == -1:
                print('you loos')
                main_menu = True
                score = 0


        if game_over == 1:
           game_over = 0
           if level < max_level:
               level += 1
               world = reset_lvl()
           else:
               print('win')
               main_menu = True
               score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
