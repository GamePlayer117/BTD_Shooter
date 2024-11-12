from random import randint
from time import time as timer  # import the timing function so that the interpreter doesn’t need to look for this function in the pygame module time, give it a different name ourselves
from pygame import *


# loading font functions separately
font.init()
font1 = font.Font(None, 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))

font2 = font.Font(None, 36)

# backgournd music
mixer.init()
mixer.music.load("Child's Nightmare.ogg")
mixer.music.play()
mixer.music.set_volume(0.5)
fire_sound = mixer.Sound('fire.ogg.opus')

# we need the following images:
img_back = "grass_back.jfif"  # game background
img_bullet = "bullet-removebg-preview.png"  # bullet
img_hero = "Sniper_monkey-removebg-preview.png"  # hero
img_enemy = "mqdefault-removebg-preview.png"  # enemy

score = 0  # ships destroyed
goal = 10  # how many ships need to be shot down to win
lost = 0  # ships missed
max_lost = 3  # lose if you miss that many
life = 3  # life points

new_y = 0
# parent class for other sprites
class GameSprite(sprite.Sprite):
    # class constructor
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # Call for the class (Sprite) constructor:
        sprite.Sprite.__init__(self)

        # every sprite must store the image property
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        # every sprite must have the rect property – the rectangle it is fitted in
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.new_y = 0

    # method drawing the character on the window
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


# main player class
class Player(GameSprite):
    # method to control the sprite with arrow keys
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    # method to "shoot" (use the player position to create a bullet there)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, bullets_w, bullets_h, bullets_s)
        bullets.add(bullet)


# enemy sprite class
class Enemy(GameSprite):
    # enemy movement
    def update(self):
        self.new_y += self.speed
        self.rect.y = int(self.new_y)
        global lost
        # disappears upon reaching the screen edge
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1


# bullet sprite class
class Bullet(GameSprite):
    # enemy movement
    def update(self):
        self.rect.y += self.speed
        # disappears upon reaching the screen edge
        if self.rect.y < 0:
            self.kill()


# Create a window
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))
# create sprites
ship_w = 50
ship_h = 50
ship_s = 5
ship = Player(img_hero, 5, win_height - 100, ship_w, ship_h, ship_s)

# creating a group of enemy sprites
enemy_w = 50
enemy_h = 50
enemy_s = 0.1
monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, enemy_w, enemy_h, enemy_s)
    monsters.add(monster)

bullets_w = 10
bullets_h = 10
bullets_s = -15
bullets = sprite.Group()

# the "game is over" variable: as soon as True is there, sprites stop working in the main loop
finish = False
# Main game loop:
run = True  # the flag is reset by the window close button

rel_time = False  # flag in charge of reload

num_fire = 0  # variable to count shots

num_bullets = 15

while run:

    # "Close" button press event
    for e in event.get():
        if e.type == QUIT:
            run = False
        # space bar press event – the sprite shoots
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                # check how many shots have been fired and whether reload is in progress
                if num_fire < num_bullets and rel_time == False:
                    num_fire = num_fire + 1
                    fire_sound.play()
                    ship.fire()

                if num_fire >= num_bullets and rel_time == False:  # if the player fired 5 shots
                    last_time = timer()  # record time when this happened
                    rel_time = True  # set the reload flag

    # the game itself: actions of sprites, checking the rules of the game, redrawing
    if not finish:

        # update the background
        window.blit(background, (0, 0))

        # launch sprite movements
        ship.update()
        
        bullets.update()
        monsters.update()

        # update them in a new location in each loop iteration
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)

        # reload
        if rel_time == True:
            now_time = timer()  # read time

            if now_time - last_time < 1:  # before 1 seconds are over, display reload message
                reload = font2.render('Wait, reload...', 1, (150, 0, 0))
                window.blit(reload, (260, 460))
            else:
                num_fire = 0  # set the bullets counter to zero
                rel_time = False  # reset the reload flag

        # check for a collision between a bullet and monsters (both monster and bullet disappear upon a touch)
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            # this loop will repeat as many times as the number of monsters hit
            score = score + 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, enemy_s)
            monsters.add(monster)

        '''
        # possible lose: missed too many monsters or the character collided with an enemy or an asteroid
        if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False) or lost >= max_lost:
            finish = True # lose, set the background and no longer control the sprites.
            window.blit(lose, (200, 200))
        '''
        # reduces lives, if the sprite has touched an enemy
        if sprite.spritecollide(ship, monsters, False):
            sprite.spritecollide(ship, monsters, True)
            life = life - 1

        # losing
        if life == 0 or lost >= max_lost:
            finish = True  # lose, set the background and no longer control the sprites.
            window.blit(lose, (200, 200))

        # win checking: how many points scored?
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))

        # write text on the screen
        text = font2.render("Score: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render("Missed: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        # set a different color depending on the number of lives
        if life == 3:
            life_color = (0, 150, 0)
        if life == 2:
            life_color = (150, 150, 0)
        if life == 1:
            life_color = (150, 0, 0)

        text_life = font1.render(str(life), 1, life_color)
        window.blit(text_life, (650, 10))

        display.update()
