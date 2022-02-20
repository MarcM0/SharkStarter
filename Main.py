#this project is built on this repo https://github.com/moritree/PY-MAN

import pygame
import pygame.freetype
from Maze import Maze
from Pac_Man import Pac_Man
from Items import *
from Ghost import Ghost
from Constants import *
scaling_factor = 0.75 #factor by which we scale dimensions of game window

class Main:
    def __init__(self):
        self.maze_width = 28
        self.maze_height = 31

        self.lives = 2

        self.display_width = self.maze_width * block_size
        self.display_height = self.maze_height * block_size + offset

        self.fps = 60
        self.fps_clock = pygame.time.Clock()
        self.tick_counter = 1
        self.temp_counter = 0

        self.score = 0
        self.collected_pellets = 0
        self.pellets = []
        self.power_pellets = []
        self.running = True

        self.game_state = "run"

    def events(self, player):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    setattr(player, "look_dir", player.DIR["UP"])
                if event.key == pygame.K_DOWN:
                    setattr(player, "look_dir", player.DIR["DOWN"])
                if event.key == pygame.K_LEFT:
                    setattr(player, "look_dir", player.DIR["LEFT"])
                if event.key == pygame.K_RIGHT:
                    setattr(player, "look_dir", player.DIR["RIGHT"])
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        return

    def loop(self):
        if self.game_state == "run":
            # activate inky once 30 coins have been collected
            if self.ghosts["inky"].mode != "normal" and self.collected_pellets > 30:
                self.ghosts["inky"].mode = "normal"
            # activate clyde once 1/3 of total coins have been collected
            if self.ghosts["clyde"].mode != "normal" and self.collected_pellets > len(self.pellets) / 3:
                self.ghosts["clyde"].mode = "normal"

            self.player.move(self.maze, self.display_width)

            if self.player.powered_up and self.player.update_power_up():
                for ghost in self.ghosts.values():
                    if ghost.mode != "dead" and not ghost.blue:
                        ghost.blue = True
                        ghost.blue_timer = 0
            
            for pellet in self.pellets:
                if pellet.collide(self.player):
                    self.collected_pellets += 1
                    self.score += 10

            for power_pellet in self.power_pellets:
                if power_pellet.collide(self.player):
                    self.score += 50
                    self.player.power_up(8 * self.fps)

            for ghost in self.ghosts.values():
                ghost.move(self.player, self.maze, self.display_width, self.tick_counter, self.ghosts["blinky"].array_coord)
                if ghost.collide(self.player):
                    if ghost.blue:
                        self.score += 200
                    else:
                        if self.lives > 0:
                            self.game_state = "respawn"
                            self.lives -= 1
                            self.temp_counter = 0
                        else:
                            self.game_state = "lose"

    def draw(self, surface, window):
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, self.display_width, self.display_height))

        self.maze.draw(surface)

        for power_pellet in self.power_pellets:
            power_pellet.draw(surface)
        for pellet in self.pellets:
            pellet.draw(surface)

        if self.game_state == "run":
            self.player.draw_while_running(surface, self.display_width, self.maze, self.tick_counter)
        elif self.game_state == "respawn":
            if self.temp_counter < 36:
                self.player.draw_wedge_pacman(surface, 0 + 10 * self.temp_counter)
                self.temp_counter += 1
            else:
                self.game_state = "run"
                self.player.x = spawn_x * block_size + block_size / 2
                self.player.y = spawn_y * block_size + block_size / 2
                self.player.draw_while_running(surface, self.display_width, self.maze, self.tick_counter)
        
        for ghost in self.ghosts.values():
            ghost.draw(surface, self.player, self.fps, self.tick_counter)

        game_font = pygame.freetype.SysFont("Helvetica.ttf", 40)
        game_font.render_to(surface, (15, 15), "SCORE: " + str(self.score), (255, 255, 255))
        game_font = pygame.freetype.SysFont("Helvetica.ttf", 20)
        game_font.render_to(surface, (300, 15), str(self.lives) + " LIVES", (255, 255, 255))

        #scaling code from https://stackoverflow.com/questions/43196126/how-do-you-scale-a-design-resolution-to-other-resolutions-with-pygame
        frame = pygame.transform.scale(surface, (self.display_width*scaling_factor, self.display_height*scaling_factor))
        window.blit(frame, frame.get_rect())
        pygame.display.flip()

    def run(self):
        # initialize
        pygame.init()
        pygame.display.set_caption("NEAT-MAN")
        display = pygame.display.set_mode((self.display_width*scaling_factor, self.display_height*scaling_factor))
        display_surf = pygame.Surface([self.display_width, self.display_height])
        pygame.font.init()

        # spawn maze and player
        self.maze = Maze(self.maze_width, self.maze_height)
        self.player = Pac_Man(spawn_x, spawn_y)

        # generate all pellets and power pellets
        self.power_pellets = []
        for loc in self.maze.power_pellet_locs:
            self.power_pellets.append(PowerPellet(loc[0], loc[1]))
        self.pellets = []
        for loc in self.maze.pellet_locs:
            self.pellets.append(Pellet(loc[0], loc[1]))

        self.ghosts = {}

        # spawn ghosts
        self.ghosts["blinky"] = Ghost(house_x, house_y-2, (255, 80, 80), [house_x+7, house_y-7], "shadow")
        self.ghosts["pinky"] = Ghost(house_x-1, house_y, (255, 100, 150), [house_x-7, house_y-7], "speedy")
        self.ghosts["inky"] = Ghost(house_x, house_y, (100, 255, 255), [house_x+7, house_y+9], "bashful")
        self.ghosts["clyde"] = Ghost(house_x+1, house_y, (255, 200, 000), [house_x-7, house_y+9], "pokey")

        self.ghosts["blinky"].mode = "normal"
        self.ghosts["pinky"].mode = "normal"

        # running game loop
        while self.running:
            if self.game_state in ("run", "respawn"):

                # main game loop
                self.events(self.player)
                self.loop()
                self.draw(display_surf, display)

                # check win condition
                if self.collected_pellets >= len(self.pellets):
                    self.game_state = "win"

                pygame.display.update()
                self.fps_clock.tick(self.fps)
                self.tick_counter += 1

            # end game at win/lose
            elif self.game_state == "win":
                self.running = False
            elif self.game_state == "lose":
                self.running = False


if __name__ == "__main__":
    main = Main()
    main.run()