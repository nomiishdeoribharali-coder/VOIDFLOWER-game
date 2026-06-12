import pygame
import math
import random
from game.constants import *
from game.entities import EnemyProjectile, Enemy
from game.spells import Projectile, SlashWave, DomainExpansion, VoidShield, DarkPulse
from game.enemy_data import (
    ATK_PROJECTILE, ATK_SPORES, ATK_SUMMON, ATK_BEAM, ATK_AOE,
    AI_STATIONARY, AI_SUMMONER, TRAIT_BOSS,
    ATK_BOSS_TEARS, ATK_BOSS_LAUGH, ATK_BOSS_THORNS, ATK_BOSS_TENDRILS,
    ATK_BOSS_RAGE, ATK_BOSS_COPY, ATK_BOSS_OOZE, ATK_BOSS_SOB,
    ATK_BOSS_HEAL, ATK_BOSS_VOID,
    get_enemy_weighted,
)


SPELL_DATA = {
    SPELL_VOID_BOLT: {
        "cost": 10,
        "cooldown": 0.4,
        "damage_mult": 1.0,
        "name": SPELL_VOID_BOLT,
    },
    SPELL_CURSED_SLASH: {
        "cost": 15,
        "cooldown": 0.6,
        "damage_mult": 1.5,
        "name": SPELL_CURSED_SLASH,
    },
    SPELL_DOMAIN_EXPANSION: {
        "cost": 40,
        "cooldown": 5.0,
        "damage_mult": 3.0,
        "name": SPELL_DOMAIN_EXPANSION,
    },
    SPELL_VOID_SHIELD: {
        "cost": 20,
        "cooldown": 3.0,
        "damage_mult": 0.0,
        "name": SPELL_VOID_SHIELD,
    },
    SPELL_DARK_PULSE: {
        "cost": 25,
        "cooldown": 2.0,
        "damage_mult": 2.0,
        "name": SPELL_DARK_PULSE,
    },
}


class CombatSystem:
    def __init__(self, game=None):
        self.game = game
        self.projectiles = []
        self.effects = []
        self.shield = None
        self.enemy_projectiles = []
        self.explosions = []
        self.enemies_to_spawn = []
        self.spawn_queue = []
        self.auras = []
        self.weapon_drops_to_spawn = []
        self.potion_drops_to_spawn = []
        self.killed_enemies = []

    def cast_spell(self, player, spell_name, mouse_pos, camera):
        if player.cast_cooldown > 0:
            return False
        data = SPELL_DATA.get(spell_name)
        if not data:
            return False
        if not player.use_mp(data["cost"]):
            return False
        player.cast_cooldown = data["cooldown"]
        wx, wy = camera.screen_to_world(*mouse_pos)
        dx = wx - (player.x + player.width // 2)
        dy = wy - (player.y + player.height // 2)
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            dx, dy = player.facing
        else:
            dx /= dist
            dy /= dist
        cx = player.x + player.width // 2
        cy = player.y + player.height // 2
        base = int(player.strength * data["damage_mult"])
        damage = player.get_spell_damage(base) if hasattr(player, 'get_spell_damage') else base
        if spell_name == SPELL_VOID_BOLT:
            p = Projectile(cx, cy, dx, dy, 300, damage, COLOR_VOID, 5, 2.0)
            self.projectiles.append(p)
        elif spell_name == SPELL_CURSED_SLASH:
            s = SlashWave(cx, cy, dx, dy, damage, COLOR_CURSED)
            self.effects.append(s)
        elif spell_name == SPELL_DOMAIN_EXPANSION:
            d = DomainExpansion(cx, cy)
            d.damage = damage
            self.effects.append(d)
        elif spell_name == SPELL_VOID_SHIELD:
            self.shield = VoidShield(cx, cy)
        elif spell_name == SPELL_DARK_PULSE:
            dp = DarkPulse(cx, cy, damage, (120, 60, 180))
            self.effects.append(dp)
        return True

    def update(self, dt, enemies, player):
        mx, my = player.x + player.width // 2, player.y + player.height // 2
        if self.shield:
            self.shield.x = mx
            self.shield.y = my
            self.shield.update(dt)
            if not self.shield.alive:
                self.shield = None

        # Player projectiles vs enemies
        for p in self.projectiles[:]:
            p.update(dt)
            if not p.alive:
                self.projectiles.remove(p)
                continue
            for enemy in enemies[:]:
                if not enemy.alive:
                    continue
                if p.rect.colliderect(enemy.rect):
                    enemy.take_damage(p.damage)
                    p.alive = False
                    self.projectiles.remove(p)
                    break

        # Spell effects vs enemies
        for e in self.effects[:]:
            e.update(dt)
            if not e.alive:
                self.effects.remove(e)
                continue
            for enemy in enemies[:]:
                if not enemy.alive:
                    continue
                if id(enemy) in e.hit:
                    continue
                if e.rect.colliderect(enemy.rect):
                    enemy.take_damage(e.damage)
                    e.hit.add(id(enemy))

        # Enemy projectiles vs player
        pdef = player.get_total_defense() if hasattr(player, 'get_total_defense') else player.defense
        for ep in self.enemy_projectiles[:]:
            ep.update(dt)
            if not ep.alive:
                self.enemy_projectiles.remove(ep)
                continue
            if ep.rect.colliderect(player.rect):
                dmg = max(1, int(ep.damage * ENEMY_DAMAGE_MULT) - pdef // DEFENSE_DIVISOR)
                if self.shield and self.shield.alive:
                    if ep.rect.colliderect(self.shield.rect):
                        dmg = int(dmg * 0.3)
                        self.shield.lifetime -= 0.3
                        ep.alive = False
                        self.enemy_projectiles.remove(ep)
                        self.game.audio.play_sound("shield_block")
                        continue
                self.game.audio.play_sound("player_damage")
                player.take_damage(dmg)
                ep.alive = False
                self.enemy_projectiles.remove(ep)

        # Explosions
        for exp in self.explosions[:]:
            exp["timer"] -= dt
            for enemy in enemies[:]:
                if not enemy.alive:
                    continue
                dx = enemy.x + enemy.width // 2 - exp["x"]
                dy = enemy.y + enemy.height // 2 - exp["y"]
                d = math.sqrt(dx * dx + dy * dy)
                if d < exp["radius"]:
                    enemy.take_damage(exp["damage"])
            dx = player.x + player.width // 2 - exp["x"]
            dy = player.y + player.height // 2 - exp["y"]
            d = math.sqrt(dx * dx + dy * dy)
            if d < exp["radius"]:
                dmg = max(1, int(exp["damage"] * ENEMY_DAMAGE_MULT) - pdef // DEFENSE_DIVISOR)
                player.take_damage(dmg)
            if exp["timer"] <= 0:
                self.explosions.remove(exp)
                if self.game:
                    self.game.audio.play_sound("explosion")

        # Enemy attacks
        for enemy in enemies[:]:
            if not enemy.alive:
                continue
            at = enemy.attack_type
            dist = enemy.distance_to(player)

            # Ranged attacks
            if at == ATK_PROJECTILE and enemy.can_ranged_attack(player):
                for ep in enemy.fire_projectile(player):
                    self.enemy_projectiles.append(ep)
                enemy.attack_cooldown = enemy.attack_rate

            elif at == ATK_SPORES and enemy.can_ranged_attack(player):
                for sp in enemy.fire_spores(player):
                    self.enemy_projectiles.append(sp)
                enemy.attack_cooldown = enemy.attack_rate

            elif at == ATK_BEAM and enemy.can_ranged_attack(player):
                for ep in enemy.fire_beam(player):
                    self.enemy_projectiles.append(ep)
                enemy.attack_cooldown = enemy.attack_rate

            # Summoner
            if at == ATK_SUMMON and enemy.ai_type == AI_STATIONARY:
                enemy.spawn_timer += dt
                if enemy.spawn_timer >= enemy.attack_rate:
                    enemy.spawn_timer = 0
                    if len(enemies) < 12:
                        from game.entities import Enemy
                        child = Enemy(
                            enemy.x + random.randint(-40, 40),
                            enemy.y + random.randint(-40, 40),
                            "void_mite"
                        )
                        child.hp = 8
                        child.max_hp = 8
                        self.enemies_to_spawn.append(child)

            # Melee attacks (skip for bosses — they use their own attack patterns)
            if not enemy.is_boss and enemy.can_attack(player):
                enemy.perform_attack(player, self)

            # ───────── Boss-specific attacks ─────────
            if enemy.is_boss and enemy.can_ranged_attack(player):
                boss_key = enemy.enemy_key
                cx = enemy.x + enemy.width // 2
                cy = enemy.y + enemy.height // 2
                px = player.x + player.width // 2
                py = player.y + player.height // 2
                dx = px - cx
                dy = py - cy
                d = math.sqrt(dx * dx + dy * dy)
                if d < 1:
                    dx, dy = 1, 0
                else:
                    dx /= d
                    dy /= d

                if boss_key == "sorrow":
                    # Slow-moving tear projectiles that slow
                    for off in [-0.2, 0, 0.2]:
                        rx = dx * math.cos(off) - dy * math.sin(off)
                        ry = dx * math.sin(off) + dy * math.cos(off)
                        ep = EnemyProjectile(cx, cy, rx, ry, 70, max(1, enemy.damage - 2), (140, 170, 210), size=8, lifetime=3.5)
                        self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "joy":
                    # Erratic laughing projectiles + chance to spawn illusion
                    for off in [-0.4, -0.15, 0.15, 0.4]:
                        rx = dx * math.cos(off) - dy * math.sin(off)
                        ry = dx * math.sin(off) + dy * math.cos(off)
                        ep = EnemyProjectile(cx, cy, rx, ry, 120, max(1, enemy.damage - 3), (240, 180, 210), size=5, lifetime=1.5)
                        self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "fear":
                    # Dark tendrils from ground
                    for i in range(3):
                        off_x = random.uniform(-60, 60)
                        off_y = random.uniform(-60, 60)
                        tx = px + off_x
                        ty = py + off_y
                        tdx = tx - cx
                        tdy = ty - cy
                        td = math.sqrt(tdx * tdx + tdy * tdy)
                        if td > 0:
                            tdx /= td
                            tdy /= td
                        ep = EnemyProjectile(cx, cy, tdx, tdy, 90, max(1, enemy.damage - 1), (120, 60, 150), size=6, lifetime=1.8)
                        self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "pain":
                    # Thorn burst — spread projectiles with lingering damage
                    now = pygame.time.get_ticks() * 0.001
                    for i in range(6):
                        a = i * 1.047 + now
                        rx = math.cos(a)
                        ry = math.sin(a)
                        ep = EnemyProjectile(cx, cy, rx, ry, 60, max(1, enemy.damage - 1), (180, 40, 60), size=4, lifetime=2.5)
                        self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "rage":
                    # Rage wave — single big fast projectile
                    ep = EnemyProjectile(cx, cy, dx, dy, 180, enemy.damage, (220, 120, 40), size=10, lifetime=1.2)
                    self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "envy":
                    # Copy player's projectile color and fire volley
                    p_color = player.color if hasattr(player, 'color') else (180, 140, 255)
                    for off in [-0.15, 0, 0.15]:
                        rx = dx * math.cos(off) - dy * math.sin(off)
                        ry = dx * math.sin(off) + dy * math.cos(off)
                        ep = EnemyProjectile(cx, cy, rx, ry, 140, max(1, enemy.damage - 1), p_color, size=5, lifetime=2.0)
                        self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "disgust":
                    # Toxic ooze pools — slow projectiles that linger
                    for i in range(3):
                        a = i * 2.094 + random.uniform(-0.3, 0.3)
                        rx = math.cos(a)
                        ry = math.sin(a)
                        ep = EnemyProjectile(cx, cy, rx, ry, 40, max(1, enemy.damage - 2), (100, 180, 80), size=10, lifetime=4.0)
                        self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "grief":
                    # Sobbing AoE — ring of projectiles
                    for i in range(8):
                        a = i * 0.785
                        rx = math.cos(a)
                        ry = math.sin(a)
                        ep = EnemyProjectile(cx, cy, rx, ry, 55, max(1, enemy.damage - 2), (180, 200, 220), size=7, lifetime=2.0)
                        self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "hope":
                    # Healing light — heals itself and nearby allies
                    heal_amt = 5 * dt
                    enemy.hp = min(enemy.max_hp, enemy.hp + heal_amt)
                    for ally in enemies:
                        if ally.alive and ally != enemy:
                            ad = enemy.distance_to(ally)
                            if ad < 120:
                                ally.hp = min(ally.max_hp, ally.hp + heal_amt)
                    # Also fires a slow holy projectile
                    ep = EnemyProjectile(cx, cy, dx, dy, 60, max(1, enemy.damage - 1), (255, 220, 150), size=8, lifetime=2.5)
                    self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

                elif boss_key == "despair":
                    # Void obliteration — large dark projectiles
                    for off in [-0.1, 0, 0.1]:
                        rx = dx * math.cos(off) - dy * math.sin(off)
                        ry = dx * math.sin(off) + dy * math.cos(off)
                        ep = EnemyProjectile(cx, cy, rx, ry, 100, enemy.damage, (30, 20, 50), size=10, lifetime=2.0)
                        self.enemy_projectiles.append(ep)
                    enemy.attack_cooldown = enemy.attack_rate

            # Heal aura
            if enemy.has_trait("heal_aura"):
                for ally in enemies:
                    if ally.alive and ally != enemy:
                        d = enemy.distance_to(ally)
                        if d < 80:
                            ally.hp = min(ally.max_hp, ally.hp + 3 * dt)

            # Buff aura
            if enemy.has_trait("buff_aura"):
                for ally in enemies:
                    if ally.alive and ally != enemy:
                        d = enemy.distance_to(ally)
                        if d < 100:
                            ally.speed = min(ally.base_speed * 1.3, ally.speed + dt * 10)

            # Illusion trait
            if enemy.has_trait("illusion") and random.random() < 0.005:
                pass

        # Process spawn queue from enemy deaths (splits etc.)
        for e in self.enemies_to_spawn:
            enemies.append(e)
        self.enemies_to_spawn.clear()

        # Process summoner spawned enemies
        for e in self.spawn_queue:
            enemies.append(e)
        self.spawn_queue.clear()

        # Enemy deaths and XP
        for enemy in enemies[:]:
            if not enemy.alive and not getattr(enemy, '_xp_given', False):
                was_boss = enemy.is_boss
                enemy.on_death(self, None)
                if self.game and was_boss:
                    self.game.audio.play_sound("boss_roar")
                if player.add_xp(enemy.exp_reward):
                    pass
                player.add_ult_gauge(2 if was_boss else 1)
                player.total_kills += 1
                enemy._xp_given = True

                # Guaranteed weapon drop for bosses, normal for others
                btier = getattr(enemy, 'weapon_tier', 1)
                if was_boss:
                    btier = min(6, btier + 1)
                    self.weapon_drops_to_spawn.append({
                        "x": enemy.x + enemy.width // 2,
                        "y": enemy.y + enemy.height // 2,
                        "tier": btier,
                        "guaranteed": True,
                    })
                    # Boss extra drops
                    self.weapon_drops_to_spawn.append({
                        "x": enemy.x + enemy.width // 2 + 15,
                        "y": enemy.y + enemy.height // 2 + 15,
                        "tier": max(1, btier - 1),
                        "guaranteed": True,
                    })
                else:
                    self.weapon_drops_to_spawn.append({
                        "x": enemy.x + enemy.width // 2,
                        "y": enemy.y + enemy.height // 2,
                        "tier": btier,
                    })

                if was_boss or random.random() < 0.35:
                    from game.inventory import get_consumable_drop
                    self.potion_drops_to_spawn.append({
                        "x": enemy.x + enemy.width // 2,
                        "y": enemy.y + enemy.height // 2,
                        "key": get_consumable_drop(btier),
                    })
                if was_boss:
                    self.potion_drops_to_spawn.append({
                        "x": enemy.x + enemy.width // 2 + 10,
                        "y": enemy.y + enemy.height // 2,
                        "key": get_consumable_drop(btier),
                    })
                self.killed_enemies.append(enemy)
                enemies.remove(enemy)

    def player_melee(self, player, target_x, target_y, attack_data, enemies):
        px = player.x + player.width // 2
        py = player.y + player.height // 2
        dx = target_x - px
        dy = target_y - py
        md = math.sqrt(dx * dx + dy * dy)
        if md < 1:
            return 0
        dx /= md
        dy /= md

        dmg = attack_data["damage"]
        reach = attack_data["range"]
        arc = attack_data["arc"]
        hit_count = 0
        for enemy in enemies:
            if not enemy.alive:
                continue
            ex = enemy.x + enemy.width // 2
            ey = enemy.y + enemy.height // 2
            edx = ex - px
            edy = ey - py
            ed = math.sqrt(edx * edx + edy * edy)
            if ed > reach:
                continue
            angle = math.acos((edx * dx + edy * dy) / max(ed, 0.01))
            if angle > arc / 2:
                continue
            enemy.take_damage(dmg)
            enemy.vx += dx * attack_data["knockback"]
            enemy.vy += dy * attack_data["knockback"]
            hit_count += 1
        if hit_count > 0:
            player._last_melee_hit_count = hit_count
        return hit_count

    def render(self, surface, camera):
        for p in self.projectiles:
            p.render(surface, camera)
        for e in self.effects:
            e.render(surface, camera)
        if self.shield:
            self.shield.render(surface, camera)
        for ep in self.enemy_projectiles:
            ep.render(surface, camera)
        for exp in self.explosions:
            sx, sy = camera.world_to_screen(exp["x"], exp["y"])
            r = int(exp["radius"])
            exp_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(exp_surf, (200, 80, 80, 120), (r, r), r)
            pygame.draw.circle(exp_surf, (255, 150, 80, 80), (r, r), int(r * 0.6))
            surface.blit(exp_surf, (sx - r, sy - r))
