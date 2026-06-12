import pygame
import math
import random
from game.constants import *


class Projectile:
    def __init__(self, x, y, dx, dy, speed, damage, color, size=6, lifetime=2.0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            self.dx /= length
            self.dy /= length
        self.speed = speed
        self.damage = damage
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True
        self.rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
        self.trail = []

    def update(self, dt):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        self.lifetime -= dt
        self.rect.center = (self.x, self.y)

        if len(self.trail) < 8:
            self.trail.append((self.x, self.y))
        else:
            self.trail.pop(0)
            self.trail.append((self.x, self.y))

        if self.lifetime <= 0:
            self.alive = False

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        for i, (tx, ty) in enumerate(self.trail):
            tsx, tsy = camera.world_to_screen(tx, ty)
            alpha = int(155 * (i / len(self.trail)))
            tsize = max(1, int(self.size * (i / len(self.trail)) * 0.7))
            c = (*self.color[:3], alpha)
            trail_surf = pygame.Surface((tsize * 2, tsize * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, c, (tsize, tsize), tsize)
            surface.blit(trail_surf, (tsx - tsize, tsy - tsize))

        c = (*self.color[:3], 255)
        glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color[:3], 80), (self.size * 2, self.size * 2), self.size * 2)
        surface.blit(glow_surf, (sx - self.size * 2, sy - self.size * 2))
        pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.size)


class SlashWave:
    def __init__(self, x, y, dx, dy, damage, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.color = color
        self.speed = 250
        self.size = 0
        self.max_size = 30
        self.alive = True
        self.lifetime = 0.3
        self.max_lifetime = 0.3
        self.hit = set()
        self.rect = pygame.Rect(x - self.max_size, y - self.max_size,
                               self.max_size * 2, self.max_size * 2)

    def update(self, dt):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        t = 1.0 - (self.lifetime / self.max_lifetime)
        self.size = self.max_size * (1.0 - t * 0.5)
        self.lifetime -= dt
        self.rect.center = (self.x, self.y)
        if self.lifetime <= 0:
            self.alive = False

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        s = int(self.size)
        if s < 2:
            return
        arc_rect = pygame.Rect(sx - s, sy - s, s * 2, s * 2)
        start_angle = math.atan2(self.dy, self.dx) - math.pi / 3
        end_angle = math.atan2(self.dy, self.dx) + math.pi / 3
        pygame.draw.arc(surface, self.color, arc_rect, start_angle, end_angle, max(2, s // 8))


class DomainExpansion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 120
        self.alive = True
        self.lifetime = 1.2
        self.max_lifetime = 1.2
        self.damage = 30
        self.hit = set()
        self.rect = pygame.Rect(x - self.max_radius, y - self.max_radius,
                               self.max_radius * 2, self.max_radius * 2)

    def update(self, dt):
        t = 1.0 - (self.lifetime / self.max_lifetime)
        if t < 0.3:
            self.radius = self.max_radius * (t / 0.3)
        else:
            self.radius = self.max_radius
        self.lifetime -= dt
        self.rect.center = (self.x, self.y)
        if self.lifetime <= 0:
            self.alive = False

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        r = int(self.radius)
        if r < 2:
            return
        glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        alpha = int(100 * min(1.0, self.lifetime * 3))
        pygame.draw.circle(glow_surf, (100, 60, 180, alpha), (r, r), r)
        pygame.draw.circle(glow_surf, (180, 140, 255, alpha // 2), (r, r), int(r * 0.7))
        surface.blit(glow_surf, (sx - r, sy - r))
        pygame.draw.circle(surface, COLOR_VOID_LIGHT, (int(sx), int(sy)), r, 2)


class VoidShield:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.alive = True
        self.lifetime = 2.0
        self.max_lifetime = 2.0
        self.hit = set()

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        r = int(self.radius)
        alpha = int(100 * min(1.0, self.lifetime * 2))
        shield_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(shield_surf, (120, 80, 200, alpha), (r, r), r, 2)
        pygame.draw.circle(shield_surf, (80, 60, 140, alpha // 2), (r, r), r - 2)
        surface.blit(shield_surf, (sx - r, sy - r))


class DarkPulse:
    def __init__(self, x, y, damage, color):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.radius = 0
        self.max_radius = 80
        self.speed = 200
        self.alive = True
        self.lifetime = 0.5
        self.hit = set()
        self.rect = pygame.Rect(x - self.max_radius, y - self.max_radius,
                               self.max_radius * 2, self.max_radius * 2)

    def update(self, dt):
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.alive = False
            self.radius = self.max_radius
        self.rect.center = (self.x, self.y)

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        r = int(self.radius)
        if r < 2:
            return
        pulse_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        alpha = int(180 * (1.0 - r / self.max_radius))
        pygame.draw.circle(pulse_surf, (*self.color[:3], alpha), (r, r), r)
        pygame.draw.circle(pulse_surf, (*self.color[:3], alpha // 2), (r, r), int(r * 0.8), 2)
        surface.blit(pulse_surf, (sx - r, sy - r))
