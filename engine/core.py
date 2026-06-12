import pygame
import sys
from engine.audio import AudioManager


class Scene:
    def __init__(self, game):
        self.game = game

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        pass


class Game:
    def __init__(self, title="Voidflower", width=800, height=600, fps=60):
        pygame.init()
        self.width = width
        self.height = height
        self.fps = fps
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = False
        self.dt = 0.0
        self.scenes = {}
        self.current_scene = None
        self.transitioning = False
        self.next_scene_name = None
        self.audio = AudioManager()

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def switch_scene(self, name):
        if name in self.scenes:
            if self.current_scene:
                self.current_scene.exit()
            self.current_scene = self.scenes[name]
            self.current_scene.enter()

    def run(self, start_scene="title"):
        self.running = True
        self.switch_scene(start_scene)

        while self.running:
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.dt = min(self.dt, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.current_scene:
                    self.current_scene.handle_event(event)

            self.audio.update(self.dt)

            if self.current_scene:
                self.current_scene.update(self.dt)

            if self.current_scene:
                self.current_scene.render(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def quit(self):
        self.running = False
