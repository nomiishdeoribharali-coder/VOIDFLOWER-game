import pygame
import math
import random
from game.constants import *
from game.constants import FONT_PATH

RECIPES = []

def make_recipe(key, name, wood_cost, coin_cost, output, desc, tier=1, color=(160, 120, 80), gem=None, gem_amount=0):
    rec = {
        "key": key, "name": name, "wood": wood_cost, "coins": coin_cost,
        "output": output, "desc": desc, "tier": tier, "color": color,
        "gem": gem, "gem_amount": gem_amount,
    }
    RECIPES.append(rec)
    return rec

# ─── Output format ─────────────────────────────────────────────────
# output = ("weapon", weapon_key)
# output = ("gem_weapon", base_key, gem)  — gem: ruby|sapphire|emerald|diamond|gold|void
# output = ("consumable", cons_key)
# output = ("upgrade", {"stat": "max_hp"|"max_mp"|"str"|"def"|"spd"|"mag", "amount": N})
# output = ("xp", amount)
# output = ("coins", amount)
# output = ("chest", {"capacity": N, "name": "..."})
# output = ("wall", {"hp": N})
# output = ("special", {"keys": [...], "desc": "..."})

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: WEAPONS (25)
# ═══════════════════════════════════════════════════════════════════
make_recipe("craft_club", "Wooden Club", 2, 0,
    ("weapon", "fists"), "A crude wooden club.", tier=1, color=(160, 120, 80))

make_recipe("craft_spear", "Wooden Spear", 3, 0,
    ("weapon", "broken_spear"), "A sharpened wooden spear.", tier=1, color=(150, 110, 70))

make_recipe("craft_bow", "Wooden Bow", 2, 0,
    ("weapon", "makebow"), "A simple shortbow.", tier=1, color=(170, 130, 90))

make_recipe("craft_staff", "Wooden Staff", 3, 0,
    ("weapon", "driftwood_staff"), "A channeling staff.", tier=1, color=(140, 120, 100))

make_recipe("craft_buckler", "Wooden Buckler", 2, 0,
    ("weapon", "wooden_buckler"), "A small wooden shield.", tier=1, color=(160, 140, 100))

make_recipe("craft_reinforced_club", "Reinforced Club", 5, 10,
    ("weapon", "hand_axe"), "A club bound with iron bands.", tier=2, color=(180, 140, 80))

make_recipe("craft_short_spear", "Short Spear", 5, 10,
    ("weapon", "short_spear"), "A balanced throwing spear.", tier=2, color=(170, 130, 80))

make_recipe("craft_hunters_bow", "Hunter's Bow", 6, 15,
    ("weapon", "hunters_bow"), "A sturdy hunting bow.", tier=2, color=(180, 150, 90))

make_recipe("craft_oak_staff", "Oak Staff", 5, 10,
    ("weapon", "oak_staff"), "Sturdy oak, lightly attuned.", tier=2, color=(140, 120, 80))

make_recipe("craft_thorn_whip", "Thorn Whip", 4, 8,
    ("weapon", "thorn_whip"), "A whip of woven thorn vines.", tier=2, color=(120, 160, 80))

make_recipe("craft_greatclub", "Oak Greatclub", 8, 20,
    ("weapon", "battle_axe"), "A massive oak club.", tier=3, color=(200, 160, 80))

make_recipe("craft_guardian_spear", "Guardian Spear", 8, 25,
    ("weapon", "guardian_spear"), "A spear blessed with bark.", tier=3, color=(160, 180, 100))

make_recipe("craft_recurve_bow", "Recurve Bow", 10, 25,
    ("weapon", "recurve_bow"), "A layered wood bow.", tier=3, color=(200, 170, 100))

make_recipe("craft_arcanist_staff", "Arcanist's Staff", 8, 20,
    ("weapon", "arcanists_staff"), "A staff inlaid with crystals.", tier=3, color=(160, 140, 200))

make_recipe("craft_war_hammer", "War Hammer", 12, 30,
    ("weapon", "war_hammer"), "A devastating wooden maul.", tier=3, color=(200, 160, 120))

make_recipe("craft_ironwood_spear", "Ironwood Spear", 12, 35,
    ("weapon", "void_spear"), "Spear of petrified ironwood.", tier=4, color=(120, 100, 80))

make_recipe("craft_composite_bow", "Composite Bow", 15, 40,
    ("weapon", "sky_fury"), "A masterwork composite bow.", tier=4, color=(220, 180, 100))

make_recipe("craft_runed_staff", "Runed Staff", 12, 35,
    ("weapon", "gravity_staff"), "A staff carved with runes.", tier=4, color=(160, 120, 200))

make_recipe("craft_crescent_axe", "Crescent Axe", 15, 45,
    ("weapon", "crescent_axe"), "A crescent-bladed wood axe.", tier=4, color=(200, 160, 100))

make_recipe("craft_echo_chakram", "Echo Chakram", 10, 30,
    ("weapon", "echo_chakram"), "A chakram of resonant wood.", tier=4, color=(180, 200, 140))

make_recipe("craft_ebony_blade", "Ebony Blade", 18, 60,
    ("weapon", "runeblade"), "A blade of dark ebony wood.", tier=5, color=(60, 40, 80))

make_recipe("craft_war_bow", "War Bow", 20, 70,
    ("weapon", "black_bow"), "A towering war bow.", tier=5, color=(180, 140, 80))

make_recipe("craft_elder_staff", "Elder Staff", 18, 65,
    ("weapon", "ark_staff"), "A staff from the World Tree.", tier=5, color=(180, 200, 160))

make_recipe("craft_titan_cleaver", "Titan Cleaver", 25, 80,
    ("weapon", "titan_cleaver"), "A slab of ancient petrified wood.", tier=6, color=(160, 120, 80))

make_recipe("craft_spiritwood_scythe", "Spiritwood Scythe", 25, 90,
    ("weapon", "vampiric_scythe"), "A scythe of living wood.", tier=6, color=(100, 180, 120))

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: CONSUMABLES (25)
# ═══════════════════════════════════════════════════════════════════
make_recipe("craft_wood_resin_i", "Wood Resin (Small)", 1, 0,
    ("consumable", "moonleaf"), "Crushed resin. Heals 22 HP.", tier=1, color=(140, 180, 100))

make_recipe("craft_wood_resin_ii", "Wood Resin (Medium)", 2, 3,
    ("consumable", "ember_root"), "Concentrated resin. Heals 55 HP.", tier=2, color=(180, 200, 100))

make_recipe("craft_wood_resin_iii", "Wood Resin (Large)", 4, 8,
    ("consumable", "golden_nectar"), "Pure wood essence. Heals 85 HP.", tier=3, color=(220, 200, 100))

make_recipe("craft_wood_resin_iv", "Wood Resin (Grand)", 6, 15,
    ("consumable", "vital_essence"), "Ancient resin. Heals 150 HP.", tier=4, color=(200, 220, 80))

make_recipe("craft_wood_resin_v", "Wood Resin (Royal)", 10, 30,
    ("consumable", "phoenix_fruit"), "Resin of the World Tree. Heals 55 HP.", tier=5, color=(255, 220, 80))

make_recipe("craft_mana_resin", "Mana Resin", 3, 5,
    ("consumable", "mana_biscuit"), "Sap infused with arcane energy. Restores 15 MP.", tier=2, color=(120, 160, 220))

make_recipe("craft_healing_salve", "Wood Poultice", 2, 2,
    ("consumable", "recovery_salve"), "A soothing wood poultice. Heals 20 HP.", tier=1, color=(160, 200, 140))

make_recipe("craft_great_poultice", "Great Wood Poultice", 5, 10,
    ("consumable", "regeneration_cream"), "A potent wood salve. Heals 130 HP.", tier=4, color=(140, 220, 160))

make_recipe("craft_bark_armor_i", "Bark Armor (Minor)", 2, 2,
    ("consumable", "stone_skin"), "Thick bark. +3 DEF for 12s.", tier=2, color=(120, 160, 100))

make_recipe("craft_bark_armor_ii", "Bark Armor (Major)", 5, 10,
    ("consumable", "fortress_potion"), "Ironwood bark. +10 DEF for 8s.", tier=4, color=(100, 200, 140))

make_recipe("craft_sap_elixir_i", "Sap Elixir (Strength)", 3, 5,
    ("consumable", "iron_heart"), "Fermented sap. +3 STR for 10s.", tier=2, color=(200, 140, 80))

make_recipe("craft_sap_elixir_ii", "Sap Elixir (Giants)", 8, 20,
    ("consumable", "giants_strength"), "Ancient tree sap. +8 STR for 8s.", tier=4, color=(220, 160, 80))

make_recipe("craft_sap_elixir_iii", "Sap Elixir (Titans)", 15, 40,
    ("consumable", "titans_brew"), "Primordial sap. +12 STR for 6s.", tier=5, color=(255, 180, 60))

make_recipe("craft_sap_tonic", "Sap Tonic (Speed)", 3, 5,
    ("consumable", "swift_step"), "Sap extract. +30 SPD for 8s.", tier=2, color=(140, 200, 220))

make_recipe("craft_wood_oil_i", "Wood Oil (Swift)", 4, 8,
    ("consumable", "wind_runner"), "Oil of the swiftwood. +50 SPD for 6s.", tier=3, color=(160, 220, 240))

make_recipe("craft_wood_oil_ii", "Wood Oil (Blitz)", 10, 25,
    ("consumable", "blitz_vial"), "Refined wood oil. +60 SPD for 5s.", tier=4, color=(200, 240, 255))

make_recipe("craft_bark_shield", "Bark Shield Tonic", 3, 5,
    ("consumable", "aegis_charm"), "Bark shield charm. +4 DEF for 14s.", tier=2, color=(100, 180, 140))

make_recipe("craft_sap_mantle", "Sap Mantle", 6, 15,
    ("consumable", "earth_mantle"), "A cloak of hardened sap. +6 DEF for 12s.", tier=3, color=(140, 120, 80))

make_recipe("craft_regen_poultice", "Regeneration Poultice", 4, 8,
    ("consumable", "sweet_dew"), "Heals 15 HP and 10 MP over time.", tier=2, color=(180, 220, 200))

make_recipe("craft_wood_infusion_i", "Wood Infusion (HP)", 3, 5,
    ("consumable", "arcane_infusion"), "Wood-arcane blend. Heals 50 HP and 30 MP.", tier=3, color=(160, 160, 255))

make_recipe("craft_wood_infusion_ii", "Wood Infusion (Soul)", 8, 20,
    ("consumable", "soul_essence"), "Soul-infused wood extract. Heals 90 HP and 60 MP.", tier=4, color=(200, 160, 255))

make_recipe("craft_cleanse_resin", "Cleansing Resin", 3, 5,
    ("consumable", "sun_blossom"), "Purifying tree resin. Heals 90 HP and cleanses.", tier=3, color=(255, 220, 120))

make_recipe("craft_great_cleanse", "Great Cleansing Resin", 8, 20,
    ("consumable", "abyssal_rose"), "Deepwood cleansing resin. Heals 140 HP.", tier=4, color=(200, 100, 140))

make_recipe("craft_wood_tome_i", "Wood Tome (Minor XP)", 3, 5,
    ("consumable", "crystal_lichen"), "A tome bound in bark. Gain XP.", tier=2, color=(180, 200, 180))

make_recipe("craft_wood_tome_ii", "Wood Tome (Major XP)", 8, 20,
    ("consumable", "ethereal_fern"), "A tome of living wood. Major XP.", tier=4, color=(200, 220, 200))

# ═══════════════════════════════════════════════════════════════════
# SECTION 3: UPGRADES (20) — permanent stat boosts that apply on craft
# ═══════════════════════════════════════════════════════════════════
make_recipe("craft_upgrade_hp_i", "Heartwood Vitality I", 5, 10,
    ("upgrade", {"stat": "max_hp", "amount": 10}), "+10 Max HP (permanent).", tier=2, color=(200, 80, 80))

make_recipe("craft_upgrade_hp_ii", "Heartwood Vitality II", 10, 25,
    ("upgrade", {"stat": "max_hp", "amount": 25}), "+25 Max HP (permanent).", tier=3, color=(220, 100, 100))

make_recipe("craft_upgrade_hp_iii", "Heartwood Vitality III", 18, 50,
    ("upgrade", {"stat": "max_hp", "amount": 50}), "+50 Max HP (permanent).", tier=4, color=(240, 120, 120))

make_recipe("craft_upgrade_hp_iv", "Heartwood Vitality IV", 28, 80,
    ("upgrade", {"stat": "max_hp", "amount": 100}), "+100 Max HP (permanent).", tier=5, color=(255, 140, 140))

make_recipe("craft_upgrade_mp_i", "Sap Mind I", 5, 10,
    ("upgrade", {"stat": "max_mp", "amount": 10}), "+10 Max MP (permanent).", tier=2, color=(80, 80, 200))

make_recipe("craft_upgrade_mp_ii", "Sap Mind II", 10, 25,
    ("upgrade", {"stat": "max_mp", "amount": 25}), "+25 Max MP (permanent).", tier=3, color=(100, 100, 220))

make_recipe("craft_upgrade_mp_iii", "Sap Mind III", 18, 50,
    ("upgrade", {"stat": "max_mp", "amount": 50}), "+50 Max MP (permanent).", tier=4, color=(120, 120, 240))

make_recipe("craft_upgrade_str_i", "Oak Strength I", 5, 10,
    ("upgrade", {"stat": "str", "amount": 1}), "+1 STR (permanent).", tier=2, color=(200, 160, 80))

make_recipe("craft_upgrade_str_ii", "Oak Strength II", 12, 30,
    ("upgrade", {"stat": "str", "amount": 2}), "+2 STR (permanent).", tier=3, color=(220, 180, 100))

make_recipe("craft_upgrade_str_iii", "Oak Strength III", 22, 60,
    ("upgrade", {"stat": "str", "amount": 3}), "+3 STR (permanent).", tier=5, color=(240, 200, 120))

make_recipe("craft_upgrade_def_i", "Ironbark Defense I", 5, 10,
    ("upgrade", {"stat": "def", "amount": 1}), "+1 DEF (permanent).", tier=2, color=(100, 180, 120))

make_recipe("craft_upgrade_def_ii", "Ironbark Defense II", 12, 30,
    ("upgrade", {"stat": "def", "amount": 2}), "+2 DEF (permanent).", tier=3, color=(120, 200, 140))

make_recipe("craft_upgrade_def_iii", "Ironbark Defense III", 22, 60,
    ("upgrade", {"stat": "def", "amount": 3}), "+3 DEF (permanent).", tier=5, color=(140, 220, 160))

make_recipe("craft_upgrade_spd_i", "Windwood Agility I", 5, 10,
    ("upgrade", {"stat": "spd", "amount": 10}), "+10 SPD (permanent).", tier=2, color=(140, 200, 220))

make_recipe("craft_upgrade_spd_ii", "Windwood Agility II", 12, 30,
    ("upgrade", {"stat": "spd", "amount": 20}), "+20 SPD (permanent).", tier=3, color=(160, 220, 240))

make_recipe("craft_upgrade_mag_i", "Glowwood Magic I", 5, 10,
    ("upgrade", {"stat": "mag", "amount": 1}), "+1 MAG (permanent).", tier=2, color=(160, 120, 200))

make_recipe("craft_upgrade_mag_ii", "Glowwood Magic II", 12, 30,
    ("upgrade", {"stat": "mag", "amount": 2}), "+2 MAG (permanent).", tier=3, color=(180, 140, 220))

make_recipe("craft_upgrade_mag_iii", "Glowwood Magic III", 22, 60,
    ("upgrade", {"stat": "mag", "amount": 3}), "+3 MAG (permanent).", tier=5, color=(200, 160, 240))

make_recipe("craft_upgrade_regen", "Regeneration Sap", 15, 35,
    ("upgrade", {"stat": "hp_regen", "amount": 1}), "+1 HP regen per second (permanent).", tier=4, color=(100, 220, 140))

make_recipe("craft_upgrade_mana_regen", "Mana Sap", 15, 35,
    ("upgrade", {"stat": "mp_regen", "amount": 1}), "+1 MP regen per second (permanent).", tier=4, color=(100, 140, 220))

# ═══════════════════════════════════════════════════════════════════
# SECTION 4: SPECIAL ITEMS (15)
# ═══════════════════════════════════════════════════════════════════
make_recipe("craft_xp_tome_i", "Wood XP Tome (Small)", 3, 5,
    ("xp", 50), "Grants 50 XP.", tier=2, color=(180, 200, 160))

make_recipe("craft_xp_tome_ii", "Wood XP Tome (Medium)", 6, 15,
    ("xp", 150), "Grants 150 XP.", tier=3, color=(200, 220, 180))

make_recipe("craft_xp_tome_iii", "Wood XP Tome (Large)", 12, 35,
    ("xp", 400), "Grants 400 XP.", tier=4, color=(220, 240, 200))

make_recipe("craft_xp_tome_iv", "Wood XP Tome (Grand)", 20, 60,
    ("xp", 1000), "Grants 1000 XP.", tier=5, color=(240, 255, 220))

make_recipe("craft_coin_pouch_i", "Wood Coin Pouch (Small)", 2, 0,
    ("coins", 20), "Craft into 20 coins.", tier=1, color=(200, 180, 100))

make_recipe("craft_coin_pouch_ii", "Wood Coin Pouch (Medium)", 5, 0,
    ("coins", 50), "Craft into 50 coins.", tier=2, color=(220, 200, 120))

make_recipe("craft_coin_pouch_iii", "Wood Coin Pouch (Large)", 12, 0,
    ("coins", 150), "Craft into 150 coins.", tier=3, color=(240, 220, 140))

make_recipe("craft_coin_pouch_iv", "Wood Coin Pouch (Grand)", 22, 0,
    ("coins", 400), "Craft into 400 coins.", tier=5, color=(255, 240, 160))

make_recipe("craft_sap_bomb", "Sap Bomb", 4, 8,
    ("consumable", "gas_bomb"), "A sticky sap bomb. Deals 20 poison over 6s.", tier=3, color=(140, 200, 100))

make_recipe("craft_refined_sap_bomb", "Refined Sap Bomb", 10, 25,
    ("consumable", "plague_bomb"), "A potent sap bomb. Deals 45 poison over 6s.", tier=5, color=(160, 220, 80))

make_recipe("craft_tangle_vial", "Tangle Vial", 5, 10,
    ("consumable", "curare_tip"), "A vial of tangling sap.", tier=2, color=(120, 180, 100))

make_recipe("craft_wood_repair_kit", "Wood Repair Kit", 3, 5,
    ("consumable", "health_potion"), "Repairs wooden gear. Heals 30 HP.", tier=2, color=(180, 160, 120))

make_recipe("craft_mystic_bark", "Mystic Bark Scroll", 8, 20,
    ("consumable", "guardian_elixir"), "Bark inscribed with wards. +7 DEF for 10s.", tier=3, color=(140, 200, 180))

make_recipe("craft_wood_key", "Wood Key", 10, 25,
    ("consumable", "fortress_stone"), "A strange wooden key. +4 DEF for 18s.", tier=3, color=(200, 180, 120))

make_recipe("craft_flare_log", "Flare Log", 2, 3,
    ("consumable", "ember_root"), "A slow-burning log. Heals 55 HP.", tier=2, color=(220, 160, 80))

# ═══════════════════════════════════════════════════════════════════
# SECTION 5: WALLS / BARRICADES (8) → grant DEF buff on use
# ═══════════════════════════════════════════════════════════════════
make_recipe("craft_wood_wall_i", "Wooden Barricade", 3, 0,
    ("consumable", "shield_herb"), "A basic barricade. +2 DEF for 15s.", tier=1, color=(160, 120, 80))

make_recipe("craft_wood_wall_ii", "Wooden Wall", 5, 5,
    ("consumable", "stone_skin"), "A solid wood wall. +3 DEF for 12s.", tier=2, color=(170, 130, 90))

make_recipe("craft_wood_wall_iii", "Reinforced Wall", 8, 15,
    ("consumable", "guardian_elixir"), "A reinforced wall. +7 DEF for 10s.", tier=3, color=(180, 140, 100))

make_recipe("craft_wood_wall_iv", "Ironwood Wall", 12, 30,
    ("consumable", "fortress_potion"), "A wall of petrified wood. +10 DEF for 8s.", tier=4, color=(140, 120, 80))

make_recipe("craft_spiked_barricade_i", "Spiked Barricade", 6, 10,
    ("consumable", "ironhide_scroll"), "A spiked barricade. +6 DEF for 8s.", tier=2, color=(180, 100, 80))

make_recipe("craft_spiked_barricade_ii", "Heavy Spiked Wall", 12, 25,
    ("consumable", "titanium_coating"), "A deadly spiked wall. +9 DEF for 8s.", tier=4, color=(200, 120, 80))

make_recipe("craft_ward_wall", "Warded Wood Wall", 10, 25,
    ("consumable", "void_armor"), "A wall with warding runes. +10 DEF for 8s.", tier=3, color=(140, 160, 200))

make_recipe("craft_gate", "Wooden Gate", 15, 40,
    ("consumable", "diamond_skin"), "A massive fortified gate. +15 DEF for 6s.", tier=5, color=(200, 180, 120))

# ═══════════════════════════════════════════════════════════════════
# SECTION 6: CHESTS / STORAGE (7) → reward coins on use
# ═══════════════════════════════════════════════════════════════════
make_recipe("craft_small_chest", "Small Wood Chest", 4, 5,
    ("consumable", "honeyed_ambrosia"), "A small chest. Grants rewards.", tier=1, color=(160, 140, 100))

make_recipe("craft_wood_chest", "Wood Chest", 8, 15,
    ("consumable", "sapphire"), "A standard chest. Worth 100 coins.", tier=2, color=(180, 160, 120))

make_recipe("craft_large_chest", "Large Wood Chest", 14, 30,
    ("consumable", "ancient_tablet"), "A large chest. Worth 160 coins.", tier=3, color=(200, 180, 140))

make_recipe("craft_reinforced_chest", "Reinforced Chest", 20, 50,
    ("consumable", "sapphire_crown"), "A reinforced chest. Worth 350 coins.", tier=4, color=(180, 160, 100))

make_recipe("craft_ironwood_chest", "Ironwood Chest", 28, 75,
    ("consumable", "astral_wine"), "A mighty ironwood chest. Restores 80 MP.", tier=5, color=(140, 120, 80))

make_recipe("craft_wardrobe", "Wooden Wardrobe", 10, 20,
    ("consumable", "golden_nectar"), "A wardrobe of cured wood. Heals 85 HP.", tier=3, color=(200, 180, 160))

make_recipe("craft_treasure_chest", "Treasure Chest", 5, 50,
    ("consumable", "phoenix_fruit"), "A golden-trimmed treasure chest. Heals 55 HP.", tier=2, color=(255, 215, 0))


# ═══════════════════════════════════════════════════════════════════
# GEM WEAPONS (generated)
# Format: base weapon key -> list of (gem_key, output_tuple)
# ═══════════════════════════════════════════════════════════════════
_GEM_PREFIXES = {
    "ruby":    ("Ruby",    3, 3, 20, (220, 40, 60)),
    "sapphire": ("Sapphire", 3, 3, 20, (40, 80, 220)),
    "emerald": ("Emerald", 3, 3, 20, (40, 200, 100)),
    "diamond": ("Diamond", 4, 4, 30, (200, 200, 255)),
    "gold":    ("Gold",    4, 4, 30, (255, 200, 40)),
    "void":    ("Void",    5, 5, 40, (140, 60, 220)),
}

_CRAFTABLE_BASE_WEAPONS = [
    "broken_spear", "makebow", "driftwood_staff", "wooden_buckler",
    "hand_axe", "short_spear", "hunters_bow", "oak_staff", "thorn_whip",
    "battle_axe", "guardian_spear", "recurve_bow", "arcanists_staff", "war_hammer",
    "void_spear", "sky_fury", "gravity_staff", "crescent_axe", "echo_chakram",
    "runeblade", "black_bow", "ark_staff", "titan_cleaver", "vampiric_scythe",
]

for base_key in _CRAFTABLE_BASE_WEAPONS:
    from game.weapons_inf import get_weapon
    base_w = get_weapon(base_key)
    if not base_w:
        continue
    for gem_key, (gem_label, gem_tier, wood_cost, coin_cost, gem_color) in _GEM_PREFIXES.items():
        suffix = f"_{gem_key}"
        out_key = f"{base_key}{suffix}"
        out = ("gem_weapon", (base_key, gem_key))
        make_recipe(
            f"craft_gem_{base_key}_{gem_key}",
            f"{gem_label} {base_w['name']}",
            wood_cost, coin_cost, out,
            f"{gem_label}-infused {base_w['name']}. {base_w['description']}",
            tier=gem_tier, color=gem_color, gem=gem_key, gem_amount=1,
        )


class CraftTable:
    def __init__(self):
        self.open = False
        self.anim_t = 0.0
        self.animating = False
        self.open_direction = 1
        self.time = 0.0
        self.selected_idx = 0
        self.font_large = pygame.font.Font(FONT_PATH, 28)
        self.font_med = pygame.font.Font(FONT_PATH, 18)
        self.font_small = pygame.font.Font(FONT_PATH, 14)

    def toggle(self):
        self.open_direction = 1 if not self.open else -1
        self.animating = True
        self.open = not self.open
        if self.open:
            self.selected_idx = 0

    def close(self):
        self.open_direction = -1
        self.animating = True
        self.open = False

    def update(self, dt):
        self.time += dt
        if self.animating:
            self.anim_t += dt * 4 * self.open_direction
            if self.anim_t <= 0 or self.anim_t >= 1:
                self.anim_t = max(0, min(1, self.anim_t))
                self.animating = False

    def craft_selected(self, player):
        if not RECIPES:
            return False
        idx = self.selected_idx
        if idx < 0 or idx >= len(RECIPES):
            return False
        recipe = RECIPES[idx]
        if player.wood < recipe["wood"]:
            return False
        if player.coins < recipe["coins"]:
            return False

        player.wood -= recipe["wood"]
        player.coins -= recipe["coins"]
        otype, odata = recipe["output"]

        if otype == "weapon":
            from game.weapons_inf import get_weapon
            wdef = get_weapon(odata)
            if wdef and player.inventory.add_weapon(wdef):
                return True
            player.wood += recipe["wood"]
            player.coins += recipe["coins"]
            return False

        if otype == "gem_weapon":
            base_key = ""
            gem = ""
            if isinstance(odata, tuple) and len(odata) == 2:
                base_key, gem = odata
            elif isinstance(odata, str):
                base_key = odata
                gem = recipe.get("gem", "")
            else:
                player.wood += recipe["wood"]
                player.coins += recipe["coins"]
                return False
            from game.weapons_inf import get_gem_variant
            wdef = get_gem_variant(base_key, gem)
            if wdef and player.inventory.add_weapon(wdef):
                return True
            player.wood += recipe["wood"]
            player.coins += recipe["coins"]
            return False

        if otype == "consumable":
            if player.inventory.add_consumable(odata):
                return True
            player.wood += recipe["wood"]
            player.coins += recipe["coins"]
            return False

        if otype == "upgrade":
            stat = odata["stat"]
            amount = odata["amount"]
            if not hasattr(player, "permanent_bonuses"):
                player.permanent_bonuses = {}
            current = player.permanent_bonuses.get(stat, 0)
            player.permanent_bonuses[stat] = current + amount
            if stat == "max_hp":
                player.max_hp += amount
                player.hp += amount
            elif stat == "max_mp":
                player.max_mp += amount
                player.mp += amount
            elif stat == "str":
                player.base_damage = getattr(player, "base_damage", 0) + amount
            elif stat == "def":
                player.base_defense = getattr(player, "base_defense", 0) + amount
            elif stat == "spd":
                player.speed = getattr(player, "speed", 120) + amount
            elif stat == "mag":
                player.base_magic = getattr(player, "base_magic", 0) + amount
            elif stat == "hp_regen":
                player.hp_regen = getattr(player, "hp_regen", 0) + amount
            elif stat == "mp_regen":
                player.mp_regen = getattr(player, "mp_regen", 0) + amount
            return True

        if otype == "xp":
            player.add_xp(odata)
            return True

        if otype == "coins":
            player.coins += odata
            return True

        return False

    def render(self, surface, player):
        if not self.open and self.anim_t == 0:
            return

        fade = self.anim_t
        panel_w = 640
        panel_h = 460
        panel_x = (WINDOW_WIDTH - panel_w) // 2
        panel_y = (WINDOW_HEIGHT - panel_h) // 2

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(100 * fade)))
        surface.blit(overlay, (0, 0))

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((12, 8, 24, int(230 * fade)))
        surface.blit(panel_surf, (panel_x, panel_y))

        border_pulse = 0.6 + 0.4 * math.sin(self.time * 1.5)
        bc = (int(160 * border_pulse), int(140 * border_pulse), 80)
        pygame.draw.rect(surface, bc, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=6)

        title = self.font_large.render("◇  C R A F T  ◇", True, (180, 200, 120))
        surface.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 8))

        res_text = self.font_small.render(f"Wood: {player.wood}   Coins: {player.coins}", True, (200, 200, 180))
        surface.blit(res_text, (panel_x + panel_w - res_text.get_width() - 14, panel_y + 14))

        if not RECIPES:
            empty = self.font_med.render("No recipes available.", True, (120, 110, 160))
            surface.blit(empty, (panel_x + panel_w // 2 - empty.get_width() // 2, panel_y + panel_h // 2))
            return

        list_x = panel_x + 16
        list_y = panel_y + 50
        slot_h = 46
        slot_gap = 3
        max_visible = min(len(RECIPES), 7)

        scroll_offset = max(0, self.selected_idx - max_visible + 1) if self.selected_idx >= max_visible else 0

        for i in range(max_visible):
            idx = i + scroll_offset
            if idx >= len(RECIPES):
                break
            recipe = RECIPES[idx]
            sy = list_y + i * (slot_h + slot_gap)
            slot_rect = pygame.Rect(list_x, sy, panel_w - 150, slot_h)
            is_selected = idx == self.selected_idx
            can_afford = player.wood >= recipe["wood"] and player.coins >= recipe["coins"]

            bg = (28, 22, 44) if is_selected else (16, 12, 30)
            pygame.draw.rect(surface, bg, slot_rect, border_radius=4)
            if is_selected:
                sel_pulse = 0.5 + 0.5 * math.sin(self.time * 4)
                sc = (int(140 * sel_pulse), int(180 * sel_pulse), 80)
                pygame.draw.rect(surface, sc, slot_rect, 2, border_radius=4)
            else:
                pygame.draw.rect(surface, (50, 45, 70), slot_rect, 1, border_radius=4)

            icon_rect = pygame.Rect(list_x + 5, sy + 6, 34, 34)
            icon_color = recipe["color"]
            pygame.draw.rect(surface, icon_color, icon_rect, border_radius=3)
            icon_label = {"weapon": "W", "consumable": "I", "upgrade": "U", "xp": "X", "coins": "C", "wall": "▣", "chest": "▤", "special": "?"}.get(recipe["output"][0], "?")
            il = self.font_small.render(icon_label, True, (0, 0, 0))
            surface.blit(il, (list_x + 5 + 17 - il.get_width() // 2, sy + 11))

            name_label = self.font_med.render(recipe["name"], True, (210, 200, 230))
            surface.blit(name_label, (list_x + 48, sy + 3))

            cost_label = self.font_small.render(f"🪵{recipe['wood']}", True, (160, 120, 80))
            if recipe["coins"] > 0:
                cost_label = self.font_small.render(f"🪵{recipe['wood']}  ✦{recipe['coins']}", True, (200, 190, 130) if recipe["coins"] > 0 else (160, 120, 80))
                if not can_afford:
                    if player.wood < recipe["wood"]:
                        cost_label = self.font_small.render(f"🪵{recipe['wood']}  ✦{recipe['coins']}", True, (200, 80, 80))
                    else:
                        cost_label = self.font_small.render(f"🪵{recipe['wood']}  ✦{recipe['coins']}", True, (200, 80, 80))
            surface.blit(cost_label, (list_x + 50, sy + 24))

            otype, odata = recipe["output"]
            tier_label = "★" * recipe["tier"]
            tl = self.font_small.render(tier_label, True, (180, 180, 120))
            surface.blit(tl, (panel_x + panel_w - 140, sy + 5))

        # ── Selected info box ──
        sel_recipe = RECIPES[self.selected_idx]
        info_x = panel_x + panel_w - 140
        info_y = list_y + 5
        desc_lines = self._wrap_text(sel_recipe["desc"], self.font_small, 130)
        for li, line in enumerate(desc_lines):
            dl = self.font_small.render(line, True, (160, 150, 180))
            surface.blit(dl, (info_x, info_y + li * 16))

        otype, odata = sel_recipe["output"]
        olabel = f"→ {otype.title()}"
        if otype == "wall":
            olabel += f": {odata.get('name', 'Wall')} (❤{odata['hp']})"
        elif otype == "chest":
            olabel += f": {odata.get('name', 'Chest')} ({odata['capacity']} slots)"
        ol = self.font_small.render(olabel, True, (200, 220, 180))
        surface.blit(ol, (info_x, info_y + 60))

        controls = self.font_small.render("[↑↓] Navigate  [Enter] Craft  [V] Close", True, (140, 130, 160))
        surface.blit(controls, (panel_x + panel_w // 2 - controls.get_width() // 2, panel_y + panel_h - 28))

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = current + " " + word if current else word
            if font.render(test, True, (0, 0, 0)).get_width() <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [""]
