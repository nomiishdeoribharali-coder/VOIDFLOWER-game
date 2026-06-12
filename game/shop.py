import pygame
import math
from game.constants import *
from game.constants import FONT_PATH


class DealerShop:
    def __init__(self):
        self.open = False
        self.anim_t = 0.0
        self.animating = False
        self.open_direction = 1
        self.time = 0.0
        self.selected_idx = 0
        self.dealer = None
        self.font_large = pygame.font.Font(FONT_PATH, 28)
        self.font_med = pygame.font.Font(FONT_PATH, 18)
        self.font_small = pygame.font.Font(FONT_PATH, 14)

    def open_for(self, dealer):
        self.dealer = dealer
        self.selected_idx = 0
        self.open_direction = 1
        self.animating = True
        self.open = True
        self.anim_t = 0.0

    def close(self):
        self.open_direction = -1
        self.animating = True
        self.open = False

    def update(self, dt):
        self.time += dt
        if self.animating:
            self.anim_t += dt * 4 * self.open_direction
            if self.anim_t <= 0 or self.anim_t >= 1:
                self.anim_t = max(0, min(1, self.anim_t))
                self.animating = False

    def render(self, surface, player):
        if not self.open and self.anim_t == 0:
            return

        fade = self.anim_t
        panel_w = 560
        panel_h = 420
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
        title = self.font_large.render("◇  D E A L E R  ◇", True, (255, 215, 0))
        surface.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 10))

        coin_text = self.font_small.render(f"Coins: {player.coins}", True, (255, 215, 0))
        surface.blit(coin_text, (panel_x + panel_w - coin_text.get_width() - 12, panel_y + 14))

        # Items list
        if not self.dealer or not self.dealer.inventory:
            empty = self.font_med.render("No items for sale.", True, (120, 110, 160))
            surface.blit(empty, (panel_x + panel_w // 2 - empty.get_width() // 2, panel_y + panel_h // 2))
            return

        inv = self.dealer.inventory
        list_x = panel_x + 20
        list_y = panel_y + 55
        slot_h = 50
        slot_gap = 4
        max_visible = min(len(inv), 6)

        # Scroll offset if needed
        scroll_offset = max(0, self.selected_idx - max_visible + 1) if self.selected_idx >= max_visible else 0

        for i in range(max_visible):
            idx = i + scroll_offset
            if idx >= len(inv):
                break
            itype, data, price = inv[idx]
            sy = list_y + i * (slot_h + slot_gap)
            slot_rect = pygame.Rect(list_x, sy, panel_w - 130, slot_h)
            is_selected = idx == self.selected_idx
            can_afford = player.coins >= price

            bg = (30, 24, 50) if is_selected else (18, 14, 34)
            pygame.draw.rect(surface, bg, slot_rect, border_radius=4)
            if is_selected:
                sel_pulse = 0.5 + 0.5 * math.sin(self.time * 4)
                sc = (int(255 * sel_pulse), int(215 * sel_pulse), 0)
                pygame.draw.rect(surface, sc, slot_rect, 2, border_radius=4)
            else:
                pygame.draw.rect(surface, (60, 50, 80), slot_rect, 1, border_radius=4)

            # Icon
            icon_color = data.get("color", (200, 200, 200)) if isinstance(data, dict) else (200, 200, 200)
            icon_rect = pygame.Rect(list_x + 6, sy + 8, 34, 34)
            pygame.draw.rect(surface, icon_color, icon_rect, border_radius=3)
            icon_label = "W" if itype == "weapon" else "I"
            il = self.font_small.render(icon_label, True, (0, 0, 0))
            surface.blit(il, (list_x + 6 + 17 - il.get_width() // 2, sy + 14))

            # Name
            name = data.get("name", "?") if isinstance(data, dict) else "?"
            nl = self.font_med.render(name, True, (220, 210, 240))
            surface.blit(nl, (list_x + 50, sy + 5))

            # Desc / stats
            if itype == "weapon":
                desc = f"DMG+{data.get('damage',0)} MAG+{data.get('magic',0)} DEF+{data.get('defense',0)}"
            else:
                desc = data.get("desc", "")
            dl = self.font_small.render(desc, True, (120, 110, 160))
            surface.blit(dl, (list_x + 50, sy + 26))

            # Price
            price_color = (100, 255, 100) if can_afford else (255, 80, 80)
            pl = self.font_small.render(f"{price}c", True, price_color)
            surface.blit(pl, (panel_x + panel_w - 80, sy + 16))

        # Controls
        controls_y = panel_y + panel_h - 30
        ctrl = self.font_small.render("[↑↓] Navigate  [Enter] Buy  [G/ESC] Close", True, (120, 110, 160))
        surface.blit(ctrl, (panel_x + 20, controls_y))
