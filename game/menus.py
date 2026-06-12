import pygame
import math
import random
from engine.core import Scene
from engine.ui import Text, Button
from game.constants import *
from game.constants import FONT_PATH


MENU_THEME = "data/audio/a3_menu"

class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title_text = Text("VOIDFLOWER", 64, COLOR_TITLE)
        self.subtitle_text = Text("A Sorcery RPG", 24, COLOR_TEXT_DIM)
        self.start_btn = Button(
            pygame.Rect(WINDOW_WIDTH // 2 - 100, 350, 200, 50),
            "Begin Journey",
            callback=self.start_game,
            color=(60, 50, 90),
            hover_color=(100, 80, 140),
            audio_manager=self.game.audio,
        )
        self.controls_btn = Button(
            pygame.Rect(WINDOW_WIDTH // 2 - 100, 420, 200, 50),
            "Controls",
            callback=self.show_controls,
            color=(40, 35, 60),
            hover_color=(70, 60, 100),
            audio_manager=self.game.audio,
        )
        self.showing_controls = False
        self.controls_text = Text("", 18, COLOR_TEXT)
        self.back_btn = None
        self.time = 0.0
        self.stars = []
        self._init_stars()

    def _init_stars(self):
        for _ in range(15):
            self.stars.append({
                "x": random.randint(0, WINDOW_WIDTH),
                "y": random.randint(0, WINDOW_HEIGHT // 2),
                "speed": random.uniform(80, 180),
                "life": 0,
                "timer": random.uniform(0, 3),
                "active": False,
            })

    def enter(self):
        self.showing_controls = False
        self.game.audio.play_theme("menu", MENU_THEME)

    def start_game(self):
        self.game.switch_scene("game")

    def show_controls(self):
        self.showing_controls = True
        self.back_btn = Button(
            pygame.Rect(WINDOW_WIDTH // 2 - 80, 500, 160, 40),
            "Back",
            callback=self.hide_controls,
            color=(40, 35, 60),
            hover_color=(70, 60, 100),
            audio_manager=self.game.audio,
        )

    def hide_controls(self):
        self.showing_controls = False
        self.back_btn = None

    def handle_event(self, event):
        if self.showing_controls:
            if self.back_btn:
                self.back_btn.handle_event(event)
        else:
            self.start_btn.handle_event(event)
            self.controls_btn.handle_event(event)

    def update(self, dt):
        self.time += dt
        for s in self.stars:
            s["timer"] -= dt
            if s["timer"] <= 0 and not s["active"]:
                s["active"] = True
                s["x"] = random.randint(-100, 0)
                s["y"] = random.randint(0, WINDOW_HEIGHT // 3)
                s["life"] = random.uniform(0.6, 1.5)
                s["timer"] = random.uniform(2, 5)
            if s["active"]:
                s["x"] += s["speed"] * dt
                s["y"] += s["speed"] * 0.3 * dt
                s["life"] -= dt
                if s["life"] <= 0 or s["x"] > WINDOW_WIDTH + 100:
                    s["active"] = False
                    s["timer"] = random.uniform(2, 6)
                    s["life"] = 0

    def render_controls(self, surface):
        surface.fill(COLOR_BG)
        controls = [
            "WASD / Arrow Keys - Move",
            "Mouse - Aim spells",
            "Left Click - Cast spell",
            "Right Click - Melee with weapon",
            "1-5 - Select spell slot",
            "F - Pick up weapon from ground",
            "M - Toggle music on/off",
            "",
            "Spells:",
            "1. Void Bolt - Basic projectile",
            "2. Cursed Slash - Melee wave",
            "3. Dark Pulse - AoE burst (Lv.3)",
            "4. Void Shield - Defense barrier (Lv.5)",
            "5. Domain Expansion - Ultimate (Lv.7)",
            "",
            "30 Enemy Types across 6 Tiers:",
            "T1: Void Mite, Ash Crawler, Hollow Sprout, Drift Slime, Static Rat",
            "T2: Void Hound, Lantern Leech, Echo Stalker, Thorn Wisp, Broken Sentinel",
            "T3: Petal Reaper, Memory Husk, Rift Walker, Ink Parasite, Bloom Wraith",
            "T4: Void Strategist, Fragment Clone, Data Leech, Silent Executioner, Root Node",
            "T5: Withered Gardener, Hollow Bloom Beast, Rift Colossus, Mirror Warden, Seedless King",
            "T6: Void Bloom Storm, Wanderer, God Shard, Glitch Angel, Quiet Root",
        ]
        title = Text("Controls", 48, COLOR_TITLE, (WINDOW_WIDTH // 2 - 80, 50))
        title.render(surface)
        y = 130
        for line in controls:
            c = COLOR_GOLD if line.startswith("Spells:") or line.startswith("30 Enemy") else COLOR_TEXT
            t = Text(line, 16, c, (WINDOW_WIDTH // 2 - 220, y))
            t.render(surface)
            y += 22
        if self.back_btn:
            self.back_btn.render(surface)

    def render(self, surface):
        if self.showing_controls:
            self.render_controls(surface)
            return

        surface.fill(COLOR_BG)
        t = self.time

        # ── Purplish-white sun (top-right corner) ──
        sun_x = WINDOW_WIDTH - 140
        sun_y = 110
        sun_pulse = 0.9 + 0.1 * math.sin(t * 0.8)

        # Outer glow layers
        for radius, alpha in [(160, 12), (120, 20), (80, 35), (50, 50)]:
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            gc = (200, 180, 255, int(alpha * sun_pulse))
            pygame.draw.circle(glow_surf, gc, (radius, radius), radius)
            surface.blit(glow_surf, (sun_x - radius, sun_y - radius))

        # Sun core (purplish-white)
        core_r = int(30 * sun_pulse)
        core_color = (220 + int(35 * sun_pulse), 190 + int(40 * sun_pulse), 255, 200)
        pygame.draw.circle(surface, core_color[:3], (sun_x, sun_y), core_r)
        pygame.draw.circle(surface, (255, 240, 255), (sun_x, sun_y), int(core_r * 0.5))

        # Sun rays
        for i in range(12):
            angle = t * 0.3 + i * (2 * math.pi / 12)
            ray_len = 40 + 15 * math.sin(t * 1.2 + i)
            ex = sun_x + math.cos(angle) * ray_len
            ey = sun_y + math.sin(angle) * ray_len
            ray_alpha = int(30 + 20 * math.sin(t * 0.8 + i))
            pygame.draw.line(surface, (200, 180, 255, ray_alpha),
                            (sun_x, sun_y), (ex, ey), 1)

        # ── Shooting stars ──
        for s in self.stars:
            if s["active"]:
                sx, sy = int(s["x"]), int(s["y"])
                # Trail
                for j in range(5):
                    trail_alpha = int(60 * (1 - j / 5) * min(1, s["life"] * 2))
                    tsx = sx - int(j * s["speed"] * 0.008)
                    tsy = sy - j
                    pygame.draw.circle(surface, (200, 180, 255, trail_alpha),
                                     (tsx, tsy), max(1, 2 - j // 2))
                # Head
                pygame.draw.circle(surface, (255, 240, 255), (sx, sy), 2)
                pygame.draw.circle(surface, (220, 200, 255), (sx, sy), 1)

        # ── Decorative background particles ──
        for i in range(30):
            x = (i * 137 + int(t * 20)) % WINDOW_WIDTH
            y = (i * 89 + int(t * 15)) % WINDOW_HEIGHT
            alpha = 30 + i * 7 % 40
            pygame.draw.circle(surface, (100, 60, 180, alpha), (x, y), 1)

        self.title_text.render(surface, (WINDOW_WIDTH // 2 - self.title_text.width // 2, 150))
        self.subtitle_text.render(surface, (WINDOW_WIDTH // 2 - self.subtitle_text.width // 2, 220))

        glow_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (100, 60, 180, 30), (100, 100), 100)
        surface.blit(glow_surf, (WINDOW_WIDTH // 2 - 100, 240))

        self.start_btn.render(surface)
        self.controls_btn.render(surface)

        ver_text = Text("v1.0", 14, COLOR_TEXT_DIM, (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 25))
        ver_text.render(surface)


class GameOverScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.level = 1
        self.time = 0.0
        self.title = Text("YOU ARE DEAD", 48, (200, 30, 30))
        self.subtitle = Text("", 22, COLOR_TEXT_DIM)
        self.detail = Text("The void claims another soul...", 16, (120, 100, 130))
        self.retry_btn = Button(
            pygame.Rect(WINDOW_WIDTH // 2 - 100, 360, 200, 50),
            "Try Again",
            callback=self.retry,
            color=(60, 30, 40),
            hover_color=(100, 50, 60),
            audio_manager=game.audio,
        )
        self.menu_btn = Button(
            pygame.Rect(WINDOW_WIDTH // 2 - 100, 430, 200, 50),
            "Title Screen",
            callback=self.go_title,
            color=(40, 35, 60),
            hover_color=(70, 60, 100),
            audio_manager=game.audio,
        )

    def enter(self):
        self.time = 0.0
        game_scene = self.game.scenes.get("game")
        if game_scene and game_scene.player:
            self.level = game_scene.player.level
        self.subtitle.set_text(f"Sorcerer Level {self.level}")
        self.game.audio.crossfade_to("menu", MENU_THEME, 1.5)

    def retry(self):
        self.game.switch_scene("game")

    def go_title(self):
        self.game.switch_scene("title")

    def update(self, dt):
        self.time += dt

    def handle_event(self, event):
        if self.time < 0.5:
            return
        self.retry_btn.handle_event(event)
        self.menu_btn.handle_event(event)

    def render(self, surface):
        surface.fill(COLOR_BG)
        t = self.time

        # Pulsing red glow behind title
        pulse = 0.6 + 0.4 * math.sin(t * 1.5)
        glow_surf = pygame.Surface((400, 100), pygame.SRCALPHA)
        glow_alpha = int(30 * pulse)
        pygame.draw.rect(glow_surf, (180, 20, 20, glow_alpha), (0, 0, 400, 100), border_radius=12)
        gx = WINDOW_WIDTH // 2 - 200
        gy = 160
        surface.blit(glow_surf, (gx, gy))

        self.title.render(surface, (WINDOW_WIDTH // 2 - self.title.width // 2, 180))
        self.subtitle.render(surface, (WINDOW_WIDTH // 2 - self.subtitle.width // 2, 240))
        self.detail.render(surface, (WINDOW_WIDTH // 2 - self.detail.width // 2, 280))

        if t >= 0.5:
            self.retry_btn.render(surface)
            self.menu_btn.render(surface)
