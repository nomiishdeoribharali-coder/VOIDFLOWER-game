import pygame
from game.constants import *
from game.constants import FONT_PATH


def get_stat_bonus_for_level(level):
    return {
        "hp": HP_PER_LEVEL,
        "mp": MP_PER_LEVEL,
        "strength": STR_PER_LEVEL,
        "defense": DEF_PER_LEVEL,
    }


def render_level_up_notification(surface, player, timer):
    if timer <= 0:
        return
    alpha = min(255, int(255 * timer / 2.0))
    font = pygame.font.Font(FONT_PATH, 48)
    text = font.render(f"Level {player.level}!", True, COLOR_GOLD)
    text.set_alpha(alpha)
    tx = (WINDOW_WIDTH - text.get_width()) // 2
    ty = WINDOW_HEIGHT // 3
    surface.blit(text, (tx, ty))

    font_small = pygame.font.Font(FONT_PATH, 24)
    details = f"HP +{HP_PER_LEVEL}  MP +{MP_PER_LEVEL}  STR +{STR_PER_LEVEL}  DEF +{DEF_PER_LEVEL}"
    detail_text = font_small.render(details, True, COLOR_TEXT)
    detail_text.set_alpha(alpha)
    dx = (WINDOW_WIDTH - detail_text.get_width()) // 2
    dy = ty + 50
    surface.blit(detail_text, (dx, dy))

    if player.level in (3, 5, 7):
        spell_names = {3: SPELL_DARK_PULSE, 5: SPELL_VOID_SHIELD, 7: SPELL_DOMAIN_EXPANSION}
        spell_text = font_small.render(f"New spell: {spell_names[player.level]}", True, COLOR_VOID_LIGHT)
        spell_text.set_alpha(alpha)
        sx = (WINDOW_WIDTH - spell_text.get_width()) // 2
        sy = dy + 30
        surface.blit(spell_text, (sx, sy))
