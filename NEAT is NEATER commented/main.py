# NEAT Pew Pew Fighter
# Coded by Anmay Gupta
# Submitted on May 12th, 2020
# This is commented for understanding, but it's still going to be an annoying piece of junk
# Plus it has a bunch of useless artifacts from previous iterations that I felt could be useful in some places

# ---------------------------------------------------------------------------------------------------------------------

# ______________________NOTES____________________
# The best way to explain this is through a "piloting school" view,
# so I'll be referencing that a lot in the harder places Go to the bottom for a complete explanation of how NEAT and
# normal neural networks work I did take some code off of Stack Overflow and other places, but it's mainly tutorials
# (like how to use pygame) I tried to push away from a lot of it though, and use some of my own stuff The logic I
# also cobbled together from papers and stuff (Kenneth O. Stanley's papers are actually helpful) Please grade this
# one last because it needs to be run overnight in order for you to see its true effects Also write down the result
# of the first couple generations so you can compare, the console/catalog doesn't hold anything

# Libraries and junk
import time
import pygame
from somethingreasonable import *

# CONSTANTS DECLARATION
enemynum = 2
population = 1000

# Setting up the display using pygame and loading all the images
pygame.init()
dwidth = 800
dheight = 600
d = pygame.display.set_mode((dwidth, dheight))
pygame.display.set_caption("Pew Pew Fighter NEAT")
img1 = pygame.image.load("pewpew.png").convert_alpha()
img2 = pygame.image.load("pewpew2.png").convert_alpha()


# Defining a player sprite because pygame needs its own class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = img1
        self.rect = self.surf.get_rect()
        self.dead = False
        self.killedby = False
        self.x = 79
        self.y = round(dheight * 0.45)

    def update(self):
        # This is a reset function
        self.dead = False
        self.killedby = False
        self.x = 79
        self.y = dheight * 0.45


p = Player()
pewpeww = p.rect.right - p.rect.left
pewpewh = p.rect.bottom - p.rect.top
x = 0
y = dheight * 0.45
gens = []


# Enemies, yay
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((20, 10))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=(random.randint(dwidth + 20, dwidth + 100), random.randint(0, dheight)))
        self.speed = 15

    def update(self):
        # moving is fun
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            enemies.add(Enemy())
            self.kill()


enemies = pygame.sprite.Group()
for i in range(enemynum):
    enemies.add(Enemy())
clock = pygame.time.Clock()


def text(message, font2, size, x, y):
    # fairly explanatory
    font = pygame.font.Font(font2, size)
    ts = font.render(message, True, (255, 255, 255))
    tr = ts.get_rect()
    tr.center = (x, y)
    d.blit(ts, tr)


# Framerates, used when this program wasn't so laggy
def changeframerate(n):
    global framerate
    if n == 1:
        framerate = 30
    elif n == 2:
        framerate = 1024


def button(x, y, w, h, ic, ac, bnum):
    # This was used to make a button for a framerate change, allowing me to speed up and slow down time
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed(1)
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(d, ac, (x, y, w, h))
        if click[0] == 1:
            changeframerate(bnum)
    else:
        pygame.draw.rect(d, ic, (x, y, w, h))


def game(player):
    # This is when the human plays, so feel free to skip this
    global x, y
    start = time.time()
    dead = False
    overall = Student(enemies, 0, False, player)
    while not dead:
        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            dead = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                dead = True
                pygame.quit()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP] and y > 0:
            y -= 5
        elif pressed[pygame.K_DOWN] and y < dheight - pewpewh:
            y += 5
        d.fill((0, 0, 0))
        player.rect.topleft = x, y
        d.blit(player.surf, (x, y))
        for enemy in enemies:
            d.blit(enemy.surf, enemy.rect)
        enemies.update()
        score = round(time.time() - start)
        text("Score: " + str(score), "freesansbold.ttf", 25, 725, 25)
        overall.move(enemies)
        pygame.display.update()
        clock.tick(30)
    time.sleep(1)
    d.fill((0, 0, 0))
    text("You died!", "freesansbold.ttf", 115, dwidth / 2, dheight / 2)
    pygame.display.update()
    time.sleep(2)
    pygame.quit()


# This makes all of the planes for my pilots, so I can modify one without calling the others
# I'd like to think this cuts down on lag, but who knows
species = pygame.sprite.Group()
for pop in range(population):
    species.add(Player())
framerate = 1024


def drawn(student):
    # This is drawing the neural network of the "best" person
    # It's really just the person who isn't dead
    # All I do is give each node a position and draw connections between those positions
    s = student.brain
    nodesplit = [[] for l in range(s.layers)]
    for layer in range(s.layers):
        for n in s.nodes:
            if n.layer == layer:
                nodesplit[layer].append(n)
    nodepos = []
    nodeids = []
    for l in range(len(nodesplit)):
        for n in range(len(nodesplit[l])):
            if len(nodesplit) < 3:
                nodepos.append((600 + l * 75, 450 + n * 25))
            else:
                nodepos.append((525 + l * 75, 450 + n * 25))
            nodeids.append(nodesplit[l][n].id)
    for c in s.cons:
        fro = nodepos[nodeids.index(c.n1.id)]
        to = nodepos[nodeids.index(c.n2.id)]
        if c.enabled:
            pygame.draw.line(d, (0, 255, 0), fro, to, 2)
        else:
            pygame.draw.line(d, (255, 0, 0), fro, to, 2)
    for n in nodepos:
        pygame.draw.circle(d, (255, 255, 255), n, 10)
    # This highlights the person that I'm drawing the network of
    student.player.surf = img2


def network():
    # This is the good stuff
    global enemies, population, species
    print("Start")
    overallnetwork = Overall(enemies, species)
    lasthigh = 0
    lastavg = 0
    xedout = False
    # There's a ton of loops here, but this one is just making sure that the window isn't closed out or anything
    # This loop controls the generations, think of it as the actual program
    while not xedout:
        # Every generation, I reset the planes and the enemies
        species.update()
        enemies = pygame.sprite.Group()
        for ierhfi in range(enemynum):
            enemies.add(Enemy())
        # These are my trackers, they're really only there for display purposes (except the scores)
        ycat = [[] for pkuft in range(population)]
        # In order to make this unaffected by lag, I'm using the number of ticks that passed to measure score
        # This is instead of a time-based score, which could mean that scores become unreliable
        ticknum = 0
        scores = [[] for fioahwgipf in range(population)]
        bx, by = 0, 0
        # This is the actual generation, just saying that as long as the planes aren't dead to keep on going
        while False in [pl.dead for pl in species.sprites()]:
            # Pygame cosmetic stuff, also moving the enemies
            enemies.update()
            d.fill((0, 0, 0))
            # This gets all of the movements from my pilots
            moveset = overallnetwork.updatestudents(enemies, False)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            # Each student made a move, so I'm moving them
            for move in range(len(moveset)):
                movement = moveset[move]
                if movement == 1000000:
                    continue
                # Updating the students
                px, py = species.sprites()[move].x, species.sprites()[move].y
                ycat[move].append(py)
                if movement <= 0 < py:
                    py -= 5
                elif movement > 0 and py < dheight - pewpewh:
                    py += 5
                if movement != 1000000 and species.sprites()[move] != overallnetwork.themanthemysterythelegend().player:
                    species.sprites()[move].rect.topright = px, py
                    species.sprites()[move].x, species.sprites()[move].y = px, py
                    species.sprites()[move].surf = img1
                    d.blit(species.sprites()[move].surf, (px, py))
                elif species.sprites()[move] == overallnetwork.themanthemysterythelegend().player:
                    species.sprites()[move].rect.topright = px, py
                    species.sprites()[move].x, species.sprites()[move].y = px, py
                    bx, by = px, py
                # Making sure that dead players die
                # There are 2 criteria: 1, you hit a missile, and 2 you go offscreen (this will set your score to 1)
                if py == 0 or py == 600 - pewpewh:
                    species.sprites()[move].dead = True
                if pygame.sprite.spritecollideany(species.sprites()[move], enemies) or species.sprites()[move].dead:
                    overallnetwork.students[move].score = ticknum
                    if species.sprites()[move].dead:
                        overallnetwork.students[move].score = 1
                    scores[move].append(overallnetwork.students[move].score)
                    if overallnetwork.students[move].score == 0.0:
                        print(enemies, overallnetwork.students[move].badscoords, species.sprites()[move].x,
                              species.sprites()[move].y, overallnetwork.students[move].id)
                    species.sprites()[move].dead = True
            # I'm taking the best person and drawing them and their network last so they'll show up
            drawn(overallnetwork.themanthemysterythelegend())
            d.blit(overallnetwork.themanthemysterythelegend().player.surf, (bx, by))
            for enemy in enemies:
                d.blit(enemy.surf, enemy.rect)
            text("Score: " + str(ticknum), "freesansbold.ttf", 25, 725, 25)
            text("Gen Number: " + str(overallnetwork.gen), "freesansbold.ttf", 25,
                 800 - (7.5 * len("Gen Number: " + str(overallnetwork.gen))), 50)
            text(f"Last High: {lasthigh}", "freesansbold.ttf", 25, 800 - (7.5 * len(f"Last High: {lasthigh}")), 75)
            text(f"Last Avg: {lastavg}", "freesansbold.ttf", 25, 800 - (7.5 * len(f"Last Avg: {lastavg}")), 100)
            text(f"Movement: {moveset[overallnetwork.students.index(overallnetwork.themanthemysterythelegend())]}",
                 "freesansbold.ttf", 25, 800 - (7.5 * len(
                    f"Movement: {moveset[overallnetwork.students.index(overallnetwork.themanthemysterythelegend())]}")),
                 125)
            # drawnn(student)
            pygame.display.update()
            clock.tick(30)
            ticknum += 1
        scores = [s[0] for s in scores]
        lasthigh = np.amax(scores)
        lastavg = np.average(scores)
        print(np.amax(scores), np.average(scores), len(scores), scores)
        # This is the natural selection part, so literally magic
        overallnetwork.magic()
        # And this assigns each student a plane
        overallnetwork.parsepop(species)


# game(p)
network()