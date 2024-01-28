from settings import *
import math


class Walls:
    def __init__(self):
        self.walls = []

        for i in range(len(map)):
            for j in range(len(map[i])):
                if map[i][j] in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    self.walls.append((map[i][j], i, j))

        self.blinkcounter = 0
        self.blink = False

    def blinker(self):
        self.blinkcounter += 1
        return self.blinkcounter % 40 < 20

    def draw_wall(self, window):
        if self.blink and self.blinker():
            self.color = "yellow"
        else:
            self.color = "blue"

        for wall in self.walls:
            wall_type, i, j = wall
            if wall_type == "1":
                pygame.draw.line(
                    window,
                    self.color,
                    (TWID * j + TWOFST, THGT * i + WOFST),
                    (TWID * j + TWOFST, THGT * i + THGT + WOFST),
                )
            elif wall_type == "2":
                pygame.draw.line(
                    window,
                    self.color,
                    (TWID * j, WOFST + (THGT * i + THOFST)),
                    (TWID * j + TWID, WOFST + (THGT * i + THOFST)),
                )
            elif wall_type == "3":
                pygame.draw.arc(
                    window,
                    self.color,
                    [((TWID * j) - TWOFST), (THGT * i + THOFST + WOFST), TWID, THGT],
                    0,
                    math.pi / 2,
                )
            elif wall_type == "4":
                pygame.draw.arc(
                    window,
                    self.color,
                    [(TWID * j + TWOFST), (THGT * i + THOFST + WOFST), TWID, THGT],
                    math.pi / 2,
                    math.pi,
                )
            elif wall_type == "5":
                pygame.draw.arc(
                    window,
                    self.color,
                    [(TWID * j + TWOFST), (THGT * i - THOFST + WOFST), TWID, THGT],
                    math.pi,
                    1.5 * math.pi,
                )
            elif wall_type == "6":
                pygame.draw.arc(
                    window,
                    self.color,
                    [(TWID * j - TWOFST), (THGT * i - THOFST + WOFST), TWID, THGT],
                    1.5 * math.pi,
                    0,
                )
            elif wall_type == "7" and not self.blink:
                pygame.draw.line(
                    window,
                    "white",
                    (TWID * j, WOFST + (THGT * i + THOFST)),
                    (TWID * j + TWID, WOFST + (THGT * i + THOFST)),
                    2,
                )

    def update(self, window):
        self.draw_wall(window)


class Pillets:
    def __init__(self, player):
        self.pillets = []
        self.powerpillets = []

        for i in range(len(map)):
            for j in range(len(map[i])):
                if map[i][j] == "." or map[i][j] == "n":
                    self.pillets.append((i, j))
                elif map[i][j] == "p" or map[i][j] == "P":
                    self.powerpillets.append((i, j))

        self.player = player

        # Blinking Pillets
        self.blinkcounter = 0
        self.blink = True

        self.allow_blit = 1

        # chomp_sound music
        self.chompidx = 0
        self.chomp_sound = (
            pygame.mixer.Sound("sound/sound_chomp1.ogg"),
            pygame.mixer.Sound("sound/sound_chomp2.ogg"),
        )
        self.chomp_sound[0].set_volume(0.1)
        self.chomp_sound[1].set_volume(0.1)

    def chomp(self):
        self.chomp_sound[self.chompidx].play()
        self.chompidx = 1 - self.chompidx

    def eaten(self, i, j):
        x, y = self.player.constructKey(j, i)
        px, py = self.player.rect.centerx, self.player.rect.centery
        d = math.sqrt((x - px) ** 2 + (y - py) ** 2)
        if self.player.allow_move:
            return d < 4
        else:
            return 0

    def blinker(self):
        self.blinkcounter += 1
        self.blink = self.blinkcounter % 40 < 20

    def draw_pillets(self, window):
        pillets_to_remove = []
        powerpillets_to_remove = []

        for pillet in self.pillets:
            i, j = pillet
            if not self.eaten(i, j):
                pygame.draw.rect(
                    window,
                    "pink",
                    [(TWID * j) + TWOFST - 2, (THGT * i) + THOFST + WOFST - 2, 4, 4],
                    width=0,
                    border_radius=0,
                )
            else:
                pillets_to_remove.append(pillet)

        self.blinker()
        for powerpillet in self.powerpillets:
            i, j = powerpillet
            if not self.eaten(i, j):
                if self.blink:
                    pygame.draw.circle(
                        window,
                        "yellow",
                        ((TWID * j) + TWOFST, (THGT * i) + THOFST + WOFST),
                        6,
                    )
            else:
                powerpillets_to_remove.append(powerpillet)

        # Removing the Eaten Pillets
        for pillet in pillets_to_remove:
            self.player.pillet_eaten += 1
            self.chomp()
            self.pillets.remove(pillet)

        for powerpillet in powerpillets_to_remove:
            self.player.power = 1
            self.player.pillet_eaten += 1
            self.chomp()
            self.powerpillets.remove(powerpillet)

    def update(self, window):
        if self.allow_blit == 1:
            self.draw_pillets(window)


class Text:
    def __init__(self, player):
        self.font = pygame.font.Font("font/Emulogic-zrEw.ttf", 17)
        self.rfont = pygame.font.Font("font/Emulogic-zrEw.ttf", 10)

        self.score = 0
        self.high_score = 0

        self.level = 1
        self.player = player

        self.text_surf = self.font.render("HIGH SCORE", True, "white")
        self.text_rect = self.text_surf.get_rect(center=(WWID / 2, 10))

        self.up_surf = self.font.render("1UP", True, "white")
        self.up_rect = self.up_surf.get_rect(topleft=(WWID / 12, 5))

        self.lives = pygame.image.load(f"graphics/pacman/2.png").convert_alpha()
        self.scaled_surface = pygame.transform.scale(self.lives, (25, 25))
        self.scaled_surface = pygame.transform.flip(self.scaled_surface, 1, 0)
        self.live_rect = self.scaled_surface.get_rect(topleft=(30, WHGT - 30))
        self.liveoffset = 40

        self.ready = pygame.image.load(f"graphics/text/ready.png").convert_alpha()
        self.ready_surf = pygame.transform.scale(self.ready, (100, 20))
        self.ready_rect = self.ready_surf.get_rect(center=(WWID / 2, WHGT / 2 + 40))

        self.over = pygame.image.load(f"graphics/text/over.png").convert_alpha()
        self.over_surf = pygame.transform.scale(self.over, (150, 20))
        self.over_rect = self.over_surf.get_rect(center=(WWID / 2, WHGT / 2 + 40))

        self.blinkcounter = 0

    def blinker(self):
        self.blinkcounter += 1
        return self.blinkcounter % 40 < 20

    def update_score(self, window):
        # HIGH SCORE TEXT
        window.blit(self.text_surf, self.text_rect)

        # HIGH SCORE
        self.format_high_score = "{:04d}".format(self.high_score)
        self.high_score_surf = self.font.render(
            str(self.format_high_score), True, "white"
        )
        self.high_score_rect = self.high_score_surf.get_rect(center=(WWID / 2, 30))
        window.blit(self.high_score_surf, self.high_score_rect)

        # SCORE
        self.score = self.player.pillet_eaten * 10
        self.score_surf = self.font.render(str(self.score), True, "white")
        self.score_rect = self.score_surf.get_rect(midtop=(WWID / 5, 25))
        window.blit(self.score_surf, self.score_rect)

        # 1UP
        if self.blinker():
            window.blit(self.up_surf, self.up_rect)

        # PACMAN LIVES
        for i in range(self.player.lives - 1):
            self.live_rect = self.scaled_surface.get_rect(
                topleft=(30 + (i * self.liveoffset), WHGT - 30)
            )
            window.blit(self.scaled_surface, self.live_rect)

        # READY
        if self.score == 0:
            window.blit(self.ready_surf, self.ready_rect)

        # GAME OVER
        if self.player.lives == 0:
            self.restart_surf = self.rfont.render(
                "Enter Space to Restart", True, "white"
            )
            self.restart_rect = self.text_surf.get_rect(center=(WWID / 4 + 95, 590))
            window.blit(self.over_surf, self.over_rect)
            window.blit(self.restart_surf, self.restart_rect)


class Fruit:
    def __init__(self,player):
        self.player = player
        self.image = pygame.image.load(
                f"graphics/fruit/fruit.png"
            ).convert_alpha()

        self.font = pygame.font.Font("font/Emulogic-zrEw.ttf", 10)
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect(center=(WWID / 2, WHGT / 2 + 40))
        self.pointer_rect = self.image.get_rect(center=(WWID / 2, WHGT / 2 + 50))
        self.points = 500
        self.ate = 0
        self.life_span = 500
        self.count = 0
        self.erase = 0

    def eaten(self):
        x, y = self.rect.centerx,self.rect.centery
        px, py = self.player.rect.centerx, self.player.rect.centery
        d = math.sqrt((x - px) ** 2 + (y - py) ** 2)
        if self.player.allow_move:
            if(d<15):
                self.ate = 1

    def counter(self):
        self.count += 1
        if(self.count>self.life_span):
            self.erase = 1
            self.count = 0

    def update(self,window):
        self.eaten()
        if(self.player.pillet_eaten>10 and not self.ate and not self.erase):
            self.counter()
            window.blit(self.image, self.rect)

     
