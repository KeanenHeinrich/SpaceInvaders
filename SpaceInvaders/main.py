import math
import threading
import random
import time
import pygame
from pygame import mixer

# initialize the pygame
pygame.init()

# set up deltaTime
clock = pygame.time.Clock()
previousTime = time.time()
dt = 0
FPS = 120

# create the Screen
screen = pygame.display.set_mode((800, 500))

# background
background = pygame.image.load('img/background.png').convert()

# sound
mixer.music.load('audio/background.mp3')
mixer.music.play(-1)

# caption and icon
pygame.display.set_caption('Space Invaders')
icon = pygame.image.load('img/ufo.png').convert()
pygame.display.set_icon(icon)

# player
playerImg = pygame.image.load('img/player.png').convert()
playerX = 370
playerY = 450
playerX_change = 0

# enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = 150
enemyY_change = 10
collision_blacklist = []
collision_busy = 0
no_collide = False
collision_count = 0
collision_complete = []
num_of_enemies = 0
total_enemies = 0
level = 0
loading = False


def start_level(in_level):
    over_text = over_font.render('LEVEL 1', True, (255, 255, 255))
    screen.blit(over_text, (200, 250))
    time.sleep(3)
    global loading
    global num_of_enemies
    global total_enemies
    match in_level:
        case 0:
            num_of_enemies = 10
            total_enemies = 10
        case 1:
            num_of_enemies = 20
            total_enemies = 20
        case 2:
            num_of_enemies = 30
            total_enemies = 30
        case 3:
            num_of_enemies = 40
            total_enemies = 40
    for p in range(num_of_enemies):
        enemyImg.append([pygame.image.load('img/enemy.png'), p])
        if p < 10:
            enemyX.append((150+p*35))
            enemyY.append(35)
        elif p < 20:
            enemyX.append((150 + (p-10) * 35))
            enemyY.append(75)
        elif p < 30:
            enemyX.append((150 + (p-20) * 35))
            enemyY.append(115)
        elif p < 40:
            enemyX.append((150 + (p-30) * 35))
            enemyY.append(155)
    loading = False


# Bullet
# Ready - you can't see the bullet on screen
# Fire - the bullet is currently moving

bulletImg = pygame.image.load('img/bullet.png')
bulletX = 0
bulletY = 380
bulletX_change = 0
bulletY_change = 800
bullet_state = "ready"
reloadComplete = True

# Enemy Bullet
enemyBulletImg = pygame.image.load('img/bullet2.png')
enemyBulletX = -10
enemyBulletY = -10
enemyBulletX_change = 0
enemyBulletY_change = 300
enemyBullet_state = "ready"
enemy_chosen = False
enemyShooting = True

# score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
testX = 10
testY = 10

# lives
playerLives = 3
deathBusy = False
font_lives = pygame.font.Font('freesansbold.ttf', 20)
testX_lives = 35
testY_lives = 45

# game over
over_font = pygame.font.Font('freesansbold.ttf', 64)
game_over = False


# Displays Remaining Lives
def show_lives(x, y):
    lives = font_lives.render('Lives: ' + str(playerLives), True, (255, 255, 255))
    screen.blit(lives, (x, y))


# Displays Current Score
def show_score(x, y):
    score = font.render('Score: ' + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


# Displays the current level or victory / game over state
def game_over_text(game_over_check, in_level):
    if game_over_check:
        over_text = over_font.render('GAME OVER', True, (255, 255, 255))
        screen.blit(over_text, (200, 150))
    elif in_level == 1:
        over_text = over_font.render('Level 1', True, (255, 255, 255))
        screen.blit(over_text, (280, 150))
    elif in_level == 2:
        over_text = over_font.render('Level 2', True, (255, 255, 255))
        screen.blit(over_text, (280, 150))
    elif in_level == 3:
        over_text = over_font.render('Level 3', True, (255, 255, 255))
        screen.blit(over_text, (280, 150))
    elif in_level == 4:
        over_text = over_font.render('Level 4', True, (255, 255, 255))
        screen.blit(over_text, (280, 150))
    else:
        over_text = over_font.render('YOU WON', True, (255, 255, 255))
        screen.blit(over_text, (230, 150))
        t5 = threading.Thread(target=shutdown, args=())
        t5.start()


# Updates the position of the player sprite
def player(x, y):
    screen.blit(playerImg, (x, y))


# Updates the position of the enemy sprite
def enemy(x, y):
    screen.blit(enemyImg[i][0], (x, y))


# Updates the firing state of the bullet and updates position
def fire_bullet(x, y):
    global bullet_state
    bullet_state = 'fire'
    screen.blit(bulletImg, (x, y))


# Calculates whether the bullet and an enemy have touched
def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt(math.pow(enemy_x-bullet_x, 2) + (math.pow(enemy_y - bullet_y, 2)))
    if distance < 27:
        return True
    else:
        return False


# Calculates whether an enemy bullet and the player have touched
def is_collision_player(player_x, player_y, bullet_x, bullet_y):
    distance = math.sqrt(math.pow(player_x-bullet_x, 2) + (math.pow(player_y - bullet_y, 2)))
    if distance < 27:
        return True
    else:
        return False


# Updates the enemy bullet's position
def enemy_fire_bullet(x, y):
    screen.blit(enemyBulletImg, (x, y))


# Plays reload audio and prevents firing for 1 second after
def reloading():
    reload = mixer.Sound('audio/reload.mp3')
    reload.play()
    time.sleep(1)
    global reloadComplete
    reloadComplete = True


# Plays damage audio and damage animation, and prevents enemies from firing for its duration
def player_damaged():
    global enemyShooting
    enemyShooting = False
    global playerImg
    oof = mixer.Sound('audio/oof.mp3')
    oof.play()
    playerImg = pygame.image.load('img/playerHit.png').convert()
    time.sleep(0.1)
    playerImg = pygame.image.load('img/player.png').convert()
    time.sleep(0.1)
    playerImg = pygame.image.load('img/playerHit.png').convert()
    time.sleep(0.1)
    playerImg = pygame.image.load('img/player.png').convert()
    time.sleep(0.1)
    playerImg = pygame.image.load('img/playerHit.png').convert()
    time.sleep(0.1)
    playerImg = pygame.image.load('img/player.png').convert()
    enemyShooting = True


# Plays player death audio and animation, preventing enemies from shooting or players from moving for the duration
def player_killed():
    global playerImg
    global deathBusy
    death = mixer.Sound('audio/playerExplosion.mp3')
    death.play()
    deathBusy = True
    playerImg = pygame.image.load('img/explosion1.png')
    time.sleep(1)
    playerImg = pygame.image.load('img/explosion2.png')
    time.sleep(1)
    playerImg = pygame.image.load('img/explosion3.png')
    time.sleep(1)
    playerImg = pygame.image.load('img/invis.png')


# Closes the game after 3 seconds
def shutdown():
    time.sleep(3)
    global running
    running = False


# Randomises an enemy location to shoot from, and firing from the lowest down row of that position.
def choose_enemy_shoot():
    shooter = random.randint(0, 9)
    global enemyImg
    global enemyY
    global enemyX
    global enemyBulletY
    global enemyBulletX
    global total_enemies
    global num_of_enemies
    global enemy_chosen
    for count in reversed(range(num_of_enemies)):
        if total_enemies == 10:
            if shooter != enemyImg[count][1]:
                pass
            else:
                enemyBulletY = enemyY[count]
                enemyBulletX = enemyX[count]
                enemy_chosen = True
                break
        elif total_enemies == 20:
            if shooter + 10 != enemyImg[count][1]:
                if shooter != enemyImg[count][1]:
                    pass
                else:
                    enemyBulletY = enemyY[count]
                    enemyBulletX = enemyX[count]
                    enemy_chosen = True
                    break
            else:
                enemyBulletY = enemyY[count]
                enemyBulletX = enemyX[count]
                enemy_chosen = True
                break
        elif total_enemies == 30:
            if shooter + 20 != enemyImg[count][1]:
                if shooter + 10 != enemyImg[count][1]:
                    if shooter != enemyImg[count][1]:
                        pass
                    else:
                        enemyBulletY = enemyY[count]
                        enemyBulletX = enemyX[count]
                        enemy_chosen = True
                        break
                else:
                    enemyBulletY = enemyY[count]
                    enemyBulletX = enemyX[count]
                    enemy_chosen = True
                    break
            else:
                enemyBulletY = enemyY[count]
                enemyBulletX = enemyX[count]
                enemy_chosen = True
                break
        elif total_enemies == 40:
            if shooter + 30 != enemyImg[count][1]:
                if shooter + 20 != enemyImg[count][1]:
                    if shooter + 10 != enemyImg[count][1]:
                        if shooter != enemyImg[count][1]:
                            pass
                        else:
                            enemyBulletY = enemyY[count]
                            enemyBulletX = enemyX[count]
                            enemy_chosen = True
                            break
                    else:
                        enemyBulletY = enemyY[count]
                        enemyBulletX = enemyX[count]
                        enemy_chosen = True
                        break
                else:
                    enemyBulletY = enemyY[count]
                    enemyBulletX = enemyX[count]
                    enemy_chosen = True
                    break
            else:
                enemyBulletY = enemyY[count]
                enemyBulletX = enemyX[count]
                enemy_chosen = True
                break


# Plays explosion animation for enemy
def explode_animation(target):
    enemyImg[target][0] = pygame.image.load("img/explosion1.png")
    time.sleep(0.2)
    enemyImg[target][0] = pygame.image.load("img/explosion2.png")
    time.sleep(0.2)
    enemyImg[target][0] = pygame.image.load("img/explosion3.png")
    time.sleep(0.2)
    collision_complete.append(target)
    global collision_busy
    collision_busy += 1


# Allows for held down buttons to repeat their press signal
pygame.key.set_repeat(True)

# game loop
running = True

while running:

    # delta time calculation
    clock.tick(FPS)
    now = time.time()
    dt = now - previousTime
    previousTime = now

    # loads in enemies when there are no active enemies
    if num_of_enemies == 0 and not loading:
        loading = True
        t3 = threading.Thread(target=start_level, args=(level,))
        t3.start()
        level += 1

    # Update background and level display
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    game_over_text(game_over, level)

    # runs for each event
    for event in pygame.event.get():

        # end game on quit pressed
        if event.type == pygame.QUIT:
            running = False
            break

        # runs if a button was pressed
        if event.type == pygame.KEYDOWN and not deathBusy:

            # update player X coordinate to the left if left arrow pressed
            if event.key == pygame.K_LEFT:
                playerX_change = -200
                playerX += playerX_change*dt
                break

            # update player X coordinate to the right if right arrow pressed
            if event.key == pygame.K_RIGHT:
                playerX_change = 200
                playerX += playerX_change*dt
                break

            # fire bullet when space is pressed (if not loading) and start reload
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready" and reloadComplete:
                    reloadComplete = False
                    bulletX = playerX
                    fire_bullet(bulletX, bulletY)
                    t2 = threading.Thread(target=reloading, args=())
                    t2.start()
                    break

        # stop player movement if the movement keys are released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0
                playerX += playerX_change

    # start enemy updates
    if not loading:
        for i in range(num_of_enemies):

            # if enemies pass a certain point, game is lost
            if enemyY[i] > 340:
                for j in range(num_of_enemies):
                    enemyY[j] = 2000
                    game_over = True
                    t4 = threading.Thread(target=shutdown, args=())
                    t4.start()
                    break

            # Update enemy X coordinate
            enemyX[i] += enemyX_change*dt

            # change enemy direction when left wall hit
            if enemyX[i] <= 0:
                enemyX_change = 120
                for q in range(num_of_enemies):
                    enemyY[q] += enemyY_change

            # change enemy direction when wall hit
            elif enemyX[i] >= 770:
                enemyX_change = -120
                for q in range(num_of_enemies):
                    enemyY[q] += enemyY_change

            # update enemy position
            enemy(enemyX[i], enemyY[i])

            # look for a collision
            collision = is_collision(enemyX[i], enemyY[i], bulletX, bulletY)

            # check to see if any enemy has already been hit and disable their collision
            if collision_blacklist:
                for k in range(collision_count):
                    if collision_blacklist[k] == i:
                        no_collide = True
                        break

            # add shot enemy to the collision blacklist and start the explosion animation
            if collision and not no_collide:
                collision_blacklist.append(i)
                collision_count += 1
                explosionSound = mixer.Sound('audio/explosion.wav')
                explosionSound.play()
                bulletY = 380
                bullet_state = "ready"
                score_value += 1
                t1 = threading.Thread(target=explode_animation, args=(i,))
                t1.start()

        # Fire enemy bullet if it's not already active
        while not enemy_chosen and enemyShooting:
            choose_enemy_shoot()
            bulletSound = mixer.Sound('audio/laser.wav')
            bulletSound.play()

        # If enemy bullet misses player, reset position and firing state
        if enemyBulletY >= 500:
            enemyBulletY = -10
            enemy_chosen = False

        # Move enemy bullet if firing
        if enemy_chosen:
            enemy_fire_bullet(enemyBulletX, enemyBulletY)
            enemyBulletY += enemyBulletY_change * dt

    # if player bullet misses enemy, reset position and firing state
    if bulletY <= 0:
        bulletY = 380
        bullet_state = "ready"

    # if bullet is firing, update position and Y coordinate
    if bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bulletY_change*dt

    # Update player position
    player(playerX, playerY)

    # Update player score display
    show_score(testX, testY)

    # Update player lives display
    show_lives(testX_lives, testY_lives)

    # loop through all enemies that have finished exploding and remove them from the enemy list
    no_collide = False
    for k in range(collision_busy):
        for i in range(collision_count):
            if collision_complete[k] == collision_blacklist[i]:
                enemyImg.pop(collision_blacklist[i])
                enemyX.pop(collision_blacklist[i])
                enemyY.pop(collision_blacklist[i])
                num_of_enemies -= 1
                temp1 = collision_blacklist[i]
                if collision_complete[k] in collision_blacklist:
                    collision_blacklist.pop(i)
                collision_count -= 1
                if temp1 in collision_complete:
                    collision_complete.pop(k)
                collision_busy -= 1

    # if enemy bullet hits player, update lives and reset enemy bullet
    if is_collision_player(playerX, playerY, enemyBulletX, enemyBulletY) and playerLives > 0:
        playerLives -= 1
        enemyBulletY = -10
        enemy_chosen = False

        # if player is killed, play death animation and end game
        if playerLives <= 0 and not deathBusy:
            game_over = True
            t6 = threading.Thread(target=player_killed, args=())
            t6.start()
            t4 = threading.Thread(target=shutdown, args=())
            t4.start()
            enemyShooting = False

        # if not dead, play damaged animation
        else:
            t6 = threading.Thread(target=player_damaged, args=())
            t6.start()

    # prevent player movement past walls
    if playerX <= 0:
        playerX = 0
    elif playerX >= 768:
        playerX = 768

    # update display
    pygame.display.update()


quit()
