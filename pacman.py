import random
from abc import abstractmethod

import pygame
from pygame import Surface
from pygame.event import Event


# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 600, 400   # Ширина и высота окна игры
CELL_SIZE = 20   # Размер клетки
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE   # Количество строк и столбцов
FPS = 10   # Частота кадров
DIRECTIONS = (-1, 1)   # Возможные направления движения

# Цвета
BLACK = 0, 0, 0
YELLOW = 255, 255, 0
BLUE = 0, 0, 255
WHITE = 255, 255, 255
GREEN = 0, 255, 0
RED = 255, 0, 0


class MoveableObject:
    """Интерфейс движущегося объекта"""

    def __init__(self):
        self.x = COLS // 2
        self.y = ROWS // 2
        self.direction = (0, 0)

    def move(self):
        self.x += self.direction[0]
        self.y += self.direction[1]
        self.x = max(0, min(COLS - 1, self.x))
        self.y = max(0, min(ROWS - 1, self.y))

    @abstractmethod
    def draw(self, screen: Surface):
        """Абстрактный метод для отрисовки объекта на экране"""
        ...


class Pacman(MoveableObject):
    """Игрок (Пакман)"""

    def __init__(self):
        super().__init__()
        self.mouth_open = True   # Состояние рта (открыт/закрыт)

    def draw(self, screen: Surface):
        if self.mouth_open:
            start_angle = 30
            end_angle = 330
            self.mouth_open = False
        else:
            start_angle = 0
            end_angle = 360
            self.mouth_open = True
        pygame.draw.arc(
            screen,
            YELLOW,
            (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            start_angle * (3.14 / 180),
            end_angle * (3.14 / 180),
            CELL_SIZE // 2
        )

class Ghost(MoveableObject):
    """Призрак"""

    def __init__(self):
        super().__init__()
        self.x = random.randint(0, COLS)
        self.y = random.randint(0, ROWS)
        self.color = random.choice((RED, GREEN, BLUE))
        self.set_random_direction()

    def move(self):
        super().move()
        if self.x in (0, COLS - 1) or self.y in (0, ROWS - 1):
            self.set_random_direction()

    def set_random_direction(self) -> None:
        """Генерация случайного направления"""

        x = random.choice((0, *DIRECTIONS))
        y = random.choice(DIRECTIONS) if x == 0 else 0
        self.direction = x, y


    def draw(self, screen: Surface):
        pygame.draw.rect(
            screen,
            self.color,
            (
                self.x * CELL_SIZE + CELL_SIZE // 2,
                self.y * CELL_SIZE + CELL_SIZE // 2,
                CELL_SIZE // 2,
                CELL_SIZE // 2,
            ),
        )


class Game:
    """Объект игры"""

    def __init__(self, count_ghosts: int, timer_update_move_sec: int):
        self.count_ghosts = count_ghosts
        self.timer = timer_update_move_sec

        # Персонажи
        self.pacman = Pacman()
        self.ghosts = [Ghost() for _ in range(count_ghosts)]

    def _check_keydown(self, event: Event) -> None:
        """Отработка нажатия клавиш (стрелок)"""

        if event.key == pygame.K_UP:
            self.pacman.direction = (0, -1)
        elif event.key == pygame.K_DOWN:
            self.pacman.direction = (0, 1)
        elif event.key == pygame.K_LEFT:
            self.pacman.direction = (-1, 0)
        elif event.key == pygame.K_RIGHT:
            self.pacman.direction = (1, 0)

    def _move_objects(self) -> None:
        """Перемещение всех объектов (Пакмана и призраков) на экране."""

        for ghost in self.ghosts:
            ghost.move()
        self.pacman.move()

    def _draw_objects(self, screen: Surface) -> None:
        """Отрисовка всех объектов на экране."""

        for ghost in self.ghosts:
            ghost.draw(screen)
        self.pacman.draw(screen)

    def _remove_eat_ghost(self) -> None:
        """Проверка на столкновение Пакмана с призраками и их удаление."""

        pacman_x = (self.pacman.x - 1, self.pacman.x, self.pacman.x + 1)
        pacman_y = (self.pacman.y - 1, self.pacman.y, self.pacman.y + 1)

        for ghost in self.ghosts:
            if ghost.x in pacman_x and ghost.y in pacman_y:
                self.ghosts.remove(ghost)

        if len(self.ghosts) <= 0:
            self.ghosts = [Ghost() for _ in range(self.count_ghosts)]

    def run(self):
        """Основной метод, запускающий игру"""

        # Настройка окна и отрисовки
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man")
        clock = pygame.time.Clock()

        # Настройка таймера для обновления движения призраков
        pygame.time.set_timer(pygame.USEREVENT, 1000 * self.timer)

        # Бесконечный цикл, запускающий игру
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown(event)
                elif event.type == pygame.USEREVENT:
                    for ghost in self.ghosts:
                        ghost.set_random_direction()
            self._move_objects()
            self._remove_eat_ghost()

            screen.fill(BLACK)
            self._draw_objects(screen)

            pygame.display.flip()
            clock.tick(FPS)

        # Закрытие окна
        pygame.quit()


if __name__ == "__main__":
    game = Game(4, 5)
    game.run()
