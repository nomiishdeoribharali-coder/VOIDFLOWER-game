import pygame
import random
import math


class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=3, shrink=True, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.start_color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.start_size = size
        self.shrink = shrink
        self.fade = fade
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.alive = False
            return

        t = 1.0 - (self.lifetime / self.max_lifetime)

        if self.shrink:
            self.size = self.start_size * (1.0 - t * 0.8)

        self.vx *= 0.98
        self.vy *= 0.98

    def render(self, surface, camera=None):
        if not self.alive:
            return
        sx, sy = self.x, self.y
        if camera:
            sx, sy = camera.world_to_screen(self.x, self.y)

        t = 1.0 - (self.lifetime / self.max_lifetime)
        color = self.color
        if self.fade:
            alpha = int(255 * (1.0 - t))
            r = max(0, min(255, color[0]))
            g = max(0, min(255, color[1]))
            b = max(0, min(255, color[2]))
            color = (r, g, b, alpha)

        size = max(1, int(self.size))
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (size, size), size)
        surface.blit(surf, (sx - size, sy - size))


class ParticleEmitter:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=10, color=(200, 200, 255), speed=100,
             lifetime=1.0, size=3, spread=2*math.pi, shrink=True, fade=True):
        for _ in range(count):
            angle = random.uniform(0, spread)
            if spread >= 2 * math.pi:
                angle = random.uniform(0, 2 * math.pi)
            speed_v = random.uniform(speed * 0.5, speed * 1.5)
            vx = math.cos(angle) * speed_v
            vy = math.sin(angle) * speed_v
            lt = random.uniform(lifetime * 0.5, lifetime * 1.5)
            sz = random.uniform(size * 0.5, size * 1.5)
            p = Particle(x, y, vx, vy, color, lt, sz, shrink, fade)
            self.particles.append(p)

    def burst(self, x, y, color, count=20, speed=150, lifetime=0.8, size=4):
        self.emit(x, y, count, color, speed, lifetime, size, spread=2*math.pi)

    def stream(self, x, y, color, rate=20, speed=80, lifetime=0.6, size=2):
        self.emit(x, y, 1, color, speed, lifetime, size, spread=0.5)

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self.particles.remove(p)

    def render(self, surface, camera=None):
        for p in self.particles:
            p.render(surface, camera)

    def clear(self):
        self.particles.clear()
