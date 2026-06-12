import pygame
from game.constants import *


class StatusEffect:
    def __init__(self, name, duration, tick_interval=1.0):
        self.name = name
        self.duration = duration
        self.max_duration = duration
        self.tick_interval = tick_interval
        self.tick_timer = 0.0
        self.active = True

    def apply(self, target, dt):
        if not self.active:
            return
        self.duration -= dt
        if self.duration <= 0:
            self.active = False
            self.on_expire(target)
            return
        self.tick_timer += dt
        while self.tick_timer >= self.tick_interval:
            self.tick_timer -= self.tick_interval
            self.on_tick(target)

    def on_tick(self, target):
        pass

    def on_expire(self, target):
        pass

    def overlay_color(self):
        return None

    def ui_text(self):
        return self.name


class PoisonEffect(StatusEffect):
    def __init__(self, damage_per_tick=4, duration=4.0):
        super().__init__("Poison", duration, 0.8)
        self.damage_per_tick = damage_per_tick

    def on_tick(self, target):
        target.take_damage(self.damage_per_tick)

    def overlay_color(self):
        t = self.duration / self.max_duration
        return (40, int(80 * t), 40)


class SlowEffect(StatusEffect):
    def __init__(self, factor=0.5, duration=3.0):
        super().__init__("Slow", duration, 0.5)
        self.factor = factor
        self.original_speed = None

    def on_tick(self, target):
        if hasattr(target, 'speed'):
            if self.original_speed is None:
                self.original_speed = target.speed
            target.speed = self.original_speed * self.factor

    def on_expire(self, target):
        if self.original_speed is not None and hasattr(target, 'speed'):
            target.speed = self.original_speed
            self.original_speed = None

    def overlay_color(self):
        return (40, 40, 80)


class LeechEffect(StatusEffect):
    def __init__(self, drain_per_tick=3, duration=3.0):
        super().__init__("Leech", duration, 0.6)
        self.drain_per_tick = drain_per_tick
        self.attached = True

    def on_tick(self, target):
        target.take_damage(self.drain_per_tick)

    def overlay_color(self):
        return (80, 20, 40)


class RegenEffect(StatusEffect):
    def __init__(self, heal_per_tick=5, duration=5.0):
        super().__init__("Regen", duration, 1.0)
        self.heal_per_tick = heal_per_tick

    def on_tick(self, target):
        if hasattr(target, 'heal'):
            target.heal(self.heal_per_tick)

    def overlay_color(self):
        return (40, 80, 40)


class StatBuffEffect(StatusEffect):
    def __init__(self, stat, amount, duration=5.0):
        super().__init__(f"Buff {stat}", duration, 0.5)
        self.stat = stat
        self.amount = amount
        self.applied = False

    def on_tick(self, target):
        if not self.applied and hasattr(target, self.stat):
            original = getattr(target, self.stat)
            setattr(target, self.stat, original + self.amount)
            self.applied = True

    def on_expire(self, target):
        if self.applied and hasattr(target, self.stat):
            current = getattr(target, self.stat)
            setattr(target, self.stat, current - self.amount)
            self.applied = False

    def overlay_color(self):
        return (60, 40, 80)


class CosmeticEffect(StatusEffect):
    def __init__(self, name, color, duration=8.0):
        super().__init__(f"Cosmetic:{name}", duration, 1.0)
        self.cosmetic_color = color

    def overlay_color(self):
        t = self.duration / self.max_duration
        return tuple(int(c * 0.3 * t) for c in self.cosmetic_color[:3])

    def ui_text(self):
        return f"✨ {self.name.split(':')[-1]}"


class StatusManager:
    def __init__(self):
        self.effects = []

    def add(self, effect):
        for e in self.effects:
            if e.name == effect.name:
                e.duration = max(e.duration, effect.duration)
                return
        self.effects.append(effect)

    def remove(self, name):
        self.effects = [e for e in self.effects if e.name != name]

    def clear(self):
        for e in self.effects:
            e.active = False
            e.on_expire(None)
        self.effects.clear()

    def update(self, target, dt):
        for e in self.effects[:]:
            e.apply(target, dt)
            if not e.active:
                self.effects.remove(e)

    def has(self, name):
        return any(e.name == name for e in self.effects)

    def get_overlay_color(self):
        if not self.effects:
            return None
        for e in self.effects:
            c = e.overlay_color()
            if c:
                return c
        return None

    def get_ui_texts(self):
        return [e.ui_text() for e in self.effects if e.active]
