import pygame


class AnimatedSprite:
    def __init__(self, frames, frame_duration=0.1):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.timer = 0.0
        self.paused = False
        self.loop = True
        self.finished = False

    def update(self, dt):
        if self.paused or self.finished:
            return
        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer -= self.frame_duration
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

    def get_frame(self):
        if not self.frames:
            return None
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.timer = 0.0
        self.finished = False

    def copy(self):
        a = AnimatedSprite(self.frames[:], self.frame_duration)
        a.current_frame = self.current_frame
        a.timer = self.timer
        a.paused = self.paused
        a.loop = self.loop
        a.finished = self.finished
        return a


def create_surface(color, width, height):
    surf = pygame.Surface((width, height))
    surf.fill(color)
    return surf


def load_spritesheet(path, tile_width, tile_height):
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for y in range(0, sheet.get_height(), tile_height):
        for x in range(0, sheet.get_width(), tile_width):
            frame = sheet.subsurface((x, y, tile_width, tile_height))
            frames.append(frame)
    return frames


def generate_pixel_character(w, h, colors):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            color = colors.get((x, y))
            if color:
                surf.set_at((x, y), color)
    return surf
