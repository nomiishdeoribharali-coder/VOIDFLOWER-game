import pygame
import math
from game.constants import *
from game.constants import FONT_PATH

COSMETIC_ITEMS = [
    # (key, name, type, color, price, description)
    # ── Permanent color skins ──
    ("skin_blood_red", "Blood Red", "skin", (200, 40, 50), 30, "A fierce crimson hue."),
    ("skin_royal_blue", "Royal Blue", "skin", (50, 80, 220), 30, "A deep regal blue."),
    ("skin_emerald", "Emerald Green", "skin", (40, 200, 80), 30, "A vibrant emerald tone."),
    ("skin_golden", "Golden", "skin", (220, 180, 40), 50, "A shimmering golden gleam."),
    ("skin_shadow_purple", "Shadow Purple", "skin", (100, 50, 160), 25, "A dark mystical purple."),
    ("skin_ice_cyan", "Ice Cyan", "skin", (60, 200, 220), 30, "A frigid cyan frost."),
    ("skin_lava_orange", "Lava Orange", "skin", (240, 120, 30), 35, "A molten orange blaze."),
    ("skin_neon_pink", "Neon Pink", "skin", (240, 40, 180), 40, "A blazing neon pink."),
    ("skin_snow_white", "Snow White", "skin", (220, 220, 235), 25, "A pale winter white."),
    ("skin_abyssal", "Abyssal Blue", "skin", (20, 40, 100), 35, "An endless abyss blue."),
    ("skin_toxic_green", "Toxic Green", "skin", (60, 220, 40), 30, "A poisonous green glow."),
    ("skin_twilight", "Twilight", "skin", (140, 60, 140), 40, "A dusky twilight mauve."),
    ("skin_solar_flare", "Solar Flare", "skin", (255, 160, 20), 50, "A blazing solar flare."),
    ("skin_void_black", "Void Black", "skin", (30, 20, 45), 25, "An empty void shade."),
    ("skin_crimson", "Crimson", "skin", (160, 20, 40), 35, "A deep rich crimson."),
    # ── Temporary auras ──
    ("aura_neon", "Neon Aura", "aura", (255, 40, 180), 60, "A blazing neon aura (8s)."),
    ("aura_ghostly", "Ghostly Aura", "aura", (160, 140, 200), 50, "A ghostly glow (8s)."),
    ("aura_inferno", "Inferno Aura", "aura", (255, 60, 20), 70, "A raging inferno aura (8s)."),
    ("aura_arcane", "Arcane Aura", "aura", (140, 80, 220), 60, "An arcane shimmer (8s)."),
    ("aura_rainbow", "Rainbow Aura", "aura", (255, 200, 200), 80, "A shifting rainbow (8s)."),
]


class CosmeticShop:
    def __init__(self):
        self.open = False
        self.anim_t = 0.0
        self.animating = False
        self.open_direction = 1
        self.time = 0.0
        self.selected_idx = 0
        self.scroll_offset = 0
        self.visible_count = 8
        self.items = COSMETIC_ITEMS
        self.purchased_skins = set()
        self.equipped_skin = None
        self.font_large = pygame.font.Font(FONT_PATH, 28)
        self.font_med = pygame.font.Font(FONT_PATH, 18)
        self.font_small = pygame.font.Font(FONT_PATH, 14)

    def open_shop(self):
        self.selected_idx = 0
        self.scroll_offset = 0
        self.open_direction = 1
        self.animating = True
        self.open = True
        self.anim_t = 0.0

    def close(self):
        self.open_direction = -1
        self.animating = True

    def is_open(self):
        return self.open or self.animating

    def update(self, dt):
        self.time += dt
        if self.animating:
            self.anim_t += dt * 4 * self.open_direction
            if self.anim_t <= 0 or self.anim_t >= 1:
                self.anim_t = max(0, min(1, self.anim_t))
                self.animating = False
                if self.open_direction < 0:
                    self.open = False

    def scroll(self, direction):
        max_idx = len(self.items) - 1
        self.selected_idx = max(0, min(max_idx, self.selected_idx + direction))
        self._clamp_scroll()

    def _clamp_scroll(self):
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + self.visible_count:
            self.scroll_offset = self.selected_idx - self.visible_count + 1

    def handle_event(self, event, player):
        try:
            if not self.is_open():
                return False
            if event.type == pygame.KEYDOWN:
                k = getattr(event, 'key', None)
                if k == pygame.K_ESCAPE:
                    self.close()
                    return True
                elif k == pygame.K_UP:
                    self.scroll(-1)
                    return True
                elif k == pygame.K_DOWN:
                    self.scroll(1)
                    return True
                elif k == pygame.K_RETURN or k == pygame.K_SPACE:
                    self._buy_selected(player)
                    return True
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll(-getattr(event, 'y', 0))
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN and getattr(event, 'button', 0) == 1:
                mx, my = getattr(event, 'pos', (0, 0))
                panel_w = 560
                panel_h = 440
                panel_x = (WINDOW_WIDTH - panel_w) // 2
                panel_y = (WINDOW_HEIGHT - panel_h) // 2
                list_x = panel_x + 20
                list_y = panel_y + 55
                slot_h = 50
                slot_gap = 4
                for i in range(self.visible_count):
                    idx = i + self.scroll_offset
                    if idx >= len(self.items):
                        break
                    sy = list_y + i * (slot_h + slot_gap)
                    slot_rect = pygame.Rect(list_x, sy, panel_w - 60, slot_h)
                    if slot_rect.collidepoint(mx, my):
                        self.selected_idx = idx
                        self._clamp_scroll()
                        return True
                close_rect = pygame.Rect(panel_x + panel_w - 40, panel_y + 10, 30, 30)
                if close_rect.collidepoint(mx, my):
                    self.close()
                    return True
        except Exception:
            pass
        return False

    def _buy_selected(self, player):
        if self.selected_idx >= len(self.items):
            return
        key, name, item_type, color, price, desc = self.items[self.selected_idx]
        if item_type == "skin":
            if key in self.purchased_skins:
                self.equipped_skin = key
                player.color = color
            elif player.coins >= price:
                player.coins -= price
                self.purchased_skins.add(key)
                self.equipped_skin = key
                player.color = color
        elif item_type == "aura":
            if player.coins >= price:
                player.coins -= price
                from game.status import CosmeticEffect
                player.status.add(CosmeticEffect(name, color, 8.0))

    def render(self, surface, player):
        if not self.open and self.anim_t == 0:
            return
        fade = self.anim_t
        panel_w = 560
        panel_h = 440
        panel_x = (WINDOW_WIDTH - panel_w) // 2
        panel_y = (WINDOW_HEIGHT - panel_h) // 2

        # Dim overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(100 * fade)))
        surface.blit(overlay, (0, 0))

        # Panel bg
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((12, 8, 28, int(230 * fade)))
        surface.blit(panel_surf, (panel_x, panel_y))

        # Border
        border_pulse = 0.6 + 0.4 * math.sin(self.time * 1.5)
        bc = (int(255 * border_pulse), int(215 * border_pulse), 0)
        pygame.draw.rect(surface, bc, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=6)

        # Title
        title = self.font_large.render("✦  C O S M E T I C   S H O P  ✦", True, (255, 215, 0))
        surface.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 10))

        # Close X
        cx = panel_x + panel_w - 28
        cy = panel_y + 14
        close_color = (160, 140, 200)
        pygame.draw.line(surface, close_color, (cx - 6, cy - 6), (cx + 6, cy + 6), 2)
        pygame.draw.line(surface, close_color, (cx + 6, cy - 6), (cx - 6, cy + 6), 2)

        # Coins
        coin_text = self.font_small.render(f"Coins: {player.coins}", True, (255, 215, 0))
        surface.blit(coin_text, (panel_x + panel_w - coin_text.get_width() - 40, panel_y + 14))

        # Equipped skin indicator
        eq_text = None
        if self.equipped_skin:
            for k, n, t, c, p, d in self.items:
                if k == self.equipped_skin:
                    eq_text = self.font_small.render(f"Skin: {n}", True, (180, 220, 180))
                    break
        if eq_text:
            surface.blit(eq_text, (panel_x + 20, panel_y + panel_h - 28))

        # Item list
        if not self.items:
            empty = self.font_med.render("No items available.", True, (120, 110, 160))
            surface.blit(empty, (panel_x + panel_w // 2 - empty.get_width() // 2, panel_y + panel_h // 2))
            return

        list_x = panel_x + 20
        list_y = panel_y + 55
        slot_h = 50
        slot_gap = 4
        item_area_h = self.visible_count * (slot_h + slot_gap)

        for i in range(self.visible_count):
            idx = i + self.scroll_offset
            if idx >= len(self.items):
                break
            key, name, item_type, color, price, desc = self.items[idx]
            sy = list_y + i * (slot_h + slot_gap)
            slot_rect = pygame.Rect(list_x, sy, panel_w - 90, slot_h)
            is_selected = idx == self.selected_idx
            is_purchased = item_type == "skin" and key in self.purchased_skins
            is_equipped = key == self.equipped_skin
            can_afford = player.coins >= price

            bg = (30, 24, 50) if is_selected else (18, 14, 34)
            if is_equipped:
                bg = (20, 45, 30)
            pygame.draw.rect(surface, bg, slot_rect, border_radius=4)
            if is_selected:
                sel_pulse = 0.5 + 0.5 * math.sin(self.time * 4)
                sc = (int(255 * sel_pulse), int(215 * sel_pulse), 0)
                pygame.draw.rect(surface, sc, slot_rect, 2, border_radius=4)
            else:
                pygame.draw.rect(surface, (60, 50, 80), slot_rect, 1, border_radius=4)

            # Color swatch
            swatch_rect = pygame.Rect(list_x + 6, sy + 8, 34, 34)
            pygame.draw.rect(surface, color, swatch_rect, border_radius=3)
            if is_equipped:
                pygame.draw.rect(surface, (100, 255, 100), swatch_rect, 2, border_radius=3)

            # Type icon
            icon_label = "S" if item_type == "skin" else "A"
            il = self.font_small.render(icon_label, True, (0, 0, 0))
            surface.blit(il, (list_x + 6 + 17 - il.get_width() // 2, sy + 14))

            # Name
            nl = self.font_med.render(name, True, (220, 210, 240))
            surface.blit(nl, (list_x + 50, sy + 4))

            # Desc
            dl = self.font_small.render(desc, True, (120, 110, 160))
            surface.blit(dl, (list_x + 50, sy + 26))

            # Price / status
            if is_equipped:
                status_text = self.font_small.render("EQUIPPED", True, (100, 255, 100))
                surface.blit(status_text, (panel_x + panel_w - 98, sy + 16))
            elif is_purchased:
                status_text = self.font_small.render("OWNED", True, (140, 200, 140))
                surface.blit(status_text, (panel_x + panel_w - 98, sy + 16))
            else:
                price_color = (100, 255, 100) if can_afford else (255, 80, 80)
                pl = self.font_small.render(f"{price}c", True, price_color)
                surface.blit(pl, (panel_x + panel_w - 88, sy + 16))

        # Scrollbar
        if len(self.items) > self.visible_count:
            sb_x = panel_x + panel_w - 18
            sb_y = list_y
            sb_h = item_area_h
            track_h = sb_h
            thumb_h = max(20, sb_h * self.visible_count // len(self.items))
            thumb_y = sb_y + (sb_h - thumb_h) * self.scroll_offset // (len(self.items) - self.visible_count)
            pygame.draw.rect(surface, (30, 25, 50), (sb_x, sb_y, 6, track_h), border_radius=3)
            pygame.draw.rect(surface, (100, 90, 140), (sb_x, thumb_y, 6, thumb_h), border_radius=3)

        # Controls
        controls_y = panel_y + panel_h - 28
        ctrl = self.font_small.render("[↑↓/Wheel] Browse  [Enter] Buy/Equip  [ESC] Close", True, (120, 110, 160))
        surface.blit(ctrl, (panel_x + 20, controls_y))
