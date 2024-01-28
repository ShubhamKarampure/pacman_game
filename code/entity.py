from settings import *
from node import NodeGroup
import random


class Entity(NodeGroup):
    def __init__(self, name, start_position, speed):
        # path setup
        super().__init__(name)
        self.setPortalPair((0, 15), (29, 15))
        # name setup
        self.name = name
        if name == "player":
            self.curr_node = self.getNodeFromTiles(*start_position)
        self.start_position = start_position
        self.next_node = None
        self.curr_direction = STOP
        self.prev_direction = STOP
        self.speed = speed

        # life setup
        self.kill = 0

        # To allow movement and display
        self.allow_move = 0
        self.allow_blit = 1

    def move(self):
        if self.allow_move:
            if self.curr_direction == LEFT:
                self.rect.centerx -= self.speed
            elif self.curr_direction == RIGHT:
                self.rect.centerx += self.speed
            elif self.curr_direction == UP:
                self.rect.centery -= self.speed
            elif self.curr_direction == DOWN:
                self.rect.centery += self.speed

    def check_dest_reached(self):
        x, y = self.rect.centerx, self.rect.centery
        px, py = self.next_node.position.x, self.next_node.position.y
        d = math.sqrt((x - px) ** 2 + (y - py) ** 2)
        if d < 2:
            self.curr_node = self.next_node
            self.prev_direction = self.curr_direction
            self.curr_direction = STOP

    def handle_portal(self):
        self.curr_node = self.curr_node.neighbours[PORTAL]
        self.next_node = self.curr_node.neighbours[self.prev_direction]
        self.rect.centerx = self.curr_node.position.x
        self.rect.centery = self.curr_node.position.y
        self.curr_direction = self.prev_direction

    def reset(self):
        self.kill = 0
        self.allow_blit = 1
        self.curr_node = self.getNodeFromTiles(*self.start_position)
        self.rect = self.image.get_rect(center=(self.curr_node.position))
        self.curr_direction = STOP


class Player(Entity):
    def __init__(self):
        # path setup
        super().__init__("player", player_spawn, speed)
        self.next_node = self.curr_node.neighbours[RIGHT]
        # direction setup
        self.angle = RIGHT

        # image setup
        self.import_frames()
        self.frame_index = 0
        self.dframe_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(self.curr_node.position))

        # lives setup
        self.lives = 3

        # Pillet and Power
        self.power = 0
        self.pillet_eaten = 0
        self.ghost_killed = 0
        self.no_of_ghost_killed = 0

    def import_frames(self):
        self.frames = []
        self.death_frames = []
        for i in range(3):
            surf = pygame.image.load(f"graphics/pacman/{i+1}.png").convert_alpha()
            scaled_surface = pygame.transform.scale(surf, (30, 30))
            self.frames.append(scaled_surface)
        for i in range(11):
            surf = pygame.image.load(
                f"graphics/pacman/sprite_pacman_death{i+1}.png"
            ).convert_alpha()
            scaled_surface = pygame.transform.scale(surf, (30, 30))
            self.death_frames.append(scaled_surface)

    def rotate(self, direction):
        if direction == UP:
            self.image = pygame.transform.rotate(self.image, 90)
        elif direction == DOWN:
            self.image = pygame.transform.rotate(self.image, -90)
        elif direction == LEFT:
            self.image = pygame.transform.flip(self.image, 1, 0)

    def animate(self):
        if not self.kill:
            self.dframe_index = 0
            self.frame_index += 0.1
            if self.frame_index >= 3:
                self.frame_index = 0
            return self.frames[int(self.frame_index)]
        else:
            if self.dframe_index < 10:
                self.dframe_index += 0.05
            else:
                self.dframe_index = 10
            return self.death_frames[int(self.dframe_index)]

    def check_valid_direction(self, direction):
        if self.curr_node.neighbours[direction] is not None:
            return True
        return False

    def reverse_run(self):
        if self.curr_direction != STOP:
            self.curr_node, self.next_node = self.next_node, self.curr_node
            self.prev_direction = self.curr_direction
            self.curr_direction = OPPOSITE_DIRECTION[self.curr_direction]

    def next_direction(self, direction):
        if self.check_valid_direction(direction):
            self.prev_direction = self.curr_direction
            self.curr_direction = direction
            self.next_node = self.curr_node.neighbours[direction]
        else:
            if self.prev_direction != STOP and self.check_valid_direction(
                self.prev_direction
            ):
                self.curr_direction = self.prev_direction
                self.next_node = self.curr_node.neighbours[self.prev_direction]

    def run(self, direction, window):
        self.image = self.animate()  # get image
        if direction != STOP:
            if self.curr_direction != STOP:
                if self.curr_direction == OPPOSITE_DIRECTION[direction]:
                    self.reverse_run()
            elif self.curr_node.neighbours[PORTAL] is not None:
                self.handle_portal()
            else:
                self.next_direction(direction)

            if self.curr_direction == STOP:
                self.angle = self.prev_direction
            else:
                self.angle = self.curr_direction

            if not self.kill:
                self.rotate(self.angle)
                self.move()
            if self.curr_direction != STOP:
                self.check_dest_reached()

        if self.allow_blit:
            window.blit(self.image, self.rect)


class Ghost(Entity):
    def __init__(self, name, start_position, home, speed, player):
        super().__init__(name, start_position, speed)

        # player
        self.player = player

        # movement setup
        self.home = home
        self.target = None

        # image setup
        self.import_image()
        self.image = self.images[0]

        # mode setup
        self.mode = SCATTER
        self.state = BRAVE

        # blinking mode setup
        self.blinkcounter = 0
        self.blink = 0

        self.font = pygame.font.Font("font/Emulogic-zrEw.ttf", 10)

        # Music
        self.pacman_die = pygame.mixer.Sound("sound/pacman_death.ogg")
        self.pacman_die.set_volume(0.1)

        self.ghost_die = pygame.mixer.Sound("sound/pacman_eatghost.ogg")
        self.ghost_die.set_volume(0.1)

        self.indx = 0
        self.trap = 1
        self.eye = 0
        self.close_gate()

    def import_image(self):
        image_paths = [
            f"graphics/ghost_images/{self.name.lower()}{i}.png" for i in range(1, 5)
        ]

        image_paths += [
            "graphics/ghost_images/blue.png",
            "graphics/ghost_images/blue2.png",
            "graphics/ghost_images/white.png",
            "graphics/ghost_images/white2.png",
            "graphics/ghost_images/eye.png",
        ]

        self.images = []

        for path in image_paths:
            image = pygame.transform.scale(
                pygame.image.load(path).convert_alpha(), (23, 23)
            )
            scaled_surface = pygame.transform.scale(image, (30, 30))
            self.images.append(scaled_surface)

    def check_valid_direction(self, direction):
        if self.prev_direction != STOP:
            if (
                self.curr_node.neighbours[direction] is not None
                and self.prev_direction is not OPPOSITE_DIRECTION[direction]
            ):
                return True
        else:
            if self.curr_node.neighbours[direction] is not None:
                return True
            else:
                return False

    def next_direction(self):
        next_min_dist = [math.inf] * 4

        bx, by = self.rect.centerx, self.rect.centery
        px, py = self.target

        if self.check_valid_direction(LEFT):
            next_min_dist[0] = math.sqrt(pow(bx - fudge - px, 2) + pow(by - py, 2))
        if self.check_valid_direction(RIGHT):
            next_min_dist[1] = math.sqrt(pow(bx + fudge - px, 2) + pow(by - py, 2))
        if self.check_valid_direction(UP):
            next_min_dist[2] = math.sqrt(pow(bx - px, 2) + pow(by - fudge - py, 2))
        if self.check_valid_direction(DOWN):
            next_min_dist[3] = math.sqrt(pow(bx - px, 2) + pow(by + fudge - py, 2))

        i = next_min_dist.index(min(next_min_dist))

        if next_min_dist[i] != math.inf:
            self.curr_direction = i
        self.next_node = self.curr_node.neighbours[self.curr_direction]

    def reverse_direction(self):
        self.curr_direction = OPPOSITE_DIRECTION[self.curr_direction]
        self.curr_node, self.next_node = self.next_node, self.curr_node

    def blinker(self):
        self.blinkcounter += 1
        return self.blinkcounter % 40 < 20

    def animate(self):
        if self.curr_direction == -1 and self.prev_direction == -1:
            self.image = self.images[1]
        elif self.curr_direction == -1:
            self.image = self.images[self.prev_direction]
        else:
            self.image = self.images[self.curr_direction]

    def check_collision(self):
        x, y = self.rect.centerx, self.rect.centery
        px, py = self.player.rect.centerx, self.player.rect.centery
        d = math.sqrt((x - px) ** 2 + (y - py) ** 2)
        if d < 4 and self.player.kill != 1 and self.kill != 1:
            if self.state == BRAVE:
                self.player.kill = 1
                self.pacman_die.play()
            else:
                self.player.ghost_killed = 1
                self.ghost_die.play()
                self.kill = 1

    def target_reached(self):
        x, y = self.rect.centerx, self.rect.centery
        px, py = self.target
        d = math.sqrt((x - px) ** 2 + (y - py) ** 2)
        if d < 8:
            return True
        return False

    def trap_logic(self):
        self.release_logic()
        if self.check_trapped() and self.trap:
            self.close_gate()
            self.target = self.constructHomeKey(*GHOSTEXIT)
        elif self.check_trapped() and not self.trap:
            self.open_gate()
            self.target = self.constructHomeKey(*GHOSTEXIT)
        elif not self.check_trapped() and self.trap:
            self.open_gate()
            self.target = self.constructHomeKey(*GHOSTHOUSE)
        elif not self.check_trapped() and not self.trap:
            self.close_gate

    def release_logic(self):
        if self.player.pillet_eaten > self.dot_limit:
            self.trap = 0

    def check_trapped(self):
        if (
            self.curr_node.position.x,
            self.curr_node.position.y,
        ) in self.homeLUT and self.curr_node != self.getHomeNodeFromTiles(2, 0):
            return True
        return False

    def update(self):
        self.check_trapped()
        if self.curr_direction != STOP:
            self.move()
        else:
            if self.curr_node.neighbours[PORTAL] is not None:
                self.handle_portal()
            else:
                self.next_direction()

        self.check_collision()
        self.check_dest_reached()

    def run(self, window):
        self.animate()

        if not self.kill:
            self.speed = speed
            if self.state == FRIGHTEN:
                self.speed = die
                self.indx = 1 - self.indx
                if self.indx == 1:
                    self.image = self.images[4]
                else:
                    self.image = self.images[5]

                if self.blink and self.blinker():
                    if self.indx == 1:
                        self.image = self.images[6]
                    else:
                        self.image = self.images[7]

                self.target = (random.randint(0, 400), random.randint(0, 600))
            else:
                if self.mode == CHASE:
                    self.target = self.get_target()
                elif self.mode == SCATTER:
                    self.target = self.home
        else:
            if not self.allow_move and not self.eye:
                points = (2 ** (self.player.no_of_ghost_killed + 1)) * 100
                self.image = self.font.render(str(points), True, "skyblue")
            else:
                self.trap = 1
                self.speed = eye
                self.image = self.images[8]
                self.target = self.constructHomeKey(*GHOSTHOUSE)
                self.eye = 1
                if self.target_reached():
                    self.kill = 0
                    self.trap = 0
                    self.state = BRAVE
                    self.eye = 0
        self.trap_logic()
        self.update()
        if self.allow_blit:
            window.blit(self.image, self.rect)


class Blinky(Ghost):
    def __init__(self, player):
        # path setup
        super().__init__("blinky", blinky_spawn, blinkyhome, blinkyspeed, player)
        self.curr_node = self.getHomeNodeFromTiles(2, 0)
        self.next_node = self.curr_node.neighbours[LEFT]
        self.rect = self.image.get_rect(center=(self.curr_node.position))
        self.dot_limit = 0

    def get_target(self):
        return (self.player.rect.centerx, self.player.rect.centery)


class Pinky(Ghost):
    def __init__(self, player):
        # path setup
        super().__init__("pinky", pinky_spawn, pinkyhome, pinkyspeed, player)
        self.curr_node = self.getHomeNodeFromTiles(2, 2)
        self.next_node = self.curr_node.neighbours[RIGHT]
        self.rect = self.image.get_rect(center=(self.curr_node.position))
        self.dot_limit = 0

    def get_target(self):
        return (
            self.player.rect.centerx + pinky_fudge[self.player.angle][0],
            self.player.rect.centery + pinky_fudge[self.player.angle][1],
        )


class Inky(Ghost):
    def __init__(self, player, blinky):
        # path setup
        super().__init__("inky", inky_spawn, inkyhome, inkyspeed, player)
        self.blinky = blinky
        self.curr_node = self.getHomeNodeFromTiles(2, 2)
        self.next_node = self.curr_node.neighbours[RIGHT]
        self.rect = self.image.get_rect(center=(self.curr_node.position))
        self.dot_limit = 30

    def get_target(self):
        self.origin = (
            self.player.rect.centerx - inky_fudge[self.player.angle][0],
            self.player.rect.centery - inky_fudge[self.player.angle][1],
        )
        dx = self.blinky.rect.centerx - self.origin[0]
        dy = self.blinky.rect.centery - self.origin[1]
        return (self.origin[0] - dx, self.origin[1] - dy)


class Clyde(Ghost):
    def __init__(self, player):
        # path setup
        super().__init__("clyde", clyde_spawn, clydehome, clydespeed, player)

        self.curr_node = self.getHomeNodeFromTiles(2, 2)
        self.next_node = self.curr_node.neighbours[RIGHT]
        self.rect = self.image.get_rect(center=(self.curr_node.position))
        self.dot_limit = 90

    def get_target(self):
        px = self.player.rect.centerx
        py = self.player.rect.centery
        cx = self.rect.centerx
        cy = self.rect.centery
        d = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
        if d < 100:
            return (px, py)
        else:
            return clydehome
