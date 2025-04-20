import pygame
import os
import random
import time  # Импортируем модуль time

pygame.init()
window_width = 700
window_height = 500
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Космическое приключение")

clock = pygame.time.Clock()
FPS = 60
background_color = (0, 0, 0)
try:
    background_image = pygame.image.load("superfon.jpeg")
    background = pygame.transform.scale(background_image, (window_width, window_height))
except pygame.error as message:
    print("Не удалось загрузить фон:", message)
    background = None

pygame.mixer.init()
try:
    pygame.mixer.music.load("vampire.mp3")
    pygame.mixer.music.play(-1)
except pygame.error as message:
    print("Не удалось загрузить музыку:", message)

pygame.mixer.music.set_volume(0.3)

# Инициализация звуков
try:
    fire_sound = pygame.mixer.Sound("fire.ogg")
    fire_sound.set_volume(0.1)  # Устанавливаем громкость звука выстрела на 10%
except pygame.error as message:
    print("Не удалось загрузить звук выстрела:", message)
    fire_sound = None

# Инициализация шрифта
pygame.font.init()
font = pygame.font.Font(None, 30)
text_color = (255, 255, 255)

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed, width=65, height=65):
        super().__init__()
        try:
            self.image = pygame.transform.scale(pygame.image.load(player_image), (width, height))
        except pygame.error as message:
            print("Не удалось загрузить спрайт:", message)
            self.image = pygame.Surface((width, height))
            self.image.fill((0, 0, 0))

        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__(player_image, player_x, player_y, player_speed)
        self.ammo = 5  # Начальное количество патронов
        self.hp = 3 # Здоровье игрока

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.x < window_width - 65:
            self.rect.x += self.speed

    def fire(self):
        if self.ammo > 0:
            bullet = Bullet("bullet.png", self.rect.centerx - 5, self.rect.top, 10, 10, 20) # Создаем пулю с учетом позиции игрока
            bullets.add(bullet)
            if fire_sound:
                fire_sound.play()
            self.ammo -= 1  # Уменьшаем кол-во патронов
        else:
            print("Нет патронов!")

    def reload(self):
        self.ammo = 5  # Перезагружаем патроны

    def take_damage(self):
        self.hp -= 1
        print("Игроку нанесен урон! Осталось HP:", self.hp)

class Enemy(GameSprite):
    def __init__(self, enemy_image, enemy_x, enemy_y, enemy_speed):
        super().__init__(enemy_image, enemy_x, enemy_y, enemy_speed)
        self.speed = enemy_speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > window_height:
            self.rect.y = -65  # Возвращаем наверх экрана
            self.rect.x = random.randint(0, window_width - 65)
            return True  # Сигнализируем о пропуске

class Bullet(GameSprite):
    def __init__(self, bullet_image, bullet_x, bullet_y, bullet_speed, width, height):
        super().__init__(bullet_image, bullet_x, bullet_y, bullet_speed, width, height)
        self.speed = bullet_speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill() # Удаляем пулю, если она улетела за верхний край

player = Player("dark.jpg", 300, 400, 5)

# Создание группы врагов
enemies = pygame.sprite.Group()
for i in range(5):
    enemy = Enemy("enemems.jpeg", random.randint(0, window_width - 65), random.randint(-500, -65), 2) # Случайная позиция по y
    enemies.add(enemy)

# Создание группы пуль
bullets = pygame.sprite.Group()

# Переменные статистики
killed = 0
missed = 0
missed_limit = 15
kill_goal = 100

# Функция для проверки, все ли враги уничтожены
def all_enemies_killed():
    return not enemies  # Проверяем, пуста ли группа enemies

running = True
game_over = False # флаг окончания игры
game_over_time = 0 # Время когда игра закончилась
win = False # Флаг победы

while running:
    # Список для хранения "прошедших" врагов
    enemies_to_remove = []
    bullets_to_remove = [] # Список для хранения попавших пуль

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_RETURN:
                player.fire()  # Вызываем метод выстрела у игрока

    if not game_over: #если игра не закончена продолжаем игру
        player.update()

        # Обновление врагов и подсчет пропущенных
        for enemy in enemies:
            if enemy.update():  # Если Enemy пропущен
                missed += 1
                enemies_to_remove.append(enemy)  # Добавляем врага на удаление

            # Проверка столкновения с игроком
            if enemy.rect.colliderect(player.rect):
                player.take_damage()  # Игрок получает урон
                enemies_to_remove.append(enemy) # Удаляем врага

        # Обновление пуль
        bullets.update()

        # Проверка столкновений пуль и врагов
        for bullet in bullets:
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    # Пуля попала во врага!
                    killed += 1
                    enemies_to_remove.append(enemy)
                    bullets_to_remove.append(bullet) #удаление пули
                    bullet.kill() #Удаляем пулю сразу
                    enemy.kill()  # Удаляем врага сразу
                    break # Важно: чтобы одна пуля не убила нескольких врагов за один кадр

        # Удаляем "прошедших" врагов после завершения цикла
        for enemy in enemies_to_remove:
            enemies.remove(enemy)

        #Обновляем пули, которые улетели за экран
        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        # Проверка условий проигрыша
        if player.hp <= 0 or missed >= missed_limit:
            game_over = True
            game_over_time = time.time()  # запоминаем время окончания игры
            win = False # Убеждаемся что это проигрыш

        #Проверка условий выйгрыша
        elif killed >= kill_goal:
            game_over = True
            game_over_time = time.time()
            win = True

    if background:
        window.blit(background, (0, 0))
    else:
        window.fill(background_color)

    player.reset()

    # Отображение врагов
    for enemy in enemies:
        enemy.reset()

    # Отображение пуль
    bullets.draw(window)

    # Отображение статистики и кол-ва патронов
    text_killed = font.render("Сбито: " + str(killed), True, text_color)
    text_missed = font.render("Пропущено: " + str(missed), True, text_color)
    text_ammo = font.render("Патроны: " + str(player.ammo), True, text_color) # Отображаем кол-во патронов
    text_hp = font.render("HP: " + str(player.hp), True, text_color) # Отображаем HP

    window.blit(text_killed, (10, 10))
    window.blit(text_missed, (10, 40))
    window.blit(text_ammo, (10, 70)) # Отображаем патроны
    window.blit(text_hp, (10, 100)) # Отображаем HP

    if game_over:
        if win:
            text_game_over = font.render("Dark Win!", True, text_color)
        else:
            text_game_over = font.render("Light Win!", True, text_color)
        text_rect = text_game_over.get_rect(center=(window_width // 2, window_height // 2))
        window.blit(text_game_over, text_rect)

    pygame.display.flip()
    clock.tick(FPS)

    # Проверка на перезарядку и создание новой волны (если игра не окончена)
    if all_enemies_killed() and not game_over: # перезагрузка только когда все убиты и игра не окончена
        player.reload()
        enemies = pygame.sprite.Group() # Создаем пустую группу
        for i in range(5):  # Создаем новую волну
            enemy = Enemy("enemems.jpeg", random.randint(0, window_width - 65), random.randint(-500, -65), 2)  # Случайная позиция по y
            enemies.add(enemy)

    # Задержка в 1 секунду после проигрыша
    if game_over and time.time() - game_over_time > 1:
        running = False

pygame.quit()