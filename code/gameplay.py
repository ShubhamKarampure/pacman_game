from settings import *


class Clock:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.cur_t = time.time()
        self.last_t = time.time()

        self.power_timer = OFF
        self.power_time = 0
        self.cooling_timer = OFF
        self.cooling_time = 0

    def time_elapsed(self):
        self.cur_t = time.time()
        dt = self.cur_t - self.last_t
        self.last_t = self.cur_t
        return dt

    def tick(self):
        dt = self.time_elapsed()
        if self.power_timer == ON:
            self.power_time += dt
        if self.cooling_timer == ON:
            self.cooling_time += dt

    def reset_timer(self, type):
        setattr(self, f"{type}_time", 0)
        setattr(self, f"{type}_timer", 0)


class GameManager(Clock):
    def __init__(self):
        super().__init__()
        self.game = OFF
        self.game_started = OFF
        self.KEYBOARD = STOP

        # Game Mode
        self.phase = 1
        self.level = 1

        # Entity
        self.ghost_mode = SCATTER
        self.ghost_state = BRAVE

        self.last_time = 0

        self.ghost_sound = pygame.mixer.Sound("sound/sound_ghost.ogg")
        self.ghost_sound_playing = False

        self.ghost_frighten = pygame.mixer.Sound("sound/ghost_frighten.ogg")

        self.victory = 0
        self.victory_sound = pygame.mixer.Sound("sound/pacman_victory.ogg")

        self.lost = 0
        self.lost_sound = pygame.mixer.Sound("sound/Cutscene.ogg")

    def start(self):
        if self.ghost_sound_playing == 0:
            self.ghost_sound.play(-1)
            self.ghost_sound_playing = 1

        self.player.allow_move = 1
        self.last_time = pygame.time.get_ticks()
        for ghost in self.ghosts:
            ghost.allow_move = 1

        self.ghost_mode = SCATTER
        self.scatter_mode()
        self.ghost_state = BRAVE
        pygame.mixer.music.stop()
        self.game_started = ON

    def stop(self):
        self.player.allow_move = 0
        for ghost in self.ghosts:
            ghost.allow_move = 0

    def reset(self):
        self.player.reset()
        for ghost in self.ghosts:
            ghost.reset()
        self.KEYBOARD = STOP
        self.start()

    def chase_mode(self):
        self.ghost_mode = CHASE
        self.last_time = pygame.time.get_ticks()
        for ghost in self.ghosts:
            ghost.mode = CHASE
            if ghost.curr_direction != STOP:
                ghost.reverse_direction()

    def scatter_mode(self):
        self.ghost_mode = SCATTER
        self.last_time = pygame.time.get_ticks()
        for ghost in self.ghosts:
            ghost.mode = SCATTER
            if ghost.curr_direction != STOP:
                ghost.reverse_direction()

    def frighten_state(self):
        self.ghost_sound.stop()
        self.ghost_sound_playing = 0
        pygame.mixer.music.pause()
        self.power_timer = 1
        self.reset_timer("power")
        self.ghost_state = FRIGHTEN
        for ghost in self.ghosts:
            ghost.blink = 0
            ghost.state = FRIGHTEN

    def brave_state(self):
        self.player.no_of_ghost_killed = 0
        self.ghost_frighten.stop()
        if not self.ghost_sound_playing:
            self.ghost_sound.play()
            self.ghost_sound_playing = 1

        self.power_timer = 0
        self.ghost_state = BRAVE
        for ghost in self.ghosts:
            ghost.state = BRAVE

    def switch_modes(self):
        now = pygame.time.get_ticks()
        if self.phase <= 4:
            if self.ghost_mode == SCATTER and (now - self.last_time) / 1000 >= 7:
                self.chase_mode()
            elif self.ghost_mode == CHASE and (now - self.last_time) / 1000 >= 20:
                self.scatter_mode()
                self.phase += 1  # Next Phase

    def switch_states(self):
        if self.player.power:
            self.last_time = self.last_time + 6 * 1000
            self.frighten_state()
            self.power_timer = 1
            self.player.power = 0

        if self.power_time >= 6:
            self.brave_state()
            for ghost in self.ghosts:
                ghost.blink = 0
        elif 5 <= self.power_time <= 6:
            for ghost in self.ghosts:
                ghost.blink = 1

        if self.player.ghost_killed == 1:
            self.ghost_killed()

    def pacman_killed(self):
        self.cooling_timer = ON
        self.stop()
        self.ghost_sound.stop()
        self.ghost_sound_playing = 0

        for ghost in self.ghosts:
            ghost.allow_blit = 0

        if 1.9 < self.cooling_time and self.player.kill:
            self.window.fill("black")

        if self.cooling_time > 2:
            self.player.kill = 0
            self.player.lives -= 1
            self.text.high_score = self.text.score
            self.reset_timer("cooling")
            self.reset()

    def ghost_killed(self):
        self.cooling_timer = ON
        self.power_timer = OFF
        self.stop()
        self.player.allow_blit = 0
        for ghost in self.ghosts:
            ghost.blink = 0

        if self.cooling_time > 0.5:
            self.power_timer = ON
            self.reset_timer("cooling")
            for ghost in self.ghosts:
                ghost.allow_move = 1
            self.text.score += (2**(self.player.no_of_ghost_killed + 1)) * 100
            self.player.allow_blit = 1
            self.player.allow_move = 1
            self.player.ghost_killed = 0
            self.player.no_of_ghost_killed += 1

    def update(self):
        self.tick()
        self.fruit.update(self.window)
        self.player.run(self.KEYBOARD,self.window)

        for ghost in self.ghosts:
            ghost.run(self.window)

        if self.game == ON and not self.game_started:
            self.start()

        if self.game == ON:
            if self.ghost_state == BRAVE:
                self.switch_modes()
            self.switch_states()

        elif self.game == OFF:
            self.stop()

        if self.player.kill == 1:
            self.pacman_killed()

        if self.player.lives == 0:
            self.game = OFF
            self.ghost_sound_playing = 0
            self.ghost_sound.stop()
            if not self.lost:
                self.lost_sound.play()
                self.lost = 1
            for ghost in self.ghosts:
                ghost.allow_blit = 0
            self.pillet.allow_blit = 0
            self.player.allow_blit = 0

        if len(self.pillet.pillets) == 0 and len(self.pillet.powerpillets) == 0:
            self.cooling_timer = ON
            self.text.high_score = self.text.score
            if not self.victory:
                self.victory_sound.play()
                self.victory = 1

            self.ghost_sound.stop()
            self.game = OFF
            self.wall.blink = 1

            if self.cooling_time > 8:
                self.key = 0
