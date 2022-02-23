import os
import sys
import time

import pygame
import numpy as np

from ex.main import tiles_group

WIDTH = 550
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        if not isinstance(obj, Player) :
            obj.rect.x = obj.abs_pos[0] + self.dx
            obj.rect.y = obj.abs_pos[1] + self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - WIDTH // 2)



class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def shift(self, vector):
        if vector == "up":
            max_lay_y = max(self, key=lambda sprite: sprite.abs_pos[1]).abs_pos[1]
            print('MAX lay y', max_lay_y)
            for sprite in self:
                sprite.abs_pos[1] -= (tile_height * max_y
                                      if sprite.abs_pos[1] == max_lay_y else 0)
        elif vector == "down":
            min_lay_y = min(self, key=lambda sprite: sprite.abs_pos[1]).abs_pos[1]
            print(min_lay_y)
            for sprite in self:
                sprite.abs_pos[1] += (tile_height * max_y
                                      if sprite.abs_pos[1] == min_lay_y else 0)
        elif vector == "left":
            max_lay_x = max(self, key=lambda sprite: sprite.abs_pos[0]).abs_pos[0]
            print(max_lay_x)
            for sprite in self:
                if sprite.abs_pos[0] == max_lay_x:
                    sprite.abs_pos[0] -= tile_width * max_x
        elif vector == "right":
            min_lay_x = min(self, key=lambda sprite: sprite.abs_pos[0]).abs_pos[0]
            print(min_lay_x)
            for sprite in self:
                sprite.abs_pos[0] += (tile_height * max_x
                                      if sprite.abs_pos[0] == min_lay_x else 0)


tiles_group = SpriteGroup()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, WIDTH))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return # начинаем игру
        pygame.display.flip()


def render_map(level):
    data = []
    for el in level:
        data.append([int(i) for i in el.replace("#", str(WALL)).replace(".", str(EMPTY)).replace("@", str(PLAYER))])
    return np.array(data)


def load_image(name, colorkey=None):
    """Функция загрузки изображения"""
    fullname = os.path.join("data", name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


WALL = 1
EMPTY = 0
PLAYER = 2


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == EMPTY:
                Tile('empty', x, y)
            elif level[y][x] == WALL:
                Tile('wall', x, y)
            elif level[y][x] == PLAYER:
                print("bi")
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def load_level(filename):
    try:
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        # и подсчитываем максимальную длину
        max_width = max(map(len, level_map))

        # дополняем каждую строку пустыми клетками ('.')
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))
    except FileNotFoundError:
        print("Файл не найден")
        terminate()



tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]

    def set_pos(self, x, y):
        self.abs_pos = [x, y]


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def update(self, *args):
        CELL_SIZE = 50
        data = zip(("right", "left", "up", "down"), ((CELL_SIZE, 0), (-CELL_SIZE, 0), (0, -CELL_SIZE), (0, CELL_SIZE)),
                   [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN])

        if args and args[0].type == pygame.KEYDOWN:
            for string, move, direction in data:
                if args[0].key == direction:
                    tiles_group.shift(string)
                    self.rect = self.rect.move(*move)
            for sprite in all_sprites:
                camera.apply(sprite)


def main():
    """Главная функция запуска"""
    active = True
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            player_group.update(event)

        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in tiles_group:
            camera.apply(sprite)

        screen.fill("black")
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()


screen = pygame.display.set_mode((WIDTH, WIDTH))
fps = 120
clock = pygame.time.Clock()
# print(*load_level('levels/map.txt'), sep="\n")
camera = Camera()
# path = input("Путь до карты: ")  # data/levels/map3.txt
path = "data/levels/map4.txt"
field = render_map(load_level(path))

player, max_x, max_y = generate_level(field)
if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Движущийся круг 2')
    start_screen()
    main()
    pygame.quit()