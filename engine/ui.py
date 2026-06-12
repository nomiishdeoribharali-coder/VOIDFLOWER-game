import pygame
from game.constants import FONT_PATH


class Text:
    def __init__(self, text, size=16, color=(255, 255, 255), pos=(0, 0)):
        self.text = text
        self.size = size
        self.color = color
        self.pos = pos
        self._font = None
        self._rendered = None
        self._dirty = True
        self._load_font()

    def _load_font(self):
        try:
            self._font = pygame.font.Font(FONT_PATH, self.size)
        except:
            try:
                self._font = pygame.font.Font(None, self.size)
            except:
                self._font = pygame.font.SysFont("monospace", self.size)
        self._dirty = True

    def set_text(self, text):
        if self.text != text:
            self.text = text
            self._dirty = True

    def set_color(self, color):
        self.color = color
        self._dirty = True

    @property
    def width(self):
        if self._dirty:
            self._render()
        return self._rendered.get_width()

    @property
    def height(self):
        if self._dirty:
            self._render()
        return self._rendered.get_height()

    def _render(self):
        self._rendered = self._font.render(self.text, True, self.color)
        self._dirty = False

    def render(self, surface, pos=None):
        if self._dirty:
            self._render()
        p = pos if pos else self.pos
        surface.blit(self._rendered, p)


class Button:
    def __init__(self, rect, text, callback=None, color=(80, 80, 120),
                 hover_color=(120, 120, 180), text_color=(255, 255, 255),
                 audio_manager=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self._text_obj = Text(text, size=20, color=text_color)
        self._audio = audio_manager

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self._audio:
                    self._audio.play_sound("ui_click")
                if self.callback:
                    self.callback()

    def render(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        pygame.draw.rect(surface, (200, 200, 255), self.rect, 2, border_radius=4)
        tx = self.rect.x + (self.rect.width - self._text_obj.width) // 2
        ty = self.rect.y + (self.rect.height - self._text_obj.height) // 2
        self._text_obj.render(surface, (tx, ty))


class ProgressBar:
    def __init__(self, rect, value=1.0, color=(0, 200, 0), bg_color=(60, 60, 60),
                 border_color=(200, 200, 200)):
        self.rect = pygame.Rect(rect)
        self.value = value
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color

    def render(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        fill_w = int(self.rect.width * max(0, min(1, self.value)))
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.height)
            pygame.draw.rect(surface, self.color, fill_rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
