import pygame
import json

pygame.init()

width = 800
height = 800
tile_size = 40

game_over = 0
lives = 3
score = 0

WHITE = (255, 255, 255)

clock = pygame.time.Clock()
fps = 60

display = pygame.display.set_mode((width, height))
pygame.display.set_caption("Platformer")

bg = pygame.image.load("images/bg3.png")
bg_rect = bg.get_rect()

jumpSound = pygame.mixer.Sound("music/jump.wav")
game_overSound = pygame.mixer.Sound("music/game_over.wav")
coinSound = pygame.mixer.Sound("music/coin.wav")

level = 1
max_level = 4


class World:
    def __init__(self, data):
        lava_img = pygame.image.load("images/tile6.png")
        grass_img = pygame.image.load("images/tile7.png")
        lavaBlock_img = pygame.image.load("images/tile12.png")
        stoneBlock_img = pygame.image.load("images/tile10.png")
        exitDoor_img = pygame.image.load("images/exit.png")
        coin_img = pygame.image.load("images/coin.png")
        images = {1: stoneBlock_img, 2: grass_img,
                  3: lava_img, 4: lavaBlock_img,
                  5: exitDoor_img, 6: coin_img}

        self.tile_list = []
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile in [1, 2, 4]:
                    img = pygame.transform.scale(images[tile],
                                                 (tile_size, tile_size))
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
                                row_count * tile_size)
                    exit_group.add(exit)
                elif tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2),
                                row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                col_count += 1
            row_count += 1

    def draw(self):
        for every_tile in self.tile_list:
            display.blit(every_tile[0], every_tile[1])


class Button:
    def __init__(self, x, y, fileName):
        self.image = pygame.image.load(fileName)
        self.image = pygame.transform.scale(self.image, (120, 50))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        action = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        display.blit(self.image, self.rect)
        return action


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        lava_img = pygame.image.load("images/tile6.png")
        self.image = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


lava_group = pygame.sprite.Group()


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("images/exit.png")
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size * 1.25))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


exit_group = pygame.sprite.Group()


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("images/coin.png")
        self.image = pygame.transform.scale(self.image, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


coin_group = pygame.sprite.Group()


class Player:
    def __init__(self, fileName, imageSize):
        # self.font_style = pygame.font.SysFont("comicsans", 20)
        # livesAmount = self.font_style.render(f"Lives: {self.playerLives}", True, RED)
        self.gravity = 0
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.direction = 0
        self.jumped = False
        for num in range(1, 5):
            img_right = pygame.image.load(f"images/player{num}.png")
            img_right = pygame.transform.scale(img_right, imageSize)
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = 70
        self.rect.y = height - 130
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.ghost_img = pygame.image.load("images/ghost.png")

    def update(self):
        global game_over
        global main_menu
        x = 0
        y = 0
        walk_speed = 10
        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_a]:
                x -= 5
                self.direction = -1
                self.counter += 1
            if key[pygame.K_d]:
                x += 5
                self.direction = 1
                self.counter += 1
            if self.counter > walk_speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]
            if (key[pygame.K_SPACE] or key[pygame.K_w]) and not self.jumped:
                self.gravity = -15
                self.jumped = True
                jumpSound.play()
            self.gravity += 1
            if self.gravity > 10:
                self.gravity = 10
            y += self.gravity
            for tile in world1.tile_list:
                if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                    x = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + y, self.width, self.height):
                    if self.gravity < 0:
                        y = tile[1].bottom - self.rect.top
                        self.gravity = 0
                    elif self.gravity >= 0:
                        y = tile[1].top - self.rect.bottom
                        self.gravity = 0
                        self.jumped = False
            if pygame.sprite.spritecollide(self, lava_group, False):
                # self.playerLives -= 1
                game_over = -1
                self.image = self.ghost_img
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
                # self.playerLives = 5

            if self.rect.bottom > height:
                self.rect.bottom = height
                self.jumped = False
            self.rect.x += x
            self.rect.y += y

        elif game_over == -1:
            self.rect.y -= 2
        # print(self.playerLives)
        display.blit(self.image, self.rect)


player1 = Player("images/player1.png", (35, 70))
restartBtn = Button(400, 400, "images/restart_btn 2.png")
exitBtn = Button(400, 200, "images/exit_btn 2.png")
startBtn = Button(400, 100, "images/start_btn 2.png")


def scoreText(text, colour, size, x, y):
    font_style = pygame.font.SysFont("comicsans", size)
    scoreAmount = font_style.render(text, True, colour)
    display.blit(scoreAmount, (x, y))


def livesText(text, colour, size, x, y):
    font_style = pygame.font.SysFont("comicsans", size)
    livesAmount = font_style.render(text, True, colour)
    display.blit(livesAmount, (x, y))


def reset_level():
    player1.rect.x = 70
    player1.rect.y = height - 130
    lava_group.empty()
    exit_group.empty()
    coin_group.empty()
    with open(f"levels/level{level}.json", "r") as file:
        world_data = json.load(file)
    world1 = World(world_data)
    return world1


with open("levels/level1.json", "r") as file:
    world_data = json.load(file)
world1 = World(world_data)

run = True
main_menu = True
while run:
    clock.tick(fps)
    display.blit(bg, bg_rect)
    world1.draw()
    lava_group.draw(display)
    exit_group.draw(display)
    coin_group.draw(display)
    livesText(f"Lives: {lives}", WHITE, 20, 700, 10)
    scoreText(f"Score: {score}", WHITE, 20, 10, 10)

    if pygame.sprite.spritecollide(player1, coin_group, True):
        score += 1
        print(score)
        coinSound.play()

    if not main_menu:
        player1.update()
    lava_group.update()
    exit_group.update()
    coin_group.update()
    # display.blit(livesAmount, (700, 10))

    if main_menu:
        if startBtn.draw():
            main_menu = False
            level = 1
            score = 0
            lives = 3
            world1 = reset_level()
        if exitBtn.draw():
            run = False
    else:
        if game_over == -1:
            if restartBtn.draw():
                score = 0
                game_overSound.play()
                lives -= 1
                if lives == 0:
                    main_menu = True
                    world1 = reset_level()

                # currentLives = player1.playerLives
                player1 = Player("images/player1.png", (35, 70))
                world1 = reset_level()
                game_over = 0

        if game_over == 1:
            game_over = 0
            if level < max_level:
                # currentLives = player1.playerLives
                level += 1
                player1 = Player("images/player1.png", (35, 70))
                world1 = reset_level()
            else:
                print("win")
                main_menu = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
