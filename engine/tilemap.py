import pygame
import math
import random

TILE_SIZE = 32

# ─── Palette Definitions ───────────────────────────────────────
# Each palette overrides tile_colors (tile_id -> RGB) and
# optional animated colors (tile_id -> {"color": RGB, ...}).
# None = use default tilemap colors.

PALETTES = {
    "default": {
        "tile_colors": {
            0: (20, 20, 30), 1: (40, 40, 60), 2: (60, 50, 80),
            3: (100, 40, 40), 4: (30, 60, 30), 5: (50, 30, 50),
            6: (80, 60, 100), 7: (60, 100, 80), 8: (100, 60, 120),
            9: (40, 80, 100),
        },
        "animated": {
            4: {"color": (60, 140, 60)}, 5: {"color": (100, 60, 120)},
            6: {"color": (140, 100, 180)}, 7: {"color": (60, 180, 120)},
            8: {"color": (160, 80, 180)}, 9: {"color": (60, 120, 180)},
        },
    },
    "purple": {
        "tile_colors": {
            0: (15, 10, 25), 1: (50, 30, 70), 2: (70, 40, 90),
            3: (90, 30, 60), 4: (40, 20, 50), 5: (70, 30, 80),
            6: (100, 50, 130), 7: (70, 50, 100), 8: (120, 50, 140),
            9: (50, 30, 90),
        },
        "animated": {
            4: {"color": (100, 40, 120)}, 5: {"color": (140, 50, 160)},
            6: {"color": (160, 70, 190)}, 7: {"color": (100, 60, 140)},
            8: {"color": (180, 60, 200)}, 9: {"color": (80, 50, 160)},
        },
    },
    "green": {
        "tile_colors": {
            0: (15, 22, 15), 1: (30, 55, 35), 2: (40, 70, 45),
            3: (60, 80, 35), 4: (25, 75, 30), 5: (35, 65, 40),
            6: (50, 90, 60), 7: (40, 110, 55), 8: (60, 100, 50),
            9: (30, 90, 55),
        },
        "animated": {
            4: {"color": (40, 180, 60)}, 5: {"color": (60, 160, 70)},
            6: {"color": (70, 200, 90)}, 7: {"color": (50, 200, 80)},
            8: {"color": (80, 190, 60)}, 9: {"color": (40, 170, 80)},
        },
    },
    "red": {
        "tile_colors": {
            0: (25, 10, 10), 1: (65, 25, 25), 2: (85, 35, 30),
            3: (120, 25, 20), 4: (60, 20, 20), 5: (75, 25, 30),
            6: (100, 35, 40), 7: (90, 40, 30), 8: (130, 30, 40),
            9: (70, 30, 35),
        },
        "animated": {
            4: {"color": (140, 30, 30)}, 5: {"color": (160, 40, 40)},
            6: {"color": (190, 50, 50)}, 7: {"color": (160, 50, 30)},
            8: {"color": (200, 40, 50)}, 9: {"color": (140, 40, 40)},
        },
    },
    "blue": {
        "tile_colors": {
            0: (10, 15, 30), 1: (25, 40, 70), 2: (35, 50, 85),
            3: (40, 35, 80), 4: (15, 40, 60), 5: (25, 35, 70),
            6: (40, 55, 100), 7: (30, 65, 90), 8: (50, 50, 120),
            9: (20, 60, 100),
        },
        "animated": {
            4: {"color": (30, 80, 160)}, 5: {"color": (40, 70, 180)},
            6: {"color": (60, 90, 210)}, 7: {"color": (40, 100, 180)},
            8: {"color": (60, 70, 200)}, 9: {"color": (30, 90, 190)},
        },
    },
    "cyan": {
        "tile_colors": {
            0: (10, 22, 25), 1: (25, 55, 60), 2: (35, 65, 75),
            3: (40, 60, 65), 4: (15, 60, 55), 5: (25, 55, 65),
            6: (40, 80, 90), 7: (30, 100, 85), 8: (50, 75, 100),
            9: (20, 85, 80),
        },
        "animated": {
            4: {"color": (30, 150, 130)}, 5: {"color": (40, 130, 150)},
            6: {"color": (60, 170, 180)}, 7: {"color": (40, 190, 150)},
            8: {"color": (60, 140, 180)}, 9: {"color": (30, 160, 150)},
        },
    },
    "rainbow": {
        "tile_colors": {
            0: random.choice([(20, 10, 30), (10, 22, 15), (25, 10, 10), (10, 15, 30)]),
            1: (55, 40, 65), 2: (75, 50, 80),
            3: (110, 35, 40), 4: (50, 55, 35), 5: (65, 40, 55),
            6: (90, 60, 100), 7: (70, 95, 75), 8: (120, 55, 110),
            9: (50, 75, 95),
        },
        "animated": {
            4: {"color": (100, 160, 60)}, 5: {"color": (180, 60, 140)},
            6: {"color": (140, 100, 200)}, 7: {"color": (60, 200, 120)},
            8: {"color": (200, 80, 160)}, 9: {"color": (60, 120, 210)},
        },
    },
}


class Tilemap:
    def __init__(self, width, height, palette_name="default"):
        self.width = width
        self.height = height
        self.tiles = [[0 for _ in range(width)] for _ in range(height)]
        self.collision_map = [[False for _ in range(width)] for _ in range(height)]
        self.time = 0.0

        self.tile_colors = dict(PALETTES["default"]["tile_colors"])
        self.animated = {}
        for tid, data in PALETTES["default"]["animated"].items():
            self.animated[tid] = dict(data)
            base_anim = {
                4: {"type": "pulse", "speed": 2.0, "amp": 30},
                5: {"type": "pulse", "speed": 1.5, "amp": 40},
                6: {"type": "pulse", "speed": 2.5, "amp": 35},
                7: {"type": "glow", "speed": 1.2, "amp": 20},
                8: {"type": "flicker", "speed": 8.0, "amp": 50},
                9: {"type": "deep_glow", "speed": 1.8, "amp": 30},
            }
            for k, v in base_anim.get(tid, {}).items():
                if k not in self.animated[tid]:
                    self.animated[tid][k] = v

        self.set_palette(palette_name)

    def set_palette(self, name):
        p = PALETTES.get(name)
        if not p:
            return
        for tid, color in p["tile_colors"].items():
            self.tile_colors[tid] = color
        for tid, data in p.get("animated", {}).items():
            if tid in self.animated:
                for k, v in data.items():
                    self.animated[tid][k] = v

    def set_tile(self, col, row, tile_id, solid=False):
        if 0 <= row < self.height and 0 <= col < self.width:
            self.tiles[row][col] = tile_id
            self.collision_map[row][col] = solid

    def get_tile(self, col, row):
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.tiles[row][col]
        return 0

    def is_solid(self, col, row):
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.collision_map[row][col]
        return True

    def collides_with_rect(self, rect):
        left = rect.left // TILE_SIZE
        right = (rect.right - 1) // TILE_SIZE
        top = rect.top // TILE_SIZE
        bottom = (rect.bottom - 1) // TILE_SIZE
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if self.is_solid(col, row):
                    return True
        return False

    def _get_anim_color(self, tile_id, base_color):
        anim = self.animated.get(tile_id)
        if not anim:
            return base_color
        t = self.time * anim["speed"]
        amp = anim["amp"]
        if anim["type"] == "pulse":
            factor = 0.5 + 0.5 * math.sin(t)
            r = min(255, int(anim["color"][0] * factor + base_color[0] * (1 - factor * 0.3)))
            g = min(255, int(anim["color"][1] * factor + base_color[1] * (1 - factor * 0.3)))
            b = min(255, int(anim["color"][2] * factor + base_color[2] * (1 - factor * 0.3)))
            return (r, g, b)
        elif anim["type"] == "glow":
            factor = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(t))
            r = min(255, int(base_color[0] + anim["color"][0] * factor * 0.4))
            g = min(255, int(base_color[1] + anim["color"][1] * factor * 0.4))
            b = min(255, int(base_color[2] + anim["color"][2] * factor * 0.4))
            return (r, g, b)
        elif anim["type"] == "flicker":
            flicker = abs(math.sin(t))
            offset = int(amp * flicker)
            r = min(255, base_color[0] + offset)
            g = min(255, base_color[1] + offset)
            b = min(255, base_color[2] + offset)
            return (r, g, b)
        elif anim["type"] == "deep_glow":
            factor = 0.5 + 0.5 * math.sin(t + 1.0)
            r = min(255, int(base_color[0] + anim["color"][0] * factor * 0.3))
            g = min(255, int(base_color[1] + anim["color"][1] * factor * 0.3))
            b = min(255, int(base_color[2] + anim["color"][2] * factor * 0.3))
            return (r, g, b)
        return base_color

    def update(self, dt):
        self.time += dt

    def render_tile_decorations(self, surface, camera, tile_id, sx, sy):
        anim = self.animated.get(tile_id)
        if not anim:
            return
        cx = sx + TILE_SIZE // 2
        cy = sy + TILE_SIZE // 2
        t = self.time * anim["speed"]
        amp = anim.get("amp", 20)

        if tile_id == 4:
            radius = 2 + int(math.sin(t) * 1.5)
            c = anim["color"]
            for i in range(4):
                ox = int(math.cos(t + i * 1.57) * 6)
                oy = int(math.sin(t + i * 1.57) * 6)
                pygame.draw.circle(surface, (c[0], c[1], c[2], 100), (cx + ox, cy + oy), max(1, radius))
        elif tile_id == 5:
            radius = 2 + int(1.5 + 1.0 * math.sin(t))
            pygame.draw.circle(surface, anim["color"], (cx, cy), radius)
        elif tile_id == 6:
            radius = 3 + int(2.0 * math.sin(t))
            for i in range(3):
                ox = int(math.cos(t * 0.7 + i * 2.09) * radius)
                oy = int(math.sin(t * 0.7 + i * 2.09) * radius)
                pygame.draw.circle(surface, anim["color"], (cx + ox, cy + oy), max(1, radius // 2))
        elif tile_id == 7:
            size = 4 + int(2.0 * math.sin(t))
            glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*anim["color"][:3], 80), (size, size), size)
            surface.blit(glow_surf, (cx - size, cy - size))
        elif tile_id == 8:
            if abs(math.sin(t)) > 0.7:
                size = 3
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*anim["color"][:3], 60), (size * 2, size * 2), size * 2)
                surface.blit(glow_surf, (cx - size * 2, cy - size * 2))
                pygame.draw.circle(surface, anim["color"], (cx, cy), size)
        elif tile_id == 9:
            radius = 2 + int(1.5 * math.sin(t * 0.5))
            pygame.draw.circle(surface, anim["color"], (cx - 4 + int(math.sin(t) * 3), cy - 4 + int(math.cos(t) * 3)), radius)
            pygame.draw.circle(surface, anim["color"], (cx + 4 + int(math.cos(t) * 3), cy + 4 + int(math.sin(t) * 3)), radius)

    def render(self, surface, camera=None):
        start_col = max(0, int(camera.x // TILE_SIZE)) if camera else 0
        start_row = max(0, int(camera.y // TILE_SIZE)) if camera else 0
        end_col = min(self.width, start_col + (surface.get_width() // TILE_SIZE) + 2)
        end_row = min(self.height, start_row + (surface.get_height() // TILE_SIZE) + 2)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_id = self.tiles[row][col]
                if tile_id == 0:
                    continue
                base = self.tile_colors.get(tile_id, (255, 0, 255))
                color = self._get_anim_color(tile_id, base)
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                if camera:
                    sx, sy = camera.world_to_screen(x, y)
                else:
                    sx, sy = x, y
                pygame.draw.rect(surface, color, (sx, sy, TILE_SIZE, TILE_SIZE))
                if self.collision_map[row][col]:
                    pygame.draw.rect(surface, (0, 0, 0), (sx, sy, TILE_SIZE, TILE_SIZE), 1)
                self.render_tile_decorations(surface, camera, tile_id, sx, sy)

        # Ground-level fog for deeper tiers
        if camera:
            for row in range(start_row, end_row):
                for col in range(start_col, end_col):
                    tile_id = self.tiles[row][col]
                    if tile_id in (6, 8, 9):
                        x = col * TILE_SIZE
                        y = row * TILE_SIZE
                        sx, sy = camera.world_to_screen(x, y)
                        fog = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        alpha = int(15 + 10 * math.sin(self.time * 0.5 + row * 0.3 + col * 0.7))
                        fog.fill((0, 0, 20, alpha))
                        surface.blit(fog, (sx, sy))
