import pygame
import os

AUDIO_EXTENSIONS = [".wav", ".mp3", ".ogg", ".flac"]


def _resolve_path(base_path):
    base = os.path.splitext(base_path)[0]
    for ext in AUDIO_EXTENSIONS:
        p = base + ext
        if os.path.exists(p):
            return p
    return base_path


class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except pygame.error:
            pass
        self.sounds = {}
        self.music_volume = 0.4
        self.sfx_volume = 0.35
        self.music_enabled = True
        self.sfx_enabled = True

        # Soundtrack state
        self.current_theme = None
        self.fading_out = False
        self.fading_in = False
        self.fade_timer = 0.0
        self.fade_duration = 1.5
        self.pending_theme = None
        self.pending_path = None
        self.fade_out_vol = 0.0

    def load_sound(self, name, path):
        resolved = _resolve_path(path)
        if os.path.exists(resolved):
            try:
                self.sounds[name] = pygame.mixer.Sound(resolved)
            except pygame.error:
                pass

    def play_sound(self, name):
        if self.sfx_enabled and name in self.sounds:
            self.sounds[name].set_volume(self.sfx_volume)
            self.sounds[name].play()

    def crossfade_to(self, theme_name, path, duration=1.5):
        resolved = _resolve_path(path)
        if not os.path.exists(resolved):
            self.current_theme = theme_name
            return
        if theme_name == self.current_theme and not self.fading_out and not self.fading_in:
            return

        if self.pending_theme == theme_name:
            return

        if self.fading_in or self.fading_out:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except:
                pass

        self.pending_theme = theme_name
        self.pending_path = resolved
        self.fade_duration = duration
        self.fade_timer = 0.0

        if pygame.mixer.music.get_busy() and self.current_theme is not None:
            self.fading_out = True
            self.fading_in = False
            self.fade_out_vol = self.music_volume
        else:
            self._start_new_theme()

    def play_theme(self, theme_name, path):
        resolved = _resolve_path(path)
        if not os.path.exists(resolved):
            return
        self.pending_theme = None
        self.pending_path = None
        self.fading_out = False
        self.fading_in = False
        self.current_theme = theme_name
        try:
            pygame.mixer.music.load(resolved)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def _start_new_theme(self):
        if not self.pending_path:
            return
        try:
            pygame.mixer.music.load(self.pending_path)
            if self.music_enabled:
                pygame.mixer.music.set_volume(0.0)
                pygame.mixer.music.play(-1)
                self.fading_in = True
                self.fading_out = False
                self.fade_timer = 0.0
            self.current_theme = self.pending_theme
            self.pending_theme = None
            self.pending_path = None
        except pygame.error:
            self.fading_in = False
            self.fading_out = False

    def update(self, dt):
        if not self.music_enabled:
            return

        if self.fading_out:
            self.fade_timer += dt
            t = min(1.0, self.fade_timer / self.fade_duration)
            vol = self.fade_out_vol * (1.0 - t)
            try:
                pygame.mixer.music.set_volume(max(0.0, vol))
            except:
                pass
            if t >= 1.0:
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
                self.fading_out = False
                self.fade_timer = 0.0
                self._start_new_theme()

        if self.fading_in:
            self.fade_timer += dt
            t = min(1.0, self.fade_timer / self.fade_duration)
            vol = self.music_volume * min(1.0, t * 2.0)
            try:
                pygame.mixer.music.set_volume(vol)
            except:
                pass
            if t >= 1.0:
                try:
                    pygame.mixer.music.set_volume(self.music_volume)
                except:
                    pass
                self.fading_in = False

        elif not self.fading_out and self.fading_in is False:
            if self.pending_theme and self.pending_path:
                self._start_new_theme()
            elif not pygame.mixer.music.get_busy() and self.current_theme:
                try:
                    pygame.mixer.music.play(-1)
                except:
                    pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except:
            pass
        self.current_theme = None
        self.pending_theme = None
        self.pending_path = None
        self.fading_out = False
        self.fading_in = False

    def set_music_volume(self, vol):
        self.music_volume = max(0.0, min(1.0, vol))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except:
            pass

    def set_sfx_volume(self, vol):
        self.sfx_volume = max(0.0, min(1.0, vol))

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
