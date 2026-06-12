import random

# ─── Weapon Type Constants ───────────────────────────────────────
DAGGER = "dagger"
SWORD = "sword"
GREATSWORD = "greatsword"
STAFF = "staff"
WAND = "wand"
BOW = "bow"
SPEAR = "spear"
SCYTHE = "scythe"
CHAKRAM = "chakram"
VOID_BLADE = "void_blade"
CURSED_BLADE = "cursed_blade"
FIST = "fist"
RED_BLADE = "red_blade"
LIFE_EDGE = "life_edge"
FORBIDDEN_FRUIT = "forbidden_fruit"

MELEE_TYPES = {DAGGER, SWORD, GREATSWORD, SPEAR, SCYTHE, VOID_BLADE, CURSED_BLADE, RED_BLADE, LIFE_EDGE}
RANGED_TYPES = {BOW, CHAKRAM}
MAGIC_TYPES = {STAFF, WAND, FORBIDDEN_FRUIT}

WEAPON_TIER_NAMES = {
    1: "Common", 2: "Uncommon", 3: "Rare",
    4: "Epic", 5: "Legendary", 6: "Mythic",
}


def make_weapon(key, name, wtype, tier, damage, magic, speed_bonus,
                defense, color, desc, effect=None, crit=0):
    return {
        "key": key,
        "name": name,
        "type": wtype,
        "tier": tier,
        "damage": damage,
        "magic": magic,
        "speed_bonus": speed_bonus,
        "defense": defense,
        "color": color,
        "description": desc,
        "effect": effect,
        "crit": crit,
    }


WEAPONS = [
    # ══════════════════════════════════════════════════════════════
    # TIER 1 — Common (8)
    # ══════════════════════════════════════════════════════════════
    make_weapon("fists", "Fists", FIST, 1, 2, 0, 0.0, 0,
                (200, 180, 160), "Your bare hands.", crit=0),

    make_weapon("rusty_dagger", "Rusty Dagger", DAGGER, 1, 4, 0, 0.08, 0,
                (160, 120, 80), "A worn dagger. Better than nothing.", crit=5),

    make_weapon("cracked_staff", "Cracked Staff", STAFF, 1, 1, 3, -0.05, 0,
                (120, 100, 80), "A splintered wooden staff. Channels weakly.", crit=0),

    make_weapon("worn_shortsword", "Worn Shortsword", SWORD, 1, 6, 0, 0.0, 1,
                (140, 140, 120), "A short blade, nicked and dull.", crit=2),

    make_weapon("makebow", "Makebow", BOW, 1, 5, 0, 0.03, 0,
                (130, 110, 80), "Crudely fashioned from branches.", crit=3),

    make_weapon("broken_spear", "Broken Spear", SPEAR, 1, 7, 0, -0.08, 2,
                (150, 130, 100), "Snapped in half but still sharp.", crit=2),

    make_weapon("twig_wand", "Twig Wand", WAND, 1, 0, 4, 0.05, 0,
                (100, 160, 100), "A living twig that hums faintly.", crit=0),

    make_weapon("chipped_chakram", "Chipped Chakram", CHAKRAM, 1, 5, 0, 0.05, 0,
                (180, 160, 120), "A throwing ring with dull edges.", crit=4),

    # ══════════════════════════════════════════════════════════════
    # TIER 2 — Uncommon (9)
    # ══════════════════════════════════════════════════════════════
    make_weapon("iron_dagger", "Iron Dagger", DAGGER, 2, 8, 0, 0.10, 0,
                (180, 160, 140), "A standard iron blade. Reliable.", crit=7),

    make_weapon("oak_staff", "Oak Staff", STAFF, 2, 2, 6, -0.03, 1,
                (140, 120, 80), "Sturdy oak, lightly attuned.", crit=0),

    make_weapon("longsword", "Longsword", SWORD, 2, 12, 0, 0.0, 3,
                (180, 180, 180), "A balanced steel longsword.", crit=3),

    make_weapon("hunters_bow", "Hunter's Bow", BOW, 2, 10, 0, 0.05, 0,
                (160, 130, 80), "Strung tight. Fires true.", crit=5),

    make_weapon("bronze_spear", "Bronze Spear", SPEAR, 2, 14, 0, -0.05, 4,
                (180, 150, 80), "Heavy bronze tip. Good reach.", crit=3),

    make_weapon("void_touched_dagger", "Void-Touched Dagger", DAGGER, 2, 9, 3, 0.08, 0,
                (120, 80, 160), "Gleams with faint void energy.", crit=8),

    make_weapon("quartz_wand", "Quartz Wand", WAND, 2, 1, 8, 0.08, 0,
                (200, 200, 240), "A clear quartz tip amplifies magic.", crit=0),

    make_weapon("battle_axe", "Battle Axe", GREATSWORD, 2, 16, 0, -0.12, 5,
                (160, 140, 120), "Heavy and devastating.", crit=2),

    make_weapon("iron_chakram", "Iron Chakram", CHAKRAM, 2, 10, 0, 0.07, 0,
                (180, 160, 160), "Well-balanced throwing ring.", crit=6),

    # ══════════════════════════════════════════════════════════════
    # TIER 3 — Rare (9)
    # ══════════════════════════════════════════════════════════════
    make_weapon("silver_rapier", "Silver Rapier", SWORD, 3, 18, 2, 0.12, 2,
                (220, 220, 240), "Elegant and precise.", crit=10),

    make_weapon("katana", "Katana", SWORD, 3, 22, 4, 0.15, 2,
                (200, 160, 255), "A curved blade that cuts through the void. Swift and sharp.", crit=12),

    make_weapon("void_staff", "Void Staff", STAFF, 3, 3, 12, 0.0, 2,
                (100, 60, 160), "Pulsing with void energy.", crit=2),

    make_weapon("scythe_of_thorns", "Scythe of Thorns", SCYTHE, 3, 22, 3, -0.08, 3,
                (100, 160, 60), "Wrapped in living thorn vines.", crit=6),

    make_weapon("cursed_blade", "Cursed Blade", CURSED_BLADE, 3, 20, 4, 0.03, 0,
                (160, 40, 60), "Whispers dark promises.", crit=8,
                effect="life_steal"),

    make_weapon("flame_wand", "Flame Wand", WAND, 3, 2, 14, 0.10, 0,
                (220, 120, 40), "Crackles with contained fire.", crit=2),

    make_weapon("spirit_bow", "Spirit Bow", BOW, 3, 16, 4, 0.07, 0,
                (140, 200, 220), "Arrows phase through armor.", crit=7,
                effect="armor_pierce"),

    make_weapon("void_chakram", "Void Chakram", CHAKRAM, 3, 16, 4, 0.08, 0,
                (120, 80, 180), "Leaves trails of void energy.", crit=8),

    make_weapon("guardian_spear", "Guardian Spear", SPEAR, 3, 24, 0, -0.03, 8,
                (160, 180, 200), "Wards off dark forces.", crit=4,
                effect="defense_up"),

    make_weapon("shadow_dagger", "Shadow Dagger", DAGGER, 3, 16, 3, 0.15, 0,
                (60, 40, 80), "Melts into darkness.", crit=14,
                effect="crit_up"),

    # ══════════════════════════════════════════════════════════════
    # TIER 4 — Epic (8)
    # ══════════════════════════════════════════════════════════════
    make_weapon("moonlight_greatsword", "Moonlight Greatsword", GREATSWORD, 4, 34, 6, -0.08, 6,
                (160, 200, 240), "Forged from a fallen star.", crit=5,
                effect="magic_boost"),

    make_weapon("void_reaper", "Void Reaper", SCYTHE, 4, 36, 8, -0.06, 4,
                (120, 60, 180), "Harvests souls for the void.", crit=8,
                effect="life_steal"),

    make_weapon("eldritch_staff", "Eldritch Staff", STAFF, 4, 4, 20, 0.02, 3,
                (80, 40, 120), "Contains knowledge from beyond.", crit=3),

    make_weapon("storm_bow", "Storm Bow", BOW, 4, 28, 6, 0.08, 2,
                (100, 120, 220), "Each arrow carries lightning.", crit=9,
                effect="chain"),

    make_weapon("inferno_blade", "Inferno Blade", SWORD, 4, 32, 5, 0.03, 4,
                (220, 80, 40), "Engulfed in eternal flame.", crit=6,
                effect="burn"),

    make_weapon("void_wand", "Void Wand", WAND, 4, 2, 22, 0.12, 1,
                (140, 80, 220), "Pure void crystal focus.", crit=2),

    make_weapon("phantom_chakram", "Phantom Chakram", CHAKRAM, 4, 26, 5, 0.10, 1,
                (180, 140, 220), "Passes through walls.", crit=10,
                effect="armor_pierce"),

    make_weapon("abyssal_spear", "Abyssal Spear", SPEAR, 4, 38, 4, -0.02, 10,
                (60, 40, 100), "Dragged from the deep dark.", crit=5,
                effect="defense_up"),

    make_weapon("red_blade", "Red Blade", RED_BLADE, 4, 34, 6, 0.18, 2,
                (220, 40, 40), "A crimson blade that drinks deep. High crit, burning rage.", crit=18,
                effect="burn"),

    make_weapon("blade_of_lifes_edge", "Blade of Life's Edge", LIFE_EDGE, 4, 30, 10, 0.10, 4,
                (80, 220, 120), "Drains life from foes with every cut.", crit=8,
                effect="life_steal"),

    make_weapon("forbidden_fruit", "Forbidden Fruit", FORBIDDEN_FRUIT, 4, 4, 24, 0.08, 2,
                (220, 80, 200), "Throwable void fruit. Explodes with chaotic magic.", crit=5),

    # ══════════════════════════════════════════════════════════════
    # TIER 5 — Legendary (8)
    # ══════════════════════════════════════════════════════════════
    make_weapon("soul_render", "Soul Render", GREATSWORD, 5, 52, 10, -0.05, 8,
                (200, 60, 80), "Feeds on the souls it slays.", crit=8,
                effect="life_steal"),

    make_weapon("void_arbiter", "Void Arbiter", VOID_BLADE, 5, 40, 18, 0.08, 6,
                (160, 100, 255), "Judges all who oppose the void.", crit=12,
                effect="void_brand"),

    make_weapon("cosmic_staff", "Cosmic Staff", STAFF, 5, 5, 32, 0.05, 5,
                (80, 100, 220), "Channels the cosmos themselves.", crit=4,
                effect="magic_boost"),

    make_weapon("doom_bow", "Doom Bow", BOW, 5, 42, 10, 0.10, 3,
                (180, 40, 40), "Predicts death with every shot.", crit=14,
                effect="chain"),

    make_weapon("twilight_scythe", "Twilight Scythe", SCYTHE, 5, 56, 12, -0.04, 6,
                (140, 80, 180), "Scythe of dusk and dawn.", crit=10,
                effect="void_brand"),

    make_weapon("stormbringer", "Stormbringer", SWORD, 5, 48, 8, 0.05, 6,
                (120, 140, 240), "Crackles with tempest fury.", crit=8,
                effect="chain"),

    make_weapon("infinite_chakram", "Infinite Chakram", CHAKRAM, 5, 40, 10, 0.15, 2,
                (200, 180, 255), "Never stops spinning.", crit=16,
                effect="crit_up"),

    make_weapon("world_end", "World-End", SPEAR, 5, 60, 6, -0.06, 14,
                (60, 20, 40), "The tip that ends all things.", crit=6,
                effect="defense_up"),

    # ══════════════════════════════════════════════════════════════
    # TIER 6 — Mythic (8)
    # ══════════════════════════════════════════════════════════════
    make_weapon("voidheart", "Voidheart", VOID_BLADE, 6, 60, 30, 0.12, 10,
                (180, 100, 255), "The heart of the void made blade.",
                effect="void_brand", crit=15),

    make_weapon("soul_eater", "Soul Eater", CURSED_BLADE, 6, 70, 15, 0.10, 8,
                (200, 40, 60), "Devours the essence of all it cuts.",
                effect="life_steal", crit=12),

    make_weapon("infinite_staff", "Infinite Staff", STAFF, 6, 8, 50, 0.08, 8,
                (100, 80, 255), "Contains a universe within.",
                effect="magic_boost", crit=5),

    make_weapon("apocalypse_bow", "Apocalypse Bow", BOW, 6, 60, 18, 0.15, 5,
                (220, 100, 40), "Fires bolts of pure devastation.",
                effect="chain", crit=18),

    make_weapon("quietus", "Quietus", SCYTHE, 6, 80, 18, 0.0, 10,
                (80, 40, 100), "The silence after the end.",
                effect="void_brand", crit=14),

    make_weapon("oblivion_blade", "Oblivion Blade", GREATSWORD, 6, 90, 14, -0.02, 14,
                (60, 20, 80), "Erases existence on contact.",
                effect="life_steal", crit=10),

    make_weapon("chaos_chakram", "Chaos Chakram", CHAKRAM, 6, 56, 20, 0.20, 4,
                (255, 100, 200), "Reality bends around its path.",
                effect="crit_up", crit=22),

    make_weapon("first_lance", "First Lance", SPEAR, 6, 100, 10, -0.04, 20,
                (200, 180, 160), "The spear that felled the first god.",
                effect="defense_up", crit=8),

    # ══════════════════════════════════════════════════════════════
    # TIER 1 — Common (+7)
    # ══════════════════════════════════════════════════════════════
    make_weapon("bone_dagger", "Bone Dagger", DAGGER, 1, 4, 0, 0.06, 0,
                (220, 200, 180), "Carved from a hollow beast's rib.", crit=4),
    make_weapon("driftwood_staff", "Driftwood Staff", STAFF, 1, 1, 3, -0.02, 0,
                (140, 120, 100), "Sea-worn wood with a faint hum.", crit=0),
    make_weapon("flint_knife", "Flint Knife", DAGGER, 1, 5, 0, 0.10, 0,
                (180, 140, 100), "Sharp flint edges. Brittle but deadly.", crit=6),
    make_weapon("reed_bow", "Reed Bow", BOW, 1, 4, 0, 0.04, 0,
                (160, 150, 120), "Light and easy to draw.", crit=3),
    make_weapon("clay_sword", "Clay Sword", SWORD, 1, 5, 1, -0.04, 1,
                (160, 120, 100), "Baked clay blade. Fragile.", crit=1),
    make_weapon("wooden_buckler", "Wooden Buckler", SWORD, 1, 3, 0, -0.06, 4,
                (150, 130, 100), "A small shield used as a blunt weapon.", crit=1),
    make_weapon("copper_wand", "Copper Wand", WAND, 1, 0, 4, 0.06, 0,
                (180, 120, 80), "Conducts magic poorly but reliably.", crit=0),

    # ══════════════════════════════════════════════════════════════
    # TIER 2 — Uncommon (+8)
    # ══════════════════════════════════════════════════════════════
    make_weapon("serrated_dagger", "Serrated Dagger", DAGGER, 2, 9, 1, 0.12, 0,
                (200, 160, 140), "Rips flesh on the way out.", crit=9),
    make_weapon("crystal_staff", "Crystal Staff", STAFF, 2, 2, 7, 0.0, 1,
                (160, 180, 220), "A small crystal amplifies will.", crit=1),
    make_weapon("scimitar", "Scimitar", SWORD, 2, 13, 0, 0.06, 2,
                (200, 180, 140), "Curved for sweeping strikes.", crit=5),
    make_weapon("short_spear", "Short Spear", SPEAR, 2, 13, 1, 0.0, 3,
                (170, 150, 120), "Compact and versatile.", crit=4),
    make_weapon("war_fan", "War Fan", CHAKRAM, 2, 9, 2, 0.10, 1,
                (200, 180, 200), "Deceptive. Sharp edges fold out.", crit=7),
    make_weapon("thorn_whip", "Thorn Whip", SCYTHE, 2, 11, 2, 0.02, 1,
                (120, 160, 60), "Barbed vines that bite deep.", crit=5,
                effect="burn"),
    make_weapon("pulse_staff", "Pulse Staff", STAFF, 2, 2, 6, 0.04, 0,
                (100, 140, 200), "Emits rhythmic energy pulses.", crit=0),
    make_weapon("hand_axe", "Hand Axe", GREATSWORD, 2, 15, 0, -0.08, 4,
                (180, 160, 140), "One-handed but packs a wallop.", crit=3),

    # ══════════════════════════════════════════════════════════════
    # TIER 3 — Rare (+8)
    # ══════════════════════════════════════════════════════════════
    make_weapon("frost_dagger", "Frost Dagger", DAGGER, 3, 15, 4, 0.14, 0,
                (160, 200, 240), "Leaves ice in its wake.", crit=11,
                effect="burn"),
    make_weapon("arcanists_staff", "Arcanist's Staff", STAFF, 3, 3, 13, 0.02, 2,
                (120, 80, 200), "Inscribed with ancient runes.", crit=2,
                effect="magic_boost"),
    make_weapon("war_hammer", "War Hammer", GREATSWORD, 3, 26, 1, -0.15, 8,
                (180, 180, 160), "Crushing force incarnate.", crit=3),
    make_weapon("recurve_bow", "Recurve Bow", BOW, 3, 18, 2, 0.08, 1,
                (180, 160, 100), "Twin curves for extra power.", crit=8),
    make_weapon("void_spear", "Void Spear", SPEAR, 3, 22, 4, -0.01, 5,
                (100, 60, 160), "Tipped with void crystal.", crit=5,
                effect="void_brand"),
    make_weapon("serpent_chakram", "Serpent Chakram", CHAKRAM, 3, 17, 3, 0.09, 1,
                (80, 200, 80), "Winding like a snake.", crit=9),
    make_weapon("blood_wand", "Blood Wand", WAND, 3, 2, 14, 0.09, 0,
                (180, 40, 40), "Pulsates with a warm heartbeat.", crit=1,
                effect="life_steal"),
    make_weapon("night_scythe", "Night Scythe", SCYTHE, 3, 24, 2, -0.06, 3,
                (40, 40, 80), "Drinks the light around it.", crit=7),

    # ══════════════════════════════════════════════════════════════
    # TIER 4 — Epic (+9)
    # ══════════════════════════════════════════════════════════════
    make_weapon("runeblade", "Runeblade", SWORD, 4, 32, 8, 0.04, 4,
                (160, 120, 200), "Glowing runes carve deeper wounds.", crit=7,
                effect="magic_boost"),
    make_weapon("sky_fury", "Sky Fury", BOW, 4, 30, 5, 0.12, 2,
                (180, 200, 240), "Arrows rain from above.", crit=10,
                effect="chain"),
    make_weapon("gravity_staff", "Gravity Staff", STAFF, 4, 4, 20, 0.0, 4,
                (120, 60, 120), "Bends space around the caster.", crit=2,
                effect="void_brand"),
    make_weapon("fang_of_asmodeus", "Fang of Asmodeus", DAGGER, 4, 28, 7, 0.18, 1,
                (200, 40, 60), "A demon's fang, still hungry.", crit=18,
                effect="life_steal"),
    make_weapon("crescent_axe", "Crescent Axe", GREATSWORD, 4, 40, 3, -0.10, 8,
                (200, 180, 100), "Moon-shaped blade of legend.", crit=5),
    make_weapon("needle_spear", "Needle Spear", SPEAR, 4, 34, 6, 0.06, 6,
                (200, 200, 220), "Thin as a needle, strikes like thunder.", crit=8,
                effect="armor_pierce"),
    make_weapon("ember_wand", "Ember Wand", WAND, 4, 2, 22, 0.14, 1,
                (240, 140, 40), "Trails of ember follow each spell.", crit=3,
                effect="burn"),
    make_weapon("void_scythe", "Void Scythe", SCYTHE, 4, 38, 7, -0.04, 5,
                (140, 80, 200), "Harvests the void itself.", crit=9,
                effect="void_brand"),
    make_weapon("echo_chakram", "Echo Chakram", CHAKRAM, 4, 28, 6, 0.12, 1,
                (120, 200, 220), "Each throw spawns a phantom copy.", crit=11,
                effect="chain"),

    # ══════════════════════════════════════════════════════════════
    # TIER 5 — Legendary (+9)
    # ══════════════════════════════════════════════════════════════
    make_weapon("excalibur", "Excalibur", SWORD, 5, 48, 12, 0.06, 8,
                (220, 220, 200), "The sword of sovereign right.", crit=10,
                effect="void_brand"),
    make_weapon("black_bow", "Black Bow", BOW, 5, 40, 12, 0.12, 3,
                (40, 40, 60), "Silent as the void between stars.", crit=15,
                effect="armor_pierce"),
    make_weapon("ark_staff", "Ark Staff", STAFF, 5, 6, 34, 0.06, 6,
                (160, 140, 255), "Fragment of the primordial ark.", crit=4,
                effect="magic_boost"),
    make_weapon("assassin_blade", "Assassin's Blade", DAGGER, 5, 38, 8, 0.22, 0,
                (100, 100, 120), "Strikes from the dark unseen.", crit=22,
                effect="crit_up"),
    make_weapon("titan_cleaver", "Titan Cleaver", GREATSWORD, 5, 64, 4, -0.10, 14,
                (160, 140, 120), "Hefted only by the worthy.", crit=5,
                effect="defense_up"),
    make_weapon("starlight_spear", "Starlight Spear", SPEAR, 5, 52, 10, 0.02, 10,
                (200, 220, 255), "Forged from a dying star.", crit=8,
                effect="chain"),
    make_weapon("vampiric_scythe", "Vampiric Scythe", SCYTHE, 5, 54, 10, -0.02, 5,
                (180, 20, 60), "Drinks deep of enemy vitality.", crit=11,
                effect="life_steal"),
    make_weapon("solar_wand", "Solar Wand", WAND, 5, 3, 34, 0.16, 2,
                (255, 220, 80), "Blazing core of a newborn sun.", crit=4,
                effect="burn"),
    make_weapon("hunter_chakram", "Hunter's Chakram", CHAKRAM, 5, 42, 8, 0.16, 2,
                (180, 220, 140), "Homes in on wounded prey.", crit=17,
                effect="crit_up"),

    # ══════════════════════════════════════════════════════════════
    # TIER 6 — Mythic (+9)
    # ══════════════════════════════════════════════════════════════
    make_weapon("godslayer", "Godslayer", GREATSWORD, 6, 88, 16, -0.01, 16,
                (220, 180, 60), "A blade that has tasted divinity.",
                effect="void_brand", crit=12),
    make_weapon("dream_staff", "Dream Staff", STAFF, 6, 7, 48, 0.10, 7,
                (200, 160, 255), "Woven from the fabric of dreams.",
                effect="magic_boost", crit=5),
    make_weapon("widowmaker", "Widowmaker", DAGGER, 6, 52, 14, 0.28, 2,
                (200, 200, 220), "One stab is all it takes.",
                effect="crit_up", crit=28),
    make_weapon("phoenix_bow", "Phoenix Bow", BOW, 6, 58, 20, 0.18, 4,
                (255, 160, 40), "Each shot ignites the air.",
                effect="burn", crit=16),
    make_weapon("worldsplitter", "Worldsplitter", SPEAR, 6, 96, 8, -0.02, 22,
                (100, 60, 40), "Cracks the earth with every thrust.",
                effect="defense_up", crit=7),
    make_weapon("reaper_song", "Reaper's Song", SCYTHE, 6, 82, 16, 0.02, 8,
                (200, 40, 80), "Whispers your name before striking.",
                effect="life_steal", crit=15),
    make_weapon("eternal_wand", "Eternal Wand", WAND, 6, 4, 52, 0.18, 3,
                (255, 200, 255), "Time itself obeys its wielder.",
                effect="magic_boost", crit=4),
    make_weapon("infinity_chakram", "Infinity Chakram", CHAKRAM, 6, 60, 18, 0.22, 3,
                (80, 80, 255), "Spins forever. Cuts everything.",
                effect="chain", crit=24),
    make_weapon("heretic_blade", "Heretic's Blade", CURSED_BLADE, 6, 74, 20, 0.08, 6,
                (180, 40, 200), "Cursed by the fallen. Blessed by the damned.",
                effect="void_brand", crit=14),
]

WEAPONS_BY_KEY = {w["key"]: w for w in WEAPONS}

TIER_WEAPONS = {t: [] for t in range(1, 7)}
for w in WEAPONS:
    if w["tier"] in TIER_WEAPONS:
        TIER_WEAPONS[w["tier"]].append(w["key"])


def get_weapon(key):
    return WEAPONS_BY_KEY.get(key)


def get_random_weapon(max_tier=6, exclude_key=None):
    pool = []
    for w in WEAPONS:
        if w["tier"] <= max_tier:
            if exclude_key and w["key"] == exclude_key:
                continue
            pool.append(w)
    if not pool:
        return None
    return random.choice(pool)


def get_weapon_drop(tier):
    tier = min(6, max(1, tier))
    available = []
    for t in range(1, tier + 1):
        for key in TIER_WEAPONS.get(t, []):
            available.append(key)
    if not available:
        available = list(TIER_WEAPONS.get(1, []))
    if not available:
        return None
    key = random.choice(available)
    return WEAPONS_BY_KEY[key]


# ═══════════════════════════════════════════════════════════════════
# GEM WEAPON VARIANTS (generated)
# ═══════════════════════════════════════════════════════════════════
_GEM_STATS = {
    "ruby":    {"damage": 1.4, "magic": 1.1, "crit": 0.1,  "speed_bonus": 0.0,  "defense": 0, "color": (220, 40, 60),   "label": "Ruby",    "tier_add": 0},
    "sapphire": {"damage": 1.3, "magic": 1.25,"crit": 0.05, "speed_bonus": 0.01, "defense": 0, "color": (40, 80, 220),   "label": "Sapphire", "tier_add": 0},
    "emerald": {"damage": 1.2, "magic": 1.4, "crit": 0.05, "speed_bonus": 0.01, "defense": 0, "color": (40, 200, 100),  "label": "Emerald",  "tier_add": 0},
    "diamond": {"damage": 1.5, "magic": 1.2, "crit": 0.15, "speed_bonus": 0.02, "defense": 1, "color": (200, 200, 255), "label": "Diamond",  "tier_add": 1},
    "gold":    {"damage": 1.6, "magic": 1.1, "crit": 0.1,  "speed_bonus": 0.03, "defense": 1, "color": (255, 200, 40),  "label": "Gold",     "tier_add": 1},
    "void":    {"damage": 2.0, "magic": 1.8, "crit": 0.3,  "speed_bonus": 0.04, "defense": 2, "color": (140, 60, 220),  "label": "Void",     "tier_add": 2},
}

_GEM_SUFFIX = {
    "ruby": "_ruby",
    "sapphire": "_sapphire",
    "emerald": "_emerald",
    "diamond": "_diamond",
    "gold": "_gold",
    "void": "_void",
}


def _build_gem_variants():
    variants = []
    for w in WEAPONS:
        if w["key"] == "fists":
            continue
        for gem, gmeta in _GEM_STATS.items():
            suffix = _GEM_SUFFIX[gem]
            new_key = w["key"] + suffix
            tier = min(6, w["tier"] + gmeta["tier_add"])
            dmg = max(1, int(w["damage"] * gmeta["damage"]))
            mag = max(0, int(w["magic"] * gmeta["magic"]))
            spd = round(w["speed_bonus"] + gmeta["speed_bonus"], 3)
            df = w["defense"] + gmeta["defense"]
            crit = w.get("crit", 0) + int(gmeta["crit"] * 100)
            desc = f"{gmeta['label']}-infused {w['name']}. {w['description']}"
            variants.append({
                "key": new_key, "name": f"{gmeta['label']} {w['name']}", "type": w["type"], "tier": tier,
                "damage": dmg, "magic": mag, "speed_bonus": spd, "defense": df,
                "color": gmeta["color"], "description": desc,
                "effect": w.get("effect"), "crit": crit,
                "base_key": w["key"], "gem": gem,
            })
    return variants


_GEM_WEAPONS = _build_gem_variants()
WEAPONS_BY_KEY.update({w["key"]: w for w in _GEM_WEAPONS})
for w in _GEM_WEAPONS:
    TIER_WEAPONS.setdefault(w["tier"], []).append(w["key"])


def get_gem_variant(base_key, gem):
    suffix = _GEM_SUFFIX.get(gem)
    if not suffix:
        return None
    return WEAPONS_BY_KEY.get(base_key + suffix)


def all_gem_weapons():
    return list(_GEM_WEAPONS)
