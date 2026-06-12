import pygame


class Camera:
    def __init__(self, width, height, world_width, world_height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.world_width = world_width
        self.world_height = world_height
        self.target = None
        self.smoothing = 5.0

    def follow(self, target):
        self.target = target

    def update(self, dt):
        if self.target:
            tx = self.target.x - self.width // 2 + self.target.width // 2
            ty = self.target.y - self.height // 2 + self.target.height // 2
            self.x += (tx - self.x) * self.smoothing * dt
            self.y += (ty - self.y) * self.smoothing * dt

        self.x = max(0, min(self.x, self.world_width - self.width))
        self.y = max(0, min(self.y, self.world_height - self.height))

    def apply(self, rect):
        return rect.move(-self.x, -self.y)

    def apply_point(self, x, y):
        return (x - self.x, y - self.y)

    def apply_rect(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

    def world_to_screen(self, x, y):
        return (x - self.x, y - self.y)

    def screen_to_world(self, x, y):
        return (x + self.x, y + self.y)
