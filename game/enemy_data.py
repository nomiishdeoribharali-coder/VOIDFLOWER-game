import pygame
import random
import math
from game.constants import *

# ─── AI Behavior Types ───────────────────────────────────────────
AI_WANDER = "wander"
AI_CHASE = "chase"
AI_AMBUSH = "ambush"
AI_TELEPORT = "teleport"
AI_KITE = "kite"
AI_ORBIT = "orbit"
AI_COPY = "copy"
AI_STATIONARY = "stationary"
AI_FLEE = "flee"
AI_HAZARD = "hazard"
AI_SUMMONER = "summoner"
AI_BURST = "burst"
AI_PHASE_WANDER = "phase_wander"
AI_BOSS = "boss"

# ─── Attack Types ────────────────────────────────────────────────
ATK_TOUCH = "touch"
ATK_MELEE = "melee"
ATK_PROJECTILE = "projectile"
ATK_SPORES = "spores"
ATK_LEECH = "leech"
ATK_POISON = "poison"
ATK_SLOW = "slow"
ATK_BURST = "burst"
ATK_SUMMON = "summon"
ATK_AOE = "aoe"
ATK_NONE = "none"
ATK_BEAM = "beam"
ATK_PULSE = "pulse"

# ─── Boss Attack Types ───────────────────────────────────────────
ATK_BOSS_TEARS = "boss_tears"
ATK_BOSS_LAUGH = "boss_laugh"
ATK_BOSS_THORNS = "boss_thorns"
ATK_BOSS_TENDRILS = "boss_tendrils"
ATK_BOSS_RAGE = "boss_rage"
ATK_BOSS_COPY = "boss_copy"
ATK_BOSS_OOZE = "boss_ooze"
ATK_BOSS_SOB = "boss_sob"
ATK_BOSS_HEAL = "boss_heal"
ATK_BOSS_VOID = "boss_void"

# ─── Traits ──────────────────────────────────────────────────────
TRAIT_SPLIT = "split"
TRAIT_INVISIBLE = "invisible"
TRAIT_PHASE = "phase"
TRAIT_BUFF_AURA = "buff_aura"
TRAIT_REGENERATES = "regenerates"
TRAIT_EXPLOSIVE = "explosive"
TRAIT_RARE = "rare"
TRAIT_HEAL_AURA = "heal_aura"
TRAIT_ILLUSION = "illusion"
TRAIT_BOSS = "boss"
TRAIT_BOSS_MINION = "boss_minion"

# ─── Tiers ───────────────────────────────────────────────────────
TIER_1 = 1
TIER_2 = 2
TIER_3 = 3
TIER_4 = 4
TIER_5 = 5
TIER_6 = 6


def make_enemy_def(
    name_key, display_name, tier, ai, attack, stats,
    color, traits=None, size=None, render_hint=None
):
    if size is None:
        size = 22
    defaults = {
        "hp": 30, "exp": 15, "damage": 8, "speed": 60,
        "attack_rate": 1.0, "detection_range": 250, "attack_range": 28,
    }
    defaults.update(stats)
    return {
        "key": name_key,
        "name": display_name,
        "tier": tier,
        "ai": ai,
        "attack": attack,
        "color": color,
        "size": size,
        "traits": traits or [],
        "render_hint": render_hint or "rect",
        "hp": defaults["hp"],
        "exp": defaults["exp"],
        "damage": defaults["damage"],
        "speed": defaults["speed"],
        "attack_rate": defaults["attack_rate"],
        "detection_range": defaults["detection_range"],
        "attack_range": defaults["attack_range"],
    }


ENEMY_TYPES = [

    # ════════════════════════════════════════════════════════════════
    # TIER 1 — Basic Void Wildlife
    # ════════════════════════════════════════════════════════════════

    make_enemy_def("void_mite", "Void Mite", TIER_1, AI_WANDER, ATK_TOUCH,
        {"hp": 8, "exp": 5, "damage": 3, "speed": 40, "attack_rate": 0.5,
         "detection_range": 0, "attack_range": 16},
        (160, 120, 200), size=14, render_hint="mite"),

    make_enemy_def("ash_crawler", "Ash Crawler", TIER_1, AI_AMBUSH, ATK_TOUCH,
        {"hp": 12, "exp": 7, "damage": 5, "speed": 80, "attack_rate": 1.0,
         "detection_range": 80, "attack_range": 20},
        (35, 30, 40), size=18, render_hint="crawler"),

    make_enemy_def("hollow_sprout", "Hollow Sprout", TIER_1, AI_STATIONARY, ATK_SPORES,
        {"hp": 15, "exp": 8, "damage": 4, "speed": 0, "attack_rate": 2.0,
         "detection_range": 180, "attack_range": 100},
        (60, 80, 50), size=20, render_hint="sprout"),

    make_enemy_def("drift_slime", "Drift Slime", TIER_1, AI_CHASE, ATK_TOUCH,
        {"hp": 18, "exp": 10, "damage": 4, "speed": 45, "attack_rate": 0.8,
         "detection_range": 180, "attack_range": 22},
        (100, 60, 140), size=22, traits=[TRAIT_SPLIT], render_hint="slime"),

    make_enemy_def("static_rat", "Static Rat", TIER_1, AI_TELEPORT, ATK_TOUCH,
        {"hp": 10, "exp": 6, "damage": 3, "speed": 60, "attack_rate": 0.6,
         "detection_range": 0, "attack_range": 18},
        (140, 130, 100), size=16, render_hint="rat"),

    # ════════════════════════════════════════════════════════════════
    # TIER 2 — Hunter Creatures
    # ════════════════════════════════════════════════════════════════

    make_enemy_def("void_hound", "Void Hound", TIER_2, AI_CHASE, ATK_MELEE,
        {"hp": 28, "exp": 15, "damage": 10, "speed": 100, "attack_rate": 0.8,
         "detection_range": 300, "attack_range": 26},
        (50, 40, 80), size=24, render_hint="hound"),

    make_enemy_def("lantern_leech", "Lantern Leech", TIER_2, AI_AMBUSH, ATK_LEECH,
        {"hp": 22, "exp": 13, "damage": 6, "speed": 70, "attack_rate": 1.5,
         "detection_range": 120, "attack_range": 24},
        (180, 140, 60), size=20, render_hint="leech"),

    make_enemy_def("echo_stalker", "Echo Stalker", TIER_2, AI_CHASE, ATK_MELEE,
        {"hp": 20, "exp": 14, "damage": 9, "speed": 85, "attack_rate": 1.0,
         "detection_range": 200, "attack_range": 24},
        (100, 90, 140), size=22, traits=[TRAIT_INVISIBLE], render_hint="stalker"),

    make_enemy_def("thorn_wisp", "Thorn Wisp", TIER_2, AI_KITE, ATK_PROJECTILE,
        {"hp": 18, "exp": 12, "damage": 7, "speed": 75, "attack_rate": 1.2,
         "detection_range": 280, "attack_range": 200},
        (200, 100, 160), size=18, render_hint="wisp"),

    make_enemy_def("broken_sentinel", "Broken Sentinel", TIER_2, AI_CHASE, ATK_MELEE,
        {"hp": 50, "exp": 20, "damage": 18, "speed": 35, "attack_rate": 1.8,
         "detection_range": 220, "attack_range": 30},
        (120, 100, 80), size=30, render_hint="sentinel"),

    # ════════════════════════════════════════════════════════════════
    # TIER 3 — Corrupted Entities
    # ════════════════════════════════════════════════════════════════

    make_enemy_def("petal_reaper", "Petal Reaper", TIER_3, AI_CHASE, ATK_MELEE,
        {"hp": 35, "exp": 22, "damage": 14, "speed": 70, "attack_rate": 1.0,
         "detection_range": 250, "attack_range": 30},
        (200, 80, 120), size=26, render_hint="reaper"),

    make_enemy_def("memory_husk", "Memory Husk", TIER_3, AI_COPY, ATK_TOUCH,
        {"hp": 30, "exp": 20, "damage": 10, "speed": 60, "attack_rate": 1.0,
         "detection_range": 0, "attack_range": 24},
        (80, 70, 90), size=24, render_hint="husk"),

    make_enemy_def("rift_walker", "Rift Walker", TIER_3, AI_TELEPORT, ATK_MELEE,
        {"hp": 25, "exp": 22, "damage": 12, "speed": 50, "attack_rate": 0.7,
         "detection_range": 260, "attack_range": 28},
        (140, 60, 180), size=22, render_hint="rift"),

    make_enemy_def("ink_parasite", "Ink Parasite", TIER_3, AI_BURST, ATK_LEECH,
        {"hp": 20, "exp": 18, "damage": 5, "speed": 90, "attack_rate": 2.0,
         "detection_range": 200, "attack_range": 20},
        (40, 20, 50), size=16, render_hint="parasite"),

    make_enemy_def("bloom_wraith", "Bloom Wraith", TIER_3, AI_PHASE_WANDER, ATK_TOUCH,
        {"hp": 22, "exp": 20, "damage": 10, "speed": 55, "attack_rate": 1.2,
         "detection_range": 0, "attack_range": 24},
        (140, 180, 200), size=24, traits=[TRAIT_PHASE], render_hint="wraith"),

    # ════════════════════════════════════════════════════════════════
    # TIER 4 — Void Intelligence
    # ════════════════════════════════════════════════════════════════

    make_enemy_def("void_strategist", "Void Strategist", TIER_4, AI_KITE, ATK_NONE,
        {"hp": 30, "exp": 28, "damage": 5, "speed": 55, "attack_rate": 3.0,
         "detection_range": 250, "attack_range": 200},
        (80, 60, 140), size=24, traits=[TRAIT_BUFF_AURA], render_hint="strategist"),

    make_enemy_def("fragment_clone", "Fragment Clone", TIER_4, AI_COPY, ATK_MELEE,
        {"hp": 28, "exp": 25, "damage": 12, "speed": 70, "attack_rate": 0.9,
         "detection_range": 0, "attack_range": 26},
        (180, 160, 220), size=22, render_hint="clone"),

    make_enemy_def("data_leech", "Data Leech", TIER_4, AI_CHASE, ATK_SLOW,
        {"hp": 25, "exp": 24, "damage": 5, "speed": 80, "attack_rate": 0.6,
         "detection_range": 220, "attack_range": 22},
        (60, 180, 160), size=18, render_hint="data_leech"),

    make_enemy_def("silent_executioner", "Silent Executioner", TIER_4, AI_BURST, ATK_BURST,
        {"hp": 35, "exp": 30, "damage": 25, "speed": 50, "attack_rate": 2.5,
         "detection_range": 280, "attack_range": 32},
        (60, 40, 80), size=26, render_hint="executioner"),

    make_enemy_def("root_network_node", "Root Network Node", TIER_4, AI_STATIONARY, ATK_SUMMON,
        {"hp": 60, "exp": 35, "damage": 0, "speed": 0, "attack_rate": 4.0,
         "detection_range": 200, "attack_range": 100},
        (80, 60, 50), size=32, render_hint="root_node"),

    # ════════════════════════════════════════════════════════════════
    # TIER 5 — Elite / Mini-Bosses
    # ════════════════════════════════════════════════════════════════

    make_enemy_def("withered_gardener", "Withered Gardener", TIER_5, AI_KITE, ATK_SUMMON,
        {"hp": 60, "exp": 50, "damage": 10, "speed": 45, "attack_rate": 3.0,
         "detection_range": 280, "attack_range": 150},
        (120, 80, 60), size=30, traits=[TRAIT_REGENERATES], render_hint="gardener"),

    make_enemy_def("hollow_bloom_beast", "Hollow Bloom Beast", TIER_5, AI_CHASE, ATK_POISON,
        {"hp": 80, "exp": 55, "damage": 12, "speed": 40, "attack_rate": 1.5,
         "detection_range": 260, "attack_range": 36},
        (140, 60, 80), size=36, render_hint="bloom_beast"),

    make_enemy_def("rift_colossus", "Rift Colossus", TIER_5, AI_CHASE, ATK_AOE,
        {"hp": 120, "exp": 65, "damage": 20, "speed": 25, "attack_rate": 2.5,
         "detection_range": 250, "attack_range": 40},
        (60, 40, 80), size=40, render_hint="colossus"),

    make_enemy_def("mirror_warden", "Mirror Warden", TIER_5, AI_ORBIT, ATK_BEAM,
        {"hp": 50, "exp": 50, "damage": 14, "speed": 30, "attack_rate": 1.8,
         "detection_range": 300, "attack_range": 180},
        (160, 140, 200), size=28, traits=[TRAIT_ILLUSION], render_hint="warden"),

    make_enemy_def("seedless_king", "Seedless King", TIER_5, AI_TELEPORT, ATK_PULSE,
        {"hp": 90, "exp": 70, "damage": 18, "speed": 60, "attack_rate": 2.0,
         "detection_range": 300, "attack_range": 200},
        (180, 100, 60), size=34, render_hint="seedless"),

    # ════════════════════════════════════════════════════════════════
    # TIER 6 — World Events / Rare Entities
    # ════════════════════════════════════════════════════════════════

    make_enemy_def("void_bloom_storm", "Void Bloom Storm", TIER_6, AI_HAZARD, ATK_POISON,
        {"hp": 40, "exp": 30, "damage": 8, "speed": 60, "attack_rate": 0.5,
         "detection_range": 0, "attack_range": 40},
        (100, 40, 120), size=30, render_hint="storm"),

    make_enemy_def("wanderer_of_nothing", "Wanderer of Nothing", TIER_6, AI_FLEE, ATK_NONE,
        {"hp": 15, "exp": 40, "damage": 0, "speed": 120, "attack_rate": 0,
         "detection_range": 0, "attack_range": 0},
        (200, 200, 220), size=20, traits=[TRAIT_RARE], render_hint="wanderer"),

    make_enemy_def("broken_god_shard", "Broken God Shard", TIER_6, AI_ORBIT, ATK_BEAM,
        {"hp": 50, "exp": 45, "damage": 16, "speed": 40, "attack_rate": 1.0,
         "detection_range": 280, "attack_range": 220},
        (220, 180, 100), size=26, traits=[TRAIT_RARE], render_hint="god_shard"),

    make_enemy_def("glitch_angel", "Glitch Angel", TIER_6, AI_TELEPORT, ATK_TOUCH,
        {"hp": 40, "exp": 50, "damage": 10, "speed": 90, "attack_rate": 1.0,
         "detection_range": 0, "attack_range": 28},
        (200, 160, 220), size=28, traits=[TRAIT_HEAL_AURA, TRAIT_RARE], render_hint="angel"),

    make_enemy_def("quiet_root", "Quiet Root", TIER_6, AI_STATIONARY, ATK_NONE,
        {"hp": 999, "exp": 100, "damage": 0, "speed": 0, "attack_rate": 0,
         "detection_range": 0, "attack_range": 0},
        (40, 60, 50), size=38, traits=[TRAIT_RARE], render_hint="quiet_root"),

    # ════════════════════════════════════════════════════════════════
    # EMOTION BOSSES
    # ════════════════════════════════════════════════════════════════

    make_enemy_def("sorrow", "Sorrow", TIER_5, AI_BOSS, ATK_BOSS_TEARS,
        {"hp": 1000, "exp": 300, "damage": 18, "speed": 35, "attack_rate": 2.5,
         "detection_range": 400, "attack_range": 220},
        (100, 130, 170), size=34, traits=[TRAIT_BOSS], render_hint="boss_sorrow"),

    make_enemy_def("joy", "Joy", TIER_5, AI_BOSS, ATK_BOSS_LAUGH,
        {"hp": 1200, "exp": 300, "damage": 16, "speed": 90, "attack_rate": 1.8,
         "detection_range": 400, "attack_range": 200},
        (240, 180, 200), size=28, traits=[TRAIT_BOSS], render_hint="boss_joy"),

    make_enemy_def("fear", "Fear", TIER_5, AI_BOSS, ATK_BOSS_TENDRILS,
        {"hp": 1500, "exp": 350, "damage": 14, "speed": 50, "attack_rate": 2.0,
         "detection_range": 450, "attack_range": 250},
        (80, 40, 100), size=32, traits=[TRAIT_BOSS], render_hint="boss_fear"),

    make_enemy_def("pain", "Pain", TIER_5, AI_BOSS, ATK_BOSS_THORNS,
        {"hp": 2500, "exp": 400, "damage": 24, "speed": 45, "attack_rate": 2.0,
         "detection_range": 350, "attack_range": 180},
        (200, 40, 60), size=36, traits=[TRAIT_BOSS], render_hint="boss_pain"),

    make_enemy_def("rage", "Rage", TIER_6, AI_BOSS, ATK_BOSS_RAGE,
        {"hp": 4000, "exp": 500, "damage": 32, "speed": 70, "attack_rate": 1.5,
         "detection_range": 400, "attack_range": 160},
        (220, 100, 40), size=38, traits=[TRAIT_BOSS], render_hint="boss_rage"),

    make_enemy_def("envy", "Envy", TIER_6, AI_BOSS, ATK_BOSS_COPY,
        {"hp": 3000, "exp": 500, "damage": 20, "speed": 60, "attack_rate": 2.0,
         "detection_range": 400, "attack_range": 240},
        (60, 140, 80), size=30, traits=[TRAIT_BOSS], render_hint="boss_envy"),

    make_enemy_def("disgust", "Disgust", TIER_6, AI_BOSS, ATK_BOSS_OOZE,
        {"hp": 5000, "exp": 600, "damage": 18, "speed": 25, "attack_rate": 3.0,
         "detection_range": 350, "attack_range": 200},
        (100, 180, 80), size=40, traits=[TRAIT_BOSS], render_hint="boss_disgust"),

    make_enemy_def("grief", "Grief", TIER_6, AI_BOSS, ATK_BOSS_SOB,
        {"hp": 4500, "exp": 600, "damage": 22, "speed": 30, "attack_rate": 3.5,
         "detection_range": 400, "attack_range": 260},
        (180, 200, 220), size=36, traits=[TRAIT_BOSS], render_hint="boss_grief"),

    make_enemy_def("hope", "Hope", TIER_6, AI_BOSS, ATK_BOSS_HEAL,
        {"hp": 7000, "exp": 800, "damage": 28, "speed": 40, "attack_rate": 2.5,
         "detection_range": 350, "attack_range": 200},
        (220, 200, 180), size=34, traits=[TRAIT_BOSS, TRAIT_REGENERATES], render_hint="boss_hope"),

    make_enemy_def("despair", "Despair", TIER_6, AI_BOSS, ATK_BOSS_VOID,
        {"hp": 9000, "exp": 1000, "damage": 35, "speed": 55, "attack_rate": 2.0,
         "detection_range": 450, "attack_range": 280},
        (30, 20, 50), size=38, traits=[TRAIT_BOSS], render_hint="boss_despair"),

]

ENEMY_BY_KEY = {e["key"]: e for e in ENEMY_TYPES}

TIER_ENEMIES = {t: [] for t in range(1, 7)}
BOSS_KEYS = []
for e in ENEMY_TYPES:
    if TRAIT_BOSS in e["traits"]:
        BOSS_KEYS.append(e["key"])
    else:
        TIER_ENEMIES[e["tier"]].append(e["key"])


def get_enemies_for_level(level):
    available = []
    if level <= 2:
        available.extend(TIER_ENEMIES[TIER_1])
    if level >= 2:
        available.extend(TIER_ENEMIES[TIER_2])
    if level >= 4:
        available.extend(TIER_ENEMIES[TIER_3])
    if level >= 6:
        available.extend(TIER_ENEMIES[TIER_4][:3])
    if level >= 8:
        available.extend(TIER_ENEMIES[TIER_4][3:])
    if level >= 10:
        available.extend(TIER_ENEMIES[TIER_5])
    if level >= 12:
        available.extend(TIER_ENEMIES[TIER_6])
    if not available:
        available = list(TIER_ENEMIES[TIER_1])
    return available


def get_enemy_def(key):
    return ENEMY_BY_KEY.get(key)


def get_enemy_weighted(level, exclude=None):
    pool = get_enemies_for_level(level)
    if not pool:
        pool = list(TIER_ENEMIES[TIER_1])
    # Weight by tier — lower tiers are more common at every level
    weights = []
    for key in pool:
        edef = ENEMY_BY_KEY[key]
        if exclude and key in exclude:
            weights.append(0)
        else:
            weights.append(max(1, 6 - edef["tier"] + max(0, 5 - level)))
    total = sum(weights)
    if total == 0:
        return pool[0]
    r = random.uniform(0, total)
    cumulative = 0
    for i, key in enumerate(pool):
        cumulative += weights[i]
        if r <= cumulative:
            return key
    return pool[-1]


def get_boss_for_level(level):
    available = []
    if level >= 3:
        available.extend(["sorrow"])
    if level >= 5:
        available.extend(["joy", "fear"])
    if level >= 7:
        available.extend(["pain"])
    if level >= 9:
        available.extend(["rage", "envy", "disgust"])
    if level >= 11:
        available.extend(["grief"])
    if level >= 14:
        available.extend(["hope", "despair"])
    if not available:
        return None
    return random.choice(available)
