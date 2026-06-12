import random
import math
import pygame
from engine.tilemap import Tilemap, TILE_SIZE
from game.constants import *


ZONE_COLORS = {
    1: (20, 18, 30),
    2: (25, 18, 35),
    3: (18, 12, 30),
    4: (14, 10, 28),
    5: (10, 6, 24),
    6: (6, 4, 20),
}


class World:
    def __init__(self, palette_name="default"):
        self.width_tiles = WORLD_WIDTH // TILE_SIZE
        self.height_tiles = WORLD_HEIGHT // TILE_SIZE
        self.tilemap = Tilemap(self.width_tiles, self.height_tiles, palette_name)
        self.palette_name = palette_name
        self.spawn_points = []
        self.portals = []
        self.portal_time = 0.0
        self._generate()
        self._place_portals()

    def _get_tier_at(self, col, row):
        cx = self.width_tiles // 2
        cy = self.height_tiles // 2
        dist = math.sqrt((col - cx) ** 2 + (row - cy) ** 2)
        max_dist = math.sqrt(cx ** 2 + cy ** 2)
        ratio = dist / max_dist
        if ratio < 0.25:
            return 1
        elif ratio < 0.45:
            return 2
        elif ratio < 0.6:
            return 3
        elif ratio < 0.75:
            return 4
        elif ratio < 0.9:
            return 5
        else:
            return 6

    def _generate(self):
        for row in range(self.height_tiles):
            for col in range(self.width_tiles):
                if (row == 0 or row == self.height_tiles - 1 or
                    col == 0 or col == self.width_tiles - 1):
                    self.tilemap.set_tile(col, row, 1, solid=True)
                else:
                    tier = self._get_tier_at(col, row)
                    if tier >= 2 and random.random() < 0.02:
                        self.tilemap.set_tile(col, row, 2, solid=True)
                    elif tier >= 3 and random.random() < 0.025:
                        self.tilemap.set_tile(col, row, 4)
                    elif tier >= 4 and random.random() < 0.02:
                        self.tilemap.set_tile(col, row, 5)

        # Animated flora tiles — pulsing trees, glowing flora, void blossoms
        for row in range(self.height_tiles):
            for col in range(self.width_tiles):
                tier = self._get_tier_at(col, row)
                r = random.random()
                if tier == 1:
                    if r < 0.04:
                        self.tilemap.set_tile(col, row, 7)
                elif tier == 2:
                    if r < 0.05:
                        self.tilemap.set_tile(col, row, 7)
                    elif r < 0.08:
                        self.tilemap.set_tile(col, row, 4)
                elif tier == 3:
                    if r < 0.06:
                        self.tilemap.set_tile(col, row, 6)
                    elif r < 0.10:
                        self.tilemap.set_tile(col, row, 5)
                    elif r < 0.13:
                        self.tilemap.set_tile(col, row, 7)
                elif tier == 4:
                    if r < 0.07:
                        self.tilemap.set_tile(col, row, 6)
                    elif r < 0.12:
                        self.tilemap.set_tile(col, row, 8)
                    elif r < 0.16:
                        self.tilemap.set_tile(col, row, 5)
                elif tier == 5:
                    if r < 0.08:
                        self.tilemap.set_tile(col, row, 8)
                    elif r < 0.14:
                        self.tilemap.set_tile(col, row, 9)
                    elif r < 0.18:
                        self.tilemap.set_tile(col, row, 6)
                else:
                    if r < 0.10:
                        self.tilemap.set_tile(col, row, 9)
                    elif r < 0.17:
                        self.tilemap.set_tile(col, row, 8)
                    elif r < 0.22:
                        self.tilemap.set_tile(col, row, 6)

        # Rock clusters
        for _ in range(10):
            rx = random.randint(5, self.width_tiles - 5)
            ry = random.randint(5, self.height_tiles - 5)
            self.tilemap.set_tile(rx, ry, 3, solid=True)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if random.random() < 0.6:
                        self.tilemap.set_tile(rx + dx, ry + dy, 3, solid=True)

        for _ in range(6):
            col = random.randint(3, self.width_tiles - 4)
            row = random.randint(3, self.height_tiles - 4)
            self.spawn_points.append((col * TILE_SIZE, row * TILE_SIZE))

    def _place_portals(self):
        margin = 3
        corners = [
            (margin, margin),
            (self.width_tiles - margin - 1, margin),
            (margin, self.height_tiles - margin - 1),
            (self.width_tiles - margin - 1, self.height_tiles - margin - 1),
        ]
        for cx, cy in corners:
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    col = cx + dx
                    row = cy + dy
                    if 0 <= col < self.width_tiles and 0 <= row < self.height_tiles:
                        self.tilemap.set_tile(col, row, 0, solid=False)
            px = cx * TILE_SIZE
            py = cy * TILE_SIZE
            self.portals.append(pygame.Rect(px - 16, py - 16, 64, 64))

    def update(self, dt):
        self.tilemap.update(dt)
        self.portal_time += dt

    def get_tier_at_position(self, x, y):
        col = int(x // TILE_SIZE)
        row = int(y // TILE_SIZE)
        return self._get_tier_at(col, row)

    def get_spawn_point(self):
        if self.spawn_points:
            p = random.choice(self.spawn_points)
            self.spawn_points.remove(p)
            return p
        return (TILE_SIZE * 5, TILE_SIZE * 5)

    def is_solid(self, x, y):
        col = int(x // TILE_SIZE)
        row = int(y // TILE_SIZE)
        return self.tilemap.is_solid(col, row)

    def collides(self, rect):
        return self.tilemap.collides_with_rect(rect)

    def resolve_collision(self, entity, phase=False):
        if phase:
            return
        if not self.collides(entity.rect):
            return
        entity.rect.x = entity.x
        if self.collides(entity.rect):
            if entity.vx > 0:
                entity.rect.right = (entity.rect.right // TILE_SIZE) * TILE_SIZE
            elif entity.vx < 0:
                entity.rect.left = ((entity.rect.left // TILE_SIZE) + 1) * TILE_SIZE
            entity.x = entity.rect.x
            entity.vx = 0
        entity.rect.y = entity.y
        if self.collides(entity.rect):
            if entity.vy > 0:
                entity.rect.bottom = (entity.rect.bottom // TILE_SIZE) * TILE_SIZE
            elif entity.vy < 0:
                entity.rect.top = ((entity.rect.top // TILE_SIZE) + 1) * TILE_SIZE
            entity.y = entity.rect.y
            entity.vy = 0

    def clamp_entity(self, entity):
        margin = TILE_SIZE
        entity.x = max(margin, min(entity.x, WORLD_WIDTH - entity.width - margin))
        entity.y = max(margin, min(entity.y, WORLD_HEIGHT - entity.height - margin))
        entity.rect.x = entity.x
        entity.rect.y = entity.y

    def render(self, surface, camera):
        self.tilemap.render(surface, camera)
        t = self.portal_time
        for rect in self.portals:
            sx = rect.x - camera.x
            sy = rect.y - camera.y
            if sx < -100 or sx > camera.width + 100 or sy < -100 or sy > camera.height + 100:
                continue
            # Glow rings
            for i in range(3):
                radius = 20 + i * 8 + int(math.sin(t * 2 + i * 1.5) * 6)
                alpha = 100 - i * 30
                c = (100 + int(math.sin(t * 1.5 + i) * 40),
                     60 + int(math.sin(t * 2.2 + i * 2) * 30),
                     180 + int(math.sin(t * 1.8 + i * 1.5) * 40))
                c = tuple(max(0, min(255, v)) for v in c)
                ring = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(ring, (*c, alpha), (radius, radius), radius, 2)
                surface.blit(ring, (sx + rect.width // 2 - radius, sy + rect.height // 2 - radius))
            # Core
            core_radius = 6 + int(math.sin(t * 3) * 2)
            core_color = (160 + int(math.sin(t * 2) * 40),
                          100 + int(math.sin(t * 2.5) * 30),
                          220 + int(math.sin(t * 1.5) * 35))
            core_color = tuple(max(0, min(255, v)) for v in core_color)
            pygame.draw.circle(surface, core_color,
                               (int(sx + rect.width // 2), int(sy + rect.height // 2)),
                               core_radius)

    def get_random_enemy_spawn(self, player_level=1):
        tier_bias = min(6, max(1, player_level // 2 + 1))
        for _ in range(30):
            x = random.randint(TILE_SIZE * 3, WORLD_WIDTH - TILE_SIZE * 3)
            y = random.randint(TILE_SIZE * 3, WORLD_HEIGHT - TILE_SIZE * 3)
            tier = self._get_tier_at(x // TILE_SIZE, y // TILE_SIZE)
            if abs(tier - tier_bias) <= 2:
                test_rect = pygame.Rect(x, y, 22, 22)
                if not self.collides(test_rect):
                    return (x, y)
        for _ in range(10):
            x = random.randint(TILE_SIZE * 3, WORLD_WIDTH - TILE_SIZE * 3)
            y = random.randint(TILE_SIZE * 3, WORLD_HEIGHT - TILE_SIZE * 3)
            test_rect = pygame.Rect(x, y, 22, 22)
            if not self.collides(test_rect):
                return (x, y)
        return (TILE_SIZE * 10, TILE_SIZE * 10)
