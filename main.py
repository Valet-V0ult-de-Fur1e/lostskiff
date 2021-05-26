import pygame as pg
import os
from os import path
import time
import sys
import random
import sqlite3

# класс базы данных
class BD:
    def __init__(self):
        self.database = sqlite3.connect("recordslist.db")
        self.cursor = self.database.cursor()

    def newresult(self, name, res):
        userinfo = (name, res)
        self.cursor.execute("INSERT INTO users VALUES(?, ?);", userinfo)
        self.database.commit()

    def giveuserlist(self):
        users = self.cursor.execute("""SELECT * FROM users""")
        userlist = (sorted(users, key=lambda x: x[1], reverse=True))
        return userlist[:15]


pscore = 0
flagpause = False
levelspase = 0
player = None
score = 50000
WIDTH = 1280
HEIGHT = 1024
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
pg.init()
pg.mixer.init()
pg.display.set_caption('The lost skiff beta.9.3.25')
clock = pg.time.Clock()
all_sprites = pg.sprite.Group()
bullets = pg.sprite.Group()
emenems = pg.sprite.Group()
emenembul = pg.sprite.Group()
mobs = pg.sprite.Group()
objects = pg.sprite.Group()
players = pg.sprite.Group()
meteor_images = []
explosion_anim = {}
emenemsb = pg.sprite.Group()
emenemsz = pg.sprite.Group()
emenemsu = pg.sprite.Group()
splayer = None
basadata = BD()

mainmenusound = pg.mixer.Sound("sounds/s9.mpeg")
gameoversound = pg.mixer.Sound("sounds/gameover.mp3")
gameoverscreensound = pg.mixer.Sound("sounds/newgameover.mp3")
shotsound = pg.mixer.Sound("sounds/shot.mp3")
shopsound = pg.mixer.Sound("sounds/s6.mpeg")
boomsound = pg.mixer.Sound("sounds/boom.mp3")
boomplayersound = pg.mixer.Sound("sounds/boom2.mp3")
upsound = pg.mixer.Sound("sounds/upuser.mp3")

# класс врага
class Emenem(pg.sprite.Sprite):
    def __init__(self, typem):
        pg.sprite.Sprite.__init__(self)
        self.type = typem
        self.defim = None
        self.image = None
        self.speedx = None
        self.speedy = None
        self.power = random.randint(1, 3)
        self.healh = None
        self.gab = None
        self.shoot_delay = None
        self.sideflag = None
        probility = random.randint(1, 10)
        if self.type == "zerg":
            if probility <= 8:
                self.defim = "data/zergzerlog.png"
                self.healh = 10
                self.gab = (60, 45)
                self.shoot_delay = 400
            if probility == 9:
                self.defim = "data/zergmutalist.png"
                self.healh = 20
                self.gab = (75, 45)
                self.shoot_delay = 400
            if probility == 10:
                self.defim = "data/zerghunter.png"
                self.healh = 30
                self.gab = (80, 50)
                self.shoot_delay = 400
        elif self.type == "bot":
            if probility <= 8:
                self.defim = "data/botsolder.png"
                self.healh = 20
                self.gab = (45, 45)
                self.shoot_delay = 400
            if probility == 9:
                self.defim = "data/bothevysolder.png"
                self.healh = 50
                self.gab = (75, 60)
                self.shoot_delay = 400
            if probility == 10:
                self.defim = "data/botsolderupper.png"
                self.healh = 30
                self.gab = (60, 60)
                self.shoot_delay = 400
        elif self.type == "ufo":
            if probility <= 8:
                self.defim = "data/ufo1lv.png"
                self.healh = 40
                self.gab = (60, 45)
                self.shoot_delay = 450
            if probility == 9:
                self.defim = "data/ufo2lv.png"
                self.healh = 60
                self.gab = (75, 45)
                self.shoot_delay = 400
            if probility == 10:
                self.defim = "data/ufobomber.png"
                self.healh = 30
                self.gab = (80, 50)
                self.shoot_delay = 800
        self.image = pg.image.load(self.defim).convert()
        self.image.set_colorkey((255, 255, 255))
        self.image = pg.transform.scale(self.image, self.gab)
        self.rect = self.image.get_rect()
        self.last_shot = pg.time.get_ticks()
        if self.power == 1:
            self.speedx = 0
            self.speedy = 1
            self.rect.x = random.randint(0, 1250)
            self.rect.y = random.randint(-100, -80)
        elif self.power == 2:
            self.speedy = 0
            self.sideflag = random.randint(0, 1)
            if self.sideflag:
                self.speedx = 1
                self.rect.x = -70
            else:
                self.speedx = -1
                self.rect.x = 1200
            self.rect.y = random.randint(10, 200)
        elif self.power == 3:
            self.speedx = 0
            self.speedy = 1
            self.rect.x = random.randint(0, 1250)
            self.rect.y = random.randint(-100, -80)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.x > 1180:
            self.speedx = -2
        elif self.rect.x < -50:
            self.speedx = 2
        if self.rect.y > 1300:
            self.rect.y = random.randint(-100, -10)
            self.rect.x = random.randint(0, 1180)
        self.shoot()

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.x + 25, self.rect.y + 15, 1, "Acid2", "down", 10, 15)
                all_sprites.add(bullet)
                emenembul.add(bullet)
            elif self.power == 2:
                bullet = Bullet(self.rect.x + 25, self.rect.y + 15, 1, "Fire3", "down", 10, 20)
                all_sprites.add(bullet)
                emenembul.add(bullet)
            elif self.power == 3:
                bullet = Bullet(self.rect.x + 25, self.rect.y + 15, 1, "Frize2", "down", 10, 15)
                all_sprites.add(bullet)
                emenembul.add(bullet)

# класс кнопки меню
class MenuButton:
    def __init__(self, x, y, text):
        self.font = pg.font.Font(None, 100)
        self.butx = x
        self.buty = y
        self.butColor = (255, 255, 255)
        self.butText = self.font.render(text, False, self.butColor)

    def showbut(self, screen):
        screen.blit(self.butText, (self.butx, self.buty))


class ModeButton:
    def __init__(self, image, checkimage, flag):
        self.image = pg.image.load(image).convert()
        self.newimage = pg.image.load(checkimage).convert()
        self.image.set_colorkey((0, 0, 0))
        self.newimage.set_colorkey((0, 0, 0))
        self.flag = flag

    def showbut(self):
        if not self.flag:
            return self.image
        else:
            return self.newimage

# класс игрока
class Player(pg.sprite.Sprite):
    def __init__(self, sp=1, x=590, y=900, ptype="Studart", level=1, phealth=3, lives=2, workb=1):
        pg.sprite.Sprite.__init__(self)
        self.ptype = ptype
        self.gl = None
        self.lives = lives
        self.levelb = workb
        self.usertipe = 0
        if self.ptype == "Studart":
            self.gl = "data/userfirstskiff.png"
            self.lives = 1
        elif self.ptype == "Acid1":
            self.gl = "data/acidskiff1lv.png"
            self.lives = 2
        elif self.ptype == "Acid2":
            self.gl = "data/acidskiff2lv.png"
            self.lives = 3
        elif self.ptype == "Acid3":
            self.gl = "data/acidskiff3lv.png"
            self.lives = 4
        elif self.ptype == "Freeze1":
            self.gl = "data/frizeskiff1lv.png"
            self.lives = 2
        elif self.ptype == "Freeze2":
            self.lives = 3
            self.gl = "data/frizekiff2lv.png"
        elif self.ptype == "Freeze3":
            self.lives = 4
            self.gl = "data/frizekiff3lv.png"
        elif self.ptype == "Fire1":
            self.gl = "data/fireskiff1lv.png"
            self.lives = 2
        elif self.ptype == "Fire2":
            self.gl = "data/fireeskiff2lv.png"
            self.lives = 3
        elif self.ptype == "Fire3":
            self.gl = "data/fireskiff3lv.png"
            self.lives = 4
        self.image = pg.image.load(self.gl).convert()
        self.image.set_colorkey((255, 255, 255))
        self.image = pg.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.speed = sp
        self.speedx = 0
        self.speedy = 0
        self.rect.x = self.x
        self.rect.y = self.y
        self.pclass = ptype
        self.level = level
        self.health = phealth
        self.last_shot = pg.time.get_ticks()
        self.shoot_delay = 250

    def goLeft(self):
        if self.rect.x >= 0:
            self.speedx = - self.speed
            self.x += self.speedx
            self.rect.x = self.x

    def goRight(self):
        if self.rect.x <= 1230:
            self.speedx = + self.speed
            self.x += self.speedx
            self.rect.x = self.x

    def goUp(self):
        if self.rect.y >= 0:
            self.speedy = - self.speed
            self.y += self.speedy
            self.rect.y = self.y

    def goDown(self):
        if self.rect.y <= 974:
            self.speedy = + self.speed
            self.y += self.speedy
            self.rect.y = self.y

    def shoot(self):
        now = pg.time.get_ticks()
        pg.mixer.Sound.play(shotsound)
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.levelb == 1:
                bullet = Bullet(self.x + 25, self.y - 5)
                all_sprites.add(bullet)
                bullets.add(bullet)
            if self.levelb == 2:
                bullet1 = Bullet(self.x + 12, self.y - 5)
                all_sprites.add(bullet1)
                bullets.add(bullet1)
                bullet2 = Bullet(self.x + 38, self.y - 5)
                all_sprites.add(bullet2)
                bullets.add(bullet2)
            if self.levelb == 3:
                bullet1 = Bullet(self.x + 25, self.y - 5)
                all_sprites.add(bullet1)
                bullets.add(bullet1)
                bullet2 = Bullet(self.x + 10, self.y - 5, 1, "Frize2", "up", 6, 15)
                all_sprites.add(bullet2)
                bullets.add(bullet2)
                bullet3 = Bullet(self.x + 40, self.y - 5)
                all_sprites.add(bullet3)
                bullets.add(bullet3)
            if self.levelb == 4:
                bullet = Bullet(self.x + 25, self.y - 5, 1, "Fire3", "up", 10, 15)
                all_sprites.add(bullet)
                bullets.add(bullet)
                bullet1 = Bullet(self.x + 15, self.y - 5, 1, "Frize3", "up", 6, 15)
                all_sprites.add(bullet1)
                bullets.add(bullet1)
                bullet2 = Bullet(self.x + 35, self.y - 5, 1, "Frize3", "up", 6, 15)
                all_sprites.add(bullet2)
                bullets.add(bullet2)
                bullet3 = Bullet(self.x, self.y - 5)
                all_sprites.add(bullet3)
                bullets.add(bullet3)
                bullet4 = Bullet(self.x + 50, self.y - 5)
                all_sprites.add(bullet4)
                bullets.add(bullet4)

    def upuser(self):
        if self.usertipe <= 9:
            self.usertipe += 1
        if self.usertipe == 1:
            self.gl = "data/acidskiff1lv.png"
        elif self.usertipe == 2:
            self.gl = "data/acidskiff2lv.png"
        elif self.usertipe == 3:
            self.gl = "data/acidskiff3lv.png"
        elif self.usertipe == 4:
            self.gl = "data/frizeskiff1lv.png"
        elif self.usertipe == 5:
            self.gl = "data/frizeskiff2lv.png"
        elif self.usertipe == 6:
            self.gl = "data/frizeskiff3lv.png"
        elif self.usertipe == 7:
            self.gl = "data/fireskiff1lv.png"
        elif self.usertipe == 8:
            self.gl = "data/fireskiff2lv.png"
        elif self.usertipe == 9:
            self.gl = "data/fireskiff3lv.png"
        self.image = pg.image.load(self.gl).convert()
        self.image.set_colorkey((255, 255, 255))
        self.image = pg.transform.scale(self.image, (50, 50))

# класс снарядов
class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, clv=1, typen="Stand", vect="up", xpm=3, ypm=6):
        pg.sprite.Sprite.__init__(self)
        self.damage = None
        self.imageb = None
        zs = 1
        self.typeb = typen
        if vect == "up":
            zs = -1
        if vect == "down":
            zs = 1
        if self.typeb == "Stand":
            self.imageb = "data/standartbullet.png"
            self.damage = 10
            self.speed = 2 * zs
        elif self.typeb == "Fire1":
            self.imageb = "data/firebul1.png"
            self.damage = 10
            self.speed = 2 * zs
        elif self.typeb == "Fire3":
            self.imageb = "data/firebul3.png"
            self.damage = 20
            self.speed = 2 * zs
        elif self.typeb == "Acid1":
            self.imageb = "data/acidbullet1.png"
            self.damage = 5
            self.speed = 3 * zs
        elif self.typeb == "Acid2":
            self.imageb = "data/acidbullet2.png"
            self.damage = 10
            self.speed = 2.5 * zs
        elif self.typeb == "Frize1":
            self.imageb = "data/frigebul1.png"
            self.damage = 10
            self.speed = 2 * zs
        elif self.typeb == "Frize2":
            self.imageb = "data/frigebul2.png"
            self.damage = 25
            self.speed = 2.5 * zs
        elif self.typeb == "Frize3":
            self.imageb = "data/frigebul3.png"
            self.damage = 15
            self.speed = 1 * zs
        self.image = pg.image.load(self.imageb).convert()
        self.image.set_colorkey(WHITE)
        self.image = pg.transform.scale(self.image, (xpm, ypm))
        self.rect = self.image.get_rect()
        self.level = clv
        self.bx = x
        self.by = y
        self.rect.x = self.bx
        self.rect.y = self.by

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
        if self.rect.y > 1050 or self.rect.y < -1 or self.rect.x > 1300 or self.rect.x < 0:
            self.kill()

# класс обЪестов
class Mob(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(WHITE)
        self.image_orig = pg.transform.scale(self.image_orig, (random.randint(50, 100), random.randint(50, 100)))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .90 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-5, -1)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-1, 1)
        self.rotation = 0
        self.rotation_speed = random.randrange(-1, 1)
        self.last_update = pg.time.get_ticks()

    def rotate(self):
        time_now = pg.time.get_ticks()
        if time_now - self.last_update > 50:
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pg.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if (self.rect.top > HEIGHT + 5) or (self.rect.left < -25) or (self.rect.right > WIDTH + 10):
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-2, -1)
            self.speedy = random.randrange(1, 2)

        if self.rect.x > 2000:
            self.kill()

# создание нового обЪекта
def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)

# главный режим
def TestMode():
    pg.mixer.music.load("sounds/s3.mpeg")
    pg.mixer.music.set_volume(0.5)
    pg.mixer.music.play(4)
    global score, player, flagpause, splayer, pscore
    for elem in all_sprites:
        elem.kill()
    givebots()
    givezergs()
    giveufo()
    background_position = [0, 0]
    background_image = pg.image.load("data/space-bg.png").convert()
    testmodescreen = pg.display.set_mode((WIDTH, HEIGHT))
    if flagpause:
        player = splayer
        flagpause = False
    else:
        player = Player()
    all_sprites.add(player)
    players.add(player)
    playeronline = True
    meteor_list = [
        'data/metior1.png',
        'data/metior2.png',
        'data/metior3.png',
        'data/metior4.png',
        'data/metior5.png',
        'data/metior6.png',
        'data/metior7.png',
        'data/metior8.png'
    ]
    for imagem in meteor_list:
        meteor_images.append(pg.image.load(imagem).convert())
    for i in range(11):
        newmob()
    while playeronline:
        testmodescreen.blit(background_image, background_position)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    if score != 0 and score >= 1000:
                        splayer = player
                        flagpause = True
                        pg.mixer.music.stop()
                        SHOP()
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            player.goLeft()
        elif keys[pg.K_RIGHT]:
            player.goRight()
        if keys[pg.K_UP]:
            player.goUp()
        elif keys[pg.K_DOWN]:
            player.goDown()
        if keys[pg.K_SPACE]:
            player.shoot()
        if player.lives == 0:
            pg.mixer.music.stop()
            pg.mixer.Sound.play(gameoversound)
            if score >= 2000:
                pscore = score
                score = 0
                result()
            else:
                pscore = score
                score = 0
                GAMEOVERSCREEN()
        all_sprites.update()
        hits = pg.sprite.groupcollide(emenembul, bullets, True, True)
        hits = pg.sprite.groupcollide(emenemsb, bullets, True, True)
        for hit in hits:
            pg.mixer.Sound.play(boomsound)
            score += 20
            newbot()
        hits = pg.sprite.groupcollide(emenemsz, bullets, True, True)
        for hit in hits:
            pg.mixer.Sound.play(boomsound)
            score += 50
            newzerg()
        hits = pg.sprite.groupcollide(emenemsu, bullets, True, True)
        for hit in hits:
            pg.mixer.Sound.play(boomsound)
            score += 100
            newufo()
        hits = pg.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            pg.mixer.Sound.play(boomsound)
            score += 10
            newmob()
        hits = pg.sprite.groupcollide(mobs, players, True, False)
        for hit in hits:
            pg.mixer.Sound.play(boomsound)
            pg.mixer.Sound.play(boomplayersound)
            player.lives -= 1
            newmob()
        hits = pg.sprite.groupcollide(emenembul, players, True, False)
        for hit in hits:
            pg.mixer.Sound.play(boomplayersound)
            player.lives -= 1
        all_sprites.draw(testmodescreen)
        drowscore(testmodescreen)
        drowlives(player.lives, testmodescreen)
        pg.display.flip()

# магазин
def SHOP():
    pg.mixer.Sound.play(shopsound)
    global splayer, score
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    background_position = [0, 0]
    background_image = pg.image.load("data/shopscreen.png").convert()
    flaggame = True
    while flaggame:
        screen.blit(background_image, background_position)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    pg.mixer.Sound.stop(shopsound)
                    TestMode()
                if event.key == pg.K_1:
                    if splayer.lives <= 4 and score - 1000 >= 0:
                        pg.mixer.Sound.play(upsound)
                        splayer.lives += 1
                        score -= 1000
                if event.key == pg.K_2:
                    if splayer.levelb <= 3 and score - 5000 >= 0:
                        pg.mixer.Sound.play(upsound)
                        splayer.levelb += 1
                        score -= 1000
                if event.key == pg.K_3:
                    if score - 10000 >= 0 and splayer.usertipe <= 9:
                        pg.mixer.Sound.play(upsound)
                        splayer.upuser()
                        score -= 10000
                if event.key == pg.K_s:
                    pass
        printres1(screen, score)
        pg.display.flip()


def printres1(screen, scr):
    font = pg.font.Font(None, 90)
    text = font.render(str(scr), True, WHITE)
    screen.blit(text, (700, 120))

# создание новых ботов
def givebots():
    for i in range(3):
        newbot()


def givezergs():
    for i in range(5):
        newzerg()


def giveufo():
    for i in range(2):
        newufo()


def newbot():
    bot = Emenem("bot")
    all_sprites.add(bot)
    emenemsb.add(bot)


def newzerg():
    bot = Emenem("zerg")
    all_sprites.add(bot)
    emenemsz.add(bot)


def newufo():
    bot = Emenem("ufo")
    all_sprites.add(bot)
    emenemsu.add(bot)

# окно результатов
def result():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    background_position = [0, 0]
    background_image = pg.image.load("data/resultlist.png").convert()
    flaggame = True
    pos = 0
    fst = 65
    sc = 65
    thr = 65
    while flaggame:
        screen.blit(background_image, background_position)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    pos -= 1
                    if pos == -1:
                        pos = 2
                elif event.key == pg.K_RIGHT:
                    pos += 1
                    if pos == 3:
                        pos = 0
                if event.key == pg.K_UP:
                    if pos == 0:
                        fst += 1
                        if fst == 91:
                            fst = 65
                    elif pos == 1:
                        sc += 1
                        if sc == 91:
                            sc = 65
                    elif pos == 2:
                        thr += 1
                        if thr == 91:
                            thr = 65
                elif event.key == pg.K_DOWN:
                    if pos == 0:
                        fst -= 1
                        if fst == 64:
                            fst = 90
                    elif pos == 1:
                        sc -= 1
                        if sc == 64:
                            sc = 90
                    elif pos == 2:
                        thr -= 1
                        if thr == 64:
                            thr = 90
                if event.key == pg.K_RETURN:
                    newresult(chr(fst) + chr(sc) + chr(thr), int(pscore))
                    GAMEOVERSCREEN()
        print1(screen, fst)
        print2(screen, sc)
        print3(screen, thr)
        printres(screen, pscore)
        pg.display.flip()


def print1(screen, fb):
    font = pg.font.Font(None, 90)
    text = font.render(chr(fb), True, WHITE)
    screen.blit(text, (450, 350))


def print2(screen, sc):
    font = pg.font.Font(None, 90)
    text = font.render(chr(sc), True, WHITE)
    screen.blit(text, (625, 350))


def print3(screen, thr):
    font = pg.font.Font(None, 90)
    text = font.render(chr(thr), True, WHITE)
    screen.blit(text, (800, 350))


def printres(screen, scr):
    font = pg.font.Font(None, 90)
    text = font.render(str(scr), True, WHITE)
    screen.blit(text, (500, 590))


def newresult(name, res):
    global basadata
    basadata.newresult(name, res)


def resultlist():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    background_position = [0, 0]
    background_image = pg.image.load("data/gameoverb.png").convert()
    flaggame = True
    while flaggame:
        screen.blit(background_image, background_position)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    TestMode()
                elif event.key == pg.K_m:
                    MAINMENU()
        pg.display.flip()


def drowscore(screen):
    font = pg.font.Font(None, 50)
    text = font.render(f"{score}", True, (100, 255, 100))
    screen.blit(text, (100, 100))


def drowlives(lives, screen):
    x = 900
    y = 100
    limg = pg.image.load("data/livesimg.png").convert()
    limg.set_colorkey(WHITE)
    limg = pg.transform.scale(limg, (50, 50))
    for i in range(lives):
        screen.blit(limg, (x, y))
        x += 70

# окно завершения игры
def GAMEOVERSCREEN():
    pg.mixer.Sound.play(gameoverscreensound)
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    background_position = [0, 0]
    background_image = pg.image.load("data/gameoverb.png").convert()
    flaggame = True
    while flaggame:
        screen.blit(background_image, background_position)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    pg.mixer.Sound.stop(gameoverscreensound)
                    TestMode()
                elif event.key == pg.K_m:
                    pg.mixer.Sound.stop(gameoverscreensound)
                    MAINMENU()
        pg.display.flip()

# окно выбора режима
def choicemode():
    testworkoutmod = ModeButton("data/tmode1.png", "data/tmode2.png", True)
    mainmod = ModeButton("data/mmode1.png", "data/mmode2.png", True)
    dualmod = ModeButton("data/dmode1.png", "data/dmode2.png", True)
    background_position = [0, 0]
    background_image = pg.image.load("data/menumodbackground.png").convert()
    playerplaying = True
    flagmod = 0
    screenmode = pg.display.set_mode((WIDTH, HEIGHT))
    while playerplaying:
        screenmode.fill(BLACK)
        screenmode.blit(background_image, background_position)
        screenmode.blit(testworkoutmod.showbut(), (20, 100))
        screenmode.blit(mainmod.showbut(), (480, 98))
        screenmode.blit(dualmod.showbut(), (910, 96))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    flagmod += 1
                    if flagmod == 3:
                        flagmod = 0
                elif event.key == pg.K_LEFT:
                    flagmod -= 1
                    if flagmod == -1:
                        flagmod = 2
                elif event.key == pg.K_RETURN:
                    if flagmod == 0:
                        TABLE()
                    elif flagmod == 1:
                        pg.mixer.Sound.stop(mainmenusound)
                        TestMode()
                    elif flagmod == 2:
                        pg.mixer.Sound.stop(mainmenusound)
                        INPROGRESS()
        if flagmod == 0:
            testworkoutmod.flag = True
            mainmod.flag = False
            dualmod.flag = False
        elif flagmod == 1:
            testworkoutmod.flag = False
            mainmod.flag = True
            dualmod.flag = False
        elif flagmod == 2:
            testworkoutmod.flag = False
            mainmod.flag = False
            dualmod.flag = True
        pg.display.flip()


def TABLE():
    background_position = [0, 0]
    background_image = pg.image.load("data/recordlist.png").convert()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    playerplaying = True
    while playerplaying:
        screen.fill(BLACK)
        screen.blit(background_image, background_position)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    choicemode()
        printrecords(screen)
        pg.display.flip()


def printrecords(screen):
    global basadata
    listusers = basadata.giveuserlist()
    font = pg.font.Font(None, 45)
    x = 300
    y = 100
    for user in range(len(listusers)):
        text = str(user + 1) + "." + " " + listusers[user][0] + " " + str(listusers[user][1])
        textt = font.render(text, True, WHITE)
        screen.blit(textt, (x, y))
        y += 50

# окно обучения
def INPROGRESS():
    flaggame = True
    background_position = [0, 0]
    background_image = pg.image.load("data/test.png").convert()
    testmodescreen = pg.display.set_mode((WIDTH, HEIGHT))
    while flaggame:
        testmodescreen.blit(background_image, background_position)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_m:
                    MAINMENU()
        pg.display.flip()   

# функция вызова главного меню
def MAINMENU():
    pg.mixer.Sound.play(mainmenusound)
    mainmenuscreen = pg.display.set_mode((WIDTH, HEIGHT))
    but_Start = MenuButton(170, 470, "START")
    but_Exit = MenuButton(200, 600, "EXIT")
    background_position = [0, 0]
    background_image = pg.image.load("data/background.png").convert()
    cursor_image = pg.image.load("data/cursor.png").convert()
    cursor_image.set_colorkey((0, 0, 0))
    cursor_position = [100, 470]
    modeflag = True
    playerplaying = True
    while playerplaying:
        mainmenuscreen.fill(BLACK)
        mainmenuscreen.blit(background_image, background_position)
        but_Start.showbut(mainmenuscreen)
        but_Exit.showbut(mainmenuscreen)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    cursor_position = [100, 470]
                    modeflag = True
                elif event.key == pg.K_DOWN:
                    cursor_position = [100, 600]
                    modeflag = False
                elif event.key == pg.K_RETURN:
                    if modeflag:
                        choicemode()
                    else:
                        sys.exit()
        mainmenuscreen.blit(cursor_image, cursor_position)
        pg.display.flip()


MAINMENU()
pg.quit()
sys.exit()
