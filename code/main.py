from settings import *
from gameplay import GameManager
from structure import Walls, Pillets, Text, Fruit
from entity import Player, Blinky, Pinky, Inky, Clyde


class Pacman(GameManager):
    def __init__(self, key, high_score):
        # display setup

        pygame.init()
        self.window = pygame.display.set_mode((WWID, WHGT))  # window size
        pygame.display.set_caption("Pac-Man")  # window title
        pygame_icon = pygame.image.load("graphics/icon/icon.png")  # icon
        pygame.display.set_icon(pygame_icon)
        self.key = key
        # game setup
        self.player = Player()
        self.text = Text(self.player)
        self.text.high_score = high_score

        self.wall = Walls()
        self.pillet = Pillets(self.player)

        self.blinky = Blinky(self.player)
        self.pinky = Pinky(self.player)
        self.inky = Inky(self.player, self.blinky)
        self.clyde = Clyde(self.player)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]
        self.fruit = Fruit(self.player)
        pygame.mixer.music.load("sound/sound_intro.ogg")
        pygame.mixer.music.play(loops=1, start=0.0)

        super().__init__()

    def run(self):
        while self.key:
            # display map

            self.window.fill("black")
            self.pillet.update(self.window)
            self.text.update_score(self.window)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.player.lives != 0:
                        self.game = ON
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.KEYBOARD = LEFT
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.KEYBOARD = RIGHT
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.KEYBOARD = DOWN
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.KEYBOARD = UP
                    elif self.player.lives == 0 and event.key == pygame.K_SPACE:
                        self.key = 0

            self.wall.update(self.window)
            self.update()

            self.clock.tick(FRT)

            pygame.display.update()

        return self.text.high_score


if __name__ == "__main__":
    key = 1
    highscore = 0
    while key == 1:
        game = Pacman(key, highscore)
        highscore = game.run()
