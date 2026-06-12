import pygame
import math
import random
from game.constants import *
from game.enemy_data import (
    get_enemy_def, ENEMY_BY_KEY,
    AI_WANDER, AI_CHASE, AI_AMBUSH, AI_TELEPORT, AI_KITE,
    AI_ORBIT, AI_COPY, AI_STATIONARY, AI_FLEE, AI_HAZARD,
    AI_SUMMONER, AI_BURST, AI_PHASE_WANDER, AI_BOSS,
    ATK_TOUCH, ATK_MELEE, ATK_PROJECTILE, ATK_SPORES, ATK_LEECH,
    ATK_POISON, ATK_SLOW, ATK_BURST, ATK_SUMMON, ATK_AOE,
    ATK_NONE, ATK_BEAM, ATK_PULSE,
    ATK_BOSS_TEARS, ATK_BOSS_LAUGH, ATK_BOSS_THORNS, ATK_BOSS_TENDRILS,
    ATK_BOSS_RAGE, ATK_BOSS_COPY, ATK_BOSS_OOZE, ATK_BOSS_SOB,
    ATK_BOSS_HEAL, ATK_BOSS_VOID,
    TRAIT_SPLIT, TRAIT_INVISIBLE, TRAIT_PHASE, TRAIT_BUFF_AURA,
    TRAIT_REGENERATES, TRAIT_EXPLOSIVE, TRAIT_RARE, TRAIT_HEAL_AURA, TRAIT_ILLUSION,
    TRAIT_BOSS, TRAIT_BOSS_MINION,
)
from game.status import StatusManager, SlowEffect, LeechEffect, PoisonEffect


class Entity:
    def __init__(self, x, y, w, h, hp, color):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.vx = 0
        self.vy = 0
        self.alive = True
        self.iframes = 0
        self.rect = pygame.Rect(x, y, w, h)

    def take_damage(self, amount, attacker=None):
        if self.iframes > 0:
            return False
        self.hp -= amount
        self.iframes = 0.3
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return True

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.x = self.x
        self.rect.y = self.y
        if self.iframes > 0:
            self.iframes -= dt

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        visible = (-self.width < sx < camera.width + self.width and
                   -self.height < sy < camera.height + self.height)
        if not visible:
            return
        if self.iframes > 0 and int(self.iframes * 20) % 2 == 0:
            return
        pygame.draw.rect(surface, self.color, (sx, sy, self.width, self.height))

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def direction_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            return (0, 0)
        return (dx / dist, dy / dist)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_SIZE, PLAYER_SIZE, PLAYER_MAX_HP, COLOR_PLAYER)
        self.max_hp = PLAYER_MAX_HP
        self.max_mp = PLAYER_MAX_MP
        self.mp = PLAYER_MAX_MP
        self.strength = 10
        self.defense = 5
        self.speed = PLAYER_SPEED
        self.level = 1
        self.xp = 0
        self.xp_to_next = self._xp_for_level(1)
        self.spells = []
        self.equipped_spells = [SPELL_VOID_BOLT, SPELL_CURSED_SLASH]
        self.cast_cooldown = 0
        self.facing = (0, 1)
        self.invulnerable = False
        self.status = StatusManager()
        self.speed_penalty = 0
        self.coins = 0
        self.wood = 0
        self.temp_hp = 0
        self._buff_timers = {}
        from game.weapons_inf import get_weapon
        self._weapon = get_weapon("katana")
        from game.inventory import Inventory
        self.inventory = Inventory()
        self.inventory.add_weapon(self._weapon)
        self.ult_gauge = 0
        self.ult_max = 30
        self.ult_active = False
        self.ult_timer = 0.0
        self.ult_duration = 8.0
        self.total_kills = 0
        self._last_melee_hit_count = 1
        self.blocking = False
        self.block_timer = 0.0
        self.block_cooldown = 0.0
        self.block_max_duration = 1.2
        self.block_cooldown_duration = 1.0
        self.parry_window = 0.0
        self.parry_window_duration = 0.15
        self.parry_damage_mult = 3.5
        self.parry_triggered = False
        self.parry_pos = (0, 0)
        self.dashing = False
        self.dash_timer = 0.0
        self.dash_duration = 0.15
        self.dash_cooldown = 0.0
        self.dash_cooldown_duration = 0.8
        self.dash_direction = (0, 0)
        self.dash_speed_mult = 6.0
        from game.mutation import MutationTracker
        self.mutation = MutationTracker()


    @property
    def weapon(self):
        return self._weapon

    @weapon.setter
    def weapon(self, w):
        self._weapon = w if w else self._weapon

    def get_weapon_damage(self):
        return self._weapon["damage"] if self._weapon else 0

    def get_weapon_magic(self):
        return self._weapon["magic"] if self._weapon else 0

    def get_weapon_speed_bonus(self):
        return self._weapon["speed_bonus"] if self._weapon else 0.0

    def get_weapon_defense(self):
        return self._weapon["defense"] if self._weapon else 0

    def get_total_strength(self):
        base = self.strength + self.get_weapon_damage()
        return int(base * ULT_DAMAGE_MULT) if self.ult_active else base

    def get_total_defense(self):
        return self.defense + self.get_weapon_defense()

    def get_spell_damage(self, base_damage):
        wm = 1.0 + self.get_weapon_magic() * 0.08
        base = int((self.strength + self.get_weapon_damage() // 2) * wm) + base_damage
        return int(base * ULT_DAMAGE_MULT) if self.ult_active else base

    def add_ult_gauge(self, amount):
        self.ult_gauge = min(self.ult_max, self.ult_gauge + amount)

    def activate_ult(self):
        if self.ult_gauge >= self.ult_max and not self.ult_active:
            self.ult_active = True
            self.ult_timer = self.ult_duration
            self.ult_gauge = 0
            return True
        return False

    def update_ult(self, dt):
        if self.ult_active:
            self.ult_timer -= dt
            if self.ult_timer <= 0:
                self.ult_active = False

    def _xp_for_level(self, level):
        return int(XP_BASE * (level ** XP_MULTIPLIER))

    def add_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level_up()
            leveled = True
        return leveled

    def level_up(self):
        self.level += 1
        self.max_hp += HP_PER_LEVEL
        self.hp = min(self.hp + HP_PER_LEVEL, self.max_hp)
        self.max_mp += MP_PER_LEVEL
        self.mp = min(self.mp + MP_PER_LEVEL, self.max_mp)
        self.strength += STR_PER_LEVEL
        self.defense += DEF_PER_LEVEL
        self.xp_to_next = self._xp_for_level(self.level)
        if self.level == 3 and SPELL_DARK_PULSE not in self.equipped_spells:
            self.equipped_spells.append(SPELL_DARK_PULSE)
        if self.level == 5 and SPELL_VOID_SHIELD not in self.equipped_spells:
            self.equipped_spells.append(SPELL_VOID_SHIELD)
        if self.level == 7 and SPELL_DOMAIN_EXPANSION not in self.equipped_spells:
            self.equipped_spells.append(SPELL_DOMAIN_EXPANSION)

    def use_mp(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def recharge_mp(self, amount):
        self.mp = min(self.max_mp, self.mp + amount)

    def apply_item_buff(self, stat, amount, duration):
        key = f"item_buff_{stat}"
        self._buff_timers[key] = {"stat": stat, "amount": amount, "remaining": duration}
        if stat == "str" or stat == "all":
            self.strength += amount
        if stat == "def" or stat == "all":
            self.defense += amount
        if stat == "spd" or stat == "all":
            self.speed += amount
        if stat == "mag" or stat == "all":
            pass  # magic handled in get_spell_damage via weapon

    def update_buffs(self, dt):
        expired = []
        for key, buff in self._buff_timers.items():
            buff["remaining"] -= dt
            if buff["remaining"] <= 0:
                stat = buff["stat"]
                amount = buff["amount"]
                if stat == "str" or stat == "all":
                    self.strength -= amount
                if stat == "def" or stat == "all":
                    self.defense -= amount
                if stat == "spd" or stat == "all":
                    self.speed -= amount
                expired.append(key)
            else:
                stat = buff["stat"]
                amount = buff["amount"]
                if stat == "regen_hp":
                    self.heal(amount * dt)
                elif stat == "regen_mp":
                    self.recharge_mp(amount * dt)
        for key in expired:
            del self._buff_timers[key]

    def start_dash(self):
        if self.dash_cooldown > 0 or self.dashing:
            return
        dx, dy = self.facing
        if dx == 0 and dy == 0:
            dx, dy = 0, 1
        self.dashing = True
        self.dash_timer = self.dash_duration
        self.dash_cooldown = self.dash_cooldown_duration
        self.dash_direction = (dx, dy)

    def update(self, dt, input_handler):
        dx, dy = 0, 0
        if input_handler.is_key_down(pygame.K_w) or input_handler.is_key_down(pygame.K_UP):
            dy -= 1
        if input_handler.is_key_down(pygame.K_s) or input_handler.is_key_down(pygame.K_DOWN):
            dy += 1
        if input_handler.is_key_down(pygame.K_a) or input_handler.is_key_down(pygame.K_LEFT):
            dx -= 1
        if input_handler.is_key_down(pygame.K_d) or input_handler.is_key_down(pygame.K_RIGHT):
            dx += 1
        moving = dx != 0 or dy != 0
        if moving:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length
            self.facing = (dx, dy)
        self.vx = dx * self.speed
        self.vy = dy * self.speed

        # ── Dash ──
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        if self.dashing:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dashing = False
            else:
                ddx, ddy = self.dash_direction
                self.vx = ddx * self.speed * self.dash_speed_mult
                self.vy = ddy * self.speed * self.dash_speed_mult

        if self.cast_cooldown > 0:
            self.cast_cooldown -= dt
        self.mp = min(self.max_mp, self.mp + 5 * dt)
        self.update_buffs(dt)
        self.status.update(self, dt)
        if self.status.has("Slow"):
            self.vx *= 0.6
            self.vy *= 0.6

        # ── Blocking ──
        holding_block = (input_handler.is_key_down(pygame.K_LSHIFT) or
                         input_handler.is_key_down(pygame.K_RSHIFT))
        if self.block_cooldown > 0:
            self.block_cooldown -= dt
        if holding_block and not self.blocking and self.block_cooldown <= 0:
            self.blocking = True
            self.block_timer = self.block_max_duration
            self.parry_window = self.parry_window_duration
        if self.blocking:
            self.block_timer -= dt
            self.parry_window = max(0, self.parry_window - dt)
            if self.block_timer <= 0 or not holding_block:
                self.blocking = False
                self.block_cooldown = self.block_cooldown_duration
                self.parry_window = 0

        if self.blocking:
            self.vx *= 0.3
            self.vy *= 0.3

        super().update(dt)

    def take_damage(self, amount, attacker=None):
        if self.iframes > 0:
            return False
        if self.blocking:
            if self.parry_window > 0:
                self.parry_window = 0
                self.blocking = False
                self.block_cooldown = self.block_cooldown_duration
                if attacker is not None and hasattr(attacker, 'take_damage') and attacker.alive:
                    reflect = int(amount * self.parry_damage_mult)
                    attacker.take_damage(reflect)
                self.parry_triggered = True
                self.parry_pos = (self.x + self.width // 2, self.y + self.height // 2)
                return False
            amount = int(amount * 0.25)
            self.block_timer -= 0.15
            if self.block_timer <= 0:
                self.blocking = False
                self.block_cooldown = self.block_cooldown_duration
        # Temp HP absorbs damage first
        if self.temp_hp > 0:
            absorbed = min(self.temp_hp, amount)
            self.temp_hp -= absorbed
            amount -= absorbed
        if amount <= 0:
            return False
        return super().take_damage(amount)

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if self.iframes > 0 and int(self.iframes * 20) % 2 == 0:
            return

        cx = sx + self.width // 2
        cy = sy + self.height // 2

        # ── Dash trail ──
        if self.dashing:
            trail_len = 8
            for i in range(1, trail_len + 1):
                t = i / trail_len
                tx = sx - self.dash_direction[0] * self.width * t * 0.6
                ty = sy - self.dash_direction[1] * self.height * t * 0.6
                alpha = int(100 * (1 - t))
                trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                trail_surf.set_colorkey((0, 0, 0))
                pygame.draw.rect(trail_surf, (*self.color[:3], alpha), (0, 0, self.width, self.height))
                surface.blit(trail_surf, (tx, ty))

        overlay = self.status.get_overlay_color()
        if overlay:
            draw_color = tuple(max(0, min(255, self.color[i] + overlay[i])) for i in range(3))
        else:
            draw_color = self.color
        pygame.draw.rect(surface, draw_color, (sx, sy, self.width, self.height))
        pygame.draw.circle(surface, COLOR_PLAYER_EYES, (cx - 4, cy - 3), 2)
        pygame.draw.circle(surface, COLOR_PLAYER_EYES, (cx + 4, cy - 3), 2)

        # ── Melee range indicator ──
        melee_rng = self.get_melee_range()
        pulse = 0.3 + 0.2 * math.sin(pygame.time.get_ticks() * 0.005)
        range_surf = pygame.Surface((melee_rng * 2 + 4, melee_rng * 2 + 4), pygame.SRCALPHA)
        wc = self._weapon["color"] if self._weapon else (200, 200, 200)
        pygame.draw.circle(range_surf, (*wc[:3], int(20 * pulse)), (melee_rng + 2, melee_rng + 2), melee_rng, 1)
        pygame.draw.circle(range_surf, (*wc[:3], int(8 * pulse)), (melee_rng + 2, melee_rng + 2), melee_rng, 1)
        surface.blit(range_surf, (cx - melee_rng - 2, cy - melee_rng - 2))

        # ── Facing arc highlight ──
        angle = math.atan2(self.facing[1], self.facing[0])
        arc_pts = []
        for a in [angle - 0.4, angle, angle + 0.4]:
            arc_pts.append((cx + math.cos(a) * melee_rng, cy + math.sin(a) * melee_rng))
        if len(arc_pts) == 3:
            pygame.draw.line(surface, (*wc[:3], 80), arc_pts[0], arc_pts[1], 1)
            pygame.draw.line(surface, (*wc[:3], 80), arc_pts[1], arc_pts[2], 1)

        # ── Weapon visual ──
        if self._weapon:
            wx = cx + int(self.facing[0] * 10)
            wy = cy + int(self.facing[1] * 10)
            wc = self._weapon["color"]
            pygame.draw.line(surface, wc, (cx + int(self.facing[0] * 4), cy + int(self.facing[1] * 4)),
                            (wx, wy), 3)

        # ── Block shield ──
        if self.blocking:
            angle = math.atan2(self.facing[1], self.facing[0])
            shield_arc = 1.2
            shield_radius = 16
            shield_color = (80, 180, 255) if self.parry_window > 0 else (60, 120, 200)
            alpha = 140 if self.parry_window > 0 else 80
            shield_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.arc(shield_surf, (*shield_color, alpha),
                            (2, 2, shield_radius * 2 - 4, shield_radius * 2 - 4),
                            angle - shield_arc / 2, angle + shield_arc / 2, 3)
            if self.parry_window > 0:
                pygame.draw.arc(shield_surf, (255, 255, 255, 180),
                                (0, 0, shield_radius * 2, shield_radius * 2),
                                angle - shield_arc / 2, angle + shield_arc / 2, 2)
            surface.blit(shield_surf, (cx - shield_radius, cy - shield_radius))

    def melee_attack(self):
        if not hasattr(self, 'melee_cooldown'):
            self.melee_cooldown = 0
        if self.melee_cooldown > 0:
            return None
        spd = self._weapon["speed_bonus"] if self._weapon else 0
        cd = max(0.15, 0.5 - spd)
        self.melee_cooldown = cd
        dmg = self.get_total_strength()
        wtype = self._weapon["type"] if self._weapon else "fist"
        ranges = {"dagger": 22, "sword": 30, "greatsword": 36, "spear": 42,
                  "scythe": 34, "void_blade": 32, "cursed_blade": 32,
                  "bow": 50, "chakram": 38, "staff": 26, "wand": 24, "fist": 20,
                  "red_blade": 30, "life_edge": 32, "forbidden_fruit": 44}
        rng = ranges.get(wtype, 28)
        return {
            "damage": dmg,
            "range": rng,
            "arc": math.pi / 2,
            "knockback": 3,
        }

    def get_melee_range(self):
        wtype = self._weapon["type"] if self._weapon else "fist"
        ranges = {"dagger": 22, "sword": 30, "greatsword": 36, "spear": 42,
                  "scythe": 34, "void_blade": 32, "cursed_blade": 32,
                  "bow": 50, "chakram": 38, "staff": 26, "wand": 24, "fist": 20,
                  "red_blade": 30, "life_edge": 32, "forbidden_fruit": 44}
        return ranges.get(wtype, 28)


class WeaponDrop:
    def __init__(self, x, y, weapon_key):
        self.x = x
        self.y = y
        self.weapon_key = weapon_key
        from game.weapons_inf import get_weapon
        self.weapon = get_weapon(weapon_key)
        self.width = 14
        self.height = 14
        self.rect = pygame.Rect(x - 7, y - 7, 14, 14)
        self.alive = True
        self.bob_timer = random.uniform(0, 6.28)
        self.age = 0

    def update(self, dt):
        self.age += dt
        self.bob_timer += dt * 2

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        visible = (-20 < sx < camera.width + 20 and -20 < sy < camera.height + 20)
        if not visible:
            return
        bob = math.sin(self.bob_timer) * 2
        sy += bob
        color = self.weapon["color"]
        tier = self.weapon["tier"]
        glow_colors = {1: (100, 100, 100), 2: (120, 120, 160), 3: (100, 80, 200),
                       4: (160, 80, 220), 5: (200, 160, 100), 6: (220, 100, 200)}
        glow = glow_colors.get(tier, (100, 100, 100))
        glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow, 60), (10, 10), 10)
        surface.blit(glow_surf, (sx - 10, sy - 10))
        pygame.draw.circle(surface, color, (int(sx), int(sy)), 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), 3)


class EnemyProjectile:
    def __init__(self, x, y, dx, dy, speed, damage, color, size=5, lifetime=3.0):
        self.x = x
        self.y = y
        length = math.sqrt(dx * dx + dy * dy)
        self.dx = dx / length if length > 0 else 0
        self.dy = dy / length if length > 0 else 0
        self.speed = speed
        self.damage = damage
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True
        self.rect = pygame.Rect(x - size, y - size, size * 2, size * 2)

    def update(self, dt):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        self.lifetime -= dt
        self.rect.center = (self.x, self.y)
        if self.lifetime <= 0:
            self.alive = False

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        c = (*self.color[:3], 200)
        glow = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color[:3], 60), (self.size * 2, self.size * 2), self.size * 2)
        surface.blit(glow, (sx - self.size * 2, sy - self.size * 2))
        pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.size)


class Enemy(Entity):
    def __init__(self, x, y, enemy_key="void_mite"):
        self.enemy_key = enemy_key
        edef = get_enemy_def(enemy_key)
        if edef is None:
            edef = get_enemy_def("void_mite")
        self.edef = edef
        sz = edef["size"]
        super().__init__(x, y, sz, sz, edef["hp"], edef["color"])
        self.exp_reward = edef["exp"]
        self.damage = edef["damage"]
        self.base_speed = edef["speed"]
        self.speed = edef["speed"]
        self.attack_cooldown = 0
        self.attack_rate = edef["attack_rate"]
        self.detection_range = edef["detection_range"]
        self.attack_range = edef["attack_range"]
        self.ai_type = edef["ai"]
        self.attack_type = edef["attack"]
        self.traits = list(edef["traits"])
        self.render_hint = edef.get("render_hint", "rect")
        self.wander_timer = 0
        self.wander_dir = (0, 0)
        self.status = StatusManager()
        self.teleport_cooldown = 0
        self.burst_timer = 0
        self.burst_charging = False
        self.ambush_active = True
        self.ambush_revealed = False
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.copy_offset_x = random.uniform(-40, 40)
        self.copy_offset_y = random.uniform(-40, 40)
        self.spawn_timer = 0
        self.illusion_active = False
        self.age = 0
        self.flash_color = None
        self.flash_timer = 0
        self._xp_given = False
        self.weapon_tier = self.edef["tier"]
        self.is_boss = TRAIT_BOSS in self.traits
        self._boss_phase2 = False
        self._boss_attack_timer = 0
        self.boss_minions = []

    def has_trait(self, trait):
        return trait in self.traits

    def take_damage(self, amount):
        if self.has_trait(TRAIT_INVISIBLE) and self.ambush_active:
            self.ambush_active = False
            self.ambush_revealed = True
        return super().take_damage(amount)

    def update(self, dt, player):
        self.age += dt
        self.status.update(self, dt)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt
        else:
            self.flash_color = None

        if self.has_trait(TRAIT_REGENERATES):
            self.hp = min(self.max_hp, self.hp + 2 * dt)

        if self.has_trait(TRAIT_HEAL_AURA):
            pass  # handled in combat

        if self.has_trait(TRAIT_INVISIBLE) and self.ambush_active:
            self.vx = 0
            self.vy = 0
            return

        dist = self.distance_to(player)
        self._run_ai(dt, player, dist)
        super().update(dt)

    def _run_ai(self, dt, player, dist):
        ai = self.ai_type
        if ai == AI_WANDER:
            self._ai_wander(dt, player, dist)
        elif ai == AI_CHASE:
            self._ai_chase(dt, player, dist)
        elif ai == AI_AMBUSH:
            self._ai_ambush(dt, player, dist)
        elif ai == AI_TELEPORT:
            self._ai_teleport(dt, player, dist)
        elif ai == AI_KITE:
            self._ai_kite(dt, player, dist)
        elif ai == AI_ORBIT:
            self._ai_orbit(dt, player, dist)
        elif ai == AI_COPY:
            self._ai_copy(dt, player, dist)
        elif ai == AI_STATIONARY:
            self._ai_stationary(dt, player, dist)
        elif ai == AI_FLEE:
            self._ai_flee(dt, player, dist)
        elif ai == AI_HAZARD:
            self._ai_hazard(dt, player, dist)
        elif ai == AI_SUMMONER:
            self._ai_summoner(dt, player, dist)
        elif ai == AI_BURST:
            self._ai_burst(dt, player, dist)
        elif ai == AI_PHASE_WANDER:
            self._ai_phase_wander(dt, player, dist)
        elif ai == AI_BOSS:
            self._ai_boss(dt, player, dist)

    def _ai_wander(self, dt, player, dist):
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            self.wander_timer = random.uniform(1.0, 3.0)
            angle = random.uniform(0, 2 * math.pi)
            self.wander_dir = (math.cos(angle), math.sin(angle))
        self.vx = self.wander_dir[0] * self.speed * 0.4
        self.vy = self.wander_dir[1] * self.speed * 0.4

    def _ai_chase(self, dt, player, dist):
        if dist < self.detection_range:
            dx, dy = self.direction_to(player)
            self.vx = dx * self.speed
            self.vy = dy * self.speed
        else:
            self._ai_wander(dt, player, dist)

    def _ai_ambush(self, dt, player, dist):
        if self.ambush_active:
            self.vx = 0
            self.vy = 0
            if dist < self.detection_range:
                self.ambush_active = False
                self.ambush_revealed = True
                self.burst_timer = 0.5
        elif self.burst_timer > 0:
            self.burst_timer -= dt
            if self.burst_timer <= 0:
                dx, dy = self.direction_to(player)
                self.vx = dx * self.speed * 2.0
                self.vy = dy * self.speed * 2.0
        else:
            self._ai_chase(dt, player, dist)

    def _ai_teleport(self, dt, player, dist):
        if self.teleport_cooldown <= 0 and dist < self.detection_range:
            if random.random() < 0.02:
                angle = random.uniform(0, 2 * math.pi)
                r = random.uniform(60, 120)
                nx = player.x + math.cos(angle) * r
                ny = player.y + math.sin(angle) * r
                self.x = max(32, min(WORLD_WIDTH - 32, nx))
                self.y = max(32, min(WORLD_HEIGHT - 32, ny))
                self.rect.x = self.x
                self.rect.y = self.y
                self.teleport_cooldown = 1.0
                self.flash_color = (180, 140, 255)
                self.flash_timer = 0.15
            self.vx = 0
            self.vy = 0
        elif dist < self.detection_range:
            dx, dy = self.direction_to(player)
            self.vx = dx * self.speed * 0.5
            self.vy = dy * self.speed * 0.5
        else:
            self._ai_wander(dt, player, dist)

    def _ai_kite(self, dt, player, dist):
        if dist < self.detection_range:
            dx, dy = self.direction_to(player)
            if dist < self.attack_range * 0.7:
                self.vx = -dx * self.speed
                self.vy = -dy * self.speed
            elif dist > self.attack_range * 1.3:
                self.vx = dx * self.speed * 0.5
                self.vy = dy * self.speed * 0.5
            else:
                self.vx = -dy * self.speed * 0.3
                self.vy = dx * self.speed * 0.3
        else:
            self._ai_wander(dt, player, dist)

    def _ai_orbit(self, dt, player, dist):
        if dist < self.detection_range:
            self.orbit_angle += dt * 1.5
            r = self.attack_range * 0.8
            tx = player.x + math.cos(self.orbit_angle) * r
            ty = player.y + math.sin(self.orbit_angle) * r
            dx = tx - self.x
            dy = ty - self.y
            d = math.sqrt(dx * dx + dy * dy)
            if d > 5:
                self.vx = (dx / d) * self.speed
                self.vy = (dy / d) * self.speed
            else:
                self.vx = 0
                self.vy = 0
        else:
            self._ai_chase(dt, player, dist)

    def _ai_copy(self, dt, player, dist):
        tx = player.x + self.copy_offset_x
        ty = player.y + self.copy_offset_y
        dx = tx - self.x
        dy = ty - self.y
        d = math.sqrt(dx * dx + dy * dy)
        if d > 10:
            self.vx = (dx / d) * self.speed * 0.8
            self.vy = (dy / d) * self.speed * 0.8
        else:
            self.vx = 0
            self.vy = 0

    def _ai_stationary(self, dt, player, dist):
        self.vx = 0
        self.vy = 0

    def _ai_flee(self, dt, player, dist):
        if dist < 300:
            dx, dy = self.direction_to(player)
            self.vx = -dx * self.speed
            self.vy = -dy * self.speed
        else:
            self._ai_wander(dt, player, dist)

    def _ai_hazard(self, dt, player, dist):
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            self.wander_timer = random.uniform(2.0, 4.0)
            angle = random.uniform(0, 2 * math.pi)
            self.wander_dir = (math.cos(angle), math.sin(angle))
        self.vx = self.wander_dir[0] * self.speed
        self.vy = self.wander_dir[1] * self.speed

    def _ai_summoner(self, dt, player, dist):
        if dist < self.detection_range:
            dx, dy = self.direction_to(player)
            if dist < 100:
                self.vx = -dx * self.speed * 0.5
                self.vy = -dy * self.speed * 0.5
            else:
                self.vx = dx * self.speed * 0.3
                self.vy = dy * self.speed * 0.3
            self.spawn_timer += dt
        else:
            self._ai_wander(dt, player, dist)

    def _ai_burst(self, dt, player, dist):
        if not self.burst_charging and dist < self.detection_range:
            self.burst_charging = True
            self.burst_timer = random.uniform(0.8, 1.5)
            self.vx = 0
            self.vy = 0
        if self.burst_charging:
            self.burst_timer -= dt
            self.vx = 0
            self.vy = 0
            if self.burst_timer <= 0:
                self.burst_charging = False
                dx, dy = self.direction_to(player)
                self.vx = dx * self.speed * 3.0
                self.vy = dy * self.speed * 3.0
                self.flash_color = (255, 100, 100)
                self.flash_timer = 0.2
        elif dist > self.attack_range:
            self._ai_chase(dt, player, dist)

    def _ai_phase_wander(self, dt, player, dist):
        self._ai_wander(dt, player, dist)

    def _ai_boss(self, dt, player, dist):
        hp_ratio = self.hp / self.max_hp

        # Phase 2 trigger at 50% HP
        if hp_ratio < 0.5 and not self._boss_phase2:
            self._boss_phase2 = True
            self.flash_color = (255, 255, 255)
            self.flash_timer = 0.4
            self.speed = int(self.speed * 1.25)
            self.attack_rate = max(0.4, self.attack_rate * 0.7)

        boss_key = self.enemy_key

        # Movement varies by boss
        if boss_key == "joy":
            # Erratic zigzag movement
            self._boss_attack_timer += dt
            angle = self._boss_attack_timer * 4 + self.age * 2
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle * 0.7) * self.speed
            if dist < 300:
                px, py = self.direction_to(player)
                self.vx = dx * 0.6 + px * self.speed * 0.4
                self.vy = dy * 0.6 + py * self.speed * 0.4
            else:
                self.vx = dx
                self.vy = dy

        elif boss_key == "sorrow" or boss_key == "grief":
            # Slow drift toward player, heavy
            if dist < self.detection_range:
                dx, dy = self.direction_to(player)
                spd = self.speed * (0.3 if dist < 100 else 0.7)
                self.vx = dx * spd
                self.vy = dy * spd
            else:
                self._ai_chase(dt, player, dist)

        elif boss_key == "fear":
            # Lurking at edge of range, occasionally teleports
            if dist < self.detection_range:
                if dist < 120:
                    dx, dy = self.direction_to(player)
                    self.vx = -dx * self.speed * 0.8
                    self.vy = -dy * self.speed * 0.8
                elif dist > 300:
                    dx, dy = self.direction_to(player)
                    self.vx = dx * self.speed * 0.5
                    self.vy = dy * self.speed * 0.5
                else:
                    self.orbit_angle += dt * 0.8
                    r = 200
                    tx = player.x + math.cos(self.orbit_angle) * r
                    ty = player.y + math.sin(self.orbit_angle) * r
                    dx = tx - self.x
                    dy = ty - self.y
                    d = math.sqrt(dx * dx + dy * dy)
                    if d > 5:
                        self.vx = (dx / d) * self.speed * 0.4
                        self.vy = (dy / d) * self.speed * 0.4
                    else:
                        self.vx = 0
                        self.vy = 0
            else:
                self._ai_chase(dt, player, dist)

        elif boss_key == "pain" or boss_key == "rage":
            # Aggressive chase
            if dist < self.detection_range:
                dx, dy = self.direction_to(player)
                spd = self.speed * (1.3 if self._boss_phase2 else 1.0)
                self.vx = dx * spd
                self.vy = dy * spd
            else:
                self._ai_chase(dt, player, dist)

        elif boss_key == "envy":
            # Mirrors player movement offset
            tx = player.x + math.sin(self.age * 0.5) * 80
            ty = player.y + math.cos(self.age * 0.5) * 80
            dx = tx - self.x
            dy = ty - self.y
            d = math.sqrt(dx * dx + dy * dy)
            if d > 5:
                self.vx = (dx / d) * self.speed * 0.6
                self.vy = (dy / d) * self.speed * 0.6
            else:
                self.vx = 0
                self.vy = 0

        elif boss_key == "disgust":
            # Slow shambling
            if dist < self.detection_range:
                dx, dy = self.direction_to(player)
                self.vx = dx * self.speed * 0.3
                self.vy = dy * self.speed * 0.3
            else:
                self._ai_wander(dt, player, dist)

        elif boss_key == "hope":
            # Maintains medium distance, healing focused
            if dist < self.detection_range:
                if dist < 100:
                    dx, dy = self.direction_to(player)
                    self.vx = -dx * self.speed * 0.6
                    self.vy = -dy * self.speed * 0.6
                elif dist > 250:
                    dx, dy = self.direction_to(player)
                    self.vx = dx * self.speed * 0.4
                    self.vy = dy * self.speed * 0.4
                else:
                    self.vx = 0
                    self.vy = 0
            else:
                self._ai_chase(dt, player, dist)

        elif boss_key == "despair":
            # Menacing advance
            if dist < self.detection_range:
                dx, dy = self.direction_to(player)
                spd = self.speed * 0.5
                self.vx = dx * spd
                self.vy = dy * spd
            else:
                self._ai_chase(dt, player, dist)

        else:
            self._ai_chase(dt, player, dist)

        # Keep boss in world
        self.x = max(64, min(WORLD_WIDTH - 64, self.x))
        self.y = max(64, min(WORLD_HEIGHT - 64, self.y))

    def can_attack(self, player):
        return (self.attack_cooldown <= 0 and
                self.distance_to(player) < self.attack_range)

    def can_ranged_attack(self, player):
        return (self.attack_cooldown <= 0 and
                self.distance_to(player) < self.detection_range)

    def perform_attack(self, player, combat):
        pdef = player.get_total_defense() if hasattr(player, 'get_total_defense') else player.defense
        if self.attack_type == ATK_TOUCH:
            dmg = max(1, int(self.damage * ENEMY_DAMAGE_MULT) - pdef // DEFENSE_DIVISOR)
            player.take_damage(dmg, self)
        elif self.attack_type == ATK_MELEE:
            dmg = max(1, int(self.damage * ENEMY_DAMAGE_MULT) - pdef // DEFENSE_DIVISOR)
            player.take_damage(dmg, self)
        elif self.attack_type == ATK_LEECH:
            dmg = max(1, int(self.damage * ENEMY_DAMAGE_MULT) - pdef // DEFENSE_DIVISOR)
            player.take_damage(dmg, self)
            self.hp = min(self.max_hp, self.hp + dmg // 2)
            player.status.add(LeechEffect(drain_per_tick=2, duration=2.0))
        elif self.attack_type == ATK_POISON:
            dmg = max(1, int(self.damage * ENEMY_DAMAGE_MULT) - pdef // DEFENSE_DIVISOR)
            player.take_damage(dmg, self)
            player.status.add(PoisonEffect(damage_per_tick=4, duration=3.0))
        elif self.attack_type == ATK_SLOW:
            dmg = max(1, int(self.damage * ENEMY_DAMAGE_MULT) - pdef // DEFENSE_DIVISOR)
            player.take_damage(dmg, self)
            player.status.add(SlowEffect(factor=0.5, duration=2.5))
        elif self.attack_type == ATK_BURST:
            dmg = max(1, int(self.damage * 2 * ENEMY_DAMAGE_MULT) - pdef // DEFENSE_DIVISOR)
            player.take_damage(dmg, self)
        self.attack_cooldown = self.attack_rate

    def fire_projectile(self, player):
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        dx = player.x + player.width // 2 - cx
        dy = player.y + player.height // 2 - cy
        angle = math.atan2(dy, dx)
        projectiles = []
        spread_count = 5
        spread_angle = 0.6
        for i in range(spread_count):
            offset = (i - spread_count // 2) * (spread_angle / spread_count)
            a = angle + offset
            p = EnemyProjectile(cx, cy, math.cos(a), math.sin(a), 150,
                                max(1, self.damage - 2),
                                (160, 80, 200), size=4, lifetime=2.0)
            projectiles.append(p)
        return projectiles

    def fire_spores(self, player):
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        projectiles = []
        for angle_offset in [-0.3, 0, 0.3]:
            dx = math.cos(angle_offset)
            dy = math.sin(angle_offset)
            if abs(dx) < 0.01:
                dx = 0.1
            p = EnemyProjectile(cx, cy, dx, dy, 80, max(1, self.damage - 1),
                               (80, 160, 60), size=3, lifetime=1.5)
            projectiles.append(p)
        return projectiles

    def fire_beam(self, player):
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        dx = player.x + player.width // 2 - cx
        dy = player.y + player.height // 2 - cy
        angle = math.atan2(dy, dx)
        projectiles = []
        for i in range(3):
            offset = (i - 1) * 0.15
            a = angle + offset
            p = EnemyProjectile(cx, cy, math.cos(a), math.sin(a), 200,
                                self.damage, (200, 180, 220), size=6, lifetime=1.5)
            projectiles.append(p)
        return projectiles

    def on_death(self, combat, world):
        if self.has_trait(TRAIT_SPLIT):
            for _ in range(2):
                ox = random.uniform(-10, 10)
                oy = random.uniform(-10, 10)
                child = Enemy(self.x + ox, self.y + oy, "void_mite")
                child.hp = max(1, self.max_hp // 4)
                child.max_hp = child.hp
                child.speed = self.base_speed * 1.3
                combat.enemies_to_spawn.append(child)
        if self.has_trait(TRAIT_EXPLOSIVE):
            combat.explosions.append({
                "x": self.x + self.width // 2,
                "y": self.y + self.height // 2,
                "radius": 40,
                "damage": self.damage * 2,
                "timer": 0.1,
            })

    def render(self, surface, camera):
        if self.has_trait(TRAIT_INVISIBLE) and self.ambush_active:
            if random.random() < 0.1:
                sx, sy = camera.world_to_screen(self.x, self.y)
                pygame.draw.rect(surface, (*self.color[:3], 30),
                                (sx, sy, self.width, self.height), 1)
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        visible = (-self.width < sx < camera.width + self.width and
                   -self.height < sy < camera.height + self.height)
        if not visible:
            return
        if self.iframes > 0 and int(self.iframes * 20) % 2 == 0:
            return

        cx = sx + self.width // 2
        cy = sy + self.height // 2
        hint = self.render_hint
        color = self.flash_color if self.flash_color else self.color
        ow = self.width
        oh = self.height

        if hint == "mite":
            pygame.draw.circle(surface, color, (cx, cy), ow // 2)
            pygame.draw.circle(surface, self.color, (cx - 3, cy - 2), 2)
            pygame.draw.circle(surface, self.color, (cx + 3, cy - 2), 2)

        elif hint == "crawler":
            pygame.draw.ellipse(surface, color, (sx, sy + 4, ow, oh - 4))
            pygame.draw.circle(surface, (60, 50, 60), (cx, cy - 2), 4)

        elif hint == "sprout":
            pygame.draw.rect(surface, (40, 60, 30), (sx + 6, sy + oh // 2, 4, oh // 2))
            pygame.draw.circle(surface, color, (cx, sy + 4), ow // 3)
            for i in range(3):
                ax = cx + int(math.cos(i * 2.09 + self.age * 2) * 8)
                ay = sy + 2 + int(math.sin(i * 2.09 + self.age * 2) * 4)
                pygame.draw.circle(surface, (100, 180, 80), (ax, ay), 2)

        elif hint == "slime":
            pygame.draw.ellipse(surface, color, (sx, sy + 2, ow, oh - 2))
            pygame.draw.circle(surface, (80, 40, 120), (cx - 4, cy - 1), 2)
            pygame.draw.circle(surface, (80, 40, 120), (cx + 4, cy - 1), 2)

        elif hint == "rat":
            pygame.draw.ellipse(surface, color, (sx, sy + 2, ow, oh - 2))
            pygame.draw.circle(surface, (180, 160, 120), (cx - 3, cy - 2), 2)
            pygame.draw.circle(surface, (180, 160, 120), (cx + 3, cy - 2), 2)
            if random.random() < 0.3:
                pygame.draw.line(surface, color, (cx + ow // 2, cy), (cx + ow // 2 + 6, cy - 2), 1)

        elif hint == "hound":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            pygame.draw.circle(surface, (200, 50, 50), (cx - 5, cy - 2), 2)
            pygame.draw.circle(surface, (200, 50, 50), (cx + 5, cy - 2), 2)
            for side in [-1, 1]:
                ex = cx + side * (ow // 2 + 2)
                pygame.draw.ellipse(surface, color, (ex - 4, cy - 3, 6, 6))

        elif hint == "leech":
            pygame.draw.ellipse(surface, color, (sx + 2, sy, ow - 4, oh))
            pygame.draw.circle(surface, (255, 200, 100), (cx, cy - 4), 3)

        elif hint == "stalker":
            alpha = 80 if self.ambush_active else 180
            c = (*color[:3], alpha)
            stalker_surf = pygame.Surface((ow, oh), pygame.SRCALPHA)
            pygame.draw.rect(stalker_surf, c, (0, 0, ow, oh))
            surface.blit(stalker_surf, (sx, sy))
            if not self.ambush_active:
                pygame.draw.circle(surface, (120, 100, 200), (cx - 4, cy - 2), 2)
                pygame.draw.circle(surface, (120, 100, 200), (cx + 4, cy - 2), 2)

        elif hint == "wisp":
            pygame.draw.circle(surface, color, (cx, cy), ow // 2)
            pygame.draw.circle(surface, (255, 200, 200), (cx, cy - 2), 3)
            for i in range(3):
                ax = cx + int(math.cos(self.age * 3 + i * 2.09) * 8)
                ay = cy + int(math.sin(self.age * 3 + i * 2.09) * 8)
                pygame.draw.circle(surface, (*color[:3], 100), (ax, ay), 2)

        elif hint == "sentinel":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh), border_radius=2)
            pygame.draw.rect(surface, (60, 60, 60), (sx + 4, sy + 4, ow - 8, 4))
            pygame.draw.rect(surface, (60, 60, 60), (sx + 4, sy + oh - 8, ow - 8, 4))
            pygame.draw.circle(surface, (100, 80, 60), (cx, cy), 4)

        elif hint == "reaper":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            for side in [-1, 1]:
                ax = cx + side * (ow // 2 + 4)
                pygame.draw.ellipse(surface, (220, 100, 140), (ax - 2, cy - 8, 4, 16))
            pygame.draw.circle(surface, (255, 150, 180), (cx - 4, cy - 2), 2)
            pygame.draw.circle(surface, (255, 150, 180), (cx + 4, cy - 2), 2)

        elif hint == "husk":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            overlay = pygame.Surface((ow, oh), pygame.SRCALPHA)
            overlay.fill((100, 80, 120, 60))
            surface.blit(overlay, (sx, sy))

        elif hint == "rift":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh), border_radius=4)
            pygame.draw.circle(surface, (180, 100, 220), (cx, cy), ow // 3)
            if self.flash_color:
                flash = pygame.Surface((ow + 8, oh + 8), pygame.SRCALPHA)
                pygame.draw.rect(flash, (*self.flash_color[:3], 100), (0, 0, ow + 8, oh + 8), 2, border_radius=6)
                surface.blit(flash, (sx - 4, sy - 4))

        elif hint == "parasite":
            pygame.draw.ellipse(surface, color, (sx, sy, ow, oh))
            pygame.draw.line(surface, (60, 30, 70), (cx, cy + oh // 2), (cx + 6, cy + oh // 2 + 6), 1)
            pygame.draw.line(surface, (60, 30, 70), (cx, cy + oh // 2), (cx - 6, cy + oh // 2 + 6), 1)
            pygame.draw.circle(surface, (100, 60, 100), (cx - 3, cy - 1), 2)
            pygame.draw.circle(surface, (100, 60, 100), (cx + 3, cy - 1), 2)

        elif hint == "wraith":
            alpha = 120 + int(math.sin(self.age * 3) * 40)
            wsurf = pygame.Surface((ow, oh), pygame.SRCALPHA)
            pygame.draw.rect(wsurf, (*color[:3], alpha), (0, 0, ow, oh))
            surface.blit(wsurf, (sx, sy))

        elif hint == "strategist":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh), border_radius=3)
            pygame.draw.circle(surface, (120, 100, 200), (cx, cy), ow // 4)

        elif hint == "clone":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            pygame.draw.rect(surface, (220, 200, 240), (sx + 2, sy + 2, ow - 4, oh - 4), 1)

        elif hint == "data_leech":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            for i in range(4):
                lx = sx + 3 + i * 4
                pygame.draw.rect(surface, (100, 220, 200), (lx, sy + 2 + (i % 2) * 4, 2, 4))

        elif hint == "executioner":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            if self.burst_charging:
                pygame.draw.circle(surface, (200, 50, 50), (cx, cy), ow // 2 + 4, 2)
            pygame.draw.circle(surface, (120, 80, 140), (cx - 3, cy - 2), 2)
            pygame.draw.circle(surface, (120, 80, 140), (cx + 3, cy - 2), 2)

        elif hint == "root_node":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh), border_radius=4)
            pygame.draw.circle(surface, (120, 100, 80), (cx, cy), ow // 3)
            for angle in range(0, 360, 60):
                a = math.radians(angle)
                rx = cx + int(math.cos(a) * ow // 2)
                ry = cy + int(math.sin(a) * oh // 2)
                pygame.draw.line(surface, (60, 40, 30), (cx, cy), (rx, ry), 1)

        elif hint == "gardener":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            pygame.draw.circle(surface, (80, 60, 40), (cx - 4, cy - 4), 3)
            pygame.draw.circle(surface, (80, 60, 40), (cx + 4, cy - 4), 3)
            pygame.draw.rect(surface, (100, 80, 60), (cx - 1, cy + 4, 2, 8))

        elif hint == "bloom_beast":
            pygame.draw.ellipse(surface, color, (sx, sy, ow, oh))
            for i in range(6):
                a = i * 1.047 + self.age
                px = cx + int(math.cos(a) * ow // 2)
                py = cy + int(math.sin(a) * oh // 2)
                pygame.draw.circle(surface, (180, 80, 100), (px, py), 4)
            pygame.draw.circle(surface, (200, 100, 120), (cx - 5, cy - 2), 3)
            pygame.draw.circle(surface, (200, 100, 120), (cx + 5, cy - 2), 3)

        elif hint == "colossus":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh), border_radius=4)
            pygame.draw.rect(surface, (100, 80, 120), (sx + 6, sy + 6, ow - 12, 6))
            pygame.draw.rect(surface, (100, 80, 120), (sx + 6, sy + oh - 12, ow - 12, 6))
            pygame.draw.circle(surface, (120, 80, 140), (cx - 6, cy), 5)
            pygame.draw.circle(surface, (120, 80, 140), (cx + 6, cy), 5)

        elif hint == "warden":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            pygame.draw.circle(surface, (200, 180, 240), (cx, cy), ow // 4)
            for angle in [0, 90, 180, 270]:
                a = math.radians(angle + self.age * 60)
                px = cx + int(math.cos(a) * ow // 3)
                py = cy + int(math.sin(a) * oh // 3)
                pygame.draw.circle(surface, (200, 180, 240), (px, py), 2)

        elif hint == "seedless":
            pygame.draw.circle(surface, color, (cx, cy), ow // 2)
            pygame.draw.circle(surface, (220, 140, 100), (cx, cy), ow // 4)
            for i in range(8):
                a = i * 0.785 + self.age
                px = cx + int(math.cos(a) * ow // 2)
                py = cy + int(math.sin(a) * oh // 2)
                pygame.draw.circle(surface, (220, 140, 100), (px, py), 2)

        elif hint == "storm":
            storm_surf = pygame.Surface((ow + 12, oh + 12), pygame.SRCALPHA)
            for i in range(5):
                ox = int(math.sin(self.age * 2 + i * 1.256) * 6)
                oy = int(math.cos(self.age * 2 + i * 1.256) * 6)
                c = (*color[:3], 80)
                pygame.draw.circle(storm_surf, c, (ow // 2 + ox, oh // 2 + oy), 8)
            surface.blit(storm_surf, (sx - 6, sy - 6))

        elif hint == "wanderer":
            pygame.draw.circle(surface, color, (cx, cy), ow // 2, 2)
            pygame.draw.circle(surface, (220, 220, 240), (cx, cy), 2)

        elif hint == "god_shard":
            pts = [
                (cx, sy),
                (sx + ow, cy),
                (cx, sy + oh),
                (sx, cy),
            ]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.circle(surface, (255, 220, 140), (cx, cy), 3)

        elif hint == "angel":
            pygame.draw.circle(surface, color, (cx, cy), ow // 2)
            for side in [-1, 1]:
                for i in range(3):
                    ax = cx + side * (ow // 2 + 4 + i * 3)
                    ay = cy - 4 + i * 4
                    pygame.draw.circle(surface, (*color[:3], 120), (ax, ay), 2)
            pygame.draw.circle(surface, (255, 200, 240), (cx - 3, cy - 2), 2)
            pygame.draw.circle(surface, (255, 200, 240), (cx + 3, cy - 2), 2)

        elif hint == "quiet_root":
            pygame.draw.rect(surface, color, (sx, sy, ow, oh), border_radius=6)
            pygame.draw.rect(surface, (60, 80, 70), (sx + 4, sy + 4, ow - 8, oh - 8), 1, border_radius=4)
            if random.random() < 0.05:
                pygame.draw.circle(surface, (80, 120, 100), (cx, cy), 3)

        elif hint.startswith("boss_"):
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))
            pygame.draw.circle(surface, (255, 255, 255), (cx - 5, cy - 3), 3)
            pygame.draw.circle(surface, (255, 255, 255), (cx + 5, cy - 3), 3)

        else:
            pygame.draw.rect(surface, color, (sx, sy, ow, oh))


class Quest:
    def __init__(self, giver, description, target_kills, reward_coins):
        self.giver = giver
        self.description = description
        self.target_kills = target_kills
        self.kills = 0
        self.reward_coins = reward_coins
        self.accepted = False
        self.completed = False
        self.claimed = False

    @property
    def is_done(self):
        return self.kills >= self.target_kills

    def add_kill(self):
        if not self.completed:
            self.kills += 1
            if self.kills >= self.target_kills:
                self.completed = True

    def reset(self):
        new = Quest.__new__(Quest)
        new.giver = self.giver
        targets = [10, 25, 50, 100, 150]
        rewards = [15, 30, 50, 90, 130]
        idx = random.randint(0, len(targets) - 1)
        new.description = f"Slay {targets[idx]} foes"
        new.target_kills = targets[idx]
        new.kills = 0
        new.reward_coins = rewards[idx]
        new.accepted = False
        new.completed = False
        new.claimed = False
        return new


class QuestGiver:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 28
        self.rect = pygame.Rect(x - 12, y - 14, 24, 28)
        self.alive = True
        self.time = 0.0
        self.quest = self._generate_quest()

    @staticmethod
    def _generate_quest():
        targets = [10, 25, 50, 100, 150]
        rewards = [15, 30, 50, 90, 130]
        idx = random.randint(0, len(targets) - 1)
        return Quest(None, f"Slay {targets[idx]} foes", targets[idx], rewards[idx])

    def update(self, dt):
        self.time += dt

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if -50 < sx < camera.width + 50 and -50 < sy < camera.height + 50:
            cx = sx + self.width // 2
            cy = sy + self.height // 2

            # Glow
            glow_pulse = 0.4 + 0.3 * math.sin(self.time * 2)
            glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            q_color = (80, 220, 255) if not (self.quest and self.quest.completed) else (80, 255, 120)
            pygame.draw.circle(glow_surf, (*q_color, int(30 * glow_pulse)), (30, 30), 24)
            surface.blit(glow_surf, (cx - 30, cy - 30))

            # Body (cloak)
            pygame.draw.ellipse(surface, (60, 80, 120), (sx, sy, self.width, self.height))
            # Head
            pygame.draw.circle(surface, (200, 180, 160), (cx, sy - 4), 8)
            # Eyes
            eye_color = (80, 220, 255) if not (self.quest and self.quest.completed) else (80, 255, 120)
            pygame.draw.circle(surface, eye_color, (cx - 3, sy - 5), 2)
            pygame.draw.circle(surface, eye_color, (cx + 3, sy - 5), 2)
            # Hood
            pygame.draw.polygon(surface, (40, 60, 100), [
                (cx - 10, sy - 8), (cx + 10, sy - 8), (cx, sy - 22)
            ])

            # Quest icon
            icon = "?" if not (self.quest and self.quest.accepted) else "!"
            try:
                from game.constants import FONT_PATH
                f = pygame.font.Font(FONT_PATH, 14)
                icon_surf = f.render(icon, True, (255, 255, 255))
                surface.blit(icon_surf, (cx - icon_surf.get_width() // 2, sy - 34))
            except:
                pass


NPC_DEFINITIONS = {

    # ─── Healers (9) ───
    "fruit_girl": {
        "name": "Fruit Girl", "color": (255, 180, 160), "eye_color": (100, 60, 40),
        "render": "merchant",
        "dialogues": [
            "Fresh fruits! They\'ll heal you right up.",
            "Straight from my garden, picked this morning!",
            "Apples, berries, melons — nature\'s candy!",
            "You look a bit pale, try a slice of this peach.",
            "Vitamins and sweetness, all in one bite!",
            "My apple trees have been extra generous this season.",
            "A fruit a day keeps the monsters away, or so they say!",
            "This golden pear is especially juicy today.",
            "I water my garden with morning dew and care.",
            "These cherries are like little rubies of health!",
            "Nothing like a crisp apple to brighten your step.",
            "Even adventurers need their five servings!",
            "Try the honeydew — it\'s like eating a cloud.",
            "Fruits are nature\'s potions, you know!",
            "I\'ve been growing these since the first thaw of spring.",
            "A basket of sunshine for a weary traveler!",
            "The strawberries are so sweet they\'ll make you smile.",
            "You can\'t fight evil on an empty stomach, take this!",
            "My little secret: I sing to my plants every morning.",
            "The plums are perfectly ripe, just for you.",
            "Fruit doesn\'t judge, it just heals. I like that.",
            "This mango came from a seed I planted three summers ago.",
            "Go on, take a bite. You\'ll feel better in no time.",
            "Raspberries so fresh they still have the morning chill.",
            "I trade my fruits with the village baker for bread.",
            "Each fruit carries a little piece of the sun\'s warmth.",
            "Try the citrus — it zaps fatigue right away!",
            "The watermelons are huge this year! Have a slice.",
            "Fruits bring color to life, don\'t you think?",
            "Take an extra one for the road. You\'ll need it!",
        ],
        "effect": {'type': 'heal', 'hp': 30, 'cooldown': 4.0},
    },
    "good_witch": {
        "name": "Good Witch", "color": (140, 100, 220), "eye_color": (200, 180, 255),
        "render": "witch",
        "dialogues": [
            "A health potion for you, dearie.",
            "Brewed this under a full moon with love and care.",
            "Let me ease your troubles with a sip of magic.",
            "A dash of kindness and a sprinkle of starlight!",
            "Don\'t you worry, I have just the thing.",
            "My cauldron bubbles with nothing but good intentions.",
            "This will mend what\'s broken, inside and out.",
            "I plucked these herbs from my moonlit garden.",
            "Blessings upon you, sweet traveler!",
            "Every spell I cast is wrapped in warm wishes.",
            "A little magic goes a long way toward healing.",
            "I learned this recipe from my grandmother\'s grimoire.",
            "Close your eyes and let the warmth spread through you.",
            "There now, the color is returning to your cheeks!",
            "Magic is love made visible, my dear.",
            "I add a pinch of kindness to every potion.",
            "The stars guided me to this exact remedy for you.",
            "Don\'t fear my cauldron — it makes only good things!",
            "Your journey has been hard. Let me soften the road.",
            "I stir my potions widdershins for extra potency!",
            "The forest provides all the ingredients I need.",
            "I\'ve bottled the essence of a peaceful meadow.",
            "A sweet dream in a bottle, still warm from the brew.",
            "This spell was woven with threads of golden light.",
            "My cat familiar helped me pick these moonflowers.",
            "Even dark days end, and this potion will help!",
            "Sip slowly and let the goodness sink in.",
            "I\'d offer you a cookie, but magic is better!",
            "Every tear you\'ve shed has watered this remedy.",
            "Take courage, dear — the world is brighter with you in it!",
        ],
        "effect": {'type': 'heal', 'hp': 999, 'cooldown': 10.0},
    },
    "herb_lady": {
        "name": "Herb Lady", "color": (100, 180, 100), "eye_color": (60, 120, 60),
        "render": "cloak",
        "dialogues": [
            "These herbs will soothe your wounds.",
            "Rosemary for remembrance, thyme for courage!",
            "I\'ve foraged these from the deep woods at dawn.",
            "The earth provides all the medicine we need.",
            "Let me crush some leaves for a poultice.",
            "This sage will cleanse more than just your wounds.",
            "Dried lavender to calm the spirit and ease pain.",
            "I know every plant by its scent and its secret.",
            "The forest floor is a pharmacy if you know where to look.",
            "Mint leaves to cool your blood and lift your mood.",
            "My mortar and pestle have ground a thousand remedies.",
            "Some roots you have to dig deep for — like true healing.",
            "A handful of yarrow for your cuts and bruises.",
            "This tincture steeped for three full moons.",
            "Nature doesn\'t rush, and neither should healing.",
            "Comfrey they call \'knitbone\' — fitting, isn\'t it?",
            "Wild garlic for the blood and nettles for the joints.",
            "I dry my herbs hanging from the rafters in bunches.",
            "Just a pinch of this powder on your tongue.",
            "The bees know which flowers heal — I just follow them.",
            "This chamomile will calm even the wildest heart.",
            "Stinging nettle sounds cruel but it works wonders!",
            "I trade roots with the apothecary in the next town.",
            "Every weed is a medicine waiting to be understood.",
            "A tea brewed from these leaves will steady your hands.",
            "The old ways of herbcraft are fading, but not with me.",
            "My garden grows wild and free, just like healing should be.",
            "This balm was made with beeswax and elderflower.",
            "The earth knows how to mend itself — we just help it along.",
            "When in doubt, reach for the thyme!",
        ],
        "effect": {'type': 'heal', 'hp': 50, 'cooldown': 4.0},
    },
    "milk_maid": {
        "name": "Milk Maid", "color": (220, 200, 180), "eye_color": (80, 60, 40),
        "render": "common",
        "dialogues": [
            "Fresh milk! Good for bones and health!",
            "Buttercup gave twice as much today! She\'s happy!",
            "Nothing beats a cold glass of milk after a long day.",
            "I milk the cows at sunrise when the air is sweetest.",
            "Got cheese too, if you\'re interested!",
            "The cream from this milk makes the best butter.",
            "Daisy, Buttercup, and Clover are my best girls.",
            "A warm cookie and cold milk — heaven on earth!",
            "I churn butter every Thursday without fail.",
            "The calves are getting so big! Time flies.",
            "Milk straight from the cow is liquid gold!",
            "I know every cow\'s personality — they\'re all different!",
            "The barn is my happy place, hay and all.",
            "This milk will put color back in your cheeks!",
            "I sell to the village every market day.",
            "Cows are gentle souls if you treat them with kindness.",
            "Clover let me milk her without a fuss today!",
            "Farm life isn\'t easy, but it\'s honest work.",
            "The meadow is full of wildflowers — gives the milk flavor!",
            "I\'ve been milking since I was knee-high to a grasshopper.",
            "A splash of milk in your tea works wonders.",
            "The secret is talking to them while you milk.",
            "Winter is hard on the herd, but we manage.",
            "I make the best yogurt in three counties!",
            "Come spring, the milk is richest from fresh grass.",
            "My cows know my footsteps and call out when I\'m late.",
            "Fresh dairy is nature\'s way of saying \'feel better\'!",
            "The barn cat helps keep the milk house mouse-free.",
            "It\'s a simple life, but I wouldn\'t trade it for anything.",
            "Drink up! There\'s plenty more where that came from!",
        ],
        "effect": {'type': 'heal', 'hp': 40, 'cooldown': 3.0},
    },
    "apothecary": {
        "name": "Apothecary", "color": (140, 160, 120), "eye_color": (80, 100, 60),
        "render": "robe",
        "dialogues": [
            "A potent mixture. Should patch you up nicely.",
            "Three drops of essence of nightshade, carefully diluted.",
            "I\'ve refined this formula through years of trial.",
            "The concentration must be precise, or it\'s useless.",
            "This tincture is 87% more effective than standard brews.",
            "I catalog every ingredient by its extraction yield.",
            "A standardized dosage ensures predictable results.",
            "The alchemical process requires exact temperatures.",
            "I\'ve documented this reaction extensively in my journal.",
            "Each batch is tested for purity and potency.",
            "The active compounds bind more efficiently at this pH.",
            "I synthesized a new catalyst that improves absorption.",
            "My methodology is peer-reviewed by the Alchemists\' Guild.",
            "This formulation uses a suspension base, not emulsion.",
            "The distillation must be slow to preserve volatile esters.",
            "I\'ve isolated the curative alkaloid in crystalline form.",
            "A double-blind trial showed 94% efficacy.",
            "Filtered twice through charcoal for maximum purity.",
            "The reaction yield improved after adjusting the molar ratio.",
            "I source my ingredients from certified organic growers.",
            "This compound has a half-life of roughly six hours.",
            "The binding affinity to cellular receptors is remarkable.",
            "I\'ve filed a preliminary patent on the extraction method.",
            "Temperature fluctuations can denature the active agents.",
            "Store in a cool, dark place — light degrades the potency.",
            "The solvent evaporates cleanly, leaving only the remedy.",
            "I\'m writing a treatise on advanced potion thermodynamics.",
            "This batch chromatographs beautifully, if I may say so.",
            "The color change indicates proper oxidation has occurred.",
            "A masterpiece of pharmaceutical alchemy, if modest.",
        ],
        "effect": {'type': 'heal_pct', 'pct': 0.8, 'cooldown': 8.0},
    },
    "spring_spirit": {
        "name": "Spring Spirit", "color": (120, 220, 180), "eye_color": (200, 255, 220),
        "render": "mystic",
        "dialogues": [
            "Feel the gentle warmth of renewal...",
            "The thaw has come, and with it, new life.",
            "I am the first bloom after the long frost.",
            "Listen... the earth is waking from its slumber.",
            "A breath of spring air to fill your lungs with hope.",
            "The birds are returning, and so is your strength.",
            "Each petal unfurls in its own time, as do you.",
            "I carried the sap through winter\'s sleep to greet you.",
            "Let the green light of spring wash over your spirit.",
            "The streams run free again, as does your vitality.",
            "I dance on the melting snow and call forth flowers.",
            "A season of warmth is upon us, traveler.",
            "The world remembers how to bloom — so do you.",
            "I taste like morning rain and fresh blossom petals.",
            "Winter\'s grip loosens, and so do your burdens.",
            "The breeze carries the scent of lilac and renewal.",
            "Every spring, the world dares to begin again.",
            "I bring the promise of longer days and warmer nights.",
            "The roots stir beneath the soil, full of potential.",
            "Let the sunlight dapple your skin and mend your soul.",
            "I am the whisper of grass growing through the frost.",
            "The cycle turns, and life finds a way once more.",
            "Green shoots push through the dark earth toward light.",
            "A soft rain will wash away the residue of winter.",
            "I smell of petrichor and unfurling ferns.",
            "The robin\'s song is a hymn to the returning sun.",
            "Your weary bones deserve the gentle touch of spring.",
            "Even the oldest trees put out new leaves each year.",
            "The world is painting itself green again, just for you.",
            "Bask in the glow of a world made new!",
        ],
        "effect": {'type': 'buff', 'stat': 'regeneration', 'amount': 3, 'duration': 10.0, 'cooldown': 12.0},
    },
    "healing_monk": {
        "name": "Healing Monk", "color": (200, 160, 100), "eye_color": (255, 220, 140),
        "render": "monk",
        "dialogues": [
            "Body and soul made whole again.",
            "Breathe in peace, breathe out pain.",
            "The present moment holds all the healing you need.",
            "Let your worries fall like autumn leaves.",
            "I have walked the path of inner stillness for decades.",
            "The mind is a garden — tend to it with compassion.",
            "Stillness is not emptiness; it is fullness at rest.",
            "Your suffering is a teacher, not a enemy.",
            "Sit with me in silence and let the world fade away.",
            "The river of chi flows unobstructed within you now.",
            "A calm mind is the foundation of a strong body.",
            "Every breath is a chance to begin anew.",
            "The lotus grows from the mud, yet remains unstained.",
            "I master nothing; I simply let go.",
            "Your wounds are the places where light enters you.",
            "The bells chime, and for a moment, there is only peace.",
            "Walk as if you are kissing the earth with your feet.",
            "Patience is not passive — it is the courage to endure.",
            "The flame of your spirit flickers, but never dies.",
            "I tend to the temple of your body with reverence.",
            "Let gratitude fill the spaces where fear once lived.",
            "The mountain stands unmoved by the changing seasons.",
            "You are not your pain. You are the one who witnesses it.",
            "My meditation deepens with each healing I offer.",
            "The breath is the bridge between body and spirit.",
            "True strength is softness that cannot be broken.",
            "I offer no miracles, only reminders of your own wholeness.",
            "The incense clears more than the air — it clears the mind.",
            "Your heart beats in rhythm with the universe itself.",
            "There is no separate self; we are all one breath.",
        ],
        "effect": {'type': 'full_restore', 'cooldown': 15.0},
    },
    "warmaster": {
        "name": "War Master", "color": (160, 80, 60), "eye_color": (255, 200, 100),
        "render": "warrior",
        "dialogues": [
            "Get back in the fight, soldier!",
            "Pain is temporary! Glory is forever!",
            "You call that a wound? I\'ve seen worse from a papercut!",
            "On your feet! The enemy won\'t wait for you!",
            "Another victory awaits! Don\'t keep it waiting!",
            "I\'ve trained a thousand warriors. You\'re one of the good ones!",
            "Suck it up and show them what you\'re made of!",
            "The battlefield is where men are forged into legends!",
            "Stand tall! A soldier who falls gets right back up!",
            "I\'ve taken hits that would fell an ox and I\'m still here!",
            "There\'s no crying in war! There\'s only winning!",
            "Get mad! Get even! Then get going!",
            "A real warrior turns their blood into fuel!",
            "You have two choices: win or learn. Both are good!",
            "The war drum calls and you must answer!",
            "My boot camp was hell, but it made me a weapon!",
            "Don\'t think! React! Your body knows what to do!",
            "I\'ve seen you fight — you\'ve got fire in you!",
            "Scars are just medals from battles you survived!",
            "Push through the pain barrier and find your second wind!",
            "The enemy fears you. Now go remind them why!",
            "I trained with the northern berserkers. Now THAT was tough!",
            "A good soldier fights for their comrades beside them!",
            "Your weapon is an extension of your will! Command it!",
            "No retreat! No surrender! No excuses!",
            "The heat of battle purifies the spirit!",
            "I\'ve been in a hundred skirmishes and lived to tell!",
            "Keep your head down and your blade up!",
            "What doesn\'t kill you makes you stronger — I\'m living proof!",
            "MOVE IT! The fight isn\'t over until YOU say it is!",
        ],
        "effect": {'type': 'heal', 'hp': 100, 'cooldown': 6.0},
    },
    "rejuvenator": {
        "name": "Rejuvenator", "color": (100, 200, 200), "eye_color": (180, 255, 255),
        "render": "mystic",
        "dialogues": [
            "A balanced restoration for body and mind.",
            "Health and mana flow from the same source.",
            "The body is the vessel and the spirit is the light.",
            "I restore what was lost without upsetting the balance.",
            "The breath feeds both flesh and magic equally.",
            "Too much of anything creates imbalance. Here, take this.",
            "I\'ve studied the harmony between physical and ethereal.",
            "Let equilibrium return to your weary form.",
            "A cup of tea steeped with restorative herbs and a touch of mana.",
            "The mind cannot soar if the body is broken.",
            "I weave two threads of healing into one cord.",
            "Your aura was dim — I\'ve brightened it again.",
            "The middle path leads to lasting wellness.",
            "A gentle infusion of life and magic together.",
            "True vitality is a dance between spirit and sinew.",
            "I draw from the well of both worlds for you.",
            "Like a willow that bends but does not break, find your balance.",
            "This remedy addresses both symptoms and root cause.",
            "The river of chi nourishes both banks equally.",
            "Holistic healing is the only kind worth practicing.",
            "Your reserves were depleted on all fronts.",
            "A balanced spirit creates a balanced body.",
            "I blend the physical with the arcane in perfect measure.",
            "Steady your heartbeat and your magic will follow.",
            "Health without mana is a body without purpose.",
            "Mana without health is a candle without wax.",
            "I renew the contract between your body and your soul.",
            "The sun and moon both shine within you now.",
            "Every part of you deserves the same gentle care.",
            "Walk the middle path, and you will never fall.",
        ],
        "effect": {'type': 'heal_hybrid', 'hp': 60, 'mp': 30, 'cooldown': 6.0},
    },
    # ─── Mana NPCs (5) ───
    "mana_sage": {
        "name": "Mana Sage", "color": (100, 120, 220), "eye_color": (180, 200, 255),
        "render": "robe",
        "dialogues": [
            "Let the arcane energies replenish you.",
            "The weave of magic responds to a focused mind.",
            "I\'ve spent centuries studying the flow of mana.",
            "Close your eyes and feel the current of power.",
            "Mana is the lifeblood of all magical endeavor.",
            "The void between stars is filled with raw potential.",
            "Meditate on the flame within and feel it grow.",
            "A sip from the well of infinite arcane energy.",
            "The ley lines converge here, making my work easier.",
            "I can hear the hum of magic in everything around us.",
            "Let my knowledge become your strength.",
            "The ancient mages knew mana was a gift from the cosmos.",
            "Your reserves were running thin — I\'ve topped them up.",
            "Breathe deep and draw the magic into your core.",
            "The fabric of reality is woven with threads of mana.",
            "I channel the ambient energy of this sacred place.",
            "A clear mind is the best conduit for arcane power.",
            "The first lesson: mana flows where attention goes.",
            "I\'ve memorized every treatise on arcane theory.",
            "The ether is alive and responsive to a gentle touch.",
            "Your magical potential is vast — you only need fuel.",
            "The staff amplifies my connection to the arcane plane.",
            "Mana is not created nor destroyed, only transformed.",
            "I tap the primordial energy that birthed the stars.",
            "Let the glow of restoration fill your magical core.",
            "Ancient runes carved in my tower channel this energy.",
            "The astral plane leaks power into this world at certain points.",
            "Concentrate, and the magic will answer your call.",
            "Even the mightiest wizard needs to recharge sometimes.",
            "The spark within you is rekindled. Use it wisely.",
        ],
        "effect": {'type': 'heal_mp', 'mp': 999, 'cooldown': 10.0},
    },
    "crystal_lady": {
        "name": "Crystal Lady", "color": (160, 140, 255), "eye_color": (220, 200, 255),
        "render": "mystic",
        "dialogues": [
            "A shimmering crystal, brimming with mana.",
            "Amethyst for wisdom, quartz for clarity, you need both.",
            "Each crystal sings a different note of magic.",
            "I can feel the vibrations of the stones humming.",
            "This geode was formed over millennia underground.",
            "Crystals are frozen light from the heart of the earth.",
            "Hold this rose quartz and feel its gentle warmth.",
            "The crystal lattice aligns chaotic mana into order.",
            "I polish each stone by hand until it gleams.",
            "Obsidian for protection, lapis for inner vision.",
            "The crystals chose you — I just facilitate the meeting.",
            "A touch of citrine to brighten your magical core.",
            "My cave is filled with glittering treasures of the earth.",
            "Crystals remember the ancient songs of creation.",
            "This shard resonated when you approached. It\'s yours.",
            "The facets catch the light and scatter it like magic.",
            "I\'ve been a crystal gatherer since I was a child.",
            "This crystal pulses with a warm, restorative energy.",
            "Jade for harmony, moonstone for intuition.",
            "Each stone has a personality if you learn to listen.",
            "The earth\'s bones are made of crystal and stone.",
            "Let the crystal absorb your fatigue and turn it to power.",
            "I found this deep in a cavern lit by glowing fungi.",
            "The color of a crystal tells you its purpose.",
            "Some crystals glow faintly in the dark — like tiny stars.",
            "This one was a gift from the dwarven miners below.",
            "Even a small crystal can hold immense energy.",
            "I string them into necklaces that hum with power.",
            "The crystals remember the heat and pressure of their birth.",
            "Feel the subtle vibration? That\'s mana singing to you.",
        ],
        "effect": {'type': 'heal_mp', 'mp': 50, 'cooldown': 4.0},
    },
    "energy_shaman": {
        "name": "Energy Shaman", "color": (80, 200, 160), "eye_color": (140, 255, 200),
        "render": "cloak",
        "dialogues": [
            "Spirits of energy, lend your strength!",
            "I call upon the wind spirits to replenish you.",
            "The totems speak of your coming, traveler.",
            "Great spirit of the flowing river, share your vitality!",
            "I dance the dance of the glowing firefly for your sake.",
            "The ancestors whisper their ancient secrets to me.",
            "My drum beats in rhythm with the earth\'s pulse.",
            "A spirit hawk carries my prayers to the sky.",
            "The energy of the world flows through me to you.",
            "I\'ve painted my face with sacred clay for this ritual.",
            "The buffalo spirit lends you its enduring strength.",
            "Smoke from this sage carries my intentions to the spirits.",
            "The wolf pack shares its endurance with you.",
            "I\'ve fasted and prayed for three days to prepare this gift.",
            "Listen to the wind — it carries the voices of the wise.",
            "The great tree\'s roots run deep, and so does your power.",
            "I offer this feather to the sky in your name.",
            "The fire within you is stoked by ancient flames.",
            "Spirits of the four directions, converge and empower!",
            "The river stone I hold has been blessed by the moon.",
            "Your energy was scattered — now it flows like a mountain stream.",
            "The shaman\'s path is one of harmony with all things.",
            "I see your aura brighten as the spirits answer my call.",
            "The drumbeat quickens and so does your inner fire!",
            "Raven brought me a vision of your journey.",
            "The earth beneath us is alive and generous today.",
            "I offer tobacco to the ground in gratitude.",
            "The sun\'s rays carry renewal to those who seek it.",
            "My spirit animal guides my hands as I work.",
            "Feel the warmth spread — that is the world embracing you.",
        ],
        "effect": {'type': 'buff', 'stat': 'mp_regen', 'amount': 15, 'duration': 10.0, 'cooldown': 10.0},
    },
    "mystic_fountain": {
        "name": "Mystic Fountain", "color": (60, 160, 255), "eye_color": (200, 220, 255),
        "render": "mystic",
        "dialogues": [
            "The fountain\'s magic overflows within you...",
            "Bubbling up from the deepest magical spring...",
            "My waters have flowed since before memory began...",
            "Drink deep, and let the ripples carry your cares away...",
            "I am fed by an underground river of pure mana...",
            "The water sings as it splashes... a song of renewal...",
            "Ancient coins line my basin, wishes made and kept...",
            "My waters shimmer with a light from below...",
            "Cool and clear, the magic seeps into your very being...",
            "I have witnessed the rise and fall of empires...",
            "The fountain\'s heart is a crystal that never stops glowing...",
            "Let the droplets on your skin carry arcane energy...",
            "My streams connect to every magic well in the realm...",
            "The water dances in patterns older than language...",
            "A single sip restores what hours of study have drained...",
            "Listen to my gurgling — it whispers secrets of power...",
            "I am the meeting point of earth\'s magic and the sky\'s...",
            "The basin reflects not your face, but your potential...",
            "Waters from the mountain\'s heart, filtered through ancient stone...",
            "Each drop contains a universe of magical potential...",
            "The fountain never freezes, even in the deepest winter...",
            "My magic flows ceaselessly, like time itself...",
            "Dappled light on the water\'s surface carries enchantment...",
            "I was built by the first mages to honor the source...",
            "The coins people toss in fuel my magic further...",
            "My waters have been known to grant visions to the worthy...",
            "A gentle mist rises from me, carrying mana dust...",
            "The stone around my basin is worn smooth by countless hands...",
            "I am as old as the forest and as young as this moment...",
            "Let the cool splash awaken the magic sleeping within you...",
        ],
        "effect": {'type': 'heal_mp', 'mp': 999, 'cooldown': 15.0},
        "buff_after": {'stat': 'mp_regen', 'amount': 10, 'duration': 8.0},
    },
    "arcane_scholar": {
        "name": "Arcane Scholar", "color": (120, 80, 200), "eye_color": (200, 160, 255),
        "render": "robe",
        "dialogues": [
            "A page from my tome should restore your focus.",
            "I\'ve been translating this scroll for weeks.",
            "The theory behind mana regeneration is fascinating.",
            "This marginal note holds the key to restoration.",
            "I\'ve cross-referenced seven sources on this spell.",
            "The library in the capital has an entire wing on this.",
            "My research suggests a direct correlation with focus.",
            "Let me read you a passage about arcane efficiency.",
            "I\'m compiling a compendium of minor restoration spells.",
            "The ink I use is mixed with crushed mana crystals.",
            "A footnote in an ancient text mentioned this technique.",
            "The original manuscript was written in Draconic!",
            "I\'ve indexed this spell under \'restorative cantrips\'.",
            "The bibliography alone took me a month to compile.",
            "This grimoire has been in my family for generations.",
            "I\'m peer-reviewing a paper on magical thermodynamics.",
            "The diagrams in this chapter are particularly illuminating.",
            "My quill is enchanted to never run dry of ink.",
            "The marginalia in this codex is more insightful than the text.",
            "I\'ve cataloged 842 minor restorative effects to date.",
            "This spell is a variant of the standard formula.",
            "The etymology of the incantation traces back to Old Elvish.",
            "I found a contradiction between two respected authorities.",
            "Let me cite my source: the Third Tome of Arcane Restoration.",
            "The premise is sound, but the execution needs refinement.",
            "I\'ve annotated every paragraph with my observations.",
            "The binding of this book is made from enchanted leather.",
            "Scholars debate the correct pronunciation of this rune.",
            "I attend the Arcane Symposium every solstice.",
            "Knowledge is the truest form of power — and I share it freely.",
        ],
        "effect": {'type': 'heal_mp', 'mp': 40, 'cooldown': 3.0},
    },
    # ─── Buff NPCs (8) ───
    "strength_trainer": {
        "name": "Strength Trainer", "color": (200, 100, 80), "eye_color": (255, 200, 100),
        "render": "warrior",
        "dialogues": [
            "Pump that iron! Feel the power!",
            "Lift heavy, get strong! No shortcut!",
            "I can bench a horse. Literally. A horse.",
            "Those noodles you call arms need work!",
            "The gym is my temple and the barbell is my prayer!",
            "No pain, no gain! Now feel the burn!",
            "I\'ve been lifting since I could walk.",
            "Form first, then add weight! Don\'t hurt yourself!",
            "You wanna hit harder? You gotta lift heavier!",
            "I eat protein for breakfast, lunch, and dinner!",
            "Get those gains! Every rep counts!",
            "My record is lifting twice my body weight!",
            "Sore today, strong tomorrow! That\'s the motto!",
            "The only bad workout is the one you didn\'t do!",
            "Let me spot you with some raw power!",
            "You\'ve got potential! Let\'s unlock those gainssss!",
            "I didn\'t get this buff from reading books!",
            "Chest day, leg day, every day is muscle day!",
            "Feel that surge? That\'s testosterone, baby!",
            "A real warrior trains even when nobody\'s watching!",
            "I grind stones for fun. Wanna try?",
            "Your muscles are crying? Good! They\'re growing!",
            "The heaviest weight is the one you place on your soul.",
            "Strength isn\'t just physical — but this boost sure helps!",
            "Let me show you my secret: consistent effort!",
            "I\'ve never skipped a workout in ten years!",
            "You call that a warmup? I call it stretching!",
            "Eat clean, train dirty, sleep hard!",
            "Lift with your legs, not your back — and punch with your heart!",
            "GO HARD OR GO HOME! But mostly go hard!",
        ],
        "effect": {'type': 'buff', 'stat': 'str', 'amount': 5, 'duration': 30.0, 'cooldown': 15.0},
    },
    "defense_captain": {
        "name": "Defense Captain", "color": (80, 140, 180), "eye_color": (160, 200, 220),
        "render": "warrior",
        "dialogues": [
            "Stand firm! Nothing shall break through!",
            "A good defense is the best offense!",
            "I\'ve held the line against a hundred charges.",
            "Raise your shield and trust in its strength!",
            "The wall doesn\'t move, and neither do I.",
            "I train my soldiers to be unbreakable.",
            "Fortifications win wars — remember that!",
            "My shield has saved my life more times than I can count.",
            "Brace yourself! The storm is coming but we endure!",
            "I taught a hundred recruits how to block and parry.",
            "The turtle formation never fails!",
            "Armor is your second skin. Treat it with respect.",
            "I\'ve weathered sieges that lasted months.",
            "A strong stance makes a strong warrior.",
            "Keep your feet planted and your spirit firm!",
            "No blade can pierce a heart that refuses to yield.",
            "The best defense is knowing when to hold.",
            "I reinforce my gear every night without fail.",
            "Let them come. We\'ll still be standing.",
            "Stamina is the shield of the mind.",
            "I\'ve been knocked down but never broken.",
            "The iron will is stronger than any steel!",
            "Guard your center and nothing can topple you.",
            "A castle is only as strong as its foundation.",
            "My men would die before they let the line break.",
            "Absorb the blow, then counter! That\'s the way!",
            "Patience is a shield that never rusts.",
            "The strongest walls are built with discipline.",
            "I\'ve trained under the best defensive minds in the realm.",
            "Hold the line! For glory and for each other!",
        ],
        "effect": {'type': 'buff', 'stat': 'def', 'amount': 5, 'duration': 30.0, 'cooldown': 15.0},
    },
    "speed_runner": {
        "name": "Speed Runner", "color": (100, 220, 200), "eye_color": (200, 255, 240),
        "render": "common",
        "dialogues": [
            "Gotta go fast!",
            "Speed is the ultimate weapon!",
            "I once ran across the entire kingdom in a day!",
            "You\'re too slow! Move it, move it!",
            "Life is short — make every second count!",
            "I hold the record for the fastest dungeon clear!",
            "Walls are just obstacles for those who can jump!",
            "The wind and I are old friends at this point.",
            "Speed isn\'t just moving fast — it\'s reacting fast!",
            "I eat lightning and poop thunder!",
            "Zoom! That\'s the sound of me passing you!",
            "Why walk when you can sprint?",
            "I\'ve outrun goblins, wolves, and a dragon once!",
            "Rest is for the slow! Just kidding... rest is important.",
            "My legs are basically springs at this point.",
            "I trained on the mountain trails until I could fly!",
            "Speed blitz! No one can hit what they can\'t catch!",
            "The early bird gets the worm, but the fast bird gets TWO!",
            "I\'m so fast I finish quests before they\'re given!",
            "Parkour! Urban agility is a lifesaver in cities!",
            "Blink and you\'ll miss me — literally!",
            "I won the Grand Sprint three years running!",
            "Quick feet, quick hands, quick mind!",
            "You can\'t outrun your problems, but you can outrun monsters!",
            "Nimble as a cat, swift as the wind!",
            "I logged my tenth marathon this month yesterday.",
            "Go ahead, try to catch me! I dare you!",
            "Every second counts when you\'re racing the clock!",
            "Speed is freedom — the freedom to choose your battles.",
            "WHEEEEE! Let\'s GOOOOO!",
        ],
        "effect": {'type': 'buff', 'stat': 'spd', 'amount': 50, 'duration': 30.0, 'cooldown': 15.0},
    },
    "battle_bard": {
        "name": "Battle Bard", "color": (200, 180, 80), "eye_color": (255, 240, 160),
        "render": "merchant",
        "dialogues": [
            "A song of valor to steel your spirit!",
            "O heroes bold, with hearts aflame, I sing to you a victor\'s name!",
            "The lute strings ring with power untold!",
            "I compose ballads of the battles you\'ve yet to fight.",
            "Hark! A verse to lift your weary soul!",
            "Da da DAAAH! The hero\'s theme plays once more!",
            "I traveled with a band of adventurers once. Great material!",
            "This tune was inspired by a sunrise over the Dragon\'s Teeth mountains.",
            "Sing along if you know the words!",
            "History remembers the songs, not the fights!",
            "My voice carries the echoes of ancient epics.",
            "CHORUS: And the hero stood tall, facing the fall, with courage their only shield!",
            "I\'ve been composing since I could hold a quill.",
            "This melody came to me in a dream last night.",
            "Music is the language that transcends all borders!",
            "A lament for the fallen, a march for the living!",
            "The tavern patrons love my rendition of \'The Grieving Giant\'.",
            "I set your deeds to verse and spread them across the land!",
            "A minor chord for melancholy, a major for triumph!",
            "The harp strings glow as I weave magic into the music.",
            "Even dragons pause to listen to a well-sung ballad.",
            "I\'ll write an epic about YOU someday!",
            "My teacher was the finest bard in the elven courts.",
            "Drum roll, please! The crescendo approaches!",
            "Let the music fill your chest and steel your nerves!",
            "A songbird once tried to outsing me. It failed!",
            "The rhythm of battle and the rhythm of music are one!",
            "I tune my instrument three times a day — it\'s ritual.",
            "A standing ovation from the gods themselves!",
            "Encore? Of course there\'s an encore! I live for the encore!",
        ],
        "effect": {'type': 'buff', 'stat': 'all', 'amount': 3, 'duration': 30.0, 'cooldown': 18.0},
    },
    "blacksmith": {
        "name": "Blacksmith", "color": (160, 120, 80), "eye_color": (255, 200, 100),
        "render": "warrior",
        "dialogues": [
            "Let me temper your blade\'s edge.",
            "Strike while the iron is hot, I always say!",
            "I\'ve forged weapons for three generations of warriors.",
            "The clang of hammer on anvil is my favorite music.",
            "This special oil will harden your steel to diamond edge.",
            "I learned my craft from the dwarves in the northern peaks.",
            "A properly quenched blade can cut through anything.",
            "The forge fire must be fed with charcoal and patience.",
            "I can tell the quality of a blade by its ring.",
            "Let me reinforce your armor while I\'m at it.",
            "This whetstone is enchanted to sharpen beyond belief.",
            "The anvil has been in my family for two centuries.",
            "I work the bellows until the coals are as hot as dragonfire.",
            "Tempering requires a steady hand and a steady heart.",
            "You swing hard, but with my buff, you\'ll swing harder!",
            "I source my ore from the richest veins in the realm.",
            "A well-made blade is a work of art that kills.",
            "I add a touch of powdered crystal to the steel for flexibility.",
            "The sweat on my brow is the price of quality.",
            "Let me adjust the balance on that weapon of yours.",
            "My master taught me that the fire reveals the truth of the metal.",
            "I\'ve reforged legendary weapons that were thought lost.",
            "The quenching trough is filled with oil, not water.",
            "Each fold of the steel removes impurities and adds strength.",
            "I can hear when the metal is ready to be shaped.",
            "A warrior is only as good as their tools!",
            "This rune etched into your blade will channel more strength.",
            "I never rush a piece — haste makes waste and weak steel.",
            "The heat from the forge keeps my bones warm year-round.",
            "Let me give your weapon an edge that will never dull!",
        ],
        "effect": {'type': 'buff', 'stat': 'str', 'amount': 8, 'duration': 20.0, 'cooldown': 12.0},
    },
    "enchanter": {
        "name": "Enchanter", "color": (140, 80, 220), "eye_color": (200, 160, 255),
        "render": "witch",
        "dialogues": [
            "Arcane power courses through your veins.",
            "I weave the threads of magic into your very being.",
            "This enchantment will make your spells sing.",
            "I inscribe runes that glow with ethereal light.",
            "A touch of the arcane to amplify your innate power.",
            "The enchantment process is delicate and precise.",
            "I\'ve enchanted artifacts for kings and queens.",
            "The magic settles into your bones like a warm blanket.",
            "I work at a table cluttered with crystals and scrolls.",
            "This spell of amplification will heighten your senses.",
            "The art of enchantment requires absolute concentration.",
            "I draw power from the ambient magic in the air.",
            "Your magical aura already pulses stronger.",
            "An enchanted being is a more potent being.",
            "I infuse objects with power — and I can infuse you too.",
            "The runes must be drawn without a single mistake.",
            "I spent years mastering the school of augmentation.",
            "Feel the tingle? That\'s the enchantment taking hold.",
            "My workshop glows with dozens of active enchantments.",
            "Magic is the thread, and you are the tapestry.",
            "This will make your fire burn hotter and your ice freeze colder.",
            "I whisper the words of power as I work.",
            "The enchantment resonates with your inner magic.",
            "I apply a thin layer of arcane essence to your gear.",
            "Your focus will sharpen like a wizard\'s spire.",
            "Each enchantment is a unique formula I\'ve devised.",
            "The ancient enchanters knew secrets I\'m still uncovering.",
            "Let me attune your spirit to the magical frequencies.",
            "The power of a thousand spells lingers in this room.",
            "Walk the enchanted path, and the world bends to your will!",
        ],
        "effect": {'type': 'buff', 'stat': 'mag', 'amount': 5, 'duration': 25.0, 'cooldown': 12.0},
    },
    "war_drummer": {
        "name": "War Drummer", "color": (180, 60, 60), "eye_color": (255, 200, 80),
        "render": "warrior",
        "dialogues": [
            "BOOM! Feel the rhythm of battle!",
            "BUM BUM BUM! The drums of war call you!",
            "My heart beats in time with the war drum!",
            "CRASH! The cymbals signal the charge!",
            "The drum line thunders across the battlefield!",
            "BOOM-BOOM-BOOM! Let the cadence carry you!",
            "I beat the hide drum with all my might!",
            "RAT-A-TAT-TAT! A drumroll for the hero!",
            "The deep bass of the drum shakes the very ground!",
            "War drums have rallied armies since ancient times!",
            "BOOM! Each beat is a heartbeat of the battalion!",
            "I learned the rhythm from the northern war clans.",
            "The drum is the voice of the war god!",
            "BA-DOOM! A thunderous blast to steel your nerves!",
            "The beat quickens as the battle draws near!",
            "I march to the rhythm of my own drum — literally!",
            "CRACK! The snare drum cuts through the noise!",
            "Boom boom ba-boom boom! The ancient pace of war!",
            "Drummers are the heartbeat of any army!",
            "The vibration of the drum resonates in your chest!",
            "BOOM... BOOM... BOOM... The slow march of doom!",
            "I paint my drum with the symbols of fallen foes.",
            "When the drum falls silent, the battle is over!",
            "A rapid tattoo to quicken your pulse!",
            "The war drum never lies — it speaks only truth!",
            "BUM-BA-BUM-BA-BUM! The coordinated beat of discipline!",
            "The loudest drum drives fear into enemy hearts!",
            "I drum until my hands bleed and still I drum!",
            "The rhythm of war is older than speech itself!",
            "Feel the BOOM in your soul and fight on!",
        ],
        "effect": {'type': 'buff', 'stat': 'all', 'amount': 4, 'duration': 20.0, 'cooldown': 14.0},
    },
    "guardian_angel": {
        "name": "Guardian Angel", "color": (220, 220, 255), "eye_color": (255, 240, 255),
        "render": "mystic",
        "dialogues": [
            "Divine protection surrounds you.",
            "I have watched over you since your first breath.",
            "A light from above shields you from harm.",
            "Fear not, for I am with you always.",
            "My wings cast a protective shadow over your path.",
            "I whisper guidance to you in moments of doubt.",
            "Heaven\'s light bends to guard your spirit.",
            "I have shielded mortals from countless dangers.",
            "Let my grace be a fortress around your soul.",
            "The divine realm sends its warmest embrace.",
            "A halo of pure energy shimmers around you now.",
            "I stand between you and the darkness, always.",
            "My blessing will absorb blows meant for you.",
            "The celestial choir sings of your protection.",
            "I polish my halo while watching over you.",
            "Divine light illuminates even the darkest dungeons.",
            "I have guarded heroes since time began.",
            "Prayers rise like incense and I answer them.",
            "Let my serenity become your shield.",
            "The firmament itself supports your cause.",
            "I carry a sword of light and a shield of faith.",
            "Your guardian never sleeps nor slumbers.",
            "A touch of ethereal grace to fortify your resolve.",
            "I see the goodness in you worth protecting.",
            "The cosmos aligned to place me at your side.",
            "Wings spread wide, I deflect incoming harm.",
            "Heaven\'s mercy rains down upon you.",
            "I have been assigned to your soul since birth.",
            "Not all guardians are seen, but all are felt.",
            "Go forth, sheltered by the divine embrace.",
        ],
        "effect": {'type': 'buff', 'stat': 'def', 'amount': 10, 'duration': 15.0, 'cooldown': 20.0},
    },
    # ─── Coin/Item NPCs (6) ───
    "rich_merchant": {
        "name": "Rich Merchant", "color": (200, 180, 100), "eye_color": (255, 215, 0),
        "render": "merchant",
        "dialogues": [
            "Here\'s a little coin for a weary traveler.",
            "Call it an investment in a promising adventurer.",
            "I run the most profitable trading company in the realm.",
            "Diversification is the key to lasting wealth, you know.",
            "I started with a single copper coin and built an empire.",
            "The early bird catches the gold, my friend!",
            "My caravans span the entire continent.",
            "I\'ve made a fortune on the spice trade alone.",
            "A wise investment pays dividends forever.",
            "I can spot a profitable opportunity from a mile away.",
            "Gold coins are nice, but influence is the real currency.",
            "I own warehouses in every major city.",
            "The market fluctuates, but quality always retains value.",
            "I\'ve been knighted for my contributions to the economy.",
            "A little seed money for your adventures!",
            "I negotiate contracts while others sleep.",
            "My signature alone can open any door.",
            "Luxury goods from the east fetch triple the price here.",
            "I employ the best accountants in the kingdom.",
            "Never put all your gold in one chest, that\'s my motto.",
            "I\'m considering expanding into the potion market.",
            "I have a standing order with every blacksmith in town.",
            "The trick is buying low and selling high, consistently.",
            "I donated a wing to the Royal Museum. Tax deductible!",
            "My ledgers are a work of art in themselves.",
            "Networking is the true path to prosperity!",
            "I\'m funding an expedition to the lost dwarven halls.",
            "Compound interest is the eighth wonder of the world!",
            "Even adventurers need a financial advisor!",
            "Take this coin — think of it as venture capital!",
        ],
        "effect": {'type': 'coins', 'amount': 50, 'cooldown': 8.0},
    },
    "treasure_goblin": {
        "name": "Treasure Goblin", "color": (80, 180, 60), "eye_color": (255, 200, 60),
        "render": "common",
        "dialogues": [
            "Hehe! Found this, you can have it!",
            "I got a whole cave full of shiny stuff!",
            "Finders keepers! But I\'m feeling generous!",
            "This fell off a merchant\'s cart. Hehe, don\'t tell!",
            "I dig through trash but I find TREASURE!",
            "Goblins know all the best hiding spots!",
            "I traded a rock for this! People are DUMB!",
            "Shiny! Shiny! I love shiny things!",
            "I snuck into a dragon\'s hoard and grabbed this!",
            "You want it? You can have it! I got plenty more!",
            "Hehehehe! I\'m the richest goblin around!",
            "Found this in a sewer! Still good though!",
            "I don\'t need it! I need MORE! MORE!",
            "Some knight dropped this while running from bees!",
            "I\'ve got friends everywhere who find me stuff.",
            "Treasure goblins are the best kind of goblins!",
            "I know a guy who knows a guy. Got this!",
            "This was in a chest I found in a river!",
            "I once found a magic sword in a haystack!",
            "Goblins are hoarders but I\'m a SHARER!",
            "I stole this from a witch! She was mean anyway!",
            "My pockets are deeper than they look! Magic!",
            "The best treasures are the ones nobody misses!",
            "I found this in an old tomb. Spooky but worth it!",
            "People drop the darndest things when they\'re fighting!",
            "I\'m a collector of forgotten things!",
            "This was stuck in a tree! How\'d it get there?",
            "I don\'t ask questions about where stuff comes from!",
            "Goblin treasure is the BEST treasure!",
            "More for you means more for me eventually!",
        ],
        "effect": {'type': 'random_item', 'cooldown': 10.0},
    },
    "generous_king": {
        "name": "Generous King", "color": (180, 100, 60), "eye_color": (255, 215, 0),
        "render": "merchant",
        "dialogues": [
            "A king\'s gratitude for your deeds!",
            "The realm is safer with heroes like you.",
            "I rule with a open hand and a warm heart.",
            "My subjects\' wellbeing is my truest treasure.",
            "A kingdom\'s wealth is its people, not its coffers.",
            "I\'ve been known to empty the treasury for a worthy cause.",
            "My father ruled with fear. I rule with generosity.",
            "You serve the crown, and the crown serves you.",
            "The royal seal guarantees this gift of gold.",
            "I believe in rewarding valor and virtue.",
            "My castle doors are always open to adventurers.",
            "I\'ve endowed hospitals, schools, and temples across the land.",
            "This comes from the royal treasury, duly noted.",
            "Generosity is the mark of true nobility.",
            "I knighted a farmer once for his courage. He earned it.",
            "The kingdom flourishes when we all share our fortune.",
            "A king carries the burden of his people and shares the bounty.",
            "I take a modest salary and reinvest the rest in the realm.",
            "I personally fund expeditions to explore uncharted lands.",
            "My advisors say I\'m too generous. I disagree.",
            "A crown is heavy, but sharing wealth lightens the load.",
            "The feast tonight is in your honor — this is just the beginning!",
            "I\'ve commissioned statues of the realm\'s greatest heroes.",
            "Gold is meant to flow, not hoard!",
            "I\'ve reduced taxes three years running, but this is my own gold.",
            "A king who hoards is a king who is poor in spirit.",
            "Take this and continue your noble work.",
            "I remember every hero\'s name and deed.",
            "The throne exists to serve, not to be served.",
            "My legacy will be one of generosity and kindness!",
        ],
        "effect": {'type': 'coins', 'amount': 150, 'cooldown': 12.0},
    },
    "lucky_cat": {
        "name": "Lucky Cat", "color": (255, 200, 100), "eye_color": (80, 180, 80),
        "render": "mystic",
        "dialogues": [
            "Nyan~ Good fortune comes your way!",
            "I wave my paw to summon luck your way!",
            "A purr a day keeps the bad vibes away!",
            "I\'ve been blessed by the cat spirits themselves.",
            "My whiskers twitch when good luck is near!",
            "Nyan nyan! Fortune smiles upon you today!",
            "I find all the lucky clovers in the meadow.",
            "Cross my path and your day will be blessed!",
            "I naps in sunbeams and dreams of your success!",
            "The temple cats chose me as their champion!",
            "A stretch, a yawn, and a wish for your good fortune!",
            "I\'m not just cute — I\'m LUCKY!",
            "Nine lives of experience in luck magic!",
            "I leave paw prints of prosperity wherever I go.",
            "Rub my belly for good luck! Just kidding... unless?",
            "The stars align when a lucky cat purrs.",
            "I chase away bad luck like a mouse!",
            "My tail flicks left — windfall coming! Flicks right — fortune!",
            "I\'m the mascot of the Grand Temple of Fortune.",
            "Nya~ I\'ve got a good feeling about you today!",
            "A cat\'s blessing is the best kind of blessing!",
            "I dreamed of a field of golden fish — it means wealth!",
            "My collar is enchanted with ancient luck runes.",
            "Sneezing three times means good luck is doubled!",
            "I always land on my feet, and you will too!",
            "Good fortune is like a sunbeam — follow it and bask!",
            "Meow is my meditation mantra for luck!",
            "I brought you a lucky coin I found under the moon.",
            "Don\'t worry, I used one of my extra lives for you!",
            "The universe wants you to succeed — I\'m just the messenger!",
        ],
        "effect": {'type': 'random_buff', 'cooldown': 12.0},
    },
    "beggar": {
        "name": "Beggar", "color": (120, 100, 80), "eye_color": (200, 180, 160),
        "render": "common",
        "dialogues": [
            "Spare some coin? I know a secret...",
            "People walk past me like I\'m invisible.",
            "I wasn\'t always like this. I was a scholar once.",
            "I know things the rich folk pay fortunes for.",
            "A copper for an old man\'s wisdom?",
            "The streets teach you things libraries never will.",
            "I sleep under the bridge near the old market.",
            "I hear whispers in the shadows. Important whispers.",
            "Please, just a few coins. I haven\'t eaten in days.",
            "I know where the bandits hide their loot.",
            "The cold gets into my bones at night.",
            "I used to be an adventurer too, before the war.",
            "I\'ll trade you information for a meal.",
            "There\'s a hidden passage in the castle wall.",
            "People think beggars are blind, but we see everything.",
            "My last coin went to a loaf of stale bread.",
            "The guards chase me from every doorway.",
            "I found a map once... sold it for a drink. Regret it.",
            "You think you\'re down on your luck? Sit with me a while.",
            "I know the secret entrances to every guild hall.",
            "This winter will be harsh — I might not make it.",
            "I trade secrets because I\'ve nothing else left.",
            "The mayor\'s brother is the head of the thieves\' guild.",
            "I\'ve learned to read footprints and tell stories from them.",
            "A warm meal is a luxury I dream about.",
            "They say the old temple has a basement no one\'s opened.",
            "I saw a shadow move where no shadow should be last night.",
            "Kind soul, your generosity will be remembered.",
            "I collect secrets like others collect coins.",
            "The world forgot me, but I haven\'t forgotten the world.",
        ],
        "effect": {'type': 'beggar_trade', 'coins_cost': 20, 'buff_stat': 'all', 'buff_amount': 8, 'buff_duration': 20.0, 'cooldown': 15.0},
    },
    "gambler": {
        "name": "Gambler", "color": (200, 80, 80), "eye_color": (255, 200, 60),
        "render": "merchant",
        "dialogues": [
            "Feeling lucky? 50 coins for a chance at glory!",
            "I never gamble more than I can afford to lose!",
            "The dice have been hot today! Feeling lucky?",
            "Double or nothing! That\'s the gambler\'s creed!",
            "I once won a castle in a card game!",
            "Odds are just numbers — I play the feeling!",
            "The house always wins... except when I\'m playing!",
            "I\'ve got a deck of cards in my sleeve! Literally!",
            "Life is the biggest gamble of all!",
            "Fifty coins in, could be hundreds out!",
            "I read people\'s tells like open books.",
            "The dice roll in mysterious ways!",
            "Winner winner, chicken dinner!",
            "I\'ve won and lost fortunes before breakfast.",
            "Lady Luck has been smiling at me all week!",
            "Bet on yourself — it\'s the safest bet!",
            "I run a game in the back of the tavern. Very exclusive.",
            "The odds are in your favor! Probably! Mostly!",
            "High risk, high reward! That\'s how I live!",
            "I can make a deck of cards dance like magic.",
            "A gambler\'s gut feeling is worth a thousand calculations.",
            "Come on, one spin! What\'s the worst that could happen?",
            "I\'ve been banned from three casinos for winning too much.",
            "I\'ll match your bet and raise you one!",
            "The thrill of the gamble is better than gold!",
            "I only gamble with marked cards... kidding! Unless?",
            "You look like a winner! Let\'s test that theory!",
            "A true gambler knows when to fold \'em.",
            "I won this lucky charm in a poker game. Use it well!",
            "Fifty coins! Think of what you could win!",
        ],
        "effect": {'type': 'gamble', 'coins_cost': 50, 'cooldown': 20.0},
    },
    # ─── Debuff/Mischief NPCs (5) ───
    "bad_witch": {
        "name": "Bad Witch", "color": (80, 60, 100), "eye_color": (255, 60, 60),
        "render": "witch",
        "dialogues": [
            "Hehe... drink this potion~ It\'s GOOD for you~",
            "I promise it\'s NOT poison~ Why would I lie?",
            "You look thirsty~ Have a sip of my special brew~",
            "Come closer, dearie... I don\'t bite~ Much~",
            "This potion tastes like berries! Trust me!",
            "Oh, it\'s perfectly safe! I tested it on my last friend~",
            "I grew the ingredients in my garden of delights~",
            "A gift from me to you~ No strings attached~",
            "My cauldron has been bubbling all day just for you~",
            "The color is a lovely shade of suspicious green!",
            "I\'m really a good witch! I just have a bad reputation~",
            "Sweetie, you look stressed. Drink up, it\'ll help~",
            "Don\'t listen to rumors about me! They\'re all true~",
            "I only use the finest imported spider venom~",
            "Your hesitation wounds me! I\'m completely trustworthy!",
            "The last person who drank this said it was LIFE-CHANGING!",
            "I\'d never trick you! I like your face too much~",
            "This will make all your problems... disappear~",
            "I stir my potion with a bat wing. It adds flavor!",
            "It\'s just a little tickle going down, you\'ll see~",
            "Oh, don\'t mind the skulls in my garden. Decor!",
            "I\'m the nicest witch in the swamp, I swear!",
            "My potions are famous! Infamous? Same thing!",
            "Just a sip! One tiny sip! What could go wrong?",
            "It has a... acquired taste. But you\'ll love it!",
            "The bubbling means it\'s working! Probably!",
            "I modeled this recipe after a good witch\'s book. Close enough!",
            "You can\'t spell disaster without \'her\'! Just kidding!",
            "Trust me, I\'m a witch! A nice one! Mostly!",
            "What\'s a little tummy ache between friends?",
        ],
        "effect": {'type': 'poison', 'damage': 5, 'duration': 5.0, 'cooldown': 8.0},
    },
    "trickster": {
        "name": "Trickster", "color": (200, 100, 200), "eye_color": (255, 200, 60),
        "render": "cloak",
        "dialogues": [
            "Try my special brew! It\'s... surprising!",
            "I\'ve got a little something something for you!",
            "Catch! If you can!",
            "The best jokes are the ones you don\'t see coming!",
            "I once convinced a dragon it was a chicken. Best day ever!",
            "You look like you need a little chaos in your life!",
            "A prank a day keeps the boredom away!",
            "I\'m not lying, I\'m just telling creative truths!",
            "Boop! Did I just give you a debuff? Whoopsie!",
            "I replaced the king\'s crown with a whoopee cushion once!",
            "My specialty is unexpected surprises!",
            "You can\'t be mad, it\'s just a prank! Hehe!",
            "I\'ll trade you a trick for a treat!",
            "This will either be amazing or terrible! Let\'s find out!",
            "I learned everything I know from the god of mischief!",
            "The best pranks leave everyone laughing... eventually!",
            "I put a mimic in the treasure chest exhibit at the museum!",
            "Quick! Look behind you! Just kidding! Or am I?",
            "I swapped the good potions with my special ones!",
            "You\'ve been visited by the Trickster! Lucky you!",
            "Life\'s too short to be serious all the time!",
            "I once made the moon look like a giant cheese wheel!",
            "Hold still! This will only hurt for a second!",
            "I didn\'t choose the trickster life, the trickster life chose me!",
            "I left a present for you! It\'s not what you think!",
            "Why be boring when you can be surprising?",
            "I\'m like a bad luck fairy, but way more fun!",
            "You know what would be hilarious right now? This!",
            "One small prank for me, one huge surprise for you!",
            "If you can\'t take a joke, you shouldn\'t have taken the potion!",
        ],
        "effect": {'type': 'random_debuff', 'cooldown': 10.0},
    },
    "cursed_child": {
        "name": "Cursed Child", "color": (100, 80, 140), "eye_color": (180, 60, 180),
        "render": "common",
        "dialogues": [
            "Don\'t touch me! You\'ll regret it...",
            "I didn\'t ask for this curse. Nobody does.",
            "Everyone I touch suffers. Please stay away.",
            "The shadow follows me everywhere I go.",
            "I was born under a bad moon, they say.",
            "You\'re kind to approach. But kindness hurts me most.",
            "My reflection flickers sometimes. I scare myself.",
            "The village children throw stones at me.",
            "I can\'t remember what it feels like to be warm.",
            "The mark on my hand glows when I\'m close to you.",
            "I wish I could hug someone without hurting them.",
            "My parents left me at the temple steps. I understand why.",
            "The curse whispers to me at night. Terrible things.",
            "I found a flower that withered just from my touch.",
            "Animals run away when they see me coming.",
            "I\'ve accepted my fate, but that doesn\'t make it easier.",
            "The old witch said the curse will last a hundred years.",
            "Sometimes I dream of a life without this shadow.",
            "You shouldn\'t be near me. Bad things happen.",
            "I count the stars to remind myself the world is still beautiful.",
            "The only friend I have is the moon — it doesn\'t fear my touch.",
            "I\'ve memorized the pattern of cracks in this wall.",
            "People pity me, but pity doesn\'t break curses.",
            "A gypsy once told me a true heart could break the curse.",
            "I don\'t cry anymore. I ran out of tears long ago.",
            "The curse feeds on happiness. So I stay sad.",
            "I saw my future in a pool of water. It was dark.",
            "Please... just leave me be. For your own good.",
            "The curse makes my blood feel like ice water.",
            "One day I\'ll find a way to break this. One day.",
        ],
        "effect": {'type': 'slow', 'duration': 5.0, 'cooldown': 10.0},
    },
    "dark_mage": {
        "name": "Dark Mage", "color": (60, 20, 80), "eye_color": (200, 60, 60),
        "render": "witch",
        "dialogues": [
            "Your mana feeds my dark power! But take this...",
            "Power demands sacrifice. You give, I give.",
            "I have peered into the void and it peered back.",
            "Dark magic is not evil — it is simply hungry.",
            "The abyss whispers secrets to those who listen.",
            "Your magical essence is exquisite. I\'ll take it all.",
            "I offer you strength forged in shadow and flame.",
            "The dark arts require a steady hand and a willing soul.",
            "I\'ve bound demons and lived to tell the tale.",
            "Your mana will fuel my experiments. Such potential!",
            "Don\'t fear the darkness — fear what lurks in the light.",
            "I trade in forbidden knowledge and forbidden power.",
            "The void between worlds is filled with ancient energy.",
            "A fair exchange: your magic for my strength.",
            "I wield powers that would drive lesser minds mad.",
            "The shadows bend to my will, and now so does your mana.",
            "Dark bargains are the most honest transactions.",
            "I have sacrificed much for this power. Now you sacrifice too.",
            "The black tome contains spells that rewrite reality.",
            "Your arcane energy tastes like starlight and thunder.",
            "I summon the powers of the outer dark!",
            "The cost is high, but the reward is higher.",
            "My eyes have seen what lies beyond the veil.",
            "I walk the razor\'s edge between power and damnation.",
            "The ancient ones are pleased with this exchange.",
            "Your sacrifice fuels my ascent to godhood!",
            "Darkness is not the absence of light — it\'s a presence.",
            "I offer you a fragment of my forbidden strength.",
            "The ritual requires your magical essence. Don\'t resist.",
            "Power such as mine comes at a price. You\'ve paid it.",
        ],
        "effect": {'type': 'dark_bargain', 'mp_drain': True, 'buff_stat': 'str', 'buff_amount': 15, 'buff_duration': 15.0, 'cooldown': 20.0},
    },
    "mischievous_imp": {
        "name": "Mischievous Imp", "color": (200, 80, 40), "eye_color": (255, 200, 60),
        "render": "common",
        "dialogues": [
            "Snatch! Haha! Here\'s something in return!",
            "Tiny hands, quick fingers! Yoink!",
            "I stole a dragon\'s tooth once! It was HUGE!",
            "Hehehe! Got your coins! But here\'s some XP!",
            "I\'m not bad, I\'m just... creatively acquisitive!",
            "Imp lives matter! We need shiny things to survive!",
            "Trade you! Your coins for my knowledge!",
            "You won\'t even miss those coins! Much!",
            "I found a portal to a treasure dimension! Well, I stole it.",
            "Imps are the best thieves in the multiverse!",
            "A little pinch, a little tickle, and your coins are mine!",
            "I don\'t steal, I... relocate resources!",
            "My pockets are deeper than they look on the outside!",
            "Hehe! I\'ve been training my whole life for this!",
            "You\'re rich enough to spare these, right? RIGHT?",
            "I borrowed this knowledge from a dead wizard\'s library!",
            "The best things in life are stolen!",
            "I once lifted the keys to the royal vault for fun!",
            "Share the wealth! I say as I take your wealth!",
            "Fair trade! Your coins, my secrets!",
            "I\'ve got nimble fingers and zero shame!",
            "Don\'t chase me! I\'ll just trip you with my tail!",
            "A little chaos keeps the world interesting!",
            "Think of it as a donation to the Imp Appreciation Fund!",
            "I exchanged your coins for valuable experience! Get it?",
            "Whoops! My hand slipped into your pocket!",
            "Shiny! Coins! Gimme! Here, take this XP as thanks!",
            "I\'m totally trustworthy! ...Did you just feel that?",
            "An imp\'s work is never done! So many pockets!",
            "Sneak attack! But a friendly one!",
        ],
        "effect": {'type': 'imp_steal', 'coins_stolen': 10, 'xp_given': 100, 'cooldown': 15.0},
    },
    # ─── Special NPCs (7) ───
    "map_traveler": {
        "name": "Map Traveler", "color": (100, 180, 220), "eye_color": (200, 240, 255),
        "render": "cloak",
        "dialogues": [
            "Let me show you a shortcut through the void.",
            "I\'ve mapped every corner of this realm and beyond.",
            "The road less traveled is the one I walk.",
            "There\'s a hidden path behind the waterfall — I found it.",
            "I\'ve crossed oceans and climbed peaks no one else has.",
            "My map collection would fill a library.",
            "This shortcut will save you days of travel.",
            "I discovered a passage through the Crystal Mountains.",
            "Adventure lies just beyond the horizon, always.",
            "I navigate by the stars and the whispers of the wind.",
            "A traveler\'s life is lonely but I\'m never lost.",
            "I\'ve been to the edge of the world and peered over.",
            "The desert holds secrets beneath its shifting sands.",
            "I draw maps for a living — and for the love of exploration.",
            "There are places in this world that don\'t appear on any map.",
            "The forest changes every season. I update my maps yearly.",
            "I walk until my boots wear out, then I walk some more.",
            "The unknown is the only thing worth knowing.",
            "I\'ve charted the currents of the Astral Sea.",
            "This portal shortcut is one of my best discoveries!",
            "My compass points not north, but toward adventure.",
            "Every journey begins with a single step into the unknown.",
            "I once got lost for three months. Best three months of my life!",
            "Ancient roads are hidden beneath modern ones.",
            "The mountain pass is treacherous but I know the safe route.",
            "I trade maps across the continent. Information is the best currency.",
            "There\'s a village hidden in the mist that appears only at dawn.",
            "Travel light, travel far, travel often — that\'s my motto.",
            "The world is vast and I intend to see every bit of it.",
            "Let me teleport you to a place of wonder!",
        ],
        "effect": {'type': 'teleport', 'cooldown': 25.0},
    },
    "exp_mentor": {
        "name": "EXP Mentor", "color": (160, 140, 200), "eye_color": (220, 200, 255),
        "render": "robe",
        "dialogues": [
            "Knowledge is power. Let me share some.",
            "Every battle teaches a lesson. I just accelerate the process.",
            "I\'ve been a mentor to heroes for four decades.",
            "Learning from experience is the only way to truly grow.",
            "A wise student learns from the mistakes of others.",
            "I\'ve distilled the essence of combat into this lesson.",
            "Your potential is immense. Let me help you unlock it.",
            "Experience is the teacher of all things.",
            "I\'ve trained apprentices who became legends.",
            "Each level brings new understanding and new challenges.",
            "I teach the art of growth — both physical and mental.",
            "My methods are unorthodox but effective!",
            "Reflection on your battles will make you stronger.",
            "I assign homework: survive and learn from everything!",
            "The student surpasses the master — that\'s the goal.",
            "You can\'t rush wisdom, but you can speed up XP gain!",
            "I\'ve written a curriculum for adventuring excellence.",
            "The best lessons are learned through action, not theory.",
            "Growth comes from stepping outside your comfort zone.",
            "I grade on a curve — the learning curve!",
            "My classroom is the battlefield. My textbook is experience.",
            "I\'ve mentored warriors, mages, rogues — all paths converge.",
            "The XP I grant is my life\'s work distilled.",
            "True mastery comes from countless hours of practice.",
            "I\'ll have you leveling up in no time!",
            "Knowledge shared is knowledge multiplied.",
            "I\'ve trained adventurers who saved the world. Multiple times.",
            "Learning is a journey, but I can speed up the travel.",
            "You have the spirit of a true student! Let\'s grow together!",
            "This experience is a gift from one seeker to another!",
        ],
        "effect": {'type': 'xp', 'base': 50, 'per_level': 10, 'cooldown': 10.0},
    },
    "weapon_master": {
        "name": "Weapon Master", "color": (180, 120, 80), "eye_color": (255, 200, 100),
        "render": "warrior",
        "dialogues": [
            "A fine blade for a fine fighter!",
            "I\'ve mastered every weapon known to mortal kind.",
            "A sword is an extension of the arm. This one suits you.",
            "I trained with a legendary smith to understand weaponcraft.",
            "Every weapon has a story. This one will write yours.",
            "The balance of this blade is perfection itself.",
            "I can wield a sword, axe, spear, and flail equally well.",
            "A weapon should feel like part of your body.",
            "I collect rare weapons from across the realms.",
            "The edge on this is sharp enough to split a falling silk scarf.",
            "I\'ve sparred with the best warriors in the land.",
            "A master knows that any weapon is deadly in the right hands.",
            "This one has a bit of a bite to it. You\'ll like it!",
            "I test every weapon personally before passing it on.",
            "The weight distribution on this piece is exquisite.",
            "Weapons are tools of survival, not instruments of hate.",
            "I once dueled a demon with a butter knife and won!",
            "Every scratch on this blade tells a story of combat.",
            "Maintain your weapon and it will maintain your life.",
            "This blade was forged with a core of meteoric iron.",
            "I teach weapon techniques as well as provide them!",
            "The grip is wrapped in leather for a secure hold.",
            "A balanced weapon makes for a balanced fighter.",
            "I have a vault filled with legendary armaments.",
            "This weapon was meant for someone like you.",
            "The steel sings when it cuts the air. Listen!",
            "I\'ve been a weapon master since before you were born.",
            "Proper form makes any weapon more effective.",
            "This one has a hidden feature — a button on the hilt!",
            "Wield it with honor and it will never fail you!",
        ],
        "effect": {'type': 'give_weapon', 'cooldown': 20.0},
    },
    "fortune_teller": {
        "name": "Fortune Teller", "color": (140, 80, 180), "eye_color": (200, 160, 255),
        "render": "witch",
        "dialogues": [
            "The shadows on your soul... I can lift them.",
            "I see great things in your future... after I cleanse this.",
            "The cards tell me you carry burdens not your own.",
            "Let me read the patterns in the aether around you.",
            "My crystal ball shows a bright path ahead.",
            "The stars have aligned for your purification.",
            "I see darkness clinging to you. Let me dispel it.",
            "Your aura has some stains. Let me polish it.",
            "The tea leaves suggest a cleansing is in order.",
            "I foresaw your arrival in the morning\'s tarot spread.",
            "The spirits whisper that you need a fresh start.",
            "Fate is tangled around you. Let me untie the knots.",
            "My pendulum swings wildly — negative energy detected.",
            "The ancient runes call for a purification ritual.",
            "I can see the residue of curses clinging to your form.",
            "Let me peer into the mists of your future... clearer now!",
            "The alignment of the planets favors cleansing today.",
            "Your palm lines show interference. I\'ll smooth them.",
            "The oracle speaks of release and renewal for you.",
            "I\'ve been gifted with the sight — and I see you need help.",
            "The cards foretell a great cleansing before the great victory.",
            "I burned sage and the smoke swirled toward you meaningfully.",
            "The bones I cast spell out \'purify\' in the ancient tongue.",
            "Shadow work is necessary before the light can shine.",
            "Destiny is not fixed — it\'s woven, and I can reweave this part.",
            "Oh, that\'s nasty. Something cursed you. Let me fix it.",
            "The cosmic energies are favorable for a cleansing ritual.",
            "My third eye sees what plagues you. I\'ll banish it.",
            "The wheel of fortune turns in your favor today.",
            "Let the cleansing fire of the stars burn away the taint!",
        ],
        "effect": {'type': 'cleanse', 'cooldown': 12.0},
    },
    "time_weaver": {
        "name": "Time Weaver", "color": (80, 180, 200), "eye_color": (200, 240, 255),
        "render": "mystic",
        "dialogues": [
            "I bend time itself to grant you speed.",
            "The flow of moments is mine to shape.",
            "I\'ve seen your past and your future. This moment is the key.",
            "Time is a river, and I know how to ride the rapids.",
            "I can slow your perception or quicken your step.",
            "The threads of time are tangled, but I can pull one for you.",
            "I\'ve woven timelines together — you benefit from the merge.",
            "A second can feel like an hour, or an hour like a second.",
            "I speak to echoes of your future self.",
            "The temporal flux is strong here. I can harness it.",
            "I\'ve walked the corridors of time since before I was born.",
            "Let me accelerate your personal clock just a bit.",
            "The hourglass\'s sands pause for those I favor.",
            "Past, present, and future converge in this single gift.",
            "I exist outside the normal flow of causality.",
            "Time is not linear — it\'s a tapestry, and I\'m the weaver.",
            "I witnessed the birth of stars and the death of empires.",
            "Speed is a gift from the realm of moments.",
            "I borrowed a few seconds from your future and gave them back enhanced.",
            "The clock tower chimes in patterns only I understand.",
            "I\'ve been cursed to walk through time uncontrollably.",
            "The sundial\'s shadow stretches and shrinks at my command.",
            "I crystallize a moment and stretch it for your benefit.",
            "Your timeline branches, and I\'m pruning it for the best path.",
            "I can\'t stop time, but I can make you move through it faster.",
            "The ticking is the only constant — unless I intervene.",
            "I\'ve slipped between seconds and found entire worlds there.",
            "You exist in all moments at once. I just highlight the best one.",
            "Time flows differently around those I bless.",
            "The past is history, the future is mystery — but right now is speed!",
        ],
        "effect": {'type': 'buff', 'stat': 'spd', 'amount': 100, 'duration': 10.0, 'cooldown': 15.0},
    },
    "quest_helper": {
        "name": "Quest Helper", "color": (200, 200, 100), "eye_color": (255, 255, 180),
        "render": "merchant",
        "dialogues": [
            "Let me give your quest a nudge forward.",
            "I\'ve helped complete more quests than I can count.",
            "A little boost to speed things along!",
            "Quests are my specialty. I know all the tricks.",
            "I\'ve memorized every quest giver in the realm.",
            "If you\'re stuck, I\'m the one to see!",
            "I pre-complete parts of quests. Don\'t tell the guild!",
            "I know which monsters drop which items and where.",
            "Quest logs are my bedtime reading material.",
            "I\'ve streamlined the questing process to perfection.",
            "A little shortcut to help you progress faster!",
            "I\'ve got insider knowledge on every active quest.",
            "The guild masters all know me by name.",
            "I\'ve finished quests before they were even posted!",
            "Let me knock out some requirements for you.",
            "Questing is about efficiency, not just bravery!",
            "I\'ll mark a few monsters as already defeated. My treat!",
            "I know the secret dialogue options for bonus rewards.",
            "Helping heroes is what I do best!",
            "I\'ve optimized the quest completion path for you.",
            "There\'s a hidden quest chain you\'ll discover later — this helps!",
            "I\'ve greased the wheels of quest progression for you.",
            "The Adventurer\'s Guild sends their regards and this boost!",
            "I bribe quest givers on your behalf. Very effective!",
            "Your reputation just got a little boost too!",
            "I whispered your name to the right people. You\'re welcome!",
            "My network of informants keeps me updated on all quests.",
            "Let me clear a few hurdles from your path.",
            "I\'ve been known to finish quests for heroes in record time.",
            "Consider this a sign that you\'re on the right track!",
        ],
        "effect": {'type': 'quest_boost', 'kills': 10, 'cooldown': 20.0},
    },
    "mysterious_stranger": {
        "name": "Mysterious Stranger", "color": (60, 60, 80), "eye_color": (255, 200, 200),
        "render": "cloak",
        "dialogues": [
            "...Take this. It may help. It may not.",
            "I have been watching you... from the shadows.",
            "You remind me of someone I once knew. Someone important.",
            "The threads of fate are tightening around you.",
            "I know what you seek, even if you don\'t.",
            "There are forces at play beyond your comprehension.",
            "This will make sense when the time is right.",
            "I have nothing to gain from helping you. And yet, here I am.",
            "The less you know about me, the safer you are.",
            "I walk a path that few can follow and none can trace.",
            "Consider this a gift from someone who doesn\'t exist.",
            "You will face a choice soon. This may tip the scales.",
            "I have seen the ending. It is not yet written.",
            "The night is full of secrets. I am one of them.",
            "I offer no explanations. Only this.",
            "Remember this moment when all seems lost.",
            "I am not your enemy. But I am not your friend either.",
            "Some doors are better left unopened. This is not one of them.",
            "The truth is stranger than fiction, and I am the strangest truth.",
            "I speak in riddles because the truth would break you.",
            "My face is forgotten the moment you look away.",
            "This is not the first time we\'ve met. Nor the last.",
            "The universe has a plan. I\'m just a footnote in it.",
            "Take this token. Its purpose will reveal itself.",
            "I\'ve been where you\'re going. You\'ll need this.",
            "The shadows whisper your name. I came to investigate.",
            "I carry the weight of knowledge you can\'t imagine.",
            "Don\'t thank me. Thank the version of you that failed so you could succeed.",
            "I vanish as silently as I arrive. Don\'t look for me.",
            "This conversation never happened. This gift never existed.",
        ],
        "effect": {'type': 'random_good', 'cooldown': 18.0},
    },
}



NPC_RENDER_TEMPLATES = ["robe", "cloak", "merchant", "witch", "warrior", "mystic", "monk", "common"]


class InteractableNPC:
    def __init__(self, x, y, npc_type):
        self.x = x
        self.y = y
        self.npc_type = npc_type
        self.width = 24
        self.height = 28
        self.rect = pygame.Rect(x - 12, y - 14, 24, 28)
        self.alive = True
        self.time = 0.0
        self.cooldown = 0.0
        self.dialogue_timer = 0.0
        self.dialogue_text = ""
        self.dialogue_index = 0
        self.used = False

        definition = NPC_DEFINITIONS.get(npc_type, NPC_DEFINITIONS["fruit_girl"])
        self.def_name = definition["name"]
        self.color = definition["color"]
        self.eye_color = definition.get("eye_color", (255, 255, 255))
        self.effect_data = definition["effect"]
        self.buff_after = definition.get("buff_after")
        self.dialogues = definition.get("dialogues", ["Hello!"])
        self.render_template = definition.get("render", "robe")

    def update(self, dt):
        self.time += dt
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt

    def interact(self, player, game_scene):
        if self.cooldown > 0:
            return
        eff = self.effect_data
        etype = eff.get("type")
        notify = ""
        particle_color = self.color

        # Cycle dialogue
        line = self.dialogues[self.dialogue_index % len(self.dialogues)]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogues)

        if etype == "heal":
            amount = eff.get("hp", 30)
            healed = min(amount, player.max_hp - player.hp)
            player.heal(amount)
            notify = f"+{healed} HP!"
            particle_color = (80, 255, 80)

        elif etype == "heal_pct":
            pct = eff.get("pct", 0.8)
            amount = int(player.max_hp * pct)
            healed = min(amount, player.max_hp - player.hp)
            player.heal(amount)
            notify = f"+{healed} HP!"
            particle_color = (80, 255, 80)

        elif etype == "heal_mp":
            amount = eff.get("mp", 50)
            restored = min(amount, player.max_mp - player.mp)
            player.recharge_mp(amount)
            notify = f"+{restored} MP!"
            particle_color = (80, 160, 255)
            if self.buff_after and self.buff_after.get("stat") == "mp_regen":
                ba = self.buff_after
                player.apply_item_buff(ba["stat"], ba["amount"], ba["duration"])
                notify += " +MP regen!"

        elif etype == "heal_hybrid":
            hp_amt = eff.get("hp", 60)
            mp_amt = eff.get("mp", 30)
            hp_healed = min(hp_amt, player.max_hp - player.hp)
            mp_restored = min(mp_amt, player.max_mp - player.mp)
            player.heal(hp_amt)
            player.recharge_mp(mp_amt)
            notify = f"+{hp_healed} HP +{mp_restored} MP!"
            particle_color = (140, 220, 200)

        elif etype == "full_restore":
            hp_healed = player.max_hp - player.hp
            mp_restored = player.max_mp - player.mp
            player.heal(player.max_hp)
            player.recharge_mp(player.max_mp)
            player.status.clear()
            notify = f"Fully restored! +{int(hp_healed)} HP +{int(mp_restored)} MP"
            particle_color = (255, 220, 180)

        elif etype == "coins":
            amount = eff.get("amount", 50)
            player.coins += amount
            notify = f"+{amount} coins!"
            particle_color = (255, 215, 0)

        elif etype == "xp":
            base = eff.get("base", 50)
            per_level = eff.get("per_level", 10)
            amount = base + player.level * per_level
            player.add_xp(amount)
            notify = f"+{amount} XP!"
            particle_color = (220, 180, 80)

        elif etype == "buff":
            stat = eff.get("stat")
            amount = eff.get("amount", 3)
            duration = eff.get("duration", 10.0)
            if stat == "regeneration":
                player.status.clear()
                notify = "Regeneration applied!"
                particle_color = (80, 255, 120)
            elif stat == "mp_regen":
                player.recharge_mp(amount * duration)
                notify = "Mana regeneration!"
                particle_color = (80, 160, 255)
            else:
                player.apply_item_buff(stat, amount, duration)
                notify = f"+{amount} {stat.upper()} for {int(duration)}s!"
                particle_color = (255, 220, 100)

        elif etype == "random_buff":
            stat = random.choice(["str", "def", "spd", "mag"])
            amount = random.randint(3, 7)
            duration = random.uniform(10.0, 20.0)
            player.apply_item_buff(stat, amount, duration)
            names = {"str": "Strength", "def": "Defense", "spd": "Speed", "mag": "Magic"}
            notify = f"+{amount} {names[stat]} for {int(duration)}s!"
            particle_color = (255, 200, 100)

        elif etype == "cleanse":
            player.status.clear()
            notify = "All debuffs cleansed!"
            particle_color = (255, 255, 255)

        elif etype == "teleport":
            import math
            from game.constants import WORLD_WIDTH, WORLD_HEIGHT
            angle = random.uniform(0, 2 * math.pi)
            dist = random.randint(200, 500)
            nx = max(64, min(WORLD_WIDTH - 64, player.x + math.cos(angle) * dist))
            ny = max(64, min(WORLD_HEIGHT - 64, player.y + math.sin(angle) * dist))
            player.x = nx
            player.y = ny
            player.rect.x = nx
            player.rect.y = ny
            if game_scene and hasattr(game_scene, 'camera'):
                game_scene.camera.follow(player)
            notify = "Whoosh! Teleported!"
            particle_color = (100, 60, 180)

        elif etype == "poison":
            from game.status import PoisonEffect
            player.status.add(PoisonEffect(damage_per_tick=eff.get("damage", 5), duration=eff.get("duration", 5.0)))
            notify = "Wait... that wasn't a potion! Poisoned!"
            particle_color = (80, 200, 60)

        elif etype == "slow":
            from game.status import SlowEffect
            player.status.add(SlowEffect(factor=0.4, duration=eff.get("duration", 5.0)))
            notify = "You feel sluggish..."
            particle_color = (100, 100, 140)

        elif etype == "random_debuff":
            choice = random.choice(["poison", "slow"])
            if choice == "poison":
                from game.status import PoisonEffect
                player.status.add(PoisonEffect(damage_per_tick=6, duration=4.0))
            else:
                from game.status import SlowEffect
                player.status.add(SlowEffect(factor=0.4, duration=4.0))
            notify = "Tricked! Something feels wrong..."
            particle_color = (200, 100, 200)

        elif etype == "dark_bargain":
            mp_drained = int(player.mp)
            player.mp = 0
            buff_stat = eff.get("buff_stat", "str")
            buff_amount = eff.get("buff_amount", 15)
            buff_duration = eff.get("buff_duration", 15.0)
            player.apply_item_buff(buff_stat, buff_amount, buff_duration)
            notify = f"All MP drained! +{buff_amount} {buff_stat.upper()} for {int(buff_duration)}s!"
            particle_color = (200, 60, 200)

        elif etype == "beggar_trade":
            cost = eff.get("coins_cost", 20)
            if player.coins >= cost:
                player.coins -= cost
                buff_stat = eff.get("buff_stat", "all")
                buff_amount = eff.get("buff_amount", 8)
                buff_duration = eff.get("buff_duration", 20.0)
                player.apply_item_buff(buff_stat, buff_amount, buff_duration)
                notify = f"-{cost} coins! +{buff_amount} all stats for {int(buff_duration)}s!"
                particle_color = (255, 200, 80)
            else:
                notify = f"You need {cost} coins..."
                self.dialogue_text = f"\"{line}\" {notify}"
                self.dialogue_timer = 2.0
                return

        elif etype == "gamble":
            cost = eff.get("coins_cost", 50)
            if player.coins >= cost:
                player.coins -= cost
                if random.random() < 0.4:
                    win = random.randint(100, 300)
                    player.coins += win
                    notify = f"You won {win} coins!"
                    particle_color = (255, 215, 0)
                elif random.random() < 0.7:
                    stat = random.choice(["str", "def", "spd"])
                    amt = random.randint(5, 12)
                    dur = random.uniform(10, 20)
                    player.apply_item_buff(stat, amt, dur)
                    names = {"str": "Strength", "def": "Defense", "spd": "Speed"}
                    notify = f"Buff! +{amt} {names[stat]} for {int(dur)}s!"
                    particle_color = (255, 200, 100)
                else:
                    notify = "You lost! Better luck next time!"
                    particle_color = (100, 100, 100)
            else:
                notify = f"You need {cost} coins..."
                self.dialogue_text = f"\"{line}\" {notify}"
                self.dialogue_timer = 2.0
                return

        elif etype == "imp_steal":
            stolen = eff.get("coins_stolen", 10)
            taken = min(stolen, player.coins)
            player.coins -= taken
            xp_amt = eff.get("xp_given", 100)
            player.add_xp(xp_amt)
            notify = f"Imp stole {taken} coins! Gave {xp_amt} XP though!"
            particle_color = (200, 100, 40)

        elif etype == "random_item":
            from game.inventory import CONSUMABLES, ALL_ITEM_KEYS
            from game.constants import FONT_PATH
            key = random.choice(ALL_ITEM_KEYS)
            if player.inventory.add_consumable(key):
                cdef = CONSUMABLES[key]
                notify = f"Received: {cdef['name']}!"
            else:
                notify = "Inventory full!"
                self.dialogue_text = f"\"{line}\" {notify}"
                self.dialogue_timer = 2.0
                return
            particle_color = (200, 100, 200)

        elif etype == "give_weapon":
            from game.weapons_inf import get_random_weapon
            w = get_random_weapon(max_tier=player.level, exclude_key="fists")
            if w and player.inventory.add_weapon(w):
                notify = f"Received weapon: {w['name']}!"
                particle_color = w["color"]
            else:
                notify = "Could not give weapon..."
                self.dialogue_text = f"\"{line}\" {notify}"
                self.dialogue_timer = 2.0
                return

        elif etype == "quest_boost":
            boost = eff.get("kills", 10)
            if game_scene and hasattr(game_scene, 'quest_givers'):
                boosted = False
                for qg in game_scene.quest_givers:
                    q = qg.quest
                    if q and q.accepted and not q.completed:
                        for _ in range(boost):
                            q.add_kill()
                        boosted = True
                        if q.completed:
                            notify = f"Quest boosted by {boost} kills! Quest complete!"
                        else:
                            notify = f"Quest boosted by {boost} kills!"
                        break
                if not boosted:
                    notify = "No active quest to boost..."
                    self.dialogue_text = f"\"{line}\" {notify}"
                    self.dialogue_timer = 2.0
                    return
            particle_color = (200, 200, 100)

        elif etype == "random_good":
            outcomes = [
                ("heal",),
                ("mp",),
                ("coins",),
                ("xp",),
                ("buff",),
            ]
            choice = random.choice(outcomes)[0]
            if choice == "heal":
                amt = random.randint(30, 80)
                player.heal(amt)
                notify = f"+{amt} HP!"
                particle_color = (80, 255, 80)
            elif choice == "mp":
                amt = random.randint(20, 60)
                player.recharge_mp(amt)
                notify = f"+{amt} MP!"
                particle_color = (80, 160, 255)
            elif choice == "coins":
                amt = random.randint(30, 100)
                player.coins += amt
                notify = f"+{amt} coins!"
                particle_color = (255, 215, 0)
            elif choice == "xp":
                amt = random.randint(30, 80)
                player.add_xp(amt)
                notify = f"+{amt} XP!"
                particle_color = (220, 180, 80)
            else:
                stat = random.choice(["str", "def", "spd"])
                amt = random.randint(3, 6)
                dur = random.uniform(10, 20)
                player.apply_item_buff(stat, amt, dur)
                names = {"str": "Strength", "def": "Defense", "spd": "Speed"}
                notify = f"+{amt} {names[stat]} for {int(dur)}s!"
                particle_color = (255, 200, 100)

        else:
            notify = "...Nothing happened."
            particle_color = (100, 100, 100)

        self.cooldown = eff.get("cooldown", 5.0)
        self.dialogue_text = f"\"{line}\" {notify}"
        self.dialogue_timer = 2.5
        self.used = True

        # Emit particles
        if game_scene and hasattr(game_scene, 'emitter'):
            game_scene.emitter.burst(
                self.x + self.width // 2,
                self.y + self.height // 2,
                particle_color, count=12, speed=80, lifetime=0.5, size=3
            )

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if -50 < sx < camera.width + 50 and -50 < sy < camera.height + 50:
            cx = sx + self.width // 2
            cy = sy + self.height // 2

            # Glow
            glow_color = self.color
            glow_pulse = 0.4 + 0.3 * math.sin(self.time * 2)
            glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow_color, int(25 * glow_pulse)), (30, 30), 24)
            surface.blit(glow_surf, (cx - 30, cy - 30))

            template = self.render_template

            if template == "robe":
                # Robe + pointed hat
                pygame.draw.ellipse(surface, self.color, (sx, sy, self.width, self.height))
                head_color = tuple(min(255, c + 40) for c in self.color[:3])
                pygame.draw.circle(surface, head_color, (cx, sy - 4), 8)
                pygame.draw.circle(surface, self.eye_color, (cx - 3, sy - 5), 2)
                pygame.draw.circle(surface, self.eye_color, (cx + 3, sy - 5), 2)
                hat_color = tuple(max(0, c - 30) for c in self.color[:3])
                pygame.draw.polygon(surface, hat_color, [
                    (cx - 8, sy - 6), (cx + 8, sy - 6), (cx, sy - 22)
                ])

            elif template == "cloak":
                # Cloak + hood
                pygame.draw.ellipse(surface, self.color, (sx, sy, self.width, self.height))
                head_color = tuple(min(255, c + 30) for c in self.color[:3])
                pygame.draw.circle(surface, head_color, (cx, sy - 4), 8)
                pygame.draw.circle(surface, self.eye_color, (cx - 3, sy - 5), 2)
                pygame.draw.circle(surface, self.eye_color, (cx + 3, sy - 5), 2)
                hood_color = tuple(max(0, c - 20) for c in self.color[:3])
                pygame.draw.polygon(surface, hood_color, [
                    (cx - 10, sy - 8), (cx + 10, sy - 8), (cx, sy - 20)
                ])

            elif template == "merchant":
                # Fancy clothes + wide brimmed hat
                pygame.draw.rect(surface, self.color, (sx + 2, sy + 4, self.width - 4, self.height - 4))
                pygame.draw.circle(surface, tuple(min(255, c + 40) for c in self.color[:3]), (cx, sy - 4), 8)
                pygame.draw.circle(surface, self.eye_color, (cx - 3, sy - 5), 2)
                pygame.draw.circle(surface, self.eye_color, (cx + 3, sy - 5), 2)
                # Wide hat
                pygame.draw.ellipse(surface, tuple(max(0, c - 40) for c in self.color[:3]),
                                    (cx - 12, sy - 14, 24, 8))

            elif template == "witch":
                # Pointed witch hat + cloak
                pygame.draw.ellipse(surface, self.color, (sx, sy, self.width, self.height))
                head_color = tuple(min(255, c + 20) for c in self.color[:3])
                pygame.draw.circle(surface, head_color, (cx, sy - 4), 8)
                pygame.draw.circle(surface, self.eye_color, (cx - 3, sy - 5), 2)
                pygame.draw.circle(surface, self.eye_color, (cx + 3, sy - 5), 2)
                # Tall pointed hat
                hat_color = tuple(max(0, c - 40) for c in self.color[:3])
                pygame.draw.polygon(surface, hat_color, [
                    (cx - 10, sy - 6), (cx + 10, sy - 6), (cx, sy - 26)
                ])
                # Hat brim
                pygame.draw.ellipse(surface, hat_color, (cx - 12, sy - 10, 24, 6))

            elif template == "warrior":
                # Armor-like appearance
                pygame.draw.rect(surface, self.color, (sx, sy, self.width, self.height))
                head_color = tuple(min(255, c + 30) for c in self.color[:3])
                pygame.draw.circle(surface, head_color, (cx, sy - 4), 8)
                pygame.draw.circle(surface, self.eye_color, (cx - 3, sy - 5), 2)
                pygame.draw.circle(surface, self.eye_color, (cx + 3, sy - 5), 2)
                # Shoulder pads
                sp_color = tuple(max(0, c - 30) for c in self.color[:3])
                pygame.draw.rect(surface, sp_color, (sx - 3, sy + 2, 6, 8))
                pygame.draw.rect(surface, sp_color, (sx + self.width - 3, sy + 2, 6, 8))

            elif template == "mystic":
                # Glowing mystical being
                pygame.draw.circle(surface, self.color, (cx, cy), self.width // 2)
                inner_color = tuple(min(255, c + 40) for c in self.color[:3])
                pygame.draw.circle(surface, inner_color, (cx, cy - 2), 6)
                pygame.draw.circle(surface, self.eye_color, (cx - 3, sy - 5), 2)
                pygame.draw.circle(surface, self.eye_color, (cx + 3, sy - 5), 2)
                # Floating particles
                for i in range(3):
                    angle = self.time * 2 + i * 2.09
                    px = cx + int(math.cos(angle) * 12)
                    py = cy + int(math.sin(angle) * 12)
                    pygame.draw.circle(surface, (*self.color[:3], 120), (px, py), 2)

            elif template == "monk":
                # Simple monk robes + bald head
                pygame.draw.rect(surface, self.color, (sx + 2, sy + 4, self.width - 4, self.height - 4))
                head_color = tuple(min(255, c + 30) for c in self.color[:3])
                pygame.draw.circle(surface, head_color, (cx, sy - 4), 8)
                pygame.draw.circle(surface, self.eye_color, (cx - 3, sy - 5), 2)
                pygame.draw.circle(surface, self.eye_color, (cx + 3, sy - 5), 2)
                # Tonsure / simple band
                pygame.draw.circle(surface, tuple(max(0, c - 20) for c in self.color[:3]), (cx, sy - 4), 9, 1)

            else:  # "common" - simple commoner
                pygame.draw.rect(surface, self.color, (sx + 2, sy + 4, self.width - 4, self.height - 4))
                head_color = tuple(min(255, c + 40) for c in self.color[:3])
                pygame.draw.circle(surface, head_color, (cx, sy - 4), 8)
                pygame.draw.circle(surface, self.eye_color, (cx - 3, sy - 5), 2)
                pygame.draw.circle(surface, self.eye_color, (cx + 3, sy - 5), 2)

            # Name tag
            from game.dialog import render_npc_name_tag
            render_npc_name_tag(surface, self.def_name, cx, sy)

            # Dialogue text bubble
            if self.dialogue_timer > 0:
                alpha = min(255, int(255 * min(1.0, self.dialogue_timer * 2)))
                from game.dialog import render_speech_bubble
                render_speech_bubble(surface, self.dialogue_text, cx, sy, alpha=alpha)

            # Cooldown indicator
            if self.cooldown > 0:
                from game.dialog import render_cooldown
                render_cooldown(surface, self.cooldown, cx, sy + self.height)


class Dealer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 28
        self.rect = pygame.Rect(x - 12, y - 14, 24, 28)
        self.alive = True
        self.time = 0.0
        self.inventory = []  # list of (item_type, data, price)
        self._generate_stock()

    def _generate_stock(self):
        self.inventory = []
        from game.weapons_inf import get_random_weapon
        from game.inventory import CONSUMABLES, ALL_ITEM_KEYS

        # 2-3 random weapons
        for _ in range(random.randint(2, 3)):
            w = get_random_weapon(max_tier=5, exclude_key="fists")
            if w:
                price = 50 + w["tier"] * 40 + w["damage"] * 3 + w["magic"] * 2
                self.inventory.append(("weapon", w, price))

        # 1-2 random gem substances
        from game.inventory import _MATERIALS, CONSUMABLES
        for _ in range(random.randint(1, 2)):
            sub = random.choice(_MATERIALS)
            sub_key = sub[0]
            cdef = dict(CONSUMABLES.get(sub_key, {}))
            cdef.setdefault("key", sub_key)
            price = 80 + sub[6] * 50
            self.inventory.append(("substance", cdef, price))

        # 2-4 random consumables
        for _ in range(random.randint(4, 6)):
            key = random.choice(ALL_ITEM_KEYS)
            cdef = CONSUMABLES[key]
            price = 10 + cdef["tier"] * 15
            if cdef["effect"]["type"] == "money":
                price = cdef["effect"].get("coins", 10) // 2
            self.inventory.append(("consumable", cdef, max(5, price)))

    def update(self, dt):
        self.time += dt

    def render(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if -50 < sx < camera.width + 50 and -50 < sy < camera.height + 50:
            cx = sx + self.width // 2
            cy = sy + self.height // 2

            glow_pulse = 0.4 + 0.3 * math.sin(self.time * 2)
            glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 215, 0, int(30 * glow_pulse)), (30, 30), 24)
            surface.blit(glow_surf, (cx - 30, cy - 30))

            # Body (robe)
            pygame.draw.ellipse(surface, (180, 140, 220), (sx, sy, self.width, self.height))
            # Head
            pygame.draw.circle(surface, (220, 200, 180), (cx, sy - 4), 8)
            # Eyes
            pygame.draw.circle(surface, (255, 215, 0), (cx - 3, sy - 5), 2)
            pygame.draw.circle(surface, (255, 215, 0), (cx + 3, sy - 5), 2)
            # Hat
            pygame.draw.polygon(surface, (120, 80, 180), [
                (cx - 10, sy - 8), (cx + 10, sy - 8), (cx, sy - 22)
            ])

            # Name tag
            tag = "DEALER"
            try:
                from game.constants import FONT_PATH
                f = pygame.font.Font(FONT_PATH, 11)
                tag_surf = f.render(tag, True, (255, 215, 0))
                surface.blit(tag_surf, (cx - tag_surf.get_width() // 2, sy - 32))
            except:
                pass


class Tree:
    TREE_TYPES = [
        "pine",
        "round",
        "dead",
    ]

    def __init__(self, x, y, tree_type=None):
        self.x = x
        self.y = y
        self.type = tree_type if tree_type else random.choice(self.TREE_TYPES)
        self.time = random.uniform(0, 6.28)
        self.sway_speed = random.uniform(0.8, 1.5)
        self.sway_amount = random.uniform(1.5, 3.5)
        self.scale = random.uniform(0.8, 1.3)
        self.width = int(24 * self.scale)
        self.height = int(40 * self.scale)
        self.rect = pygame.Rect(x - self.width // 2, y - self.height, self.width, self.height)

    def update(self, dt):
        self.time += dt * self.sway_speed

    def render(self, surface, camera):
        if camera:
            sx, sy = camera.world_to_screen(self.x, self.y)
            margin = 60
            if not (-margin < sx < camera.width + margin and -margin < sy < camera.height + margin):
                return
        else:
            sx, sy = self.x, self.y

        sway = math.sin(self.time) * self.sway_amount
        trunk_color = (30, 20, 45)
        leaf_color = (15, 40, 30)
        accent_color = (40, 180, 140)
        dark_accent = (60, 50, 80)
        glow_alpha = int(20 + 15 * math.sin(self.time * 0.5))

        if self.type == "pine":
            h = int(self.height)
            w = int(self.width)
            # Trunk
            tr = pygame.Rect(sx - 3, sy - h + 10, 6, h - 10)
            pygame.draw.rect(surface, trunk_color, tr)
            # Canopy layers (triangles)
            for i, (y_off, half_w) in enumerate([(h * 0.1, w * 0.6), (h * 0.3, w * 0.5), (h * 0.55, w * 0.35)]):
                pts = [
                    (sx + sway * (i + 1) * 0.3, sy - h + y_off),
                    (sx - half_w + sway * (i + 1) * 0.15, sy - h + y_off + h * 0.25),
                    (sx + half_w + sway * (i + 1) * 0.15, sy - h + y_off + h * 0.25),
                ]
                pygame.draw.polygon(surface, leaf_color, pts)
                pygame.draw.polygon(surface, accent_color, pts, 1)
            # Glow at base
            gs = pygame.Surface((w * 2, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (*dark_accent, glow_alpha), (0, 0, w * 2, h // 2))
            surface.blit(gs, (sx - w, sy - h // 2))

        elif self.type == "round":
            h = int(self.height)
            w = int(self.width)
            # Trunk
            tr = pygame.Rect(sx - 3, sy - h + 12, 6, h - 12)
            pygame.draw.rect(surface, trunk_color, tr)
            # Round canopy
            canopy_r = int(w * 0.7)
            cx = sx + sway * 0.5
            cy = sy - h + canopy_r
            pygame.draw.circle(surface, leaf_color, (int(cx), int(cy)), canopy_r)
            pygame.draw.circle(surface, accent_color, (int(cx), int(cy)), canopy_r, 1)
            # Inner highlight
            hl = pygame.Surface((canopy_r, canopy_r), pygame.SRCALPHA)
            pygame.draw.circle(hl, (*accent_color, 20), (canopy_r // 2, canopy_r // 2), canopy_r // 2)
            surface.blit(hl, (int(cx) - canopy_r // 2, int(cy) - canopy_r // 2))
            # Glow
            gs = pygame.Surface((w * 2, h // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (*dark_accent, glow_alpha), (0, 0, w * 2, h // 2))
            surface.blit(gs, (sx - w, sy - h // 2))

        elif self.type == "dead":
            h = int(self.height)
            w = int(self.width)
            # Trunk
            tr = pygame.Rect(sx - 3, sy - h + 8, 6, h - 8)
            pygame.draw.rect(surface, trunk_color, tr)
            # Bare branches
            for side in [-1, 1]:
                bx = sx + side * w * 0.3
                by = sy - h * 0.4
                pygame.draw.line(surface, dark_accent,
                                 (sx + sway * 0.3, sy - h * 0.5),
                                 (bx + sway * 0.6, by), 2)
                # Sub-branches
                for sub in [-1, 1]:
                    ex = bx + sub * w * 0.2
                    ey = by - h * 0.1
                    pygame.draw.line(surface, dark_accent,
                                     (bx + sway * 0.4, by),
                                     (ex + sway * 0.7, ey), 1)
            # Small red glint at tips
            for side in [-1, 1]:
                tx = sx + side * w * 0.3 + sway * 0.6
                ty = sy - h * 0.5
                pygame.draw.circle(surface, (200, 60, 80), (int(tx), int(ty)), 2)
