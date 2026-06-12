import pygame
from game.constants import FONT_PATH


def render_speech_bubble(surface, text, x, y, alpha=255, font_size=12, text_color=(255, 255, 200),
                         bg_color=(30, 25, 50), border_color=(80, 70, 120)):
    try:
        font = pygame.font.Font(FONT_PATH, font_size)
        txt = font.render(text, True, text_color)
        txt.set_alpha(alpha)
        bubble_w = txt.get_width() + 20
        bubble_h = txt.get_height() + 10
        bubble_x = x - bubble_w // 2
        bubble_y = y - 50 - bubble_h
        bubble = pygame.Surface((bubble_w, bubble_h), pygame.SRCALPHA)
        bubble.fill((*bg_color, min(200, alpha)))
        pygame.draw.rect(bubble, (*border_color, min(200, alpha)),
                        (0, 0, bubble_w, bubble_h), 1, border_radius=4)
        surface.blit(bubble, (bubble_x, bubble_y))
        txt_x = bubble_x + 10
        txt_y = bubble_y + 5
        txt.set_alpha(alpha)
        surface.blit(txt, (txt_x, txt_y))
    except Exception:
        pass


def render_npc_name_tag(surface, name, x, y, color=(255, 255, 255), font_size=10):
    try:
        font = pygame.font.Font(FONT_PATH, font_size)
        tag = font.render(name, True, color)
        tag_x = x - tag.get_width() // 2
        surface.blit(tag, (tag_x, y - 30))
    except Exception:
        pass


def render_cooldown(surface, cooldown, x, y, font_size=8):
    if cooldown <= 0:
        return
    try:
        font = pygame.font.Font(FONT_PATH, font_size)
        cd_alpha = int(100 + 100 * (cooldown * 5) % 1 * 100)
        cd_txt = font.render(f"{cooldown:.1f}s", True, (180, 180, 180))
        cd_txt.set_alpha(min(180, cd_alpha))
        surface.blit(cd_txt, (x - cd_txt.get_width() // 2, y + 2))
    except Exception:
        pass


def render_hint_key(surface, text, x, y, color=(200, 200, 255), font_size=14):
    try:
        font = pygame.font.Font(FONT_PATH, font_size)
        hint = font.render(text, True, color)
        hint.set_alpha(int(80 + 60 * (pygame.time.get_ticks() * 0.003 % 1 * 100)))
        hx = x - hint.get_width() // 2
        surface.blit(hint, (hx, y))
    except Exception:
        pass


def render_notification(surface, text, x, y, color=(255, 255, 255), font_size=18):
    try:
        font = pygame.font.Font(FONT_PATH, font_size)
        txt = font.render(text, True, color)
        tx = x - txt.get_width() // 2
        surface.blit(txt, (tx, y))
    except Exception:
        pass
