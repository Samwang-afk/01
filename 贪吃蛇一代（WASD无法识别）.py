import pygame
import sys
import random
import math
from enum import Enum
import os
pygame.init()
pygame.font.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 165
BACKGROUND = (15, 20, 30)
GRID_COLOR = (30, 35, 45)
SNAKE_HEAD_COLOR = (50, 205, 50)
SNAKE_BODY_COLOR = (34, 139, 34)
FOOD_COLOR = (220, 20, 60)
SPECIAL_FOOD_COLOR = (255, 215, 0)
OBSTACLE_COLOR = (70, 130, 180)
TEXT_COLOR = (220, 220, 220)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
class 方向(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
class 食物类型(Enum):
    NORMAL = 1
    SPECIAL = 2
def 载入字体(size):
    # 尝试加载系统字体
    try:
        # 尝试加载常见中文字体
        font_names = [
            'Arial', 'Helvetica', 'sans-serif'
        ]

        for font_name in font_names:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试字体是否能正确渲染字符
                test_surface = font.render("测试", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        return pygame.font.Font(None, size)
    except:
        return pygame.font.Font(None, size)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = 载入字体(24)
title_font = 载入字体(48)
small_font = 载入字体(18)
font_loaded = font is not None
snake_length = 3
snake_positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_direction = 方向.RIGHT
snake_next_direction = snake_direction
snake_score = 0
snake_grow_to = 3
snake_speed = 10
snake_is_alive = True

food_position = (0, 0)
food_type = 食物类型.NORMAL
food_spawn_time = 0
food_lifetime = 0

obstacle_positions = []

game_state = "MENU"  # MENU, PLAYING, GAME_OVER
last_update_time = 0
speed_multiplier = 1.0

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface, font):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)
        try:
            text_surface = font.render(self.text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        except:
            pygame.draw.rect(surface, (255, 255, 0), self.rect.inflate(-10, -10))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.action:
            return self.action
        return None

button_width, button_height = 200, 50
center_x = SCREEN_WIDTH // 2 - button_width // 2

menu_buttons = [
    Button(center_x, 250, button_width, button_height, "Start Game", "START"),
    Button(center_x, 320, button_width, button_height, "Quit", "QUIT")
]

game_over_buttons = [
    Button(center_x, 350, button_width, button_height, "Play Again", "RESTART"),
    Button(center_x, 420, button_width, button_height, "Main Menu", "MENU"),
    Button(center_x, 490, button_width, button_height, "Quit", "QUIT")
]

def reset_snake():
    global snake_length, snake_positions, snake_direction, snake_next_direction
    global snake_score, snake_grow_to, snake_is_alive

    snake_length = 3
    snake_positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    snake_direction = 方向.RIGHT
    snake_next_direction = snake_direction
    snake_score = 0
    snake_grow_to = 3
    snake_is_alive = True

def get_head_position():
    return snake_positions[0]
def update_snake():
    global snake_direction, snake_positions, snake_is_alive, game_state
    snake_direction = snake_next_direction
    head = get_head_position()
    x, y = snake_direction.value
    new_x = (head[0] + x) % GRID_WIDTH
    new_y = (head[1] + y) % GRID_HEIGHT
    new_head = (new_x, new_y)
    if new_head in snake_positions[1:]:
        snake_is_alive = False
        return
    snake_positions.insert(0, new_head)
    if len(snake_positions) > snake_grow_to:
        snake_positions.pop()

def draw_snake(surface):
    for i, p in enumerate(snake_positions):
        # 绘制蛇身
        rect = pygame.Rect(p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)

        # 蛇头使用不同颜色
        if i == 0:
            pygame.draw.rect(surface, SNAKE_HEAD_COLOR, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)

            # 绘制眼睛
            eye_size = GRID_SIZE // 5
            if snake_direction == 方向.RIGHT:
                pygame.draw.circle(surface, (0, 0, 0),
                                   (p[0] * GRID_SIZE + GRID_SIZE - eye_size, p[1] * GRID_SIZE + eye_size * 2),
                                   eye_size)
                pygame.draw.circle(surface, (0, 0, 0), (
                    p[0] * GRID_SIZE + GRID_SIZE - eye_size, p[1] * GRID_SIZE + GRID_SIZE - eye_size * 2), eye_size)
            elif snake_direction == 方向.LEFT:
                pygame.draw.circle(surface, (0, 0, 0),
                                   (p[0] * GRID_SIZE + eye_size, p[1] * GRID_SIZE + eye_size * 2), eye_size)
                pygame.draw.circle(surface, (0, 0, 0),
                                   (p[0] * GRID_SIZE + eye_size, p[1] * GRID_SIZE + GRID_SIZE - eye_size * 2),
                                   eye_size)
            elif snake_direction == 方向.UP:
                pygame.draw.circle(surface, (0, 0, 0),
                                   (p[0] * GRID_SIZE + eye_size * 2, p[1] * GRID_SIZE + eye_size), eye_size)
                pygame.draw.circle(surface, (0, 0, 0),
                                   (p[0] * GRID_SIZE + GRID_SIZE - eye_size * 2, p[1] * GRID_SIZE + eye_size),
                                   eye_size)
            elif snake_direction == 方向.DOWN:
                pygame.draw.circle(surface, (0, 0, 0),
                                   (p[0] * GRID_SIZE + eye_size * 2, p[1] * GRID_SIZE + GRID_SIZE - eye_size),
                                   eye_size)
                pygame.draw.circle(surface, (0, 0, 0), (
                    p[0] * GRID_SIZE + GRID_SIZE - eye_size * 2, p[1] * GRID_SIZE + GRID_SIZE - eye_size), eye_size)
        else:
            # 蛇身使用渐变色
            color_factor = max(0.5, 1.0 - (i / len(snake_positions)) * 0.5)
            body_color = (
                int(SNAKE_BODY_COLOR[0] * color_factor),
                int(SNAKE_BODY_COLOR[1] * color_factor),
                int(SNAKE_BODY_COLOR[2] * color_factor)
            )
            pygame.draw.rect(surface, body_color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)

def change_direction(direction):
    global snake_next_direction
    if (direction == 方向.UP and snake_direction != 方向.DOWN) or \
            (direction == 方向.DOWN and snake_direction != 方向.UP) or \
            (direction == 方向.LEFT and snake_direction != 方向.RIGHT) or \
            (direction == 方向.RIGHT and snake_direction != 方向.LEFT):
        snake_next_direction = direction

def randomize_food_position():
    global food_position, food_type, food_spawn_time, food_lifetime
    while True:
        food_position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food_position not in snake_positions and food_position not in obstacle_positions:
            break
    food_type = 食物类型.NORMAL if random.random() < 0.9 else 食物类型.SPECIAL
    if food_type == 食物类型.SPECIAL:
        food_spawn_time = pygame.time.get_ticks()
        food_lifetime = random.randint(5000, 10000)  # 5-10秒
def is_food_expired():
    if food_type == 食物类型.SPECIAL:
        return pygame.time.get_ticks() - food_spawn_time > food_lifetime
    return False

def draw_food(surface):
    rect = pygame.Rect(food_position[0] * GRID_SIZE, food_position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)

    if food_type == 食物类型.NORMAL:
        pygame.draw.circle(surface, FOOD_COLOR, rect.center, GRID_SIZE // 2 - 2)

        stem_rect = pygame.Rect(rect.centerx - 2, rect.top + 2, 4, 6)
        pygame.draw.rect(surface, (139, 69, 19), stem_rect)

        leaf_points = [
            (rect.centerx + 2, rect.top + 4),
            (rect.centerx + 6, rect.top + 2),
            (rect.centerx + 4, rect.top + 6)
        ]
        pygame.draw.polygon(surface, (50, 205, 50), leaf_points)
    else:
        current_time = pygame.time.get_ticks()
        pulse = (math.sin(current_time / 200) + 1) / 2  # 0到1的脉冲值
        color = (
            int(SPECIAL_FOOD_COLOR[0] * (0.7 + 0.3 * pulse)),
            int(SPECIAL_FOOD_COLOR[1] * (0.7 + 0.3 * pulse)),
            int(SPECIAL_FOOD_COLOR[2] * (0.7 + 0.3 * pulse))
        )

        center = rect.center
        radius = GRID_SIZE // 2 - 2
        points = []
        for i in range(5):
            # 外点
            angle = math.pi / 2 + i * 2 * math.pi / 5
            points.append((
                center[0] + radius * math.cos(angle),
                center[1] + radius * math.sin(angle)
            ))
            # 内点
            angle += math.pi / 5
            points.append((
                center[0] + radius / 2 * math.cos(angle),
                center[1] + radius / 2 * math.sin(angle)
            ))

        pygame.draw.polygon(surface, color, points)


# 生成障碍物
def generate_obstacles(count=10):
    global obstacle_positions
    obstacle_positions = []
    for _ in range(count):
        # 随机生成障碍物位置
        x = random.randint(2, GRID_WIDTH - 3)
        y = random.randint(2, GRID_HEIGHT - 3)
        obstacle_positions.append((x, y))

def draw_obstacles(surface):
    for pos in obstacle_positions:
        rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, OBSTACLE_COLOR, rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


# 绘制分数
def draw_score():

    if not font_loaded:
        score_rect = pygame.Rect(10, 10, 20 + snake_score * 5, 20)
        pygame.draw.rect(screen, (255, 255, 0), score_rect)
        return

    score_text = font.render(f"Score: {snake_score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))

    if food_type == 食物类型.SPECIAL:
        remaining_time = max(0, food_lifetime - (pygame.time.get_ticks() - food_spawn_time))
        time_text = small_font.render(f"Special: {remaining_time // 1000}s", True, SPECIAL_FOOD_COLOR)
        screen.blit(time_text, (SCREEN_WIDTH - 150, 10))



def draw_menu():
    if font_loaded:
        title_text = title_font.render("Snake Game", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)

        # 绘制游戏说明
        instructions = [
            "Use arrow keys or WASD to control the snake",
            "Normal food: +1 point, Special food: +3 points",
            "Avoid obstacles and your own body",
        ]

        for i, line in enumerate(instructions):
            instruction_text = small_font.render(line, True, TEXT_COLOR)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 25))
            screen.blit(instruction_text, instruction_rect)
    else:
        title_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 150, 200, 50)
        pygame.draw.rect(screen, (255, 255, 0), title_rect)

    for button in menu_buttons:
        button.draw(screen, font)


def draw_game_over():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    if font_loaded:
        game_over_text = title_font.render("Game Over", True, TEXT_COLOR)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(game_over_text, game_over_rect)

        score_text = font.render(f"Final Score: {snake_score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(score_text, score_rect)

        length_text = font.render(f"Max Length: {snake_grow_to}", True, TEXT_COLOR)
        length_rect = length_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        screen.blit(length_text, length_rect)
    else:
        game_over_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 150, 200, 50)
        pygame.draw.rect(screen, (255, 0, 0), game_over_rect)

        score_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 220, 200, 30)
        pygame.draw.rect(screen, (255, 255, 0), score_rect)

    for button in game_over_buttons:
        button.draw(screen, font)


# 处理事件
def handle_events():
    global game_state, running

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if game_state == "PLAYING":
                if event.key in (pygame.K_UP, pygame.K_w):
                    change_direction(方向.UP)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    change_direction(方向.DOWN)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    change_direction(方向.LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    change_direction(方向.RIGHT)
                elif event.key == pygame.K_ESCAPE:
                    game_state = "MENU"

            elif game_state == "GAME_OVER":
                if event.key == pygame.K_SPACE:
                    restart_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if game_state == "MENU":
                for button in menu_buttons:
                    action = button.check_click(mouse_pos)
                    if action == "START":
                        game_state = "PLAYING"
                    elif action == "QUIT":
                        return False

            elif game_state == "GAME_OVER":
                for button in game_over_buttons:
                    action = button.check_click(mouse_pos)
                    if action == "RESTART":
                        restart_game()
                    elif action == "MENU":
                        game_state = "MENU"
                    elif action == "QUIT":
                        return False

    # 更新按钮悬停状态
    mouse_pos = pygame.mouse.get_pos()
    if game_state == "MENU":
        for button in menu_buttons:
            button.check_hover(mouse_pos)
    elif game_state == "GAME_OVER":
        for button in game_over_buttons:
            button.check_hover(mouse_pos)

    return True


# 更新游戏状态
def update():
    global last_update_time, snake_score, snake_grow_to, game_state, snake_is_alive

    if game_state != "PLAYING":
        return

    current_time = pygame.time.get_ticks()
    update_interval = 1000 // (snake_speed * speed_multiplier)

    if current_time - last_update_time > update_interval:
        update_snake()
        last_update_time = current_time
        if get_head_position() == food_position:
            if food_type == 食物类型.NORMAL:
                snake_score += 1
                snake_grow_to += 1
            else:  # 特殊食物
                snake_score += 10
                snake_grow_to += 10

            # 每得5分增加一个障碍物
            if snake_score % 5 == 0:
                generate_obstacles(len(obstacle_positions) + 1)

            # 生成新食物
            randomize_food_position()

        # 检查特殊食物是否过期
        if is_food_expired():
            randomize_food_position()

        # 检查是否撞到障碍物
        if get_head_position() in obstacle_positions:
            snake_is_alive = False

        # 检查游戏是否结束
        if not snake_is_alive:
            game_state = "GAME_OVER"


# 重新开始游戏
def restart_game():
    reset_snake()
    randomize_food_position()
    generate_obstacles(10)  # 重置为5个障碍物
    global game_state, speed_multiplier
    game_state = "PLAYING"
    speed_multiplier = 1.0


# 绘制游戏
def draw():
    screen.fill(BACKGROUND)

    if game_state == "MENU":
        draw_menu()
    elif game_state == "PLAYING":
        draw_grid()
        draw_obstacles(screen)
        draw_food(screen)
        draw_snake(screen)
        draw_score()
    elif game_state == "GAME_OVER":
        draw_grid()
        draw_obstacles(screen)
        draw_food(screen)
        draw_snake(screen)
        draw_score()
        draw_game_over()

    pygame.display.flip()


# 初始化游戏
generate_obstacles(10)
randomize_food_position()

# 主游戏循环
running = True
while running:
    running = handle_events()
    update()
    draw()
    clock.tick(FPS)

pygame.quit()
sys.exit()