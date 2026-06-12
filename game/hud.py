import pygame
import math
from game.constants import *
from game.combat import SPELL_DATA
from engine.ui import Text


class AnimatedBar:
    def __init__(self, rect, color, bg_color, border_color, glow_color=None, delay_color=None):
        self.rect = pygame.Rect(rect)
        self.target = 1.0
        self.display = 1.0
        self.delay = 1.0
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color
        self.glow_color = glow_color or color
        self.delay_color = delay_color or (80, 80, 80)
        self.pulse_timer = 0.0

    def update(self, dt, target):
        self.target = max(0, min(1, target))
        old_display = self.display
        diff = self.target - self.display
        self.display += diff * min(1.0, dt * 8.0)
        if abs(diff) < 0.001:
            self.display = self.target
        if self.target < old_display:
            self.delay = max(self.target, self.delay - dt * 2.0)
        else:
            self.delay = self.display
        self.pulse_timer += dt

    def render(self, surface):
        r = self.rect
        pygame.draw.rect(surface, self.bg_color, r, border_radius=3)
        delay_w = int(r.width * self.delay)
        if delay_w > 0 and self.delay > self.display:
            delay_rect = pygame.Rect(r.x, r.y, delay_w, r.height)
            pygame.draw.rect(surface, self.delay_color, delay_rect, border_radius=3)
        fill_w = int(r.width * self.display)
        if fill_w > 0:
            fill_rect = pygame.Rect(r.x, r.y, fill_w, r.height)
            pygame.draw.rect(surface, self.color, fill_rect, border_radius=3)
            if self.glow_color and fill_w > 4:
                glow = pygame.Rect(r.x + fill_w - 4, r.y - 1, 6, r.height + 2)
                glow_surf = pygame.Surface((glow.width, glow.height), pygame.SRCALPHA)
                alpha = int(80 + 40 * math.sin(self.pulse_timer * 4))
                gc = (*self.glow_color[:3], alpha)
                pygame.draw.rect(glow_surf, gc, (0, 0, glow.width, glow.height), border_radius=3)
                surface.blit(glow_surf, (glow.x, glow.y))
        pygame.draw.rect(surface, self.border_color, r, 1, border_radius=3)


class SmoothNumber:
    def __init__(self, color, speed=6.0):
        self.value = 0
        self.display = 0
        self.color = color
        self.speed = speed

    def update(self, dt, value):
        self.value = value
        diff = self.value - self.display
        self.display += diff * min(1.0, dt * self.speed)
        if abs(diff) < 0.5:
            self.display = self.value

    def get_text(self):
        return str(int(round(self.display)))


class FloatingText:
    def __init__(self, x, y, text, color, lifetime=1.2, speed=40):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.timer = lifetime
        self.speed = speed
        self.font = pygame.font.Font(FONT_PATH, 14)

    def update(self, dt):
        self.timer -= dt
        self.y -= self.speed * dt
        return self.timer > 0

    def render(self, surface):
        alpha = int(255 * (self.timer / self.lifetime))
        s = self.font.render(self.text, True, (*self.color[:3], alpha))
        s.set_alpha(alpha)
        surface.blit(s, (self.x - s.get_width() // 2, self.y))


class HUD:
    def __init__(self):
        self.time = 0.0
        self.level_text = Text("", 20, COLOR_TEXT)
        self.hp_bar = AnimatedBar(
            pygame.Rect(20, 20, 200, 16), COLOR_HP_BAR, (30, 25, 25), (80, 200, 80),
            (100, 255, 100), (120, 40, 40)
        )
        self.mp_bar = AnimatedBar(
            pygame.Rect(20, 42, 200, 12), COLOR_MP_BAR, (20, 20, 35), (80, 120, 220),
            (100, 150, 255)
        )
        self.xp_bar = AnimatedBar(
            pygame.Rect(20, 60, 200, 8), COLOR_XP_BAR, (25, 25, 20), (180, 160, 80),
            (220, 200, 100)
        )
        self.ult_bar = AnimatedBar(
            pygame.Rect(20, 74, 200, 10), (255, 180, 60), (30, 25, 20), (220, 160, 60),
            (255, 200, 80)
        )
        self.hp_num = SmoothNumber((200, 240, 200), 10.0)
        self.mp_num = SmoothNumber((180, 200, 240), 10.0)
        self.damage_flash = 0.0
        self.last_hp = 0
        self.floating_texts = []

    def add_floating_text(self, x, y, text, color=(255, 255, 255), lifetime=1.2):
        self.floating_texts.append(FloatingText(x, y, text, color, lifetime))

    def update(self, dt, player):
        self.time += dt
        self.hp_bar.update(dt, player.hp / player.max_hp)
        self.mp_bar.update(dt, player.mp / player.max_mp)
        self.xp_bar.update(dt, player.xp / player.xp_to_next)
        self.hp_num.update(dt, player.hp)
        self.mp_num.update(dt, player.mp)
        if player.ult_active:
            self.ult_bar.update(dt, player.ult_timer / player.ult_duration)
        else:
            self.ult_bar.update(dt, player.ult_gauge / player.ult_max)
        self.level_text.set_text(f"Lv.{player.level}  Sorcerer  [{player.coins}]  Wood: {player.wood}")

        if player.hp < self.last_hp:
            self.damage_flash = 0.15
        self.last_hp = player.hp
        if self.damage_flash > 0:
            self.damage_flash -= dt

        self.floating_texts[:] = [ft for ft in self.floating_texts if ft.update(dt)]

    def _render_bg_panel(self, surface, rect, color, alpha=60):
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surf.fill((*color[:3], alpha))
        surface.blit(surf, (rect.x, rect.y))

    def _draw_scanlines(self, surface, rect, alpha=8):
        for y in range(rect.y, rect.y + rect.height, 3):
            pygame.draw.line(surface, (0, 0, 0, alpha), (rect.x, y), (rect.x + rect.width, y))

    def render(self, surface, player, enemies=None):
        t = self.time

        # ── Damage flash overlay ──
        if self.damage_flash > 0:
            flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            alpha = int(80 * (self.damage_flash / 0.15))
            flash.fill((180, 20, 20, alpha))
            surface.blit(flash, (0, 0))

        # ── Low health vignette ──
        hp_ratio = player.hp / player.max_hp
        if hp_ratio < 0.3:
            vignette = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            intensity = int(120 * (1.0 - hp_ratio / 0.3))
            pulse = 0.7 + 0.3 * math.sin(t * 5)
            vignette.fill((80, 0, 0, int(intensity * pulse)))
            surface.blit(vignette, (0, 0))

        # ── Top-left stats panel ──
        panel_rect = pygame.Rect(10, 5, 250, 95)
        self._render_bg_panel(surface, panel_rect, COLOR_UI_BG, 50)
        self._draw_scanlines(surface, panel_rect, 6)
        border_pulse = 0.7 + 0.3 * math.sin(t * 1.5)
        if hp_ratio < 0.3:
            bc = (int(80 + 175 * border_pulse), 50, 50)
        else:
            bc = (int(60 * border_pulse), int(50 * border_pulse), int(80 * border_pulse))
        pygame.draw.rect(surface, bc, panel_rect, 1, border_radius=4)

        self.hp_bar.render(surface)
        self.mp_bar.render(surface)
        self.xp_bar.render(surface)
        self.level_text.render(surface, (20, 5))

        hp_color = (200, 240, 200) if hp_ratio > 0.3 else (255, 100, 100)
        hp_text = Text(f"{self.hp_num.get_text()}/{player.max_hp}", 13, hp_color, (230, 20))
        mp_text = Text(f"{self.mp_num.get_text()}/{player.max_mp}", 13, (180, 200, 240), (230, 42))
        hp_text.render(surface)
        mp_text.render(surface)

        self.ult_bar.render(surface)
        ult_ready = player.ult_gauge >= player.ult_max and not player.ult_active
        if ult_ready:
            ult_pulse = 0.5 + 0.5 * math.sin(t * 6)
            ult_color = (int(255 * ult_pulse), int(220 * ult_pulse), 120)
        else:
            ult_color = (220, 160, 60) if not player.ult_active else (255, 220, 120)
        ult_label = Text("ULT", 10, ult_color, (230, 74))
        if player.ult_active or player.ult_gauge > 0:
            ult_label.render(surface)

        # ── Weapon card (top-right) ──
        if player.weapon:
            w = player.weapon
            tier_names = {1: "Common", 2: "Uncommon", 3: "Rare",
                         4: "Epic", 5: "Legendary", 6: "Mythic"}
            tier_name = tier_names.get(w["tier"], "")
            tier_colors = {1: (160, 160, 160), 2: (120, 200, 120), 3: (100, 100, 220),
                          4: (180, 100, 220), 5: (220, 180, 80), 6: (220, 100, 200)}
            tc = tier_colors.get(w["tier"], (200, 200, 200))

            card_w, card_h = 230, 50
            card_x = WINDOW_WIDTH - card_w - 10
            card_y = 8

            if w["tier"] >= 5:
                glow_pulse = 0.6 + 0.4 * math.sin(t * 3)
                glow_w = int(card_w + 12 * glow_pulse)
                glow_h = int(card_h + 12 * glow_pulse)
                outer = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
                ga = int(60 + 40 * math.sin(t * 2))
                pygame.draw.rect(outer, (*tc[:3], ga), (0, 0, glow_w, glow_h), 2, border_radius=8)
                surface.blit(outer, (card_x - 6 + (card_w + 12 - glow_w) // 2,
                                     card_y - 6 + (card_h + 12 - glow_h) // 2))

            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            self._render_bg_panel(surface, card_rect, tc, 25)
            pygame.draw.rect(surface, tc, card_rect, 2, border_radius=6)

            if w["tier"] >= 4:
                glow_alpha = int(40 + 30 * math.sin(t * 2))
                glow_surf = pygame.Surface((card_w + 8, card_h + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*tc[:3], glow_alpha),
                                (0, 0, card_w + 8, card_h + 8), 3, border_radius=8)
                surface.blit(glow_surf, (card_x - 4, card_y - 4))

            name_color = (255, 255, 255) if w["tier"] < 5 else (
                int(255 * (0.7 + 0.3 * math.sin(t * 3))),
                int(255 * (0.7 + 0.3 * math.sin(t * 3 + 1))),
                int(255 * (0.7 + 0.3 * math.sin(t * 3 + 2)))
            )
            name_text = Text(w["name"], 18, name_color, (card_x + 10, card_y + 5))
            name_text.render(surface)
            tier_text = Text(f"[{tier_name}]  DMG+{w['damage']} MAG+{w['magic']}",
                           11, tc, (card_x + 10, card_y + 28))
            tier_text.render(surface)

        # ── Spell bar (bottom) ──
        bar_y = WINDOW_HEIGHT - 62
        bar_rect = pygame.Rect(10, bar_y, 420, 52)
        self._render_bg_panel(surface, bar_rect, COLOR_UI_BG, 55)
        self._draw_scanlines(surface, bar_rect, 6)
        pygame.draw.rect(surface, (60, 50, 80, 100), bar_rect, 1, border_radius=6)

        for i, spell_name in enumerate(player.equipped_spells):
            sx = 18 + i * 100
            sy = bar_y + 8
            sd = SPELL_DATA.get(spell_name, {})
            mp_cost = sd.get("cost", 0)
            has_mp = player.mp >= mp_cost
            on_cooldown = player.cast_cooldown > 0
            is_ready = has_mp and not on_cooldown
            color = COLOR_VOID_LIGHT if is_ready else COLOR_TEXT_DIM
            slot_rect = pygame.Rect(sx, sy, 92, 36)

            if is_ready:
                pulse = 0.6 + 0.4 * math.sin(t * 3 + i * 1.5)
                gc = (*COLOR_VOID_LIGHT[:3], int(40 * pulse))
                glow_surf = pygame.Surface((92 + 6, 36 + 6), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, gc, (0, 0, 92 + 6, 36 + 6), border_radius=5)
                surface.blit(glow_surf, (sx - 3, sy - 3))

            bg = (45, 38, 60) if is_ready else (25, 22, 35)
            if on_cooldown:
                cd_progress = 1.0 - player.cast_cooldown / max(player.cast_cooldown, 0.01)
                sweep_w = int(92 * (1.0 - cd_progress))
                bg = (30, 25, 40)
            pygame.draw.rect(surface, bg, slot_rect, border_radius=4)

            if on_cooldown:
                cd_fill = pygame.Rect(sx, sy, int(92 * cd_progress), 36)
                if cd_fill.width > 0:
                    cd_pulse = 0.4 + 0.6 * (1.0 - cd_progress)
                    cd_color = (int(80 * cd_pulse), int(60 * cd_pulse), int(120 * cd_pulse))
                    pygame.draw.rect(surface, cd_color, cd_fill, border_radius=4)

            if not has_mp and not on_cooldown:
                mp_flash = 0.5 + 0.5 * math.sin(t * 4)
                dim_color = (int(80 * mp_flash), int(60 * mp_flash), int(100 * mp_flash))
                pygame.draw.rect(surface, dim_color, slot_rect, border_radius=4)

            pygame.draw.rect(surface, color, slot_rect, 1, border_radius=4)

            key_label = Text(f"[{i+1}]", 12, color, (sx + 5, sy + 3))
            name_label = Text(spell_name, 12, color, (sx + 28, sy + 10))
            key_label.render(surface)
            name_label.render(surface)

            if is_ready and i == 0:
                cost_text = Text(f"{mp_cost}MP", 10, (160, 140, 200), (sx + 52, sy + 24))
                cost_text.render(surface)

        # ── Status effects (left side, below panel) ──
        status_texts = player.status.get_ui_texts()
        if status_texts:
            for i, sname in enumerate(status_texts):
                pulse = 0.7 + 0.3 * math.sin(t * 2 + i)
                c = (200, 150, 200)
                fc = (int(c[0] * pulse), int(c[1] * pulse), int(c[2] * pulse))
                st = Text(sname, 13, fc, (20, 110 + i * 20))
                st.render(surface)
                bar_w = 80
                bar_h = 3
                decay = player.status.get_decay(sname) if hasattr(player.status, 'get_decay') else 1.0
                if decay < 1.0:
                    pygame.draw.rect(surface, (30, 25, 40), (20, 125 + i * 20, bar_w, bar_h), border_radius=1)
                    pygame.draw.rect(surface, fc, (20, 125 + i * 20, int(bar_w * decay), bar_h), border_radius=1)

        # ── Cast cooldown bar ──
        if player.cast_cooldown > 0:
            cd_w = 140
            cd_rect = pygame.Rect(WINDOW_WIDTH // 2 - cd_w // 2, WINDOW_HEIGHT - 76, cd_w, 8)
            self._render_bg_panel(surface, cd_rect, (30, 25, 40), 80)
            pygame.draw.rect(surface, (50, 45, 60), cd_rect, 1, border_radius=3)
            fill = int(cd_w * (1.0 - player.cast_cooldown / max(player.cast_cooldown, 0.01)))
            if fill > 0:
                fill_rect = pygame.Rect(cd_rect.x, cd_rect.y, fill, cd_rect.height)
                pulse = 0.5 + 0.5 * math.sin(t * 6)
                cd_color = (int(160 * pulse), int(120 * pulse), 255)
                pygame.draw.rect(surface, cd_color, fill_rect, border_radius=3)

        # ── Quick-use hotbar (left side, above spells) ──
        hotbar_y = WINDOW_HEIGHT - 128
        hotbar_x = 12
        for i, item in enumerate(player.inventory.consumables[:4]):
            hsx = hotbar_x + i * 52
            hsy = hotbar_y
            hrect = pygame.Rect(hsx, hsy, 46, 46)

            pulse = 0.6 + 0.4 * math.sin(t * 2 + i * 1.2)
            color = item.data.get("color", (200, 100, 200))
            gc = tuple(int(c * pulse) for c in color[:3])

            self._render_bg_panel(surface, hrect, (20, 16, 35), 70)
            pygame.draw.rect(surface, gc, hrect, 2, border_radius=5)
            pygame.draw.rect(surface, (gc[0], gc[1], gc[2], 60), hrect.inflate(4, 4), 1, border_radius=6)

            swatch = pygame.Rect(hsx + 8, hsy + 6, 30, 18)
            pygame.draw.rect(surface, color, swatch, border_radius=2)

            qty_text = Text(f"x{item.quantity}", 10, (200, 200, 220), (hsx + 8, hsy + 28))
            qty_text.render(surface)

        # ── Boss HP bar ──
        if enemies:
            for enemy in enemies:
                if enemy.alive and getattr(enemy, 'is_boss', False):
                    boss_bar_w = 300
                    boss_bar_h = 18
                    boss_bar_x = WINDOW_WIDTH // 2 - boss_bar_w // 2
                    boss_bar_y = 105
                    ratio = enemy.hp / enemy.max_hp

                    name_font = pygame.font.Font(FONT_PATH, 16)
                    name_surf = name_font.render(enemy.edef["name"], True, (255, 200, 100))
                    name_x = boss_bar_x + boss_bar_w // 2 - name_surf.get_width() // 2
                    name_y = boss_bar_y - 18
                    surface.blit(name_surf, (name_x, name_y))

                    tier_font = pygame.font.Font(FONT_PATH, 10)
                    tier_names = {5: "EMOTION BOSS", 6: "PRIME BOSS"}
                    tier_label = tier_names.get(enemy.edef["tier"], "BOSS")
                    tier_surf = tier_font.render(tier_label, True, (200, 150, 100))
                    tier_x = boss_bar_x + boss_bar_w // 2 - tier_surf.get_width() // 2
                    surface.blit(tier_surf, (tier_x, boss_bar_y + boss_bar_h + 5))

                    pygame.draw.rect(surface, (20, 10, 15), (boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h), border_radius=4)
                    pulse = 1.0
                    if ratio < 0.3:
                        pulse = 0.6 + 0.4 * math.sin(t * 6)

                    bar_color = (200, 60, 60) if ratio < 0.3 else (220, 140, 60)
                    if ratio > 0:
                        fill_w = int(boss_bar_w * ratio)
                        fill_rect = pygame.Rect(boss_bar_x, boss_bar_y, fill_w, boss_bar_h)
                        glow_color = (
                            int(bar_color[0] * pulse),
                            int(bar_color[1] * pulse),
                            int(bar_color[2] * pulse)
                        )
                        pygame.draw.rect(surface, glow_color, fill_rect, border_radius=4)

                        if fill_w > 4:
                            glow_r = pygame.Rect(boss_bar_x + fill_w - 4, boss_bar_y - 1, 6, boss_bar_h + 2)
                            g_surf = pygame.Surface((glow_r.width, glow_r.height), pygame.SRCALPHA)
                            ga = int(60 + 60 * math.sin(t * 4))
                            pygame.draw.rect(g_surf, (*glow_color, ga), (0, 0, glow_r.width, glow_r.height), border_radius=3)
                            surface.blit(g_surf, (glow_r.x, glow_r.y))

                    border_pulse = 0.5 + 0.5 * math.sin(t * 2)
                    border_color = (
                        int(255 * border_pulse),
                        int(150 * border_pulse),
                        int(50 * border_pulse)
                    )
                    pygame.draw.rect(surface, border_color, (boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h), 2, border_radius=4)

                    hp_font = pygame.font.Font(FONT_PATH, 11)
                    hp_surf = hp_font.render(f"{enemy.hp}/{enemy.max_hp}", True, (255, 220, 180))
                    hp_x = boss_bar_x + boss_bar_w // 2 - hp_surf.get_width() // 2
                    hp_y = boss_bar_y + boss_bar_h // 2 - hp_surf.get_height() // 2
                    surface.blit(hp_surf, (hp_x, hp_y))
                    break

        # ── Inventory hint ──
        hint_alpha = int(80 + 60 * math.sin(t * 3))
        hint_text = Text("[Space] Dash   [F] Pick up   [Tab] Inventory", 13, (*COLOR_GOLD[:3], hint_alpha),
                        (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 140))
        hint_text.render(surface)

        # ── Floating texts ──
        for ft in self.floating_texts:
            ft.render(surface)


class RadialMenu:
    def __init__(self):
        self.open = False
        self.weapons = []
        self.hover_idx = -1
        self.anim_t = 0.0
        self.animating = False
        self.open_direction = 1
        self.radius = 140
        self.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.font_name = pygame.font.Font(FONT_PATH, 14)
        self.font_tier = pygame.font.Font(FONT_PATH, 10)
        self.font_title = pygame.font.Font(FONT_PATH, 18)

    def toggle(self, inventory):
        self.open_direction = 1 if not self.open else -1
        self.animating = True
        self.open = not self.open
        if self.open:
            self.weapons = list(inventory.weapons)
            self.hover_idx = inventory.equipped_index

    def update(self, dt, inventory):
        if self.animating:
            self.anim_t += dt * 6 * self.open_direction
            if self.anim_t <= 0 or self.anim_t >= 1:
                self.anim_t = max(0, min(1, self.anim_t))
                self.animating = False
                if not self.open:
                    self.weapons = []

    def _angle_for(self, idx):
        n = max(1, len(self.weapons))
        return -math.pi / 2 + (idx / n) * math.pi * 2

    def _slot_pos(self, idx, radius):
        a = self._angle_for(idx)
        cx, cy = self.center
        return (cx + math.cos(a) * radius, cy + math.sin(a) * radius)

    def update_hover(self, mx, my):
        cx, cy = self.center
        dx = mx - cx
        dy = my - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 20:
            self.hover_idx = -1
            return
        n = max(1, len(self.weapons))
        angle = math.atan2(dy, dx)
        slot_angle = -math.pi / 2
        closest = 0
        closest_dist = float("inf")
        for i in range(n):
            a = self._angle_for(i)
            diff = abs((angle - a + math.pi) % (math.pi * 2) - math.pi)
            if diff < closest_dist:
                closest_dist = diff
                closest = i
        self.hover_idx = closest if closest < len(self.weapons) else -1

    def select_hovered(self, inventory, player):
        if 0 <= self.hover_idx < len(self.weapons):
            inventory.selected_weapon_idx = self.hover_idx
            inventory.equip_weapon(self.hover_idx, player)

    def render(self, surface):
        if not self.open and not self.animating:
            return
        t = self.anim_t
        if self.open_direction == -1:
            t = 1.0 - t

        dim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, int(80 * t)))
        surface.blit(dim, (0, 0))

        cx, cy = self.center
        n = len(self.weapons)
        if n == 0:
            return

        r = self.radius * t
        inner_r = 30 * t

        tier_colors = {1: (160, 160, 160), 2: (120, 200, 120), 3: (100, 100, 220),
                      4: (180, 100, 220), 5: (220, 180, 80), 6: (220, 100, 200)}

        # Ring background
        ring = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(ring, (30, 25, 45, int(180 * t)), self.center, int(r + 30), 0)
        pygame.draw.circle(ring, (60, 50, 80, int(100 * t)), self.center, int(r + 30), 2)
        surface.blit(ring, (0, 0))

        # Center circle
        pygame.draw.circle(surface, (20, 18, 35, int(200 * t)), self.center, int(inner_r + 10))
        pygame.draw.circle(surface, (80, 70, 100, int(80 * t)), self.center, int(inner_r + 10), 2)

        title = self.font_title.render("SELECT WEAPON", True, (180, 170, 200))
        title.set_alpha(int(200 * t))
        surface.blit(title, (cx - title.get_width() // 2, cy - title.get_height() // 2))

        # Connection lines
        for i in range(n):
            px, py = self._slot_pos(i, r)
            alpha = int(60 * t)
            if i == self.hover_idx:
                alpha = int(200 * t)
            pygame.draw.line(surface, (100, 90, 120, alpha), self.center, (px, py), 1)

        # Slots
        for i in range(n):
            pw = self.weapons[i]
            px, py = self._slot_pos(i, r)
            slot_r = int(24 * t)
            is_hover = i == self.hover_idx
            tc = tier_colors.get(pw.tier, (200, 200, 200))

            if is_hover:
                glow_r = int(32 * t)
                glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                gc = (*tc[:3], int(100 * t))
                pygame.draw.circle(glow, gc, (glow_r, glow_r), glow_r)
                surface.blit(glow, (px - glow_r, py - glow_r))

            pygame.draw.circle(surface, (25, 22, 40, int(200 * t)), (px, py), slot_r)
            bw = int(2 * t)
            bc = tc if is_hover else (80, 70, 100)
            pygame.draw.circle(surface, bc, (px, py), slot_r, max(1, bw))

            # Color swatch
            wc = pw.data.get("color", (200, 200, 200))
            swatch_r = int(8 * t)
            pygame.draw.circle(surface, wc, (px, py), swatch_r)

            # Name label
            label = self.font_name.render(pw.name, True, (220, 210, 230))
            label.set_alpha(int(220 * t))
            lx = px - label.get_width() // 2
            ly = py + slot_r + 4
            surface.blit(label, (lx, ly))

            # Tier
            tier_label = self.font_tier.render(str(pw.tier), True, tc)
            tier_label.set_alpha(int(200 * t))
            surface.blit(tier_label, (px + slot_r - tier_label.get_width() - 2, py - slot_r + 2))
