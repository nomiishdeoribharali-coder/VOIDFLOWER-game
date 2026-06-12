import pygame
import random
import math
from engine.core import Scene
from engine.input import InputHandler
from engine.camera import Camera
from engine.particle import ParticleEmitter
from engine.ui import Button
from game.constants import *
from game.entities import Player, Enemy, WeaponDrop, InteractableNPC, NPC_DEFINITIONS
from game.combat import CombatSystem
from game.world import World
from game.hud import HUD, RadialMenu
from game.progression import render_level_up_notification
from game.enemy_data import get_enemy_weighted, TIER_ENEMIES, get_boss_for_level, AI_BOSS, TRAIT_BOSS, BOSS_KEYS
from game.weapons_inf import get_weapon_drop, get_weapon
from engine.bloom import BloomEffect
from game.inventory import VaporwaveInventory
from game.shop import DealerShop
from game.cosmetic_shop import CosmeticShop
from game.mutation import evolve_weapon
from game.crafting import CraftTable, RECIPES
from game.constants import FONT_PATH

EXPLORE_THEME = "data/audio/a2_explore"
BATTLE_THEME = "data/audio/a1_battle"
BATTLE_DETECTION_RANGE = 250
ULT_SPECIAL_THEME = "data/audio/a_special"
SHOP_THEME = "data/audio/shop"
KILLZONE_THEME = "data/audio/killzone"

def palette_for_level(level):
    if level < 10:
        return "purple"
    elif level < 20:
        return "green"
    elif level < 30:
        return "red"
    elif level < 40:
        return "blue"
    elif level < 50:
        return "cyan"
    else:
        return "rainbow"

PALETTE_DIFFICULTY = {
    "purple":  {"hp": 0.70, "dmg": 0.70, "spawn": 0.5,  "max": 0.5,  "boss_min": 80,  "boss_max": 120, "label": "EASY"},
    "green":   {"hp": 0.85, "dmg": 0.85, "spawn": 0.75, "max": 0.75, "boss_min": 60,  "boss_max": 90,  "label": "NORMAL"},
    "red":     {"hp": 1.0,  "dmg": 1.0,  "spawn": 1.0,  "max": 1.0,  "boss_min": 50,  "boss_max": 75,  "label": "HARD"},
    "blue":    {"hp": 1.15, "dmg": 1.15, "spawn": 1.25, "max": 1.3,  "boss_min": 35,  "boss_max": 55,  "label": "BRUTAL"},
    "cyan":    {"hp": 1.35, "dmg": 1.35, "spawn": 1.5,  "max": 1.7,  "boss_min": 25,  "boss_max": 40,  "label": "NIGHTMARE"},
    "rainbow": {"hp": 1.70, "dmg": 1.70, "spawn": 2.5,  "max": 3.0,  "boss_min": 15,  "boss_max": 25,  "label": "EXTREME"},
}

def get_palette_config(palette_name):
    return PALETTE_DIFFICULTY.get(palette_name, PALETTE_DIFFICULTY["red"])

BOSS_THEMES = {
    "sorrow": "data/audio/b1",
    "joy": "data/audio/b2",
    "fear": "data/audio/b3",
    "pain": "data/audio/b4",
    "rage": "data/audio/b5",
    "envy": "data/audio/b6",
    "disgust": "data/audio/b7",
    "grief": "data/audio/b8",
    "hope": "data/audio/b9",
    "despair": "data/audio/b10",
}


class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.input = InputHandler()
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
        self.world = None
        self.player = None
        self.enemies = []
        self.combat = None
        self.emitter = ParticleEmitter()
        self.hud = HUD()
        self.selected_spell_index = 0
        self.level_up_timer = 0
        self.enemy_spawn_timer = 0
        self.shake_timer = 0
        self.shake_offset = (0, 0)
        self.spawned_rares = set()
        self.weapon_drops = []
        self.pickup_notify_timer = 0
        self.pickup_notify_text = ""
        self.battle_active = False
        self.theme_cooldown = 0.0
        self.bloom = BloomEffect(WINDOW_WIDTH, WINDOW_HEIGHT, quality=0.4, threshold=100, intensity=0.8)
        self.env_time = 0.0
        self.inv_ui = VaporwaveInventory()
        self.radial_menu = RadialMenu()
        self.dealers = []
        self.shop_ui = DealerShop()
        self.cosmetic_shop = CosmeticShop()
        self.craft_ui = CraftTable()
        self.nearby_dealer = None
        self.nearby_quest_giver = None
        self.boss_timer = random.uniform(0, 30)
        self.boss_interval = random.uniform(60, 90)
        self.boss_spawned_keys = set()
        self.boss_announce_text = ""
        self.boss_announce_timer = 0.0
        self.boss_theme_active = False
        self.death_state = None
        self.death_timer = 0.0
        self.death_fade_alpha = 0
        self.death_typewriter = ""
        self.death_target = "YOU ARE DEAD"
        self.death_completed = False
        self.paused = False
        self.pause_buttons = []
        self._current_boss_key = None
        self.ultimate_active = False
        self.ult_prev_state = {"boss": False, "battle": False, "boss_key": None}
        self.shop_music_active = False
        self.shop_music_prev_state = None
        self.killzone_active = False
        self.killzone_enemy_count = 0
        self.killzone_saved_x = 0
        self.killzone_saved_y = 0
        self.killzone_saved_state = None
        self.killzone_tint = 0.0
        self.mutation_notify_text = ""
        self.mutation_notify_timer = 0.0
        self.npcs = []
        self.nearby_npc = None
        self.nearby_tree = None
        self.trees = []

        self._load_sfx()

    def _load_sfx(self):
        a = self.game.audio
        a.load_sound("explosion", "FreeSFX/GameSFX/Explosion/Retro Explosion Short 01")
        a.load_sound("boss_roar", "FreeSFX/GameSFX/Roar/Retro Roar LoFi 08")
        a.load_sound("level_up", "FreeSFX/GameSFX/Events/Retro Event UI 13")
        a.load_sound("pickup", "FreeSFX/GameSFX/Blops/Retro Blop StereoUP 04")
        a.load_sound("dash", "FreeSFX/GameSFX/Bounce Jump/Retro Jump StereoUP Simple 01")
        a.load_sound("player_damage", "FreeSFX/GameSFX/Impact/Retro Impact LoFi 09")
        a.load_sound("death", "FreeSFX/GameSFX/Events/Negative/Retro Negative Short 07")
        a.load_sound("shield_block", "FreeSFX/GameSFX/Magic/Retro Magic Protection 01")
        a.load_sound("parry", "FreeSFX/GameSFX/Impact/Retro Impact Water 03")
        a.load_sound("ui_click", "FreeSFX/GameSFX/Blops/Retro Blop 18")
        a.load_sound("spell_fail", "FreeSFX/GameSFX/Events/Wrong/Retro Event Wrong Simple 03")
        a.load_sound("killzone_start", "FreeSFX/GameSFX/Cinematic/Retro Cinematic Drums 01")
        a.load_sound("killzone_clear", "FreeSFX/GameSFX/Music/Success/Retro Success Melody 01 - sawtooth lead 1")

    def enter(self):
        self.world = World(palette_for_level(1))
        spawn = self.world.get_spawn_point()
        self.player = Player(spawn[0], spawn[1])
        self.player._game_scene = self
        self.camera.follow(self.player)
        self.enemies = []
        self.combat = CombatSystem(self.game)
        self.selected_spell_index = 0
        self.level_up_timer = 0
        self.enemy_spawn_timer = 0
        self.shake_timer = 0
        self.shake_offset = (0, 0)
        self.spawned_rares.clear()
        self.weapon_drops.clear()
        self.pickup_notify_timer = 0
        self.battle_active = False
        self.theme_cooldown = 0.0

        self.game.audio.crossfade_to("explore", EXPLORE_THEME, 2.0)

        dc = get_palette_config(self.world.palette_name)
        self.boss_timer = random.uniform(10, 40)
        self.boss_interval = random.uniform(dc["boss_min"], dc["boss_max"])
        self.boss_spawned_keys = set()
        self.boss_announce_text = ""
        self.boss_announce_timer = 0.0
        self.boss_theme_active = False
        self._current_boss_key = None
        self.ultimate_active = False
        self.ult_prev_state = {"boss": False, "battle": False, "boss_key": None}
        self.death_state = None
        self.death_timer = 0.0
        self.death_fade_alpha = 0
        self.death_typewriter = ""
        self.death_target = "YOU ARE DEAD"
        self.death_completed = False

        self.dealers = []
        self.quest_givers = []
        self.quest_notify_text = ""
        self.quest_notify_timer = 0.0
        from game.entities import Dealer, QuestGiver
        for _ in range(3):
            dpos = self.world.get_random_enemy_spawn(max(1, self.player.level))
            if dpos:
                self.dealers.append(Dealer(dpos[0], dpos[1]))
            else:
                self.dealers.append(Dealer(random.randint(200, WORLD_WIDTH - 200),
                                           random.randint(200, WORLD_HEIGHT - 200)))
        for _ in range(2):
            qpos = self.world.get_random_enemy_spawn(max(1, self.player.level))
            if qpos:
                self.quest_givers.append(QuestGiver(qpos[0], qpos[1]))
            else:
                self.quest_givers.append(QuestGiver(random.randint(200, WORLD_WIDTH - 200),
                                                     random.randint(200, WORLD_HEIGHT - 200)))
        self.npcs = []
        npc_keys = list(NPC_DEFINITIONS.keys())
        for _ in range(min(50, len(npc_keys) * 2)):
            npos = self.world.get_random_enemy_spawn(max(1, self.player.level))
            if npos:
                nkey = random.choice(npc_keys)
                self.npcs.append(InteractableNPC(npos[0], npos[1], nkey))

        from game.entities import Tree
        self.trees = []
        w, h = self.world.tilemap.width, self.world.tilemap.height
        for _ in range(80):
            tx = random.randint(100, WORLD_WIDTH - 100)
            ty = random.randint(100, WORLD_HEIGHT - 100)
            col, row = tx // TILE_SIZE, ty // TILE_SIZE
            if 0 <= col < w and 0 <= row < h:
                if not self.world.tilemap.is_solid(col, row) and self.world.tilemap.tiles[row][col] == 0:
                    continue
                if not self.world.tilemap.is_solid(col, row):
                    self.trees.append(Tree(tx, ty))
        while len(self.trees) < 80:
            self.trees.append(Tree(random.randint(100, WORLD_WIDTH - 100),
                                   random.randint(100, WORLD_HEIGHT - 100)))

        count = int((30 + self.player.level * 5) * dc["spawn"])
        for _ in range(count):
            self.spawn_enemy()

    def spawn_enemy(self):
        pos = self.world.get_random_enemy_spawn(self.player.level)
        if pos:
            exclude_keys = set()
            if self.player.level < 3:
                for key in TIER_ENEMIES.get(3, []):
                    exclude_keys.add(key)
                for key in TIER_ENEMIES.get(4, []):
                    exclude_keys.add(key)
                for key in TIER_ENEMIES.get(5, []):
                    exclude_keys.add(key)

            if random.random() < 0.08 and self.player.level >= 3:
                tier5_keys = [k for k in get_enemy_weighted(self.player.level)
                             if k in TIER_ENEMIES.get(5, []) or k in TIER_ENEMIES.get(6, [])]
                if tier5_keys:
                    etype = random.choice(tier5_keys)
                else:
                    etype = get_enemy_weighted(self.player.level, exclude=exclude_keys)
            else:
                etype = get_enemy_weighted(self.player.level, exclude=exclude_keys)

            enemy = Enemy(pos[0], pos[1], etype)
            scale = 1.0 + (self.player.level - 1) * 0.12
            dc = get_palette_config(self.world.palette_name)
            enemy.hp = int(enemy.hp * scale * dc["hp"])
            enemy.max_hp = enemy.hp
            enemy.damage = int(enemy.damage * scale * dc["dmg"])
            enemy.exp_reward = int(enemy.exp_reward * scale)
            if hasattr(enemy, 'edef'):
                enemy.weapon_tier = enemy.edef["tier"]
            else:
                enemy.weapon_tier = 1
            self.enemies.append(enemy)

    def _spawn_boss(self, boss_key):
        # Find a position away from the player
        px = self.player.x + self.player.width // 2
        py = self.player.y + self.player.height // 2
        for _ in range(20):
            bx = random.randint(200, WORLD_WIDTH - 200)
            by = random.randint(200, WORLD_HEIGHT - 200)
            dx = bx - px
            dy = by - py
            if math.sqrt(dx * dx + dy * dy) > 300:
                test_rect = pygame.Rect(bx, by, 40, 40)
                if not self.world.collides(test_rect):
                    boss = Enemy(bx, by, boss_key)
                    scale = 1.0 + (self.player.level - 1) * 0.15
                    dc = get_palette_config(self.world.palette_name)
                    boss.hp = int(boss.hp * scale * dc["hp"])
                    boss.max_hp = boss.hp
                    boss.damage = int(boss.damage * scale * dc["dmg"])
                    boss.exp_reward = int(boss.exp_reward * scale)
                    self.enemies.append(boss)
                    self.boss_spawned_keys.add(boss_key)
                    self.boss_announce_text = f"⚡ {boss.edef['name']} APPEARS! ⚡"
                    self.boss_announce_timer = 3.0
                    self.shake_timer = 0.3
                    self.game.audio.play_sound("boss_roar")
                    self._play_boss_theme(boss_key)
                    return

        # Fallback: spawn near center
        bx, by = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
        boss = Enemy(bx, by, boss_key)
        scale = 1.0 + (self.player.level - 1) * 0.15
        boss.hp = int(boss.hp * scale)
        boss.max_hp = boss.hp
        boss.damage = int(boss.damage * scale)
        boss.exp_reward = int(boss.exp_reward * scale)
        self.enemies.append(boss)
        self.boss_spawned_keys.add(boss_key)
        self.boss_announce_text = f"⚡ {boss.edef['name']} APPEARS! ⚡"
        self.boss_announce_timer = 3.0
        self.shake_timer = 0.3
        self._play_boss_theme(boss_key)

    def _play_boss_theme(self, boss_key):
        theme_path = BOSS_THEMES.get(boss_key)
        if theme_path:
            self.game.audio.crossfade_to(f"boss_{boss_key}", theme_path, 1.5)
            self.boss_theme_active = True
            self._current_boss_key = boss_key

    def _stop_boss_theme(self):
        if self.boss_theme_active:
            self.game.audio.crossfade_to("explore", EXPLORE_THEME, 1.2)
            self.boss_theme_active = False
            self._current_boss_key = None
            self.battle_active = False
            self.theme_cooldown = 1.0

    def _enter_shop_music(self):
        self.shop_music_prev_state = {
            "boss": self.boss_theme_active,
            "battle": self.battle_active,
            "boss_key": self._current_boss_key,
            "ultimate": self.ultimate_active,
        }
        self.boss_theme_active = False
        self.battle_active = False
        self.ultimate_active = False
        self.shop_music_active = True
        self.game.audio.crossfade_to("shop", SHOP_THEME, 0.6)

    def _exit_shop_music(self):
        prev = self.shop_music_prev_state
        self.shop_music_active = False
        self.shop_music_prev_state = None
        if prev is None:
            self.battle_active = False
            self.game.audio.crossfade_to("explore", EXPLORE_THEME, 0.8)
            return
        if prev["ultimate"]:
            self.ultimate_active = True
            self.game.audio.crossfade_to("ultimate", ULT_SPECIAL_THEME, 0.5)
        elif prev["boss"] and prev["boss_key"]:
            self._play_boss_theme(prev["boss_key"])
        elif prev["battle"]:
            self.battle_active = True
            self.game.audio.crossfade_to("battle", BATTLE_THEME, 0.8)
        else:
            self.battle_active = False
            self.game.audio.crossfade_to("explore", EXPLORE_THEME, 0.8)

    def _update_shop_music(self):
        any_shop_open = self.cosmetic_shop.is_open() or self.shop_ui.open or self.shop_ui.anim_t > 0
        if any_shop_open and not self.shop_music_active:
            self._enter_shop_music()
        elif not any_shop_open and self.shop_music_active:
            self._exit_shop_music()

    def _trigger_killzone(self):
        self.killzone_active = True
        self.killzone_tint = 0.0
        self.killzone_saved_x = self.player.x
        self.killzone_saved_y = self.player.y
        self.killzone_saved_state = {
            "boss": self.boss_theme_active,
            "battle": self.battle_active,
            "boss_key": self._current_boss_key,
            "ultimate": self.ultimate_active,
        }
        self.boss_theme_active = False
        self.battle_active = False
        self.ultimate_active = False
        self.boss_spawned_keys.clear()
        self.game.audio.crossfade_to("killzone", KILLZONE_THEME, 0.8)

        # Teleport to arena center
        self.player.x = WORLD_WIDTH // 2
        self.player.y = WORLD_HEIGHT // 2
        self.player.rect.x = self.player.x
        self.player.rect.y = self.player.y
        self.player.vx = 0
        self.player.vy = 0
        self.camera.follow(self.player)

        # Clear regular enemies
        self.enemies.clear()

        # Spawn killzone enemies
        count = 30 + self.player.level * 3
        for _ in range(count):
            pos = self.world.get_random_enemy_spawn(self.player.level)
            if pos:
                ex, ey = pos
            else:
                ex = self.player.x + random.randint(-400, 400)
                ey = self.player.y + random.randint(-400, 400)
            self.spawn_enemy_at(ex, ey, killzone=True)

        self.boss_announce_text = f"⚔ KILLZONE: Defeat {count} enemies! ⚔"
        self.boss_announce_timer = 3.5
        self.shake_timer = 0.5
        self.game.audio.play_sound("killzone_start")

    def _complete_killzone(self):
        self.killzone_active = False
        self.killzone_tint = 0.0

        # Teleport back
        self.player.x = self.killzone_saved_x
        self.player.y = self.killzone_saved_y
        self.player.rect.x = self.player.x
        self.player.rect.y = self.player.y
        self.player.vx = 0
        self.player.vy = 0
        self.camera.follow(self.player)

        # Restore music
        prev = self.killzone_saved_state
        if prev:
            if prev["ultimate"]:
                self.ultimate_active = True
                self.game.audio.crossfade_to("ultimate", ULT_SPECIAL_THEME, 0.5)
            elif prev["boss"] and prev["boss_key"]:
                self._play_boss_theme(prev["boss_key"])
            elif prev["battle"]:
                self.battle_active = True
                self.game.audio.crossfade_to("battle", BATTLE_THEME, 0.8)
            else:
                self.battle_active = False
                self.game.audio.crossfade_to("explore", EXPLORE_THEME, 0.8)

        # Reward
        bonus_coins = 50 + self.player.level * 10
        self.player.coins += bonus_coins
        self.player.add_xp(50 + self.player.level * 20)
        self.player.total_kills = 0

        self.boss_announce_text = f"✦ KILLZONE CLEARED! +{bonus_coins} coins ✦"
        self.boss_announce_timer = 4.0
        self.shake_timer = 0.5
        self.game.audio.play_sound("killzone_clear")

    def spawn_enemy_at(self, x, y, killzone=False):
        from game.entities import Enemy
        from game.enemy_data import get_enemy_weighted
        etype = get_enemy_weighted(self.player.level)
        enemy = Enemy(x, y, etype)
        scale = 1.0 + (self.player.level - 1) * 0.12
        enemy.hp = int(enemy.hp * scale)
        enemy.damage = int(enemy.damage * scale)
        enemy.exp_reward = int(enemy.exp_reward * scale)
        enemy._killzone = killzone
        self.enemies.append(enemy)

    def spawn_weapon_drop(self, x, y, tier, guaranteed=False):
        wdef = get_weapon_drop(tier)
        if wdef and wdef["key"] != "fists":
            if guaranteed or random.random() < 0.25:
                drop = WeaponDrop(x, y, wdef["key"])
                self.weapon_drops.append(drop)

    def _regenerate_world(self, palette_name="default"):
        self.world = World(palette_name)
        spawn = self.world.get_spawn_point()
        self.player.x, self.player.y = spawn
        self.player.rect.x, self.player.rect.y = spawn
        self.player.vx = self.player.vy = 0
        self.camera.follow(self.player)
        self.camera.x = self.camera.y = 0
        self.enemies.clear()
        self.weapon_drops.clear()
        self.dealers.clear()
        self.quest_givers.clear()
        self.npcs = []
        self.nearby_npc = None
        self.nearby_tree = None
        self.quest_notify_text = ""
        self.quest_notify_timer = 0.0
        self.boss_spawned_keys.clear()
        dc = get_palette_config(self.world.palette_name)
        self.boss_timer = random.uniform(10, 40)
        self.boss_interval = random.uniform(dc["boss_min"], dc["boss_max"])
        self.boss_announce_text = ""
        self.boss_announce_timer = 0.0
        self.boss_theme_active = False
        self.shake_timer = 0
        self.spawned_rares.clear()
        self.enemy_spawn_timer = 0
        self.battle_active = False
        self.theme_cooldown = 1.0
        self.paused = False
        self.pause_buttons = []
        self.pickup_notify_timer = 0
        self.game.audio.crossfade_to("explore", EXPLORE_THEME, 1.5)
        from game.entities import Dealer, QuestGiver
        for _ in range(3):
            dpos = self.world.get_random_enemy_spawn(max(1, self.player.level))
            if dpos:
                self.dealers.append(Dealer(dpos[0], dpos[1]))
            else:
                self.dealers.append(Dealer(random.randint(200, WORLD_WIDTH - 200),
                                           random.randint(200, WORLD_HEIGHT - 200)))
        for _ in range(2):
            qpos = self.world.get_random_enemy_spawn(max(1, self.player.level))
            if qpos:
                self.quest_givers.append(QuestGiver(qpos[0], qpos[1]))
            else:
                self.quest_givers.append(QuestGiver(random.randint(200, WORLD_WIDTH - 200),
                                                      random.randint(200, WORLD_HEIGHT - 200)))
        npc_keys = list(NPC_DEFINITIONS.keys())
        for _ in range(min(50, len(npc_keys) * 2)):
            npos = self.world.get_random_enemy_spawn(max(1, self.player.level))
            if npos:
                nkey = random.choice(npc_keys)
                self.npcs.append(InteractableNPC(npos[0], npos[1], nkey))
        from game.entities import Tree
        self.trees = []
        w, h = self.world.tilemap.width, self.world.tilemap.height
        for _ in range(80):
            tx = random.randint(100, WORLD_WIDTH - 100)
            ty = random.randint(100, WORLD_HEIGHT - 100)
            col, row = tx // TILE_SIZE, ty // TILE_SIZE
            if 0 <= col < w and 0 <= row < h:
                if not self.world.tilemap.is_solid(col, row) and self.world.tilemap.tiles[row][col] == 0:
                    continue
                if not self.world.tilemap.is_solid(col, row):
                    self.trees.append(Tree(tx, ty))
        while len(self.trees) < 80:
            self.trees.append(Tree(random.randint(100, WORLD_WIDTH - 100),
                                   random.randint(100, WORLD_HEIGHT - 100)))
        dc = get_palette_config(self.world.palette_name)
        count = int((30 + self.player.level * 5) * dc["spawn"])
        for _ in range(count):
            self.spawn_enemy()

    def _process_mutations(self):
        player = self.player
        for enemy in self.combat.killed_enemies[:]:
            # ── Boss kill detection (must run before killed_enemies is cleared) ──
            if getattr(enemy, 'is_boss', False) and not getattr(enemy, '_boss_kill_handled', False):
                enemy._boss_kill_handled = True
                self.shake_timer = 0.5
                self.boss_announce_text = f"{enemy.edef['name']} VANQUISHED!"
                self.boss_announce_timer = 3.0
                self.player.add_xp(enemy.exp_reward // 2)
                self._stop_boss_theme()

            wkey = player.weapon["key"]
            num_hit = getattr(player, '_last_melee_hit_count', 1)
            time_since = self.env_time - player.mutation.get_stats(wkey)["last_kill_time"]
            hp_ratio = player.hp / player.max_hp if player.max_hp > 0 else 1.0
            near_hazard = False
            px = player.x + player.width // 2
            py = player.y + player.height // 2
            if hasattr(self, 'world') and self.world:
                col = int(px // TILE_SIZE)
                row = int(py // TILE_SIZE)
                for dc in range(-2, 3):
                    for dr in range(-2, 3):
                        tc = col + dc
                        tr = row + dr
                        if 0 <= tc < self.world.width_tiles and 0 <= tr < self.world.height_tiles:
                            if self.world.tilemap.tiles[tr][tc] == 0:
                                near_hazard = True
                                break
                    if near_hazard:
                        break
            player.mutation.record_kill(wkey, num_hit, time_since, hp_ratio, near_hazard, self.env_time)
            if player.mutation.should_mutate(wkey):
                profile = player.mutation.get_mutation_profile(wkey)
                if profile:
                    new_w = evolve_weapon(player.weapon, profile, player.level)
                    mname = player.mutation.get_mutation_name(profile)
                    old_key = player.weapon["key"]
                    new_w["key"] = old_key + "_mutated"
                    new_w["name"] = f"{mname} {player.weapon['name']}"
                    player.weapon = new_w
                    idx = player.inventory.equipped_index
                    if idx < len(player.inventory.weapons):
                        item = player.inventory.weapons[idx]
                        item.data = new_w
                    self.mutation_notify_text = f"WEAPON EVOLVED: {new_w['name']}"
                    self.mutation_notify_timer = 4.0
                    from game.mutation import reset_weapon_stats
                    reset_weapon_stats(player.mutation, wkey)
        self.combat.killed_enemies.clear()

    def handle_event(self, event):
        try:
            self.input.handle_event(event)
        except Exception:
            pass
        try:
            if self.cosmetic_shop.is_open():
                self.cosmetic_shop.handle_event(event, self.player)
                return
            if self.paused:
                if event.type == pygame.KEYDOWN:
                    k = getattr(event, 'key', None)
                    if k == pygame.K_ESCAPE:
                        self.paused = False
                        self.pause_buttons = []
                        return
                for btn in self.pause_buttons:
                    btn.handle_event(event)
                return
            if event.type == pygame.KEYDOWN:
                k = getattr(event, 'key', None)
                if k == pygame.K_1:
                    self.selected_spell_index = 0
                elif k == pygame.K_2:
                    self.selected_spell_index = min(1, len(self.player.equipped_spells) - 1)
                elif k == pygame.K_3:
                    self.selected_spell_index = min(2, len(self.player.equipped_spells) - 1)
                elif k == pygame.K_4:
                    self.selected_spell_index = min(3, len(self.player.equipped_spells) - 1)
                elif k == pygame.K_5:
                    self.selected_spell_index = min(4, len(self.player.equipped_spells) - 1)
                elif k == pygame.K_r and not self.shop_ui.open and not self.inv_ui.open and not self.cosmetic_shop.is_open():
                    if self.player.activate_ult() and not self.ultimate_active:
                        self.ultimate_active = True
                        self.ult_prev_state = {
                            "boss": self.boss_theme_active,
                            "battle": self.battle_active,
                            "boss_key": self._current_boss_key,
                        }
                        self.boss_theme_active = False
                        self.game.audio.crossfade_to("ultimate", ULT_SPECIAL_THEME, 0.5)
                elif k == pygame.K_m:
                    self.game.audio.toggle_music()
                elif k == pygame.K_f:
                    self._pickup_nearest_weapon()
                elif k == pygame.K_g:
                    if self.shop_ui.open:
                        self.shop_ui.close()
                    elif self.nearby_npc and not self.inv_ui.open and not self.shop_ui.open:
                        self.nearby_npc.interact(self.player, self)
                    elif self.nearby_dealer and not self.inv_ui.open:
                        self.shop_ui.open_for(self.nearby_dealer)
                    elif self.nearby_quest_giver:
                        q = self.nearby_quest_giver.quest
                        if q and q.completed and not q.claimed:
                            q.claimed = True
                            self.player.coins += q.reward_coins
                            self.quest_notify_text = f"Reward claimed: +{q.reward_coins} coins!"
                            self.quest_notify_timer = 3.0
                            self.nearby_quest_giver.quest = q.reset()
                            self.nearby_quest_giver.quest.giver = self.nearby_quest_giver
                        elif q and not q.accepted:
                            q.accepted = True
                            q.giver = self.nearby_quest_giver
                            self.quest_notify_text = f"Quest accepted: {q.description}"
                            self.quest_notify_timer = 3.0
                elif k == pygame.K_v and not self.inv_ui.open and not self.shop_ui.open and not self.cosmetic_shop.is_open():
                    self.craft_ui.toggle()
                elif k == pygame.K_c:
                    if self.nearby_tree and not self.inv_ui.open and not self.shop_ui.open and not self.cosmetic_shop.is_open():
                        if self.player.level >= 5:
                            self.trees.remove(self.nearby_tree)
                            self.player.wood += 1
                            self.nearby_tree = None
                            notify = "+1 Wood"
                            self.player.inventory.notify_text = notify
                            self.player.inventory.notify_timer = 2.0
                            self.emitter.burst(self.player.x + self.player.width // 2,
                                               self.player.y + self.player.height // 2,
                                               (140, 100, 60), count=8, speed=60, lifetime=0.5, size=3)
                        else:
                            self.player.inventory.notify_text = "Need level 5 to cut trees"
                            self.player.inventory.notify_timer = 2.0
                elif k == pygame.K_SPACE and not self.shop_ui.open and not self.inv_ui.open and not self.cosmetic_shop.is_open() and not self.radial_menu.open:
                    self.player.start_dash()
                    self.game.audio.play_sound("dash")
                elif k == pygame.K_q and not self.shop_ui.open and not self.inv_ui.open and not self.cosmetic_shop.is_open():
                    self.radial_menu.toggle(self.player.inventory)
                elif k == pygame.K_TAB:
                    if self.shop_ui.open:
                        self.shop_ui.close()
                    elif self.radial_menu.open:
                        self.radial_menu.toggle(self.player.inventory)
                    else:
                        self.inv_ui.toggle()
                elif k == pygame.K_ESCAPE:
                    if self.radial_menu.open:
                        self.radial_menu.toggle(self.player.inventory)
                    elif self.cosmetic_shop.is_open():
                        self.cosmetic_shop.close()
                    elif self.shop_ui.open:
                        self.shop_ui.close()
                    elif self.inv_ui.open:
                        self.inv_ui.toggle()
                    else:
                        self.paused = not self.paused
                        if self.paused:
                            cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
                            self.pause_buttons = [
                                Button(pygame.Rect(cx - 100, cy - 80, 200, 40), "Resume",
                                       callback=lambda: setattr(self, 'paused', False),
                                       color=(50, 45, 75), hover_color=(90, 75, 130),
                                       audio_manager=self.game.audio),
                                Button(pygame.Rect(cx - 100, cy - 20, 200, 40), "Cosmetic Shop",
                                       callback=lambda: (setattr(self, 'paused', False), self.cosmetic_shop.open_shop()),
                                       color=(50, 45, 75), hover_color=(90, 75, 130),
                                       audio_manager=self.game.audio),
                                Button(pygame.Rect(cx - 100, cy + 40, 200, 40), "New World",
                                       callback=self._regenerate_world,
                                       color=(50, 45, 75), hover_color=(90, 75, 130),
                                       audio_manager=self.game.audio),
                                Button(pygame.Rect(cx - 100, cy + 100, 200, 40), "Quit to Title",
                                       callback=lambda: self.game.switch_scene("title"),
                                       color=(50, 45, 75), hover_color=(90, 75, 130),
                                       audio_manager=self.game.audio),
                            ]
                        else:
                            self.pause_buttons = []

                # ── Shop navigation (when shop is open) ──
                if self.shop_ui.open:
                    if k == pygame.K_UP:
                        self.shop_ui.selected_idx = max(0, self.shop_ui.selected_idx - 1)
                    elif k == pygame.K_DOWN:
                        self.shop_ui.selected_idx = min(len(self.shop_ui.dealer.inventory) - 1, self.shop_ui.selected_idx + 1)
                    elif k == pygame.K_RETURN or k == pygame.K_SPACE:
                        inv = self.shop_ui.dealer.inventory
                        idx = self.shop_ui.selected_idx
                        if 0 <= idx < len(inv):
                            itype, data, price = inv[idx]
                            if self.player.coins >= price:
                                self.player.coins -= price
                                if itype == "weapon":
                                    from game.weapons_inf import get_weapon
                                    wdef = get_weapon(data["key"])
                                    if wdef and self.player.inventory.add_weapon(wdef):
                                        self.emitter.burst(self.player.x, self.player.y, wdef["color"],
                                                          count=5, speed=60, lifetime=0.3, size=2)
                                        inv.pop(idx)
                                        self.shop_ui.selected_idx = min(idx, len(inv) - 1)
                                elif itype == "consumable" or itype == "substance":
                                    key = data.get("key", "")
                                    if self.player.inventory.add_consumable(key):
                                        self.emitter.burst(self.player.x, self.player.y, data.get("color", (200, 200, 200)),
                                                          count=3, speed=40, lifetime=0.3, size=2)
                                        inv.pop(idx)
                                        self.shop_ui.selected_idx = min(idx, len(inv) - 1)
                    return

                # ── Crafting navigation (when crafting is open) ──
                if self.craft_ui.open:
                    if k == pygame.K_ESCAPE:
                        self.craft_ui.close()
                    elif k == pygame.K_UP:
                        self.craft_ui.selected_idx = max(0, self.craft_ui.selected_idx - 1)
                    elif k == pygame.K_DOWN:
                        self.craft_ui.selected_idx = min(len(RECIPES) - 1, self.craft_ui.selected_idx + 1)
                    elif k == pygame.K_RETURN or k == pygame.K_SPACE:
                        if self.craft_ui.craft_selected(self.player):
                            self.game.audio.play_sound("pickup")
                    return
                    return

                # ── Inventory navigation ──
                if self.inv_ui.open:
                    inv = self.player.inventory
                    cols = self.inv_ui.grid_cols
                    if k == pygame.K_a:
                        if self.inv_ui.tab == "weapons":
                            inv.selected_weapon_idx = max(0, inv.selected_weapon_idx - 1)
                        else:
                            inv.selected_cons_idx = max(0, inv.selected_cons_idx - 1)
                    elif k == pygame.K_d:
                        if self.inv_ui.tab == "weapons":
                            inv.selected_weapon_idx = min(len(inv.weapons) - 1, inv.selected_weapon_idx + 1)
                        else:
                            inv.selected_cons_idx = max(0, min(len(inv.consumables) - 1, inv.selected_cons_idx + 1))
                    elif k == pygame.K_w:
                        if self.inv_ui.tab == "weapons":
                            inv.selected_weapon_idx = max(0, inv.selected_weapon_idx - cols)
                        else:
                            inv.selected_cons_idx = max(0, inv.selected_cons_idx - cols)
                    elif k == pygame.K_s:
                        if self.inv_ui.tab == "weapons":
                            inv.selected_weapon_idx = min(len(inv.weapons) - 1, inv.selected_weapon_idx + cols)
                        else:
                            inv.selected_cons_idx = max(0, min(len(inv.consumables) - 1, inv.selected_cons_idx + cols))
                    elif k == pygame.K_e:
                        if self.inv_ui.tab == "weapons":
                            inv.equip_weapon(inv.selected_weapon_idx, self.player)
                    elif k == pygame.K_u:
                        if self.inv_ui.tab == "consumables":
                            idx = inv.selected_cons_idx
                            if 0 <= idx < len(inv.consumables):
                                item = inv.consumables[idx]
                                eff = item.data.get("effect", {})
                                was_cosmetic = eff.get("type") == "cosmetic"
                                ccolor = item.data.get("color", (200, 200, 255))
                            if inv.use_consumable(inv.selected_cons_idx, self.player) and was_cosmetic:
                                self.emitter.burst(self.player.x, self.player.y, ccolor,
                                                   count=25, speed=120, lifetime=0.8, size=4)
                    elif k == pygame.K_s:
                        if self.inv_ui.tab == "weapons":
                            inv.sell_weapon(inv.selected_weapon_idx, self.player)
                        else:
                            inv.sell_consumable(inv.selected_cons_idx, self.player)
                    elif k == pygame.K_q:
                        inv.remove_weapon(inv.selected_weapon_idx)
                    elif k == pygame.K_TAB:
                        self.inv_ui.tab = "consumables" if self.inv_ui.tab == "weapons" else "weapons"
                    return

        except Exception:
            pass

        if event.type == pygame.MOUSEBUTTONDOWN:
            try:
                if self.inv_ui.open and event.button == 1:
                    if self.inv_ui.handle_event(event, self.player.inventory, self.player):
                        return
                if event.button == 1 and (self.radial_menu.open or self.radial_menu.animating):
                    self.radial_menu.select_hovered(self.player.inventory, self.player)
                    self.radial_menu.toggle(self.player.inventory)
                    return
                if event.button == 1:
                    if self.selected_spell_index < len(self.player.equipped_spells):
                        spell = self.player.equipped_spells[self.selected_spell_index]
                        if self.combat.cast_spell(self.player, spell, event.pos, self.camera):
                            self.emitter.burst(
                                self.player.x + self.player.width // 2,
                                self.player.y + self.player.height // 2,
                                COLOR_VOID, count=5, speed=100, lifetime=0.3, size=3
                            )
                            if spell == SPELL_VOID_BOLT:
                                self.game.audio.play_sound("void_bolt")
                            elif spell == SPELL_CURSED_SLASH:
                                self.game.audio.play_sound("cursed_slash")
                            elif spell == SPELL_DARK_PULSE:
                                self.game.audio.play_sound("dark_pulse")
                            elif spell == SPELL_VOID_SHIELD:
                                self.game.audio.play_sound("void_shield")
                            elif spell == SPELL_DOMAIN_EXPANSION:
                                self.game.audio.play_sound("domain_expansion")
                            else:
                                self.game.audio.play_sound("void_bolt")
                        else:
                            self.game.audio.play_sound("spell_fail")
                elif event.button == 3:
                    atk = self.player.melee_attack()
                    if atk:
                        mx, my = self.camera.screen_to_world(*event.pos)
                        hits = self.combat.player_melee(self.player, mx, my, atk, self.enemies)
                        self.emitter.burst(
                            self.player.x + self.player.width // 2,
                            self.player.y + self.player.height // 2,
                            self.player.weapon["color"],
                            count=3, speed=50, lifetime=0.2, size=2
                        )
            except Exception:
                pass

    def _pickup_nearest_weapon(self):
        px = self.player.x + self.player.width // 2
        py = self.player.y + self.player.height // 2
        best = None
        best_dist = 50
        for drop in self.weapon_drops[:]:
            d = math.sqrt((drop.x - px) ** 2 + (drop.y - py) ** 2)
            if d < best_dist:
                best_dist = d
                best = drop
        if best:
            wdef = get_weapon(best.weapon_key)
            if wdef and self.player.inventory.add_weapon(wdef):
                self.weapon_drops.remove(best)
                self.player.inventory.equip_weapon(
                    len(self.player.inventory.weapons) - 1, self.player
                )
                self.pickup_notify_timer = 2.0
                self.pickup_notify_text = f"Equipped: {wdef['name']}"
                self.game.audio.play_sound("pickup")
                for _ in range(10):
                    self.emitter.burst(self.player.x, self.player.y, wdef["color"],
                                      count=3, speed=60, lifetime=0.3, size=2)

    def update(self, dt):
        self.input.update()
        self.cosmetic_shop.update(dt)
        self._update_shop_music()
        self.inv_ui.update(dt, self.player.inventory)
        self.shop_ui.update(dt)
        self.radial_menu.update(dt, self.player.inventory)
        if self.radial_menu.open or self.radial_menu.animating:
            self.radial_menu.update_hover(*pygame.mouse.get_pos())
        if self.paused or self.inv_ui.open or self.shop_ui.open or self.shop_ui.anim_t > 0 or self.cosmetic_shop.is_open() or self.radial_menu.open or self.radial_menu.animating:
            return
        self.player.update(dt, self.input)
        if hasattr(self.player, 'melee_cooldown') and self.player.melee_cooldown > 0:
            self.player.melee_cooldown -= dt

        phase = self.player.status.has("Phase")
        self.world.resolve_collision(self.player, phase=phase)
        self.world.clamp_entity(self.player)
        self.camera.update(dt)

        # ── Portal detection ──
        if not self.killzone_active and not self.death_state:
            px = self.player.x + self.player.width // 2
            py = self.player.y + self.player.height // 2
            player_center = pygame.Rect(px - 8, py - 8, 16, 16)
            for portal_rect in self.world.portals:
                if player_center.colliderect(portal_rect):
                    new_palette = palette_for_level(self.player.level)
                    if new_palette != self.world.palette_name:
                        self._regenerate_world(new_palette)
                    break

        for enemy in self.enemies[:]:
            can_phase = enemy.has_trait("phase")
            enemy.update(dt, self.player)
            if not can_phase:
                self.world.resolve_collision(enemy)
            self.world.clamp_entity(enemy)

        self.combat.update(dt, self.enemies, self.player)

        # ── Quest kill tracking (must run before _process_mutations clears killed_enemies) ──
        self.quest_notify_timer -= dt
        for qg in self.quest_givers:
            q = qg.quest
            if q and q.accepted and not q.completed:
                for enemy in self.combat.killed_enemies:
                    if not getattr(enemy, '_quest_counted', False):
                        enemy._quest_counted = True
                        q.add_kill()
                        if q.completed:
                            self.quest_notify_text = f"Quest complete! Return to claim {q.reward_coins} coins!"
                            self.quest_notify_timer = 4.0

        self._process_mutations()

        # ── Parry effects ──
        if self.player.parry_triggered:
            px, py = self.player.parry_pos
            self.game.audio.play_sound("parry")
            self.emitter.burst(px, py, (255, 255, 255), count=20, speed=150, lifetime=0.4, size=4)
            self.emitter.burst(px, py, (80, 200, 255), count=15, speed=120, lifetime=0.5, size=3)
            self.emitter.burst(px, py, (200, 100, 255), count=10, speed=180, lifetime=0.3, size=2)
            self.player.parry_triggered = False

        self.env_time += dt
        self.world.update(dt)

        # ── Ultimate state ──
        self.player.update_ult(dt)
        if self.ultimate_active and not self.player.ult_active:
            self.ultimate_active = False
            if self.ult_prev_state["boss"] and self.ult_prev_state["boss_key"]:
                self._play_boss_theme(self.ult_prev_state["boss_key"])
            elif self.ult_prev_state["battle"]:
                self.battle_active = True
                self.game.audio.crossfade_to("battle", BATTLE_THEME, 0.8)
            else:
                self.battle_active = False
                self.game.audio.crossfade_to("explore", EXPLORE_THEME, 0.8)

        # ── Soundtrack: detect battle state ──
        if not self.shop_music_active:
            self.theme_cooldown -= dt
        in_battle = False
        if not self.boss_theme_active and not self.ultimate_active and not self.shop_music_active and not self.killzone_active:
            if self.enemies:
                px = self.player.x + self.player.width // 2
                py = self.player.y + self.player.height // 2
                for enemy in self.enemies:
                    if not enemy.alive:
                        continue
                    ex = enemy.x + enemy.width // 2
                    ey = enemy.y + enemy.height // 2
                    dx = ex - px
                    dy = ey - py
                    if math.sqrt(dx * dx + dy * dy) < BATTLE_DETECTION_RANGE:
                        in_battle = True
                        break
            if in_battle and not self.battle_active and self.theme_cooldown <= 0:
                self.battle_active = True
                self.game.audio.crossfade_to("battle", BATTLE_THEME, 1.2)
            elif not in_battle and self.battle_active and self.theme_cooldown <= 0:
                self.battle_active = False
                self.game.audio.crossfade_to("explore", EXPLORE_THEME, 1.5)

        for drop_info in self.combat.weapon_drops_to_spawn[:]:
            guaranteed = drop_info.get("guaranteed", False)
            self.spawn_weapon_drop(drop_info["x"], drop_info["y"], drop_info["tier"], guaranteed=guaranteed)
        self.combat.weapon_drops_to_spawn.clear()

        for pdrop in self.combat.potion_drops_to_spawn[:]:
            if self.player.inventory.add_consumable(pdrop["key"]):
                self.emitter.burst(pdrop["x"], pdrop["y"], (80, 200, 255), count=3, speed=40, lifetime=0.3, size=2)
        self.combat.potion_drops_to_spawn.clear()

        for drop in self.weapon_drops[:]:
            drop.update(dt)

        if self.death_state:
            self.death_timer += dt
            fade_duration = 2.5
            self.death_fade_alpha = min(255, int(255 * (self.death_timer / fade_duration)))

            typewriter_delay = 0.5
            typewriter_speed = 0.12
            elapsed_after_delay = max(0, self.death_timer - typewriter_delay)
            chars_to_show = min(len(self.death_target), int(elapsed_after_delay / typewriter_speed))
            self.death_typewriter = self.death_target[:chars_to_show]

            self.emitter.update(dt)

            if self.death_timer >= 4.0 and not self.death_completed:
                self.death_completed = True
                self.game.switch_scene("game_over")
                self.death_state = None
            return

        if not self.player.alive and not self.death_completed:
            self.death_state = "dying"
            self.death_timer = 0.0
            self.death_fade_alpha = 0
            self.death_typewriter = ""
            self.boss_theme_active = False
            self.emitter.burst(
                self.player.x + self.player.width // 2,
                self.player.y + self.player.height // 2,
                (255, 50, 50), count=30, speed=120, lifetime=1.0, size=4
            )
            self.emitter.burst(
                self.player.x + self.player.width // 2,
                self.player.y + self.player.height // 2,
                (180, 20, 20), count=20, speed=80, lifetime=0.8, size=3
            )
            self.game.audio.crossfade_to("death", "data/audio/death.wav", 1.0)
            return

        self.emitter.update(dt)
        self.hud.update(dt, self.player)

        if self.level_up_timer > 0:
            self.level_up_timer -= dt
        if self.pickup_notify_timer > 0:
            self.pickup_notify_timer -= dt
        if self.boss_announce_timer > 0:
            self.boss_announce_timer -= dt
        if self.player.inventory.notify_timer > 0:
            self.player.inventory.notify_timer -= dt
        if self.mutation_notify_timer > 0:
            self.mutation_notify_timer -= dt

        # ── Dealer proximity ──
        self.nearby_dealer = None
        self.nearby_quest_giver = None
        px = self.player.x + self.player.width // 2
        py = self.player.y + self.player.height // 2
        for dealer in self.dealers:
            dealer.update(dt)
            dx = dealer.x - px
            dy = dealer.y - py
            if math.sqrt(dx * dx + dy * dy) < 60:
                self.nearby_dealer = dealer
        for qg in self.quest_givers:
            qg.update(dt)
            dx = qg.x - px
            dy = qg.y - py
            if math.sqrt(dx * dx + dy * dy) < 60:
                self.nearby_quest_giver = qg
        self.nearby_npc = None
        for npc in self.npcs[:]:
            if npc.used:
                self.npcs.remove(npc)
                continue
            npc.update(dt)
            dx = npc.x - px
            dy = npc.y - py
            if math.sqrt(dx * dx + dy * dy) < 60:
                self.nearby_npc = npc
        self.nearby_tree = None
        for tree in self.trees:
            tree.update(dt)
            dx = tree.x - px
            dy = tree.y - py
            if math.sqrt(dx * dx + dy * dy) < 50:
                self.nearby_tree = tree

        # ── Killzone logic ──
        if self.killzone_active:
            alive = sum(1 for e in self.enemies if e.alive and getattr(e, '_killzone', False))
            self.killzone_enemy_count = alive
            if alive == 0:
                self._complete_killzone()
        else:
            self.enemy_spawn_timer += dt
            dc = get_palette_config(self.world.palette_name)
            spawn_interval = max(0.3, (1.5 - self.player.level * 0.12) / dc["spawn"])
            if self.enemy_spawn_timer > spawn_interval:
                self.enemy_spawn_timer = 0
                max_enemies = int((40 + self.player.level * 8) * dc["max"])
                if len(self.enemies) < max_enemies:
                    self.spawn_enemy()

        # ── Boss spawn timer ──
        has_active_boss = any(e.alive and e.is_boss for e in self.enemies)
        self.boss_timer += dt
        if not has_active_boss and self.boss_timer >= self.boss_interval and self.player.level >= 3:
            self.boss_timer = 0
            dc = get_palette_config(self.world.palette_name)
            self.boss_interval = random.uniform(dc["boss_min"], dc["boss_max"])
            boss_key = get_boss_for_level(self.player.level)
            if boss_key:
                self._spawn_boss(boss_key)

        # ── Killzone trigger ──
        if self.player.total_kills >= 100 and not self.killzone_active:
            self._trigger_killzone()

        if random.random() < 0.3:
            self.emitter.stream(
                self.player.x + random.uniform(-50, 50),
                self.player.y + random.uniform(-50, 50),
                COLOR_VOID, rate=1, speed=20, lifetime=0.5, size=1
            )

        if self.shake_timer > 0:
            self.shake_timer -= dt
            ox = random.randint(-3, 3)
            oy = random.randint(-3, 3)
            self.shake_offset = (ox, oy)
        else:
            self.shake_offset = (0, 0)

        self.check_level_up()

    def check_level_up(self):
        if hasattr(self, '_last_level') and self._last_level < self.player.level:
            self.level_up_timer = 2.5
            self.shake_timer = 0.3
            self.game.audio.play_sound("level_up")
        self._last_level = self.player.level

    def render(self, surface):
        surface.fill(COLOR_BG)
        shake_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        shake_surf.fill(COLOR_BG)
        self.world.render(shake_surf, self.camera)

        # ── Spell range indicator ──
        mx, my = pygame.mouse.get_pos()
        wx, wy = self.camera.screen_to_world(mx, my)
        px = self.player.x + self.player.width // 2
        py = self.player.y + self.player.height // 2
        dx = wx - px
        dy = wy - py
        dist = math.sqrt(dx * dx + dy * dy)
        spell_rng = 180.0
        if dist > 5:
            nx, ny = dx / dist, dy / dist
            if dist > spell_rng:
                end_x = px + nx * spell_rng
                end_y = py + ny * spell_rng
                esx, esy = self.camera.world_to_screen(end_x, end_y)
                msx, msy = self.camera.world_to_screen(px, py)
                pygame.draw.line(shake_surf, (160, 120, 255, 40), (msx, msy), (esx, esy), 1)
                pygame.draw.circle(shake_surf, (160, 120, 255, 60), (esx, esy), 4, 1)
            else:
                msx, msy = self.camera.world_to_screen(px, py)
                pygame.draw.line(shake_surf, (160, 120, 255, 60), (msx, msy), (mx, my), 1)
                pygame.draw.circle(shake_surf, (100, 255, 200, 80), (mx, my), 3)

        for drop in self.weapon_drops:
            drop.render(shake_surf, self.camera)
        for tree in self.trees:
            tree.render(shake_surf, self.camera)
        for dealer in self.dealers:
            dealer.render(shake_surf, self.camera)
        for qg in self.quest_givers:
            qg.render(shake_surf, self.camera)
        for npc in self.npcs:
            npc.render(shake_surf, self.camera)
        for enemy in self.enemies:
            if enemy.alive:
                enemy.render(shake_surf, self.camera)
        self.combat.render(shake_surf, self.camera)
        self.player.render(shake_surf, self.camera)
        self.emitter.render(shake_surf, self.camera)

        bloomed = self.bloom.apply(shake_surf)
        surface.blit(bloomed, self.shake_offset)

        # ── Killzone grey tint ──
        if self.killzone_active:
            self.killzone_tint = min(1.0, self.killzone_tint + 0.02)
            tint_alpha = int(70 * self.killzone_tint)
            tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            tint_surf.fill((60, 60, 65, tint_alpha))
            surface.blit(tint_surf, (0, 0))
            # Enemy count
            try:
                kf = pygame.font.Font(FONT_PATH, 16)
                kt = kf.render(f"Enemies remaining: {self.killzone_enemy_count}", True, (200, 200, 200))
                kt.set_alpha(int(180 * self.killzone_tint))
                surface.blit(kt, (WINDOW_WIDTH // 2 - kt.get_width() // 2, 80))
            except:
                pass

        self.hud.render(surface, self.player, self.enemies)
        render_level_up_notification(surface, self.player, self.level_up_timer)

        # ── Difficulty label ──
        try:
            dc = get_palette_config(self.world.palette_name)
            df = pygame.font.Font(FONT_PATH, 14)
            dl = df.render(dc["label"], True, (180, 180, 200))
            surface.blit(dl, (10, 12))
        except:
            pass

        # Boss announcement
        if self.boss_announce_timer > 0:
            alpha = min(255, int(255 * min(1.0, self.boss_announce_timer)))
            pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)
            font = pygame.font.Font(FONT_PATH, int(36 * pulse))
            txt = font.render(self.boss_announce_text, True, (255, 200, 100))
            txt.set_alpha(alpha)
            tx = (WINDOW_WIDTH - txt.get_width()) // 2
            ty = WINDOW_HEIGHT // 2 - 80
            # Background bar
            bar_rect = pygame.Rect(tx - 20, ty - 8, txt.get_width() + 40, txt.get_height() + 16)
            bar_surf = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
            bar_surf.fill((40, 20, 10, int(120 * alpha / 255)))
            surface.blit(bar_surf, (bar_rect.x, bar_rect.y))
            pygame.draw.rect(surface, (255, 200, 100, int(180 * alpha / 255)), bar_rect, 2, border_radius=4)
            surface.blit(txt, (tx, ty))

        if self.pickup_notify_timer > 0:
            alpha = min(255, int(255 * min(1.0, self.pickup_notify_timer)))
            font = pygame.font.Font(FONT_PATH, 28)
            txt = font.render(self.pickup_notify_text, True, COLOR_GOLD)
            txt.set_alpha(alpha)
            tx = (WINDOW_WIDTH - txt.get_width()) // 2
            ty = WINDOW_HEIGHT // 2 - 60
            surface.blit(txt, (tx, ty))

        if self.inv_ui.open or self.inv_ui.anim_t > 0:
            self.inv_ui.render(surface, self.player.inventory)

        if self.craft_ui.open or self.craft_ui.anim_t > 0:
            self.craft_ui.render(surface, self.player)

        self.radial_menu.render(surface)

        if self.shop_ui.open or self.shop_ui.anim_t > 0:
            self.shop_ui.render(surface, self.player)

        if self.cosmetic_shop.is_open():
            self.cosmetic_shop.render(surface, self.player)

        if self.nearby_dealer and not self.shop_ui.open and not self.inv_ui.open:
            hint_alpha = int(80 + 60 * math.sin(pygame.time.get_ticks() * 0.003))
            try:
                hint_font = pygame.font.Font(FONT_PATH, 14)
                hint = hint_font.render("[G]  Trade with Dealer", True, (255, 215, 0))
                hint.set_alpha(hint_alpha)
                hx = (WINDOW_WIDTH - hint.get_width()) // 2
                hy = WINDOW_HEIGHT - 120
                surface.blit(hint, (hx, hy))
            except:
                pass

        if self.nearby_npc and not self.shop_ui.open and not self.inv_ui.open:
            from game.dialog import render_hint_key
            msg = "[G]  " + self.nearby_npc.def_name
            render_hint_key(surface, msg, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 140,
                           color=(200, 200, 255))

        if self.nearby_tree and not self.shop_ui.open and not self.inv_ui.open:
            from game.dialog import render_hint_key
            if self.player.level >= 5:
                msg = "[C]  Chop Tree"
                render_hint_key(surface, msg, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 120,
                               color=(140, 200, 100))
            else:
                msg = "[C]  Need Level 5"
                render_hint_key(surface, msg, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 120,
                               color=(180, 80, 80))

        if self.nearby_quest_giver and not self.shop_ui.open and not self.inv_ui.open:
            hint_alpha = int(80 + 60 * math.sin(pygame.time.get_ticks() * 0.003))
            try:
                hint_font = pygame.font.Font(FONT_PATH, 14)
                q = self.nearby_quest_giver.quest
                if q and q.completed and not q.claimed:
                    msg = "[G]  Claim Quest Reward"
                elif q and not q.accepted:
                    msg = "[G]  Accept Quest"
                else:
                    msg = None
                if msg:
                    hint = hint_font.render(msg, True, (80, 220, 255))
                    hint.set_alpha(hint_alpha)
                    hx = (WINDOW_WIDTH - hint.get_width()) // 2
                    hy = WINDOW_HEIGHT - 100
                    surface.blit(hint, (hx, hy))
            except:
                pass

        # ── Quest notification ──
        if self.quest_notify_timer > 0:
            try:
                qa = min(255, int(255 * min(1.0, self.quest_notify_timer)))
                qf = pygame.font.Font(FONT_PATH, 18)
                qt = qf.render(self.quest_notify_text, True, (80, 220, 255))
                qt.set_alpha(qa)
                qx = (WINDOW_WIDTH - qt.get_width()) // 2
                qy = WINDOW_HEIGHT - 160
                surface.blit(qt, (qx, qy))
            except:
                pass

        # ── Mutation notification ──
        if self.mutation_notify_timer > 0:
            try:
                ma = min(255, int(255 * min(1.0, self.mutation_notify_timer * 2)))
                mf = pygame.font.Font(FONT_PATH, 24)
                mt = mf.render(self.mutation_notify_text, True, (255, 200, 80))
                mt.set_alpha(ma)
                mx = (WINDOW_WIDTH - mt.get_width()) // 2
                my = WINDOW_HEIGHT // 2 - 80
                surface.blit(mt, (mx, my))
            except:
                pass

        # ── Active quest progress ──
        for qg in self.quest_givers:
            q = qg.quest
            if q and q.accepted and not q.claimed:
                try:
                    qf = pygame.font.Font(FONT_PATH, 13)
                    pct = min(1.0, q.kills / q.target_kills) if q.target_kills > 0 else 0
                    bar_w = 180
                    bar_h = 10
                    bar_x = 10
                    bar_y = WINDOW_HEIGHT - 30
                    bg_rect = pygame.Rect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2)
                    pygame.draw.rect(surface, (30, 25, 50), bg_rect, border_radius=3)
                    fill_w = int(bar_w * pct)
                    if fill_w > 0:
                        fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
                        pygame.draw.rect(surface, (80, 220, 255), fill_rect, border_radius=2)
                    txt = qf.render(f"{q.description} [{q.kills}/{q.target_kills}]", True, (180, 220, 240))
                    surface.blit(txt, (bar_x, bar_y - 16))
                except:
                    pass

        # ── Death animation overlay ──
        if self.death_state:
            # Fade to black overlay
            fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.death_fade_alpha)
            surface.blit(fade_surf, (0, 0))

            # Typewriter "YOU ARE DEAD"
            if self.death_typewriter:
                pulse = 1.0 + 0.08 * math.sin(pygame.time.get_ticks() * 0.004)
                font_size = int(56 * pulse)
                font = pygame.font.Font(FONT_PATH, font_size)
                txt = font.render(self.death_typewriter, True, (220, 30, 30))
                tx = (WINDOW_WIDTH - txt.get_width()) // 2
                ty = WINDOW_HEIGHT // 2 - 40
                # Glow behind text
                glow_surf = pygame.Surface((txt.get_width() + 40, txt.get_height() + 20), pygame.SRCALPHA)
                glow_alpha = int(60 + 60 * math.sin(pygame.time.get_ticks() * 0.003))
                pygame.draw.rect(glow_surf, (180, 20, 20, glow_alpha),
                                (0, 0, glow_surf.get_width(), glow_surf.get_height()),
                                border_radius=8)
                surface.blit(glow_surf, (tx - 20, ty - 10))
                # Main text
                txt.set_alpha(min(255, self.death_fade_alpha + 50))
                surface.blit(txt, (tx, ty))

        # ── Pause overlay ──
        if self.paused:
            dim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 160))
            surface.blit(dim, (0, 0))
            pause_font = pygame.font.Font(FONT_PATH, 48)
            pause_txt = pause_font.render("PAUSED", True, (200, 180, 255))
            tx = (WINDOW_WIDTH - pause_txt.get_width()) // 2
            ty = 120
            # Glow
            for i in range(4):
                gs = pygame.Surface((pause_txt.get_width() + 40, pause_txt.get_height() + 20), pygame.SRCALPHA)
                pygame.draw.rect(gs, (80, 60, 160, 30 - i * 5),
                                (0, 0, gs.get_width(), gs.get_height()), border_radius=10)
                surface.blit(gs, (tx - 20 + i * 2, ty - 10 + i * 2))
            surface.blit(pause_txt, (tx, ty))
            for btn in self.pause_buttons:
                btn.render(surface)
