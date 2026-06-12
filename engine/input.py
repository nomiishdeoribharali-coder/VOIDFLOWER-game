import pygame


class InputHandler:
    def __init__(self):
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]
        self.mouse_just_pressed = [False, False, False]

    def update(self):
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_just_pressed = [False, False, False]
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_buttons = list(pygame.mouse.get_pressed())

    def handle_event(self, event):
        try:
            if event.type == pygame.KEYDOWN:
                k = getattr(event, 'key', None)
                if k is not None:
                    if k not in self.keys_pressed:
                        self.keys_just_pressed.add(k)
                    self.keys_pressed.add(k)
            elif event.type == pygame.KEYUP:
                k = getattr(event, 'key', None)
                if k is not None:
                    if k in self.keys_pressed:
                        self.keys_just_released.add(k)
                    self.keys_pressed.discard(k)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                b = getattr(event, 'button', 0)
                if 1 <= b <= 3:
                    self.mouse_just_pressed[b - 1] = True
                    self.mouse_buttons[b - 1] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                b = getattr(event, 'button', 0)
                if 1 <= b <= 3:
                    self.mouse_buttons[b - 1] = False
        except Exception:
            pass

    def is_key_down(self, key):
        return key in self.keys_pressed

    def is_key_just_pressed(self, key):
        return key in self.keys_just_pressed

    def is_key_just_released(self, key):
        return key in self.keys_just_released

    def is_mouse_down(self, button=0):
        return self.mouse_buttons[button]

    def is_mouse_just_pressed(self, button=0):
        return self.mouse_just_pressed[button]
