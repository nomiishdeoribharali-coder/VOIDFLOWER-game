import pygame
import math
import random
from game.constants import *
from engine.ui import Text
from game.constants import FONT_PATH

# ─── Consumable Definitions ───────────────────────────────────────

def make_item(key, name, item_type, effect, color, desc, tier=1):
    return {
        "key": key, "name": name, "item_type": item_type,
        "effect": effect, "color": color, "desc": desc, "tier": tier,
    }

# Effect types:
#   heal:    {"type": "heal", "hp": N, "mp": N}
#   poison:  {"type": "poison", "damage": N, "duration": N}
#   death:   {"type": "death", "chance": 0.0-1.0}
#   buff:    {"type": "buff", "stat": "str"|"def"|"spd"|"mag", "amount": N, "duration": N}
#   money:   {"type": "money", "coins": N}

# ═══════════════════════════════════════════════════════════════════
# 300 ITEMS — organized by effect
# ═══════════════════════════════════════════════════════════════════
ITEMS = []

# ─── HEALING (80) ─────────────────────────────────────────────────
_HEAL = [
    ("minor_potion", "Minor Healing Potion", "potion", {"type": "heal", "hp": 15}, (220, 80, 80), "A weak restorative.", 1),
    ("healing_potion", "Healing Potion", "potion", {"type": "heal", "hp": 35}, (230, 100, 90), "Restores 35 HP.", 1),
    ("strong_healing", "Strong Healing Potion", "potion", {"type": "heal", "hp": 60}, (240, 120, 100), "Restores 60 HP.", 2),
    ("superior_healing", "Superior Healing Potion", "potion", {"type": "heal", "hp": 100}, (255, 140, 110), "Restores 100 HP.", 3),
    ("grand_healing", "Grand Healing Potion", "potion", {"type": "heal", "hp": 160}, (255, 160, 120), "Restores 160 HP.", 4),
    ("royal_elixir", "Royal Elixir", "potion", {"type": "heal", "hp": 250}, (255, 180, 130), "Restores 250 HP.", 5),
    ("life_tincture", "Life Tincture", "potion", {"type": "heal", "hp": 400}, (255, 200, 140), "Restores 400 HP.", 6),
    ("void_ambrosia", "Void Ambrosia", "potion", {"type": "heal", "hp": 999}, (200, 120, 255), "Full HP restoration.", 6),
    ("mana_potion", "Mana Potion", "potion", {"type": "heal", "mp": 20}, (80, 120, 220), "Restores 20 MP.", 1),
    ("strong_mana", "Strong Mana Potion", "potion", {"type": "heal", "mp": 45}, (90, 140, 230), "Restores 45 MP.", 2),
    ("superior_mana", "Superior Mana Potion", "potion", {"type": "heal", "mp": 80}, (100, 160, 240), "Restores 80 MP.", 3),
    ("grand_mana", "Grand Mana Potion", "potion", {"type": "heal", "mp": 130}, (110, 180, 250), "Restores 130 MP.", 4),
    ("arcane_elixir", "Arcane Elixir", "potion", {"type": "heal", "mp": 200}, (120, 200, 255), "Restores 200 MP.", 5),
    ("soul_restore", "Soul Restore", "potion", {"type": "heal", "mp": 999}, (160, 100, 255), "Full MP restoration.", 6),
    ("rejuvenation_draught", "Rejuvenation Draught", "potion", {"type": "heal", "hp": 25, "mp": 15}, (160, 180, 200), "Restores 25 HP and 15 MP.", 2),
    ("greater_rejuvenation", "Greater Rejuvenation", "potion", {"type": "heal", "hp": 60, "mp": 40}, (170, 200, 220), "Restores 60 HP and 40 MP.", 4),
    ("voidbloom_petal", "Voidbloom Petal", "herb", {"type": "heal", "hp": 10}, (180, 100, 200), "A shimmering petal. Heals 10 HP.", 1),
    ("moonleaf", "Moonleaf", "herb", {"type": "heal", "hp": 22}, (140, 200, 180), "Heals 22 HP.", 1),
    ("starlight_moss", "Starlight Moss", "herb", {"type": "heal", "hp": 30}, (100, 180, 220), "Heals 30 HP.", 1),
    ("crystal_lichen", "Crystal Lichen", "herb", {"type": "heal", "hp": 45}, (200, 180, 255), "Heals 45 HP.", 2),
    ("ember_root", "Ember Root", "herb", {"type": "heal", "hp": 55}, (220, 140, 60), "Heals 55 HP.", 2),
    ("frost_flower", "Frost Flower", "herb", {"type": "heal", "hp": 50}, (120, 200, 255), "Heals 50 HP.", 2),
    ("shadow_cap", "Shadow Cap", "herb", {"type": "heal", "hp": 70}, (100, 60, 140), "Heals 70 HP.", 3),
    ("sun_blossom", "Sun Blossom", "herb", {"type": "heal", "hp": 90}, (255, 220, 80), "Heals 90 HP.", 3),
    ("abyssal_rose", "Abyssal Rose", "herb", {"type": "heal", "hp": 140}, (180, 40, 100), "Heals 140 HP.", 4),
    ("ethereal_fern", "Ethereal Fern", "herb", {"type": "heal", "hp": 200}, (200, 180, 255), "Heals 200 HP.", 5),
    ("honeyed_ambrosia", "Honeyed Ambrosia", "food", {"type": "heal", "hp": 18}, (240, 200, 80), "A sweet treat. Heals 18 HP.", 1),
    ("phoenix_fruit", "Phoenix Fruit", "food", {"type": "heal", "hp": 55}, (255, 140, 60), "Heals 55 HP.", 2),
    ("mana_biscuit", "Mana Biscuit", "food", {"type": "heal", "mp": 15}, (140, 160, 200), "Restores 15 MP.", 1),
    ("void_berry", "Void Berry", "food", {"type": "heal", "hp": 30, "mp": 10}, (120, 80, 180), "Heals 30 HP and 10 MP.", 2),
    ("crimson_apple", "Crimson Apple", "food", {"type": "heal", "hp": 40}, (220, 60, 60), "Heals 40 HP.", 2),
    ("golden_nectar", "Golden Nectar", "food", {"type": "heal", "hp": 85}, (255, 200, 60), "Heals 85 HP.", 3),
    ("starlight_tea", "Starlight Tea", "food", {"type": "heal", "mp": 35}, (160, 180, 255), "Restores 35 MP.", 3),
    ("moon_cookie", "Moon Cookie", "food", {"type": "heal", "hp": 25, "mp": 15}, (200, 200, 220), "Heals 25 HP and 15 MP.", 2),
    ("soul_broth", "Soul Broth", "food", {"type": "heal", "hp": 110}, (140, 100, 180), "Heals 110 HP.", 4),
    ("astral_wine", "Astral Wine", "food", {"type": "heal", "mp": 80}, (160, 80, 200), "Restores 80 MP.", 4),
    ("void_fruit", "Void Fruit", "food", {"type": "heal", "hp": 180}, (100, 60, 160), "Heals 180 HP.", 5),
    ("elven_bread", "Elven Bread", "food", {"type": "heal", "hp": 35}, (220, 200, 160), "Heals 35 HP.", 1),
    ("dragon_scale_fruit", "Dragon Scale Fruit", "food", {"type": "heal", "hp": 300}, (255, 100, 60), "Heals 300 HP.", 6),
    ("arcane_infusion", "Arcane Infusion", "elixir", {"type": "heal", "hp": 50, "mp": 30}, (140, 140, 255), "Heals 50 HP and 30 MP.", 3),
    ("essence_of_dawn", "Essence of Dawn", "elixir", {"type": "heal", "hp": 75, "mp": 50}, (255, 220, 160), "Heals 75 HP and 50 MP.", 4),
    ("twilight_essence", "Twilight Essence", "elixir", {"type": "heal", "hp": 50, "mp": 50}, (160, 120, 200), "Heals 50 HP and 50 MP.", 3),
    ("void_essence", "Void Essence", "elixir", {"type": "heal", "hp": 999, "mp": 999}, (180, 100, 255), "Full HP and MP restore.", 6),
    ("serum_of_vitality", "Serum of Vitality", "elixir", {"type": "heal", "hp": 120}, (80, 220, 120), "Heals 120 HP.", 4),
    ("potion_of_power", "Potion of Power", "elixir", {"type": "heal", "mp": 100}, (200, 120, 255), "Restores 100 MP.", 4),
    ("life_crystal_shard", "Life Crystal Shard", "crystal", {"type": "heal", "hp": 40}, (200, 100, 140), "Heals 40 HP.", 2),
    ("life_crystal", "Life Crystal", "crystal", {"type": "heal", "hp": 100}, (220, 80, 160), "Heals 100 HP.", 3),
    ("greater_life_crystal", "Greater Life Crystal", "crystal", {"type": "heal", "hp": 200}, (240, 60, 180), "Heals 200 HP.", 5),
    ("mana_crystal_shard", "Mana Crystal Shard", "crystal", {"type": "heal", "mp": 30}, (100, 140, 220), "Restores 30 MP.", 2),
    ("mana_crystal", "Mana Crystal", "crystal", {"type": "heal", "mp": 75}, (80, 160, 240), "Restores 75 MP.", 3),
    ("greater_mana_crystal", "Greater Mana Crystal", "crystal", {"type": "heal", "mp": 150}, (60, 180, 255), "Restores 150 MP.", 5),
    ("recovery_salve", "Recovery Salve", "ointment", {"type": "heal", "hp": 20}, (180, 200, 140), "Heals 20 HP over time.", 1),
    ("healing_balm", "Healing Balm", "ointment", {"type": "heal", "hp": 45}, (160, 200, 120), "Heals 45 HP.", 2),
    ("void_ointment", "Void Ointment", "ointment", {"type": "heal", "hp": 80}, (120, 80, 180), "Heals 80 HP.", 3),
    ("regeneration_cream", "Regeneration Cream", "ointment", {"type": "heal", "hp": 130}, (100, 220, 140), "Heals 130 HP.", 4),
    ("phoenix_ashes", "Phoenix Ashes", "ash", {"type": "heal", "hp": 500}, (255, 160, 60), "Heals 500 HP.", 6),
    ("vitality_drop", "Vitality Drop", "drop", {"type": "heal", "hp": 5}, (200, 100, 100), "Heals 5 HP. Tiny but reliable.", 1),
    ("sweet_dew", "Sweet Dew", "drop", {"type": "heal", "hp": 15, "mp": 10}, (180, 220, 240), "Heals 15 HP and 10 MP.", 1),
    ("tear_of_the_moon", "Tear of the Moon", "drop", {"type": "heal", "hp": 60, "mp": 40}, (200, 200, 255), "Heals 60 HP and 40 MP.", 3),
    ("dewdrop_elixir", "Dewdrop Elixir", "drop", {"type": "heal", "hp": 35}, (180, 220, 200), "Heals 35 HP.", 2),
    ("soul_tear", "Soul Tear", "drop", {"type": "heal", "hp": 250, "mp": 100}, (160, 100, 220), "Heals 250 HP and 100 MP.", 5),
    ("warm_sunlight", "Warm Sunlight", "blessing", {"type": "heal", "hp": 30, "mp": 20}, (255, 240, 160), "Heals 30 HP and 20 MP.", 2),
    ("gentle_breeze", "Gentle Breeze", "blessing", {"type": "heal", "hp": 20}, (200, 240, 255), "Heals 20 HP.", 1),
    ("rain_of_life", "Rain of Life", "blessing", {"type": "heal", "hp": 90}, (140, 220, 255), "Heals 90 HP.", 3),
    ("holy_grace", "Holy Grace", "blessing", {"type": "heal", "hp": 180, "mp": 80}, (255, 220, 200), "Heals 180 HP and 80 MP.", 5),
    ("goddess_blessing", "Goddess' Blessing", "blessing", {"type": "heal", "hp": 999, "mp": 999}, (255, 200, 255), "Complete restoration.", 6),
    ("bandage", "Bandage", "tool", {"type": "heal", "hp": 8}, (220, 200, 180), "Heals 8 HP.", 1),
    ("first_aid_kit", "First Aid Kit", "tool", {"type": "heal", "hp": 25}, (200, 180, 160), "Heals 25 HP.", 1),
    ("surgical_kit", "Surgical Kit", "tool", {"type": "heal", "hp": 60}, (180, 160, 140), "Heals 60 HP.", 2),
    ("medkit", "Medkit", "tool", {"type": "heal", "hp": 100}, (200, 100, 100), "Heals 100 HP.", 3),
    ("trauma_kit", "Trauma Kit", "tool", {"type": "heal", "hp": 180}, (220, 80, 80), "Heals 180 HP.", 4),
    ("morphine_syringe", "Morphine Syringe", "tool", {"type": "heal", "hp": 300}, (200, 200, 220), "Heals 300 HP.", 5),
    ("regeneration_injector", "Regeneration Injector", "tool", {"type": "heal", "hp": 500}, (100, 255, 180), "Heals 500 HP.", 6),
    ("health_potion", "Health Potion", "potion", {"type": "heal", "hp": 30}, (255, 80, 120), "Restores 30 HP.", 1),
    ("greater_health", "Greater Health Potion", "potion", {"type": "heal", "hp": 75}, (255, 50, 80), "Restores 75 HP.", 3),
    ("soul_essence", "Soul Essence", "essence", {"type": "heal", "hp": 90, "mp": 60}, (200, 140, 255), "Heals 90 HP and 60 MP.", 4),
    ("vital_essence", "Vital Essence", "essence", {"type": "heal", "hp": 150}, (80, 200, 100), "Heals 150 HP.", 4),
    ("arcane_essence", "Arcane Essence", "essence", {"type": "heal", "mp": 120}, (100, 140, 255), "Restores 120 MP.", 4),
    ("primordial_essence", "Primordial Essence", "essence", {"type": "heal", "hp": 350, "mp": 200}, (255, 180, 100), "Heals 350 HP and 200 MP.", 6),
    ("angel_tears", "Angel's Tears", "drop", {"type": "heal", "hp": 120, "mp": 80}, (200, 200, 255), "Heals 120 HP and 80 MP.", 5),
]

# ─── POISON (50) ──────────────────────────────────────────────────
_POISON = [
    ("nightshade_extract", "Nightshade Extract", "toxin", {"type": "poison", "damage": 3, "duration": 5}, (80, 180, 60), "Deals 3 poison damage over 5s.", 1),
    ("viper_venom", "Viper Venom", "toxin", {"type": "poison", "damage": 5, "duration": 4}, (100, 200, 70), "Deals 5 poison damage over 4s.", 1),
    ("scorpion_sting", "Scorpion Sting", "toxin", {"type": "poison", "damage": 4, "duration": 6}, (120, 180, 80), "Deals 4 poison damage over 6s.", 1),
    ("spider_venom", "Spider Venom", "toxin", {"type": "poison", "damage": 6, "duration": 5}, (140, 190, 90), "Deals 6 poison damage over 5s.", 2),
    ("death_cap_extract", "Death Cap Extract", "toxin", {"type": "poison", "damage": 8, "duration": 4}, (160, 200, 100), "Deals 8 poison damage over 4s.", 2),
    ("hemlock_brew", "Hemlock Brew", "toxin", {"type": "poison", "damage": 7, "duration": 6}, (100, 180, 80), "Deals 7 poison damage over 6s.", 2),
    ("basilisk_venom", "Basilisk Venom", "toxin", {"type": "poison", "damage": 12, "duration": 5}, (80, 220, 60), "Deals 12 poison damage over 5s.", 3),
    ("wyvern_venom", "Wyvern Venom", "toxin", {"type": "poison", "damage": 15, "duration": 4}, (60, 240, 80), "Deals 15 poison damage over 4s.", 3),
    ("void_rot", "Void Rot", "cursed", {"type": "poison", "damage": 10, "duration": 8}, (120, 60, 140), "Deals 10 void damage over 8s.", 3),
    ("blight_essence", "Blight Essence", "cursed", {"type": "poison", "damage": 14, "duration": 6}, (100, 40, 120), "Deals 14 blight damage over 6s.", 3),
    ("corrupted_ichor", "Corrupted Ichor", "cursed", {"type": "poison", "damage": 18, "duration": 5}, (160, 40, 80), "Deals 18 corruption damage over 5s.", 4),
    ("plague_bottle", "Plague Bottle", "cursed", {"type": "poison", "damage": 20, "duration": 6}, (140, 80, 60), "Deals 20 plague damage over 6s.", 4),
    ("cancerous_growth", "Cancerous Growth", "cursed", {"type": "poison", "damage": 25, "duration": 5}, (180, 60, 80), "Deals 25 decay damage over 5s.", 4),
    ("necrotic_touch", "Necrotic Touch", "cursed", {"type": "poison", "damage": 30, "duration": 4}, (80, 20, 60), "Deals 30 necrotic damage over 4s.", 5),
    ("soul_rot", "Soul Rot", "cursed", {"type": "poison", "damage": 40, "duration": 5}, (60, 20, 100), "Deals 40 soul damage over 5s.", 5),
    ("tainted_crystal", "Tainted Crystal", "crystal", {"type": "poison", "damage": 10, "duration": 4}, (140, 80, 180), "Deals 10 poison damage over 4s.", 2),
    ("warped_flesh", "Warped Flesh", "flesh", {"type": "poison", "damage": 12, "duration": 5}, (160, 60, 80), "Deals 12 poison damage over 5s.", 2),
    ("corrupted_blood", "Corrupted Blood", "liquid", {"type": "poison", "damage": 15, "duration": 4}, (180, 40, 60), "Deals 15 poison damage over 4s.", 3),
    ("bog_water", "Bog Water", "liquid", {"type": "poison", "damage": 3, "duration": 8}, (80, 100, 60), "Deals 3 poison damage over 8s.", 1),
    ("sewer_waste", "Sewer Waste", "liquid", {"type": "poison", "damage": 5, "duration": 6}, (100, 120, 80), "Deals 5 poison damage over 6s.", 1),
    ("acidic_sludge", "Acidic Sludge", "liquid", {"type": "poison", "damage": 8, "duration": 5}, (180, 200, 60), "Deals 8 poison damage over 5s.", 2),
    ("toxic_ooze", "Toxic Ooze", "liquid", {"type": "poison", "damage": 15, "duration": 4}, (120, 200, 40), "Deals 15 poison damage over 4s.", 3),
    ("caustic_acid", "Caustic Acid", "liquid", {"type": "poison", "damage": 22, "duration": 4}, (200, 240, 60), "Deals 22 poison damage over 4s.", 4),
    ("decaying_brew", "Decaying Brew", "potion", {"type": "poison", "damage": 8, "duration": 5}, (100, 140, 80), "Deals 8 poison damage over 5s.", 2),
    ("stagnant_elixir", "Stagnant Elixir", "potion", {"type": "poison", "damage": 12, "duration": 6}, (120, 160, 100), "Deals 12 poison damage over 6s.", 2),
    ("fermented_venom", "Fermented Venom", "potion", {"type": "poison", "damage": 18, "duration": 4}, (160, 200, 120), "Deals 18 poison damage over 4s.", 3),
    ("poisoners_brew", "Poisoner's Brew", "potion", {"type": "poison", "damage": 25, "duration": 5}, (180, 220, 80), "Deals 25 poison damage over 5s.", 4),
    ("assassins_touch", "Assassin's Touch", "potion", {"type": "poison", "damage": 35, "duration": 4}, (200, 180, 60), "Deals 35 poison damage over 4s.", 5),
    ("black_widow_extract", "Black Widow Extract", "toxin", {"type": "poison", "damage": 20, "duration": 3}, (40, 40, 40), "Deals 20 poison damage over 3s.", 4),
    ("king_cobra_venom", "King Cobra Venom", "toxin", {"type": "poison", "damage": 28, "duration": 4}, (200, 160, 60), "Deals 28 poison damage over 4s.", 5),
    ("shadow_poison", "Shadow Poison", "cursed", {"type": "poison", "damage": 22, "duration": 6}, (80, 40, 100), "Deals 22 shadow damage over 6s.", 4),
    ("abyssal_poison", "Abyssal Poison", "cursed", {"type": "poison", "damage": 35, "duration": 5}, (40, 20, 80), "Deals 35 abyssal damage over 5s.", 5),
    ("void_poison", "Void Poison", "cursed", {"type": "poison", "damage": 50, "duration": 5}, (100, 40, 160), "Deals 50 void damage over 5s.", 6),
    ("pufferfish_spine", "Pufferfish Spine", "material", {"type": "poison", "damage": 6, "duration": 5}, (180, 180, 140), "Deals 6 poison damage over 5s.", 1),
    ("poison_ivy_sap", "Poison Ivy Sap", "material", {"type": "poison", "damage": 4, "duration": 7}, (100, 160, 80), "Deals 4 poison damage over 7s.", 1),
    ("curare_tip", "Curare Tip", "material", {"type": "poison", "damage": 10, "duration": 3}, (140, 120, 100), "Deals 10 poison damage over 3s.", 2),
    ("belladonna_extract", "Belladonna Extract", "material", {"type": "poison", "damage": 14, "duration": 5}, (160, 80, 160), "Deals 14 poison damage over 5s.", 3),
    ("gas_bomb", "Gas Bomb", "bomb", {"type": "poison", "damage": 20, "duration": 6}, (100, 200, 80), "Deals 20 poison damage over 6s.", 3),
    ("noxious_grenade", "Noxious Grenade", "bomb", {"type": "poison", "damage": 30, "duration": 5}, (80, 220, 60), "Deals 30 poison damage over 5s.", 4),
    ("plague_bomb", "Plague Bomb", "bomb", {"type": "poison", "damage": 45, "duration": 6}, (120, 180, 40), "Deals 45 poison damage over 6s.", 5),
    ("rotting_meat", "Rotting Meat", "food", {"type": "poison", "damage": 3, "duration": 6}, (120, 80, 60), "Deals 3 poison damage over 6s.", 1),
    ("spoiled_fish", "Spoiled Fish", "food", {"type": "poison", "damage": 5, "duration": 5}, (140, 100, 80), "Deals 5 poison damage over 5s.", 1),
    ("moldy_bread", "Moldy Bread", "food", {"type": "poison", "damage": 4, "duration": 6}, (160, 140, 100), "Deals 4 poison damage over 6s.", 1),
    ("toxic_mushroom", "Toxic Mushroom", "herb", {"type": "poison", "damage": 10, "duration": 4}, (180, 80, 100), "Deals 10 poison damage over 4s.", 2),
    ("death_angel", "Death Angel Mushroom", "herb", {"type": "poison", "damage": 18, "duration": 5}, (200, 60, 80), "Deals 18 poison damage over 5s.", 3),
    ("destroying_angel", "Destroying Angel", "herb", {"type": "poison", "damage": 30, "duration": 4}, (220, 40, 60), "Deals 30 poison damage over 4s.", 5),
    ("poison_gas_vial", "Poison Gas Vial", "vial", {"type": "poison", "damage": 8, "duration": 6}, (100, 180, 100), "Deals 8 poison damage over 6s.", 2),
    ("chlorine_vial", "Chlorine Vial", "vial", {"type": "poison", "damage": 15, "duration": 4}, (120, 200, 120), "Deals 15 poison damage over 4s.", 3),
    ("cyanide_vial", "Cyanide Vial", "vial", {"type": "poison", "damage": 25, "duration": 3}, (200, 240, 200), "Deals 25 poison damage over 3s.", 4),
    ("strychnine_vial", "Strychnine Vial", "vial", {"type": "poison", "damage": 35, "duration": 3}, (220, 200, 180), "Deals 35 poison damage over 3s.", 5),
]

# ─── INSTANT DEATH (25) ───────────────────────────────────────────
_DEATH = [
    ("null_crystal", "Null Crystal", "crystal", {"type": "death", "chance": 0.3}, (20, 10, 40), "30% chance of instant death.", 4),
    ("oblivion_shard", "Oblivion Shard", "crystal", {"type": "death", "chance": 0.5}, (10, 5, 30), "50% chance of instant death.", 5),
    ("deaths_whisper", "Death's Whisper", "scroll", {"type": "death", "chance": 0.25}, (40, 20, 60), "25% chance of instant death.", 4),
    ("soul_reaper_token", "Soul Reaper's Token", "token", {"type": "death", "chance": 0.4}, (60, 10, 30), "40% chance of instant death.", 5),
    ("cursed_doll", "Cursed Doll", "doll", {"type": "death", "chance": 0.35}, (80, 20, 40), "35% chance of instant death.", 4),
    ("void_contract", "Void Contract", "scroll", {"type": "death", "chance": 0.45}, (40, 20, 80), "45% chance of instant death.", 5),
    ("fragment_of_ending", "Fragment of Ending", "artifact", {"type": "death", "chance": 0.6}, (20, 5, 60), "60% chance of instant death.", 6),
    ("black_seal", "Black Seal", "seal", {"type": "death", "chance": 0.3}, (30, 30, 30), "30% chance of instant death.", 4),
    ("doom_scroll", "Doom Scroll", "scroll", {"type": "death", "chance": 0.4}, (40, 20, 20), "40% chance of instant death.", 5),
    ("abyssal_idol", "Abyssal Idol", "idol", {"type": "death", "chance": 0.5}, (60, 20, 80), "50% chance of instant death.", 5),
    ("shattered_soul_gem", "Shattered Soul Gem", "gem", {"type": "death", "chance": 0.35}, (100, 40, 80), "35% chance of instant death.", 4),
    ("chaos_orb", "Chaos Orb", "orb", {"type": "death", "chance": 0.55}, (200, 80, 40), "55% chance of instant death.", 6),
    ("death_mark", "Death Mark", "mark", {"type": "death", "chance": 0.25}, (40, 10, 10), "25% chance of instant death.", 3),
    ("executioners_blade_shard", "Executioner's Shard", "blade", {"type": "death", "chance": 0.3}, (160, 40, 40), "30% chance of instant death.", 4),
    ("heart_of_darkness", "Heart of Darkness", "organ", {"type": "death", "chance": 0.5}, (60, 20, 20), "50% chance of instant death.", 5),
    ("void_touched_eye", "Void-Touched Eye", "organ", {"type": "death", "chance": 0.4}, (120, 60, 180), "40% chance of instant death.", 5),
    ("black_rite_scroll", "Black Rite Scroll", "scroll", {"type": "death", "chance": 0.35}, (40, 20, 60), "35% chance of instant death.", 4),
    ("severed_tongue", "Severed Tongue", "flesh", {"type": "death", "chance": 0.2}, (120, 60, 60), "20% chance of instant death.", 3),
    ("curse_of_ages", "Curse of Ages", "curse", {"type": "death", "chance": 0.45}, (40, 60, 20), "45% chance of instant death.", 5),
    ("forbidden_knowledge", "Forbidden Knowledge", "tome", {"type": "death", "chance": 0.25}, (160, 140, 100), "25% chance of instant death.", 4),
    ("eldritch_sigil", "Eldritch Sigil", "sigil", {"type": "death", "chance": 0.5}, (80, 200, 100), "50% chance of instant death.", 6),
    ("memento_mori", "Memento Mori", "trinket", {"type": "death", "chance": 0.15}, (140, 140, 160), "15% chance of instant death.", 3),
    ("voidstone", "Voidstone", "stone", {"type": "death", "chance": 0.4}, (40, 20, 80), "40% chance of instant death.", 5),
    ("twisted_crown", "Twisted Crown", "crown", {"type": "death", "chance": 0.55}, (160, 100, 40), "55% chance of instant death.", 6),
    ("last_breath", "Last Breath", "essence", {"type": "death", "chance": 0.1}, (200, 200, 220), "10% chance of instant death.", 2),
]

# ─── BUFF (100) ───────────────────────────────────────────────────
_BUFF = [
    # Strength (20)
    ("iron_heart", "Iron Heart Elixir", "potion", {"type": "buff", "stat": "str", "amount": 3, "duration": 10}, (220, 60, 60), "+3 STR for 10s.", 2),
    ("berserkers_rage", "Berserker's Rage", "potion", {"type": "buff", "stat": "str", "amount": 5, "duration": 8}, (255, 40, 40), "+5 STR for 8s.", 3),
    ("strength_tonic", "Strength Tonic", "potion", {"type": "buff", "stat": "str", "amount": 2, "duration": 15}, (200, 80, 80), "+2 STR for 15s.", 1),
    ("giants_strength", "Giant's Strength", "potion", {"type": "buff", "stat": "str", "amount": 8, "duration": 8}, (255, 60, 60), "+8 STR for 8s.", 4),
    ("titans_brew", "Titan's Brew", "potion", {"type": "buff", "stat": "str", "amount": 12, "duration": 6}, (255, 40, 20), "+12 STR for 6s.", 5),
    ("warriors_charm", "Warrior's Charm", "charm", {"type": "buff", "stat": "str", "amount": 4, "duration": 12}, (200, 100, 80), "+4 STR for 12s.", 2),
    ("fury_talisman", "Fury Talisman", "talisman", {"type": "buff", "stat": "str", "amount": 6, "duration": 10}, (220, 80, 60), "+6 STR for 10s.", 3),
    ("rage_essence", "Rage Essence", "essence", {"type": "buff", "stat": "str", "amount": 10, "duration": 7}, (255, 60, 40), "+10 STR for 7s.", 4),
    ("power_rune", "Power Rune", "rune", {"type": "buff", "stat": "str", "amount": 7, "duration": 9}, (200, 80, 100), "+7 STR for 9s.", 3),
    ("battle_scar", "Battle Scar", "mark", {"type": "buff", "stat": "str", "amount": 5, "duration": 15}, (160, 60, 60), "+5 STR for 15s.", 2),
    ("bloodlust_vial", "Bloodlust Vial", "vial", {"type": "buff", "stat": "str", "amount": 9, "duration": 6}, (200, 40, 40), "+9 STR for 6s.", 4),
    ("mountain_heart", "Mountain Heart", "crystal", {"type": "buff", "stat": "str", "amount": 14, "duration": 8}, (180, 120, 80), "+14 STR for 8s.", 5),
    ("rage_shard", "Rage Shard", "shard", {"type": "buff", "stat": "str", "amount": 3, "duration": 20}, (200, 80, 60), "+3 STR for 20s.", 2),
    ("brute_force", "Brute Force", "injection", {"type": "buff", "stat": "str", "amount": 11, "duration": 5}, (180, 60, 60), "+11 STR for 5s.", 4),
    ("adrenaline_shot", "Adrenaline Shot", "injection", {"type": "buff", "stat": "str", "amount": 6, "duration": 8}, (200, 100, 60), "+6 STR for 8s.", 3),
    ("rage_powder", "Rage Powder", "powder", {"type": "buff", "stat": "str", "amount": 4, "duration": 12}, (220, 140, 80), "+4 STR for 12s.", 2),
    ("ogre_bone_dust", "Ogre Bone Dust", "powder", {"type": "buff", "stat": "str", "amount": 7, "duration": 10}, (180, 160, 120), "+7 STR for 10s.", 3),
    ("dragon_blood", "Dragon Blood", "blood", {"type": "buff", "stat": "str", "amount": 16, "duration": 6}, (255, 80, 40), "+16 STR for 6s.", 6),
    ("war_god_blessing", "War God's Blessing", "blessing", {"type": "buff", "stat": "str", "amount": 20, "duration": 5}, (255, 200, 60), "+20 STR for 5s.", 6),
    ("void_strength", "Void Strength", "essence", {"type": "buff", "stat": "str", "amount": 10, "duration": 10}, (160, 80, 200), "+10 STR for 10s.", 5),

    # Defense (20)
    ("stone_skin", "Stone Skin Potion", "potion", {"type": "buff", "stat": "def", "amount": 3, "duration": 12}, (100, 160, 100), "+3 DEF for 12s.", 2),
    ("iron_will", "Iron Will", "potion", {"type": "buff", "stat": "def", "amount": 5, "duration": 10}, (120, 180, 120), "+5 DEF for 10s.", 3),
    ("aegis_charm", "Aegis Charm", "charm", {"type": "buff", "stat": "def", "amount": 4, "duration": 14}, (80, 200, 140), "+4 DEF for 14s.", 2),
    ("guardian_elixir", "Guardian's Elixir", "elixir", {"type": "buff", "stat": "def", "amount": 7, "duration": 10}, (100, 220, 160), "+7 DEF for 10s.", 3),
    ("fortress_potion", "Fortress Potion", "potion", {"type": "buff", "stat": "def", "amount": 10, "duration": 8}, (80, 240, 180), "+10 DEF for 8s.", 4),
    ("diamond_skin", "Diamond Skin", "potion", {"type": "buff", "stat": "def", "amount": 15, "duration": 6}, (60, 255, 200), "+15 DEF for 6s.", 5),
    ("turtle_shell", "Turtle Shell", "trinket", {"type": "buff", "stat": "def", "amount": 3, "duration": 20}, (100, 140, 80), "+3 DEF for 20s.", 2),
    ("ironhide_scroll", "Ironhide Scroll", "scroll", {"type": "buff", "stat": "def", "amount": 6, "duration": 8}, (140, 180, 120), "+6 DEF for 8s.", 3),
    ("barrier_rune", "Barrier Rune", "rune", {"type": "buff", "stat": "def", "amount": 8, "duration": 7}, (100, 200, 180), "+8 DEF for 7s.", 4),
    ("obsidian_crystal", "Obsidian Crystal", "crystal", {"type": "buff", "stat": "def", "amount": 12, "duration": 6}, (60, 60, 80), "+12 DEF for 6s.", 5),
    ("void_armor", "Void Armor", "essence", {"type": "buff", "stat": "def", "amount": 10, "duration": 8}, (120, 80, 160), "+10 DEF for 8s.", 4),
    ("shield_herb", "Shield Herb", "herb", {"type": "buff", "stat": "def", "amount": 2, "duration": 15}, (80, 160, 100), "+2 DEF for 15s.", 1),
    ("hardened_resin", "Hardened Resin", "material", {"type": "buff", "stat": "def", "amount": 5, "duration": 10}, (160, 140, 80), "+5 DEF for 10s.", 3),
    ("titanium_coating", "Titanium Coating", "material", {"type": "buff", "stat": "def", "amount": 9, "duration": 8}, (140, 160, 180), "+9 DEF for 8s.", 4),
    ("adamantite_skin", "Adamantite Skin", "potion", {"type": "buff", "stat": "def", "amount": 18, "duration": 5}, (60, 180, 220), "+18 DEF for 5s.", 6),
    ("paladin_aura", "Paladin's Aura", "blessing", {"type": "buff", "stat": "def", "amount": 14, "duration": 7}, (200, 220, 160), "+14 DEF for 7s.", 5),
    ("earth_mantle", "Earth Mantle", "cloak", {"type": "buff", "stat": "def", "amount": 6, "duration": 12}, (120, 100, 60), "+6 DEF for 12s.", 3),
    ("crystal_armor", "Crystal Armor", "crystal", {"type": "buff", "stat": "def", "amount": 8, "duration": 9}, (160, 120, 200), "+8 DEF for 9s.", 4),
    ("void_barrier", "Void Barrier", "shield", {"type": "buff", "stat": "def", "amount": 20, "duration": 4}, (100, 60, 180), "+20 DEF for 4s.", 6),
    ("fortress_stone", "Fortress Stone", "stone", {"type": "buff", "stat": "def", "amount": 4, "duration": 18}, (80, 80, 60), "+4 DEF for 18s.", 2),

    # Speed (20)
    ("swift_step", "Swift Step Tonic", "potion", {"type": "buff", "stat": "spd", "amount": 30, "duration": 8}, (100, 200, 220), "+30 SPD for 8s.", 2),
    ("wind_runner", "Wind Runner's Blessing", "blessing", {"type": "buff", "stat": "spd", "amount": 50, "duration": 6}, (120, 220, 255), "+50 SPD for 6s.", 3),
    ("dash_essence", "Dash Essence", "essence", {"type": "buff", "stat": "spd", "amount": 40, "duration": 7}, (140, 200, 240), "+40 SPD for 7s.", 3),
    ("lightning_in_a_bottle", "Lightning in a Bottle", "bottle", {"type": "buff", "stat": "spd", "amount": 75, "duration": 4}, (200, 240, 255), "+75 SPD for 4s.", 5),
    ("sprint_powder", "Sprint Powder", "powder", {"type": "buff", "stat": "spd", "amount": 25, "duration": 10}, (160, 200, 220), "+25 SPD for 10s.", 2),
    ("hare_foot", "Hare's Foot", "charm", {"type": "buff", "stat": "spd", "amount": 20, "duration": 15}, (180, 160, 120), "+20 SPD for 15s.", 1),
    ("swift_feather", "Swift Feather", "feather", {"type": "buff", "stat": "spd", "amount": 35, "duration": 8}, (200, 220, 255), "+35 SPD for 8s.", 3),
    ("blitz_vial", "Blitz Vial", "vial", {"type": "buff", "stat": "spd", "amount": 60, "duration": 5}, (180, 200, 240), "+60 SPD for 5s.", 4),
    ("zoom_brew", "Zoom Brew", "potion", {"type": "buff", "stat": "spd", "amount": 45, "duration": 6}, (160, 240, 255), "+45 SPD for 6s.", 4),
    ("cat_grace", "Cat's Grace", "essence", {"type": "buff", "stat": "spd", "amount": 30, "duration": 12}, (200, 180, 140), "+30 SPD for 12s.", 2),
    ("cheetah_blood", "Cheetah Blood", "blood", {"type": "buff", "stat": "spd", "amount": 80, "duration": 4}, (200, 160, 80), "+80 SPD for 4s.", 5),
    ("sugar_rush", "Sugar Rush", "candy", {"type": "buff", "stat": "spd", "amount": 20, "duration": 10}, (255, 200, 180), "+20 SPD for 10s.", 1),
    ("energy_drink", "Energy Drink", "drink", {"type": "buff", "stat": "spd", "amount": 35, "duration": 8}, (100, 200, 100), "+35 SPD for 8s.", 2),
    ("speed_cola", "Speed Cola", "drink", {"type": "buff", "stat": "spd", "amount": 50, "duration": 6}, (255, 60, 60), "+50 SPD for 6s.", 3),
    ("nitro_boost", "Nitro Boost", "injection", {"type": "buff", "stat": "spd", "amount": 90, "duration": 3}, (200, 100, 40), "+90 SPD for 3s.", 5),
    ("wind_talisman", "Wind Talisman", "talisman", {"type": "buff", "stat": "spd", "amount": 40, "duration": 7}, (160, 220, 255), "+40 SPD for 7s.", 3),
    ("phantom_step", "Phantom Step", "scroll", {"type": "buff", "stat": "spd", "amount": 70, "duration": 4}, (160, 120, 200), "+70 SPD for 4s.", 5),
    ("zephyr_wings", "Zephyr Wings", "wings", {"type": "buff", "stat": "spd", "amount": 100, "duration": 3}, (200, 240, 255), "+100 SPD for 3s.", 6),
    ("void_dash", "Void Dash", "void", {"type": "buff", "stat": "spd", "amount": 60, "duration": 5}, (120, 80, 180), "+60 SPD for 5s.", 4),
    ("sonic_boom", "Sonic Boom", "bomb", {"type": "buff", "stat": "spd", "amount": 120, "duration": 2}, (200, 200, 255), "+120 SPD for 2s.", 6),

    # Magic (20)
    ("mind_opener", "Mind Opener Draught", "potion", {"type": "buff", "stat": "mag", "amount": 3, "duration": 12}, (100, 100, 220), "+3 MAG for 12s.", 2),
    ("arcane_surge", "Arcane Surge", "potion", {"type": "buff", "stat": "mag", "amount": 5, "duration": 10}, (120, 120, 240), "+5 MAG for 10s.", 3),
    ("sorcerers_essence", "Sorcerer's Essence", "essence", {"type": "buff", "stat": "mag", "amount": 7, "duration": 8}, (140, 140, 255), "+7 MAG for 8s.", 4),
    ("mages_wisdom", "Mage's Wisdom", "tome", {"type": "buff", "stat": "mag", "amount": 4, "duration": 15}, (100, 160, 220), "+4 MAG for 15s.", 2),
    ("void_knowledge", "Void Knowledge", "tome", {"type": "buff", "stat": "mag", "amount": 10, "duration": 8}, (160, 100, 220), "+10 MAG for 8s.", 4),
    ("crystal_mind", "Crystal Mind", "crystal", {"type": "buff", "stat": "mag", "amount": 8, "duration": 9}, (100, 180, 255), "+8 MAG for 9s.", 4),
    ("mana_well_draught", "Mana Well Draught", "potion", {"type": "buff", "stat": "mag", "amount": 6, "duration": 10}, (80, 160, 240), "+6 MAG for 10s.", 3),
    ("focus_charm", "Focus Charm", "charm", {"type": "buff", "stat": "mag", "amount": 3, "duration": 18}, (120, 140, 200), "+3 MAG for 18s.", 2),
    ("spellweaver_tea", "Spellweaver's Tea", "tea", {"type": "buff", "stat": "mag", "amount": 5, "duration": 12}, (160, 180, 220), "+5 MAG for 12s.", 3),
    ("arcane_flower", "Arcane Flower", "herb", {"type": "buff", "stat": "mag", "amount": 2, "duration": 20}, (180, 120, 200), "+2 MAG for 20s.", 1),
    ("wizard_star", "Wizard Star", "star", {"type": "buff", "stat": "mag", "amount": 9, "duration": 7}, (200, 180, 255), "+9 MAG for 7s.", 5),
    ("astral_essence", "Astral Essence", "essence", {"type": "buff", "stat": "mag", "amount": 12, "duration": 6}, (160, 120, 255), "+12 MAG for 6s.", 5),
    ("rune_of_power", "Rune of Power", "rune", {"type": "buff", "stat": "mag", "amount": 7, "duration": 9}, (100, 80, 200), "+7 MAG for 9s.", 4),
    ("enchanters_oil", "Enchanter's Oil", "oil", {"type": "buff", "stat": "mag", "amount": 4, "duration": 14}, (140, 140, 180), "+4 MAG for 14s.", 2),
    ("void_touch", "Void Touch", "void", {"type": "buff", "stat": "mag", "amount": 15, "duration": 5}, (120, 60, 180), "+15 MAG for 5s.", 6),
    ("archmage_elixir", "Archmage Elixir", "elixir", {"type": "buff", "stat": "mag", "amount": 18, "duration": 5}, (200, 100, 255), "+18 MAG for 5s.", 6),
    ("sage_cap", "Sage's Cap", "herb", {"type": "buff", "stat": "mag", "amount": 3, "duration": 16}, (140, 180, 200), "+3 MAG for 16s.", 2),
    ("lunar_essence", "Lunar Essence", "essence", {"type": "buff", "stat": "mag", "amount": 8, "duration": 8}, (180, 160, 255), "+8 MAG for 8s.", 4),
    ("crystal_tear", "Crystal Tear", "tear", {"type": "buff", "stat": "mag", "amount": 6, "duration": 10}, (100, 200, 240), "+6 MAG for 10s.", 3),
    ("primordial_magic", "Primordial Magic", "essence", {"type": "buff", "stat": "mag", "amount": 20, "duration": 4}, (200, 80, 255), "+20 MAG for 4s.", 6),

    # Special / Mixed (20)
    ("void_attunement", "Void Attunement", "void", {"type": "buff", "stat": "all", "amount": 3, "duration": 8}, (160, 80, 200), "+3 ALL for 8s.", 4),
    ("temporal_distortion", "Temporal Distortion", "chrono", {"type": "buff", "stat": "all", "amount": 2, "duration": 15}, (100, 200, 200), "+2 ALL for 15s.", 3),
    ("chaos_essence", "Chaos Essence", "essence", {"type": "buff", "stat": "all", "amount": 5, "duration": 6}, (200, 100, 60), "+5 ALL for 6s.", 5),
    ("balanced_brew", "Balanced Brew", "potion", {"type": "buff", "stat": "all", "amount": 1, "duration": 20}, (160, 160, 160), "+1 ALL for 20s.", 1),
    ("perfection_elixir", "Perfection Elixir", "elixir", {"type": "buff", "stat": "all", "amount": 4, "duration": 10}, (200, 200, 220), "+4 ALL for 10s.", 4),
    ("void_harmony", "Void Harmony", "void", {"type": "buff", "stat": "all", "amount": 7, "duration": 6}, (160, 120, 200), "+7 ALL for 6s.", 5),
    ("ascension_potion", "Ascension Potion", "potion", {"type": "buff", "stat": "all", "amount": 10, "duration": 4}, (255, 200, 100), "+10 ALL for 4s.", 6),
    ("gods_tear", "God's Tear", "tear", {"type": "buff", "stat": "all", "amount": 6, "duration": 8}, (255, 220, 180), "+6 ALL for 8s.", 5),
    ("stars_align", "Stars Align", "blessing", {"type": "buff", "stat": "all", "amount": 8, "duration": 5}, (200, 200, 255), "+8 ALL for 5s.", 6),
    ("inspiring_aura", "Inspiring Aura", "aura", {"type": "buff", "stat": "str", "amount": 3, "duration": 12}, (200, 160, 80), "+3 STR for 12s. Party buff.", 2),
    ("defiant_stand", "Defiant Stand", "aura", {"type": "buff", "stat": "def", "amount": 3, "duration": 12}, (100, 180, 120), "+3 DEF for 12s. Party buff.", 2),
    ("swift_wind", "Swift Wind", "aura", {"type": "buff", "stat": "spd", "amount": 25, "duration": 10}, (140, 200, 220), "+25 SPD for 10s. Party buff.", 2),
    ("arcane_field", "Arcane Field", "aura", {"type": "buff", "stat": "mag", "amount": 3, "duration": 12}, (120, 120, 220), "+3 MAG for 12s. Party buff.", 2),
    ("war_drums", "War Drums", "instrument", {"type": "buff", "stat": "str", "amount": 5, "duration": 8}, (180, 80, 80), "+5 STR for 8s.", 3),
    ("shield_wall", "Shield Wall", "skill", {"type": "buff", "stat": "def", "amount": 6, "duration": 8}, (100, 160, 120), "+6 DEF for 8s.", 3),
    ("battle_hymn", "Battle Hymn", "song", {"type": "buff", "stat": "all", "amount": 2, "duration": 12}, (200, 180, 140), "+2 ALL for 12s.", 3),
    ("heroic_inspiration", "Heroic Inspiration", "blessing", {"type": "buff", "stat": "all", "amount": 4, "duration": 8}, (220, 200, 160), "+4 ALL for 8s.", 4),
    ("last_stand", "Last Stand", "potion", {"type": "buff", "stat": "def", "amount": 25, "duration": 3}, (80, 60, 100), "+25 DEF for 3s.", 6),
    ("final_rage", "Final Rage", "potion", {"type": "buff", "stat": "str", "amount": 25, "duration": 3}, (255, 40, 40), "+25 STR for 3s.", 6),
    ("limit_break", "Limit Break", "essence", {"type": "buff", "stat": "all", "amount": 12, "duration": 3}, (255, 200, 60), "+12 ALL for 3s.", 6),
]

# ─── MONEY EXCHANGE (45) ──────────────────────────────────────────
_MONEY = [
    ("copper_coin", "Copper Coin", "coin", {"type": "money", "coins": 5}, (180, 120, 60), "Worth 5 coins.", 1),
    ("silver_coin", "Silver Coin", "coin", {"type": "money", "coins": 15}, (200, 200, 220), "Worth 15 coins.", 1),
    ("gold_coin", "Gold Coin", "coin", {"type": "money", "coins": 40}, (255, 215, 0), "Worth 40 coins.", 2),
    ("platinum_coin", "Platinum Coin", "coin", {"type": "money", "coins": 100}, (180, 220, 240), "Worth 100 coins.", 3),
    ("void_coin", "Void Coin", "coin", {"type": "money", "coins": 250}, (160, 100, 255), "Worth 250 coins.", 4),
    ("ancient_coin", "Ancient Coin", "coin", {"type": "money", "coins": 500}, (200, 180, 100), "Worth 500 coins.", 5),
    ("primordial_coin", "Primordial Coin", "coin", {"type": "money", "coins": 1000}, (255, 200, 80), "Worth 1000 coins.", 6),
    ("small_gem", "Small Gem", "gem", {"type": "money", "coins": 30}, (100, 200, 220), "Worth 30 coins.", 1),
    ("sparkling_gem", "Sparkling Gem", "gem", {"type": "money", "coins": 60}, (140, 220, 200), "Worth 60 coins.", 2),
    ("ruby", "Ruby", "gem", {"type": "money", "coins": 100}, (255, 60, 60), "Worth 100 coins.", 3),
    ("sapphire", "Sapphire", "gem", {"type": "money", "coins": 100}, (60, 100, 255), "Worth 100 coins.", 3),
    ("emerald", "Emerald", "gem", {"type": "money", "coins": 100}, (60, 200, 80), "Worth 100 coins.", 3),
    ("diamond", "Diamond", "gem", {"type": "money", "coins": 250}, (200, 220, 255), "Worth 250 coins.", 4),
    ("void_crystal", "Void Crystal", "gem", {"type": "money", "coins": 400}, (160, 80, 220), "Worth 400 coins.", 5),
    ("star_opal", "Star Opal", "gem", {"type": "money", "coins": 750}, (200, 180, 255), "Worth 750 coins.", 6),
    ("golden_feather", "Golden Feather", "artifact", {"type": "money", "coins": 45}, (255, 200, 80), "Worth 45 coins.", 2),
    ("silver_ring", "Silver Ring", "artifact", {"type": "money", "coins": 60}, (180, 180, 200), "Worth 60 coins.", 2),
    ("gold_ring", "Gold Ring", "artifact", {"type": "money", "coins": 120}, (255, 200, 40), "Worth 120 coins.", 3),
    ("ancient_idol", "Ancient Idol", "artifact", {"type": "money", "coins": 180}, (140, 120, 80), "Worth 180 coins.", 3),
    ("cursed_idol", "Cursed Idol", "artifact", {"type": "money", "coins": 300}, (100, 40, 80), "Worth 300 coins.", 4),
    ("relic_of_fallen", "Relic of the Fallen", "artifact", {"type": "money", "coins": 500}, (140, 100, 60), "Worth 500 coins.", 5),
    ("void_relic", "Void Relic", "artifact", {"type": "money", "coins": 800}, (120, 60, 180), "Worth 800 coins.", 6),
    ("golden_bracelet", "Golden Bracelet", "jewelry", {"type": "money", "coins": 80}, (255, 200, 60), "Worth 80 coins.", 2),
    ("pearl_necklace", "Pearl Necklace", "jewelry", {"type": "money", "coins": 140}, (220, 220, 240), "Worth 140 coins.", 3),
    ("ruby_amulet", "Ruby Amulet", "jewelry", {"type": "money", "coins": 220}, (255, 60, 80), "Worth 220 coins.", 4),
    ("sapphire_crown", "Sapphire Crown", "jewelry", {"type": "money", "coins": 350}, (60, 100, 220), "Worth 350 coins.", 4),
    ("emerald_ring", "Emerald Ring", "jewelry", {"type": "money", "coins": 280}, (60, 200, 100), "Worth 280 coins.", 4),
    ("diamond_tiara", "Diamond Tiara", "jewelry", {"type": "money", "coins": 600}, (200, 220, 255), "Worth 600 coins.", 5),
    ("void_crown", "Void Crown", "jewelry", {"type": "money", "coins": 1200}, (160, 80, 200), "Worth 1200 coins.", 6),
    ("rare_fossil", "Rare Fossil", "treasure", {"type": "money", "coins": 90}, (140, 120, 100), "Worth 90 coins.", 2),
    ("ancient_tablet", "Ancient Tablet", "treasure", {"type": "money", "coins": 160}, (180, 160, 120), "Worth 160 coins.", 3),
    ("golden_statue", "Golden Statue", "treasure", {"type": "money", "coins": 300}, (255, 200, 60), "Worth 300 coins.", 4),
    ("priceless_painting", "Priceless Painting", "treasure", {"type": "money", "coins": 450}, (200, 160, 140), "Worth 450 coins.", 5),
    ("magic_lamp", "Magic Lamp", "treasure", {"type": "money", "coins": 700}, (200, 180, 100), "Worth 700 coins.", 5),
    ("void_artifact", "Void Artifact", "treasure", {"type": "money", "coins": 1500}, (160, 100, 220), "Worth 1500 coins.", 6),
    ("bag_of_copper", "Bag of Copper", "loot", {"type": "money", "coins": 20}, (160, 120, 80), "Contains 20 coins.", 1),
    ("bag_of_silver", "Bag of Silver", "loot", {"type": "money", "coins": 60}, (180, 180, 200), "Contains 60 coins.", 2),
    ("bag_of_gold", "Bag of Gold", "loot", {"type": "money", "coins": 200}, (255, 200, 40), "Contains 200 coins.", 3),
    ("small_chest", "Small Chest", "loot", {"type": "money", "coins": 120}, (160, 120, 80), "Contains 120 coins.", 2),
    ("medium_chest", "Medium Chest", "loot", {"type": "money", "coins": 350}, (180, 140, 100), "Contains 350 coins.", 4),
    ("large_chest", "Large Chest", "loot", {"type": "money", "coins": 800}, (200, 160, 120), "Contains 800 coins.", 5),
    ("treasure_chest", "Treasure Chest", "loot", {"type": "money", "coins": 2000}, (255, 200, 60), "Contains 2000 coins.", 6),
    ("golden_egg", "Golden Egg", "egg", {"type": "money", "coins": 500}, (255, 200, 60), "Worth 500 coins.", 5),
    ("diamond_egg", "Diamond Egg", "egg", {"type": "money", "coins": 1200}, (200, 220, 255), "Worth 1200 coins.", 6),
    ("void_egg", "Void Egg", "egg", {"type": "money", "coins": 2500}, (160, 80, 200), "Worth 2500 coins.", 6),
]

# ─── COSMETIC (400) ────────────────────────────────────────────────
_COSMETIC = [
    # ── AURAS (40) ─────────────────────────────────────────────
    ("aura_crimson", "Crimson Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (220, 40, 40), "A blood-red aura.", 1),
    ("aura_azure", "Azure Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (60, 120, 255), "A deep blue aura.", 1),
    ("aura_emerald", "Emerald Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (60, 200, 100), "A vibrant green aura.", 1),
    ("aura_golden", "Golden Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 215, 0), "A radiant gold aura.", 2),
    ("aura_violet", "Violet Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (160, 80, 255), "A royal purple aura.", 1),
    ("aura_white", "Pure Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (240, 240, 255), "A pristine white aura.", 2),
    ("aura_void", "Void Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (100, 60, 180), "An abyssal void aura.", 3),
    ("aura_ember", "Ember Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 140, 40), "A smoldering ember aura.", 2),
    ("aura_frost", "Frost Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (180, 220, 255), "An icy frost aura.", 2),
    ("aura_poison", "Toxic Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (100, 220, 60), "A venomous green aura.", 2),
    ("aura_neon_pink", "Neon Pink Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 40, 180), "A blazing neon aura.", 2),
    ("aura_solar", "Solar Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 200, 80), "A warm solar aura.", 2),
    ("aura_lunar", "Lunar Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (200, 200, 255), "A pale moon aura.", 2),
    ("aura_bloodmoon", "Bloodmoon Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (180, 20, 20), "A sinister bloodmoon glow.", 3),
    ("aura_starlight", "Starlight Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (180, 160, 255), "A shimmering star aura.", 3),
    ("aura_shadow", "Shadow Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (40, 30, 60), "A dark shadow aura.", 2),
    ("aura_rainbow", "Rainbow Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 200, 200), "A shifting rainbow glow.", 3),
    ("aura_plasma", "Plasma Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (120, 200, 255), "A crackling plasma aura.", 3),
    ("aura_inferno", "Inferno Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 60, 20), "A blazing inferno aura.", 3),
    ("aura_arcane", "Arcane Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (140, 80, 220), "An ancient arcane aura.", 2),
    ("aura_coral", "Coral Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 120, 140), "A warm coral glow.", 1),
    ("aura_amber", "Amber Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 180, 60), "A fossilized amber glow.", 2),
    ("aura_jade", "Jade Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (80, 200, 120), "A smooth jade aura.", 2),
    ("aura_phantom", "Phantom Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (140, 140, 200), "A ghostly phantom glow.", 2),
    ("aura_blight", "Blight Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (80, 140, 40), "A decaying blight aura.", 3),
    ("aura_thunder", "Thunder Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (200, 200, 60), "A booming thunder aura.", 3),
    ("aura_holylight", "Holy Light Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (255, 240, 200), "A divine holy aura.", 3),
    ("aura_darkness", "Darkness Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (20, 10, 40), "An oppressive dark aura.", 3),
    ("aura_chaos", "Chaos Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (200, 80, 255), "A chaotic violet storm.", 4),
    ("aura_order", "Order Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (200, 220, 255), "A serene ordered glow.", 4),
    ("aura_tyrian", "Tyrian Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (140, 40, 100), "An imperial tyrian glow.", 2),
    ("aura_vermillion", "Vermillion Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (220, 60, 40), "A striking vermillion aura.", 2),
    ("aura_cerulean", "Cerulean Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (40, 160, 220), "A calm cerulean glow.", 1),
    ("aura_magenta", "Magenta Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (220, 40, 180), "A vivid magenta aura.", 2),
    ("aura_ochre", "Ochre Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (200, 160, 60), "An earthy ochre glow.", 1),
    ("aura_indigo", "Indigo Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (60, 40, 140), "A deep indigo aura.", 2),
    ("aura_teal", "Teal Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (40, 180, 180), "A rich teal glow.", 1),
    ("aura_sage", "Sage Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (120, 180, 100), "A muted sage aura.", 1),
    ("aura_crimson_heart", "Crimson Heart Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (200, 40, 80), "A pulsing heart aura.", 4),
    ("aura_sundered", "Sundered Aura", "cosmetic", {"type": "cosmetic", "subtype": "aura"}, (160, 100, 60), "A fractured broken glow.", 4),

    # ── TRAILS (40) ─────────────────────────────────────────────
    ("trail_star", "Starlight Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (200, 180, 255), "Leaves a trail of stars.", 1),
    ("trail_shadow", "Shadow Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (60, 40, 80), "Leaves a trail of shadow.", 1),
    ("trail_fire", "Fire Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 100, 40), "Leaves a trail of flame.", 2),
    ("trail_ice", "Ice Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (140, 200, 255), "Leaves a trail of frost.", 2),
    ("trail_void", "Void Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (100, 60, 180), "Leaves a trail of void.", 3),
    ("trail_gold", "Gold Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 215, 0), "Leaves a trail of gold.", 2),
    ("trail_blood", "Blood Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (180, 20, 20), "Leaves a trail of blood.", 2),
    ("trail_phantom", "Phantom Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (160, 140, 200), "Leaves a ghostly trail.", 2),
    ("trail_rainbow", "Rainbow Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 200, 200), "Leaves a rainbow trail.", 3),
    ("trail_neon", "Neon Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 40, 200), "Leaves a neon trail.", 2),
    ("trail_sparkle", "Sparkle Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 240, 200), "Leaves a sparkling trail.", 1),
    ("trail_smoke", "Smoke Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (120, 120, 140), "Leaves a smoky trail.", 1),
    ("trail_poison", "Poison Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (80, 200, 60), "Leaves a toxic trail.", 2),
    ("trail_arcane", "Arcane Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (140, 80, 220), "Leaves an arcane trail.", 3),
    ("trail_feather", "Feather Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (240, 220, 200), "Leaves a feathery trail.", 1),
    ("trail_crystal", "Crystal Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (180, 160, 255), "Leaves a crystalline trail.", 3),
    ("trail_ember", "Ember Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 160, 40), "Leaves an ember trail.", 2),
    ("trail_water", "Water Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (60, 180, 220), "Leaves a watery trail.", 1),
    ("trail_sand", "Sand Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (200, 180, 120), "Leaves a sandy trail.", 1),
    ("trail_magma", "Magma Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (220, 80, 20), "Leaves a magma trail.", 3),
    ("trail_thorns", "Thorn Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (60, 140, 40), "Leaves a trail of thorns.", 2),
    ("trail_petal", "Petal Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 160, 180), "Leaves a petal trail.", 1),
    ("trail_shock", "Shock Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (200, 220, 60), "Leaves a shocking trail.", 3),
    ("trail_bone", "Bone Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (200, 190, 170), "Leaves a bone-white trail.", 2),
    ("trail_ooze", "Ooze Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (80, 160, 60), "Leaves a slimy ooze trail.", 2),
    ("trail_lightning", "Lightning Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (100, 200, 255), "Leaves a lightning trail.", 3),
    ("trail_voidfire", "Voidfire Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (120, 40, 180), "Leaves a voidfire trail.", 4),
    ("trail_frostfire", "Frostfire Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (100, 200, 220), "Leaves a frostfire trail.", 3),
    ("trail_gravity", "Gravity Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (60, 20, 100), "Leaves a warped gravity trail.", 4),
    ("trail_holy", "Holy Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 240, 180), "Leaves a holy trail.", 3),
    ("trail_blight", "Blight Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (60, 100, 40), "Leaves a blighted trail.", 3),
    ("trail_storm", "Storm Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (120, 120, 200), "Leaves a stormy trail.", 2),
    ("trail_abyss", "Abyss Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (20, 10, 50), "Leaves an abyssal trail.", 4),
    ("trail_aurora", "Aurora Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (100, 220, 180), "Leaves an aurora trail.", 3),
    ("trail_bloodmoon", "Bloodmoon Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (160, 20, 20), "Leaves a bloodmoon trail.", 3),
    ("trail_sunlight", "Sunlight Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (255, 220, 100), "Leaves a warm sunlight trail.", 2),
    ("trail_moonlight", "Moonlight Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (180, 180, 255), "Leaves a cool moonlight trail.", 2),
    ("trail_night", "Night Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (30, 20, 60), "Leaves a dark night trail.", 2),
    ("trail_dream", "Dream Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (200, 160, 220), "Leaves a dreamy trail.", 3),
    ("trail_infernal", "Infernal Trail", "cosmetic", {"type": "cosmetic", "subtype": "trail"}, (200, 40, 20), "Leaves an infernal trail.", 4),

    # ── SKINS (40) ──────────────────────────────────────────────
    ("skin_void", "Void-Touched Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (100, 60, 180), "Your skin pulses with void energy.", 3),
    ("skin_crystal", "Crystal Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (180, 160, 255), "Your body crystallizes.", 3),
    ("skin_shadow", "Shadow Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (40, 30, 60), "You blend into the darkness.", 2),
    ("skin_flame", "Flame Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (255, 120, 40), "Your body wreathes in flames.", 3),
    ("skin_frost", "Frost Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (140, 200, 255), "A layer of frost covers you.", 2),
    ("skin_gold", "Gilded Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (255, 215, 0), "You shine like pure gold.", 2),
    ("skin_silver", "Silver Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (200, 210, 220), "A metallic silver sheen.", 2),
    ("skin_ghost", "Ghostly Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (160, 160, 200), "You become semi-transparent.", 2),
    ("skin_bone", "Bone Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (210, 200, 180), "Your skin turns bone-white.", 2),
    ("skin_demon", "Demon Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (200, 40, 40), "A demonic red hue.", 3),
    ("skin_angel", "Angel Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (240, 230, 255), "A radiant angelic glow.", 3),
    ("skin_abyssal", "Abyssal Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (20, 10, 50), "You are cloaked in the abyss.", 4),
    ("skin_arcane", "Arcane Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (140, 80, 220), "Arcane runes glow on your body.", 3),
    ("skin_crimson", "Crimson Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (180, 20, 40), "A deep crimson coloration.", 1),
    ("skin_azure", "Azure Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (40, 80, 200), "A bright azure hue.", 1),
    ("skin_jade", "Jade Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (60, 180, 100), "A smooth jade complexion.", 2),
    ("skin_amber", "Amber Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (220, 160, 60), "A warm amber tone.", 1),
    ("skin_obsidian", "Obsidian Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (30, 20, 40), "A glossy obsidian surface.", 3),
    ("skin_marble", "Marble Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (210, 210, 200), "Smooth marble texture.", 1),
    ("skin_rusted", "Rusted Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (160, 100, 40), "A corroded rusted look.", 2),
    ("skin_neon", "Neon Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (255, 40, 200), "You glow with neon intensity.", 3),
    ("skin_vine", "Vine Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (60, 160, 60), "Vines wrap around your body.", 2),
    ("skin_magma", "Magma Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (220, 80, 20), "Cracks of magma glow on you.", 3),
    ("skin_storm", "Storm Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (100, 100, 200), "Storm clouds swirl within you.", 3),
    ("skin_sand", "Sand Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (200, 180, 120), "Your body turns to sand.", 1),
    ("skin_coral", "Coral Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (255, 140, 160), "A coral reef pattern.", 2),
    ("skin_voidling", "Voidling Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (60, 40, 100), "You resemble a void creature.", 4),
    ("skin_star", "Star Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (200, 180, 255), "Constellations dot your body.", 3),
    ("skin_blood", "Blood Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (160, 10, 10), "Drenched in blood.", 2),
    ("skin_ooze", "Ooze Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (100, 180, 80), "Your body drips with ooze.", 2),
    ("skin_clockwork", "Clockwork Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (180, 160, 120), "Gears and cogs cover you.", 3),
    ("skin_ghostflame", "Ghostflame Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (120, 180, 220), "Ethereal flames coat you.", 4),
    ("skin_iridescent", "Iridescent Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (200, 180, 220), "Shifting rainbow reflections.", 3),
    ("skin_moss", "Moss Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (80, 140, 60), "Overgrown with moss.", 1),
    ("skin_thorn", "Thorn Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (60, 120, 40), "Thorns protrude from your body.", 2),
    ("skin_voidstone", "Voidstone Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (40, 20, 80), "Hardened voidstone armor.", 4),
    ("skin_sunfire", "Sunfire Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (255, 200, 60), "Burning with sunfire.", 3),
    ("skin_moonstone", "Moonstone Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (180, 200, 240), "A pale moonstone sheen.", 2),
    ("skin_scorched", "Scorched Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (80, 40, 20), "Blackened by flame.", 2),
    ("skin_prism", "Prism Skin", "cosmetic", {"type": "cosmetic", "subtype": "skin"}, (220, 220, 255), "Light refracts through you.", 4),

    # ── EMOTES (40) ─────────────────────────────────────────────
    ("emote_laugh", "Laughing Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (255, 200, 100), "A mask twisted in laughter.", 1),
    ("emote_weep", "Weeping Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (140, 160, 200), "A mask stained with tears.", 1),
    ("emote_rage", "Raging Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (200, 40, 40), "A contorted furious mask.", 2),
    ("emote_serene", "Serene Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (180, 220, 200), "A peaceful tranquil mask.", 1),
    ("emote_void", "Void Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (80, 40, 120), "A mask of endless emptiness.", 3),
    ("emote_smile", "Smiling Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (255, 220, 180), "A warm smiling mask.", 1),
    ("emote_frown", "Frowning Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (160, 140, 140), "A sorrowful frowning mask.", 1),
    ("emote_shock", "Shocked Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (240, 240, 200), "A mask of utter surprise.", 1),
    ("emote_skull", "Skull Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (200, 190, 180), "A bone-white skull mask.", 2),
    ("emote_demon", "Demon Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (200, 40, 40), "A horned demon mask.", 3),
    ("emote_angel", "Angel Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (240, 230, 255), "A haloed angel mask.", 3),
    ("emote_fox", "Fox Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (255, 160, 60), "A cunning fox mask.", 1),
    ("emote_oni", "Oni Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (180, 60, 60), "A fearsome oni mask.", 3),
    ("emote_blank", "Blank Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (200, 200, 200), "A featureless blank mask.", 1),
    ("emote_golden", "Golden Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (255, 215, 0), "A luxurious golden mask.", 2),
    ("emote_plague", "Plague Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (140, 120, 100), "A plague doctor's mask.", 2),
    ("emote_harlequin", "Harlequin Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (200, 40, 180), "A jester's colorful mask.", 2),
    ("emote_kabuki", "Kabuki Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (255, 220, 200), "A traditional kabuki mask.", 2),
    ("emote_cyborg", "Cyborg Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (120, 200, 220), "A high-tech cyborg visor.", 3),
    ("emote_phantom", "Phantom Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (160, 140, 200), "A translucent phantom mask.", 3),
    ("emote_wolf", "Wolf Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (140, 120, 100), "A snarling wolf mask.", 1),
    ("emote_dragon", "Dragon Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (60, 160, 60), "A scaled dragon mask.", 3),
    ("emote_tengu", "Tengu Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (200, 60, 40), "A long-nosed tengu mask.", 2),
    ("emote_vengeful", "Vengeful Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (160, 20, 20), "A mask burning with vengeance.", 3),
    ("emote_joyful", "Joyful Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (255, 220, 80), "A mask radiating joy.", 1),
    ("emote_grief", "Grief Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (100, 120, 160), "A mask heavy with grief.", 2),
    ("emote_hope", "Hope Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (255, 220, 180), "A mask filled with hope.", 2),
    ("emote_despair", "Despair Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (40, 20, 60), "A mask of utter despair.", 3),
    ("emote_fear", "Fear Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (100, 80, 140), "A mask twisted in fear.", 2),
    ("emote_envy", "Envy Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (60, 140, 60), "A green-eyed envy mask.", 2),
    ("emote_pride", "Pride Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (200, 180, 255), "A haughty prideful mask.", 2),
    ("emote_lust", "Lust Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (220, 80, 140), "A seductive lust mask.", 2),
    ("emote_gluttony", "Gluttony Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (180, 120, 60), "A bloated glutton mask.", 2),
    ("emote_sloth", "Sloth Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (140, 140, 160), "A drowsy sloth mask.", 1),
    ("emote_greed", "Greed Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (255, 215, 0), "A gold-encrusted greed mask.", 3),
    ("emote_wrath", "Wrath Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (200, 20, 20), "A wrathful crimson mask.", 3),
    ("emote_steel", "Steel Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (160, 160, 170), "A cold steel mask.", 1),
    ("emote_ivory", "Ivory Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (240, 235, 220), "A carved ivory mask.", 2),
    ("emote_ebony", "Ebony Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (20, 15, 30), "A dark ebony mask.", 2),
    ("emote_star", "Stargazer Mask", "cosmetic", {"type": "cosmetic", "subtype": "emote"}, (80, 60, 160), "A mask that gazes at stars.", 3),

    # ── SPARKLES (40) ───────────────────────────────────────────
    ("sparkle_crimson", "Crimson Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (220, 40, 40), "Bursts of crimson sparkles.", 1),
    ("sparkle_azure", "Azure Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (60, 120, 255), "Bursts of blue sparkles.", 1),
    ("sparkle_golden", "Golden Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 215, 0), "Bursts of gold sparkles.", 2),
    ("sparkle_void", "Void Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (100, 60, 180), "Bursts of void sparkles.", 3),
    ("sparkle_rainbow", "Rainbow Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 200, 200), "Bursts of rainbow sparkles.", 3),
    ("sparkle_neon", "Neon Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 40, 180), "Bursts of neon sparkles.", 2),
    ("sparkle_star", "Starlight Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (200, 180, 255), "Bursts of star sparkles.", 1),
    ("sparkle_fire", "Fire Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 140, 40), "Bursts of fiery sparkles.", 2),
    ("sparkle_ice", "Ice Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (140, 200, 255), "Bursts of frost sparkles.", 2),
    ("sparkle_shadow", "Shadow Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (40, 30, 60), "Bursts of dark sparkles.", 2),
    ("sparkle_ember", "Ember Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 160, 40), "Bursts of ember sparkles.", 1),
    ("sparkle_fairy", "Fairy Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 200, 240), "Bursts of fairy sparkles.", 1),
    ("sparkle_ghost", "Ghost Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (160, 160, 200), "Bursts of ghostly sparkles.", 2),
    ("sparkle_lightning", "Lightning Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (100, 200, 255), "Bursts of lightning sparkles.", 3),
    ("sparkle_poison", "Poison Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (80, 200, 60), "Bursts of toxic sparkles.", 2),
    ("sparkle_blood", "Blood Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (180, 20, 20), "Bursts of blood sparkles.", 2),
    ("sparkle_moon", "Moon Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (180, 180, 255), "Bursts of moonlight sparkles.", 1),
    ("sparkle_sun", "Sun Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 220, 100), "Bursts of sunlight sparkles.", 2),
    ("sparkle_arcane", "Arcane Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (140, 80, 220), "Bursts of arcane sparkles.", 3),
    ("sparkle_crystal", "Crystal Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (180, 160, 255), "Bursts of crystal sparkles.", 2),
    ("sparkle_flower", "Flower Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 160, 180), "Bursts of flower sparkles.", 1),
    ("sparkle_butterfly", "Butterfly Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 180, 200), "Bursts of butterfly sparkles.", 1),
    ("sparkle_dragon", "Dragon Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (60, 160, 60), "Bursts of dragon sparkles.", 3),
    ("sparkle_phoenix", "Phoenix Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 140, 60), "Bursts of phoenix sparkles.", 4),
    ("sparkle_abyss", "Abyss Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (20, 10, 50), "Bursts of abyssal sparkles.", 4),
    ("sparkle_holy", "Holy Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 240, 180), "Bursts of holy sparkles.", 3),
    ("sparkle_dark", "Dark Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (40, 20, 60), "Bursts of dark sparkles.", 2),
    ("sparkle_aqua", "Aqua Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (60, 220, 220), "Bursts of aqua sparkles.", 1),
    ("sparkle_magenta", "Magenta Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (220, 40, 180), "Bursts of magenta sparkles.", 2),
    ("sparkle_amber", "Amber Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 180, 60), "Bursts of amber sparkles.", 1),
    ("sparkle_jade", "Jade Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (60, 200, 100), "Bursts of jade sparkles.", 2),
    ("sparkle_inferno", "Inferno Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 60, 20), "Bursts of inferno sparkles.", 4),
    ("sparkle_frostfire", "Frostfire Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (100, 200, 220), "Bursts of frostfire sparkles.", 3),
    ("sparkle_storm", "Storm Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (120, 120, 200), "Bursts of storm sparkles.", 2),
    ("sparkle_coral", "Coral Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (255, 120, 140), "Bursts of coral sparkles.", 1),
    ("sparkle_plasma", "Plasma Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (120, 200, 255), "Bursts of plasma sparkles.", 3),
    ("sparkle_voidfire", "Voidfire Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (120, 40, 180), "Bursts of voidfire sparkles.", 4),
    ("sparkle_neon_green", "Neon Green Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (60, 255, 60), "Bursts of neon green sparkles.", 2),
    ("sparkle_neon_blue", "Neon Blue Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (60, 120, 255), "Bursts of neon blue sparkles.", 2),
    ("sparkle_voidheart", "Voidheart Sparkles", "cosmetic", {"type": "cosmetic", "subtype": "sparkle"}, (160, 80, 220), "Bursts of voidheart sparkles.", 4),

    # ── CROWNS (40) ─────────────────────────────────────────────
    ("crown_thorns", "Crown of Thorns", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (60, 120, 40), "A twisted crown of thorns.", 2),
    ("crown_gold", "Golden Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 215, 0), "A majestic golden crown.", 2),
    ("crown_void", "Void Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (100, 60, 180), "A crown of pure void.", 4),
    ("crown_star", "Star Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (200, 180, 255), "A crown adorned with stars.", 3),
    ("crown_ice", "Frost Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (140, 200, 255), "A crown of eternal ice.", 2),
    ("crown_fire", "Fire Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 100, 40), "A crown wreathed in flame.", 3),
    ("crown_skull", "Skull Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (200, 190, 170), "A crown of bleached skulls.", 3),
    ("crown_flower", "Flower Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 160, 180), "A delicate flower crown.", 1),
    ("crown_shadow", "Shadow Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (40, 30, 60), "A crown of living shadow.", 3),
    ("crown_light", "Light Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 240, 200), "A radiant crown of light.", 3),
    ("crown_bone", "Bone Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (210, 200, 180), "A crown carved from bone.", 2),
    ("crown_iron", "Iron Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (120, 120, 130), "A heavy iron crown.", 1),
    ("crown_silver", "Silver Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (200, 210, 220), "A polished silver crown.", 2),
    ("crown_crystal", "Crystal Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (180, 160, 255), "A crown of shimmering crystal.", 3),
    ("crown_demon", "Demon Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (200, 40, 40), "A horned demon crown.", 4),
    ("crown_angel", "Angel Halo", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (240, 230, 255), "A floating angelic halo.", 3),
    ("crown_abyss", "Abyssal Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (20, 10, 50), "A crown from the abyss.", 4),
    ("crown_holy", "Holy Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 240, 180), "A blessed holy crown.", 3),
    ("crown_dark", "Dark Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (30, 20, 40), "A crown of pure darkness.", 3),
    ("crown_ember", "Ember Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 140, 40), "A crown of smoldering embers.", 2),
    ("crown_arcane", "Arcane Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (140, 80, 220), "A crown pulsing with arcane.", 3),
    ("crown_blood", "Blood Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (180, 10, 10), "A crown drenched in blood.", 3),
    ("crown_wisdom", "Crown of Wisdom", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (100, 160, 220), "A crown of ancient wisdom.", 2),
    ("crown_power", "Crown of Power", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 60, 60), "A crown radiating power.", 3),
    ("crown_glory", "Crown of Glory", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 200, 100), "A glorious triumphal crown.", 3),
    ("crown_ruin", "Crown of Ruin", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (120, 60, 60), "A crown of fallen empires.", 3),
    ("crown_vermillion", "Vermillion Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (220, 40, 40), "A striking vermillion crown.", 2),
    ("crown_ivory", "Ivory Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (240, 235, 220), "A carved ivory crown.", 2),
    ("crown_ebony", "Ebony Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (20, 15, 30), "A dark ebony crown.", 2),
    ("crown_copper", "Copper Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (180, 120, 60), "A tarnished copper crown.", 1),
    ("crown_bronze", "Bronze Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (180, 150, 80), "A weathered bronze crown.", 1),
    ("crown_steel", "Steel Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (160, 160, 170), "A forged steel crown.", 1),
    ("crown_platinum", "Platinum Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (180, 220, 240), "A rare platinum crown.", 3),
    ("crown_obsidian", "Obsidian Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (30, 20, 40), "A glossy obsidian crown.", 3),
    ("crown_marble", "Marble Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (210, 210, 200), "A smooth marble crown.", 1),
    ("crown_jade", "Jade Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (60, 200, 100), "A precious jade crown.", 3),
    ("crown_amber", "Amber Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 180, 60), "A fossil-amber crown.", 2),
    ("crown_coral", "Coral Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 120, 140), "A crown of ocean coral.", 2),
    ("crown_thunder", "Thunder Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (200, 200, 60), "A crown crackling with thunder.", 3),
    ("crown_sun", "Sun Crown", "cosmetic", {"type": "cosmetic", "subtype": "crown"}, (255, 200, 60), "A crown of the sun itself.", 4),

    # ── WINGS (40) ──────────────────────────────────────────────
    ("wings_angel", "Angel Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (240, 230, 255), "Pure white angel wings.", 3),
    ("wings_demon", "Demon Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (200, 40, 40), "Leathery demon wings.", 3),
    ("wings_fairy", "Fairy Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (200, 180, 255), "Delicate fairy wings.", 2),
    ("wings_dragon", "Dragon Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (60, 160, 60), "Scaled dragon wings.", 3),
    ("wings_bat", "Bat Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (40, 30, 50), "Leathery bat wings.", 2),
    ("wings_butterfly", "Butterfly Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (255, 180, 200), "Colorful butterfly wings.", 2),
    ("wings_shadow", "Shadow Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (40, 30, 60), "Wings of living shadow.", 3),
    ("wings_light", "Light Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (255, 240, 200), "Radiant wings of light.", 4),
    ("wings_void", "Void Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (100, 60, 180), "Wings woven from void.", 4),
    ("wings_frost", "Frost Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (140, 200, 255), "Wings of crystalline frost.", 2),
    ("wings_flame", "Flame Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (255, 100, 40), "Wings wreathed in flame.", 3),
    ("wings_mechanical", "Mechanical Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (160, 160, 170), "Whirring mechanical wings.", 3),
    ("wings_feather", "Feather Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (240, 220, 200), "Soft feathered wings.", 1),
    ("wings_moth", "Moth Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (160, 140, 120), "Dusty moth wings.", 1),
    ("wings_dragonfly", "Dragonfly Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (180, 220, 240), "Iridescent dragonfly wings.", 2),
    ("wings_raven", "Raven Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (20, 20, 30), "Dark raven wings.", 2),
    ("wings_swan", "Swan Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (240, 240, 250), "Elegant swan wings.", 1),
    ("wings_hawk", "Hawk Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (160, 120, 80), "Soaring hawk wings.", 1),
    ("wings_owl", "Owl Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (120, 100, 80), "Silent owl wings.", 1),
    ("wings_phoenix", "Phoenix Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (255, 140, 60), "Wings of the reborn phoenix.", 4),
    ("wings_storm", "Storm Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (100, 100, 200), "Wings crackling with storm.", 3),
    ("wings_abyss", "Abyssal Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (10, 5, 30), "Wings from the abyss.", 4),
    ("wings_holy", "Holy Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (255, 240, 180), "Blessed holy wings.", 3),
    ("wings_dark", "Dark Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (20, 10, 40), "Wings of pure darkness.", 3),
    ("wings_silver", "Silver Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (200, 210, 220), "Shining silver wings.", 2),
    ("wings_golden", "Golden Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (255, 215, 0), "Luxurious golden wings.", 3),
    ("wings_crystal", "Crystal Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (180, 160, 255), "Translucent crystal wings.", 3),
    ("wings_ghost", "Ghost Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (160, 160, 200), "Translucent ghost wings.", 2),
    ("wings_soul", "Soul Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (140, 100, 200), "Wings of captured souls.", 4),
    ("wings_steam", "Steam Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (180, 180, 200), "Wings of billowing steam.", 2),
    ("wings_magic", "Magic Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (140, 80, 220), "Wings of pure magic.", 3),
    ("wings_bone", "Bone Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (210, 200, 180), "Skeletal bone wings.", 2),
    ("wings_wisp", "Wisp Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (100, 200, 220), "Wings of ethereal wisps.", 2),
    ("wings_echo", "Echo Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (120, 140, 180), "Wings that leave afterimages.", 3),
    ("wings_prism", "Prism Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (220, 220, 255), "Wings that refract light.", 3),
    ("wings_voidfire", "Voidfire Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (120, 40, 180), "Wings of voidfire.", 4),
    ("wings_iridescent", "Iridescent Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (200, 180, 220), "Shimmering iridescent wings.", 3),
    ("wings_plasma", "Plasma Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (120, 200, 255), "Wings of superheated plasma.", 4),
    ("wings_frostfire", "Frostfire Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (100, 200, 220), "Wings of frostfire.", 3),
    ("wings_starlight", "Starlight Wings", "cosmetic", {"type": "cosmetic", "subtype": "wings"}, (180, 160, 255), "Wings woven from starlight.", 3),

    # ── GLYPHS (40) ─────────────────────────────────────────────
    ("glyph_void", "Void Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (100, 60, 180), "A floating void symbol.", 3),
    ("glyph_flame", "Flame Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (255, 100, 40), "A burning flame sigil.", 2),
    ("glyph_frost", "Frost Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (140, 200, 255), "A frozen frost rune.", 2),
    ("glyph_lightning", "Lightning Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (100, 200, 255), "A crackling thunder rune.", 3),
    ("glyph_holy", "Holy Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (255, 240, 180), "A radiant holy symbol.", 3),
    ("glyph_dark", "Dark Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (30, 20, 40), "An ominous dark rune.", 2),
    ("glyph_arcane", "Arcane Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (140, 80, 220), "A spinning arcane sigil.", 3),
    ("glyph_life", "Life Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (80, 200, 100), "A pulsing life rune.", 2),
    ("glyph_death", "Death Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (160, 20, 20), "A menacing death sigil.", 3),
    ("glyph_balance", "Balance Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (180, 180, 180), "A balanced equilibrium rune.", 2),
    ("glyph_sun", "Sun Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (255, 200, 60), "A blazing sun symbol.", 2),
    ("glyph_moon", "Moon Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (180, 180, 255), "A crescent moon rune.", 2),
    ("glyph_star", "Star Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (200, 180, 255), "A twinkling star sigil.", 1),
    ("glyph_blood", "Blood Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (180, 10, 10), "A dripping blood rune.", 2),
    ("glyph_ancient", "Ancient Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (160, 140, 100), "A weathered ancient symbol.", 2),
    ("glyph_chaos", "Chaos Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (200, 80, 255), "A chaotic spiral sigil.", 4),
    ("glyph_order", "Order Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (200, 220, 255), "A precise ordered rune.", 4),
    ("glyph_abyss", "Abyss Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (20, 10, 50), "A haunting abyssal mark.", 4),
    ("glyph_crystal", "Crystal Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (180, 160, 255), "A faceted crystal sigil.", 2),
    ("glyph_shadow", "Shadow Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (40, 30, 60), "A shifting shadow rune.", 2),
    ("glyph_thunder", "Thunder Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (200, 200, 60), "A booming thunder mark.", 3),
    ("glyph_whisper", "Whisper Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (160, 160, 200), "A whispering wind rune.", 1),
    ("glyph_echo", "Echo Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (120, 140, 180), "A reverberating echo sigil.", 2),
    ("glyph_dream", "Dream Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (200, 160, 220), "A hazy dream symbol.", 2),
    ("glyph_nightmare", "Nightmare Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (80, 20, 100), "A terrifying nightmare rune.", 3),
    ("glyph_dawn", "Dawn Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (255, 200, 120), "A hopeful dawn sigil.", 2),
    ("glyph_dusk", "Dusk Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (160, 100, 140), "A melancholic dusk rune.", 2),
    ("glyph_twilight", "Twilight Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (140, 80, 160), "A twilight boundary mark.", 3),
    ("glyph_eternity", "Eternity Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (200, 200, 240), "An endless eternity knot.", 4),
    ("glyph_infinity", "Infinity Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (180, 140, 255), "A looping infinity symbol.", 4),
    ("glyph_truth", "Truth Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (200, 200, 180), "An eye that sees truth.", 2),
    ("glyph_lies", "Lies Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (160, 120, 140), "A twisted tangled sigil.", 2),
    ("glyph_war", "War Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (200, 40, 40), "A crossed swords war rune.", 3),
    ("glyph_peace", "Peace Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (180, 220, 180), "A gentle peace symbol.", 1),
    ("glyph_fury", "Fury Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (255, 60, 20), "A raging fury mark.", 3),
    ("glyph_calm", "Calm Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (140, 200, 220), "A serene calm rune.", 1),
    ("glyph_wind", "Wind Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (180, 220, 240), "A flowing wind sigil.", 1),
    ("glyph_earth", "Earth Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (120, 100, 60), "A grounded earth rune.", 1),
    ("glyph_water", "Water Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (60, 140, 200), "A flowing water symbol.", 1),
    ("glyph_fire", "Fire Glyph", "cosmetic", {"type": "cosmetic", "subtype": "glyph"}, (255, 80, 20), "A dancing fire sigil.", 1),

    # ── ESSENCES (40) ───────────────────────────────────────────
    ("essence_courage", "Courage Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (255, 180, 60), "A radiant spark of courage.", 2),
    ("essence_compassion", "Compassion Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 220, 255), "A warm wave of compassion.", 2),
    ("essence_wisdom", "Wisdom Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (100, 160, 220), "A serene glow of wisdom.", 2),
    ("essence_justice", "Justice Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 200, 180), "A balanced aura of justice.", 2),
    ("essence_hope", "Hope Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (255, 240, 200), "A gentle light of hope.", 2),
    ("essence_despair", "Despair Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (40, 20, 60), "A crushing wave of despair.", 3),
    ("essence_rage", "Rage Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 40, 20), "A burning core of rage.", 3),
    ("essence_serenity", "Serenity Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (180, 220, 200), "A calm pool of serenity.", 2),
    ("essence_chaos", "Chaos Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 80, 255), "A spiraling vortex of chaos.", 4),
    ("essence_order", "Order Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 220, 255), "A structured force of order.", 4),
    ("essence_life", "Life Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (80, 220, 100), "A vibrant pulse of life.", 3),
    ("essence_death", "Death Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (100, 40, 60), "A cold touch of death.", 3),
    ("essence_void", "Void Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (80, 40, 120), "An empty whisper of void.", 4),
    ("essence_star", "Star Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 180, 255), "A distant glow of stars.", 3),
    ("essence_dream", "Dream Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 160, 220), "A shifting dream mist.", 2),
    ("essence_nightmare", "Nightmare Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (80, 20, 100), "A terror from nightmares.", 3),
    ("essence_time", "Time Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (160, 200, 180), "A slow drip of time.", 4),
    ("essence_space", "Space Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (40, 40, 100), "An endless stretch of space.", 4),
    ("essence_light", "Light Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (255, 240, 220), "A blinding flash of light.", 3),
    ("essence_dark", "Dark Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (10, 10, 30), "An all-consuming darkness.", 3),
    ("essence_joy", "Joy Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (255, 220, 100), "A bubbling burst of joy.", 1),
    ("essence_sorrow", "Sorrow Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (100, 120, 160), "A heavy weight of sorrow.", 2),
    ("essence_fear", "Fear Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (80, 60, 120), "A creeping sense of fear.", 2),
    ("essence_pain", "Pain Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (180, 40, 40), "A sharp spike of pain.", 2),
    ("essence_envy", "Envy Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (60, 140, 60), "A bitter taste of envy.", 2),
    ("essence_pride", "Pride Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 180, 255), "A towering pillar of pride.", 2),
    ("essence_greed", "Greed Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (255, 215, 0), "A grasping hand of greed.", 3),
    ("essence_wrath", "Wrath Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 20, 20), "An unending wave of wrath.", 3),
    ("essence_sloth", "Sloth Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (140, 140, 160), "A heavy blanket of sloth.", 1),
    ("essence_gluttony", "Gluttony Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (180, 120, 60), "An insatiable hunger.", 2),
    ("essence_lust", "Lust Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (220, 80, 140), "A seductive crimson allure.", 2),
    ("essence_creation", "Creation Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (100, 220, 180), "A spark of creation.", 4),
    ("essence_destruction", "Destruction Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 40, 20), "A force of destruction.", 4),
    ("essence_bond", "Bond Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (200, 160, 120), "A warm feeling of connection.", 1),
    ("essence_loss", "Loss Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (120, 120, 140), "An empty ache of loss.", 2),
    ("essence_discovery", "Discovery Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (180, 200, 160), "A thrill of discovery.", 1),
    ("essence_mystery", "Mystery Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (120, 80, 160), "An enigmatic mystery.", 2),
    ("essence_glory", "Glory Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (255, 200, 80), "A triumphant blaze of glory.", 3),
    ("essence_ruin", "Ruin Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (100, 60, 60), "A crumbling ruin of old.", 3),
    ("essence_infinity", "Infinity Essence", "cosmetic", {"type": "cosmetic", "subtype": "essence"}, (180, 140, 255), "A boundless infinite spark.", 4),

    # ── PETS (40) ───────────────────────────────────────────────
    ("pet_void_cat", "Void Cat", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (100, 60, 180), "A shadowy cat follows you.", 3),
    ("pet_firefox", "Firefox", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 100, 40), "A fiery fox companion.", 3),
    ("pet_frost_owl", "Frost Owl", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (140, 200, 255), "An owl of pure ice.", 2),
    ("pet_star_rabbit", "Star Rabbit", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (200, 180, 255), "A rabbit with a star mark.", 1),
    ("pet_shadow_wolf", "Shadow Wolf", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (40, 30, 60), "A wolf of living shadow.", 3),
    ("pet_crystal_drake", "Crystal Drake", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (180, 160, 255), "A tiny crystal dragon.", 4),
    ("pet_ember_sprite", "Ember Sprite", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 140, 40), "A floating ember spirit.", 2),
    ("pet_voidling", "Voidling", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (80, 40, 120), "A small void creature.", 3),
    ("pet_ghost_dog", "Ghost Dog", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (160, 160, 200), "A translucent ghost hound.", 2),
    ("pet_golden_frog", "Golden Frog", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 215, 0), "A lucky golden frog.", 1),
    ("pet_blood_bat", "Blood Bat", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (180, 20, 20), "A crimson bat companion.", 2),
    ("pet_moon_moth", "Moon Moth", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (180, 180, 255), "A pale moon moth.", 1),
    ("pet_sun_phoenix", "Sun Phoenix", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 200, 60), "A tiny phoenix chick.", 4),
    ("pet_abyss_serpent", "Abyss Serpent", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (20, 10, 50), "A serpent from the abyss.", 4),
    ("pet_arcane_familiar", "Arcane Familiar", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (140, 80, 220), "A magical familiar.", 3),
    ("pet_thorn_turtle", "Thorn Turtle", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (60, 120, 40), "A spiky shelled turtle.", 1),
    ("pet_storm_hawk", "Storm Hawk", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (100, 100, 200), "A hawk of storm clouds.", 3),
    ("pet_silver_fish", "Silver Fish", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (200, 210, 220), "A shimmering silver fish.", 1),
    ("pet_bone_rat", "Bone Rat", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (210, 200, 180), "A skeletal rat.", 2),
    ("pet_plasma_jelly", "Plasma Jelly", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (120, 200, 255), "A floating plasma jellyfish.", 3),
    ("pet_verdant_frog", "Verdant Frog", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (60, 200, 80), "A bright green frog.", 1),
    ("pet_crimson_moth", "Crimson Moth", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (200, 40, 80), "A deep crimson moth.", 2),
    ("pet_azure_bird", "Azure Bird", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (60, 120, 255), "A small blue bird.", 1),
    ("pet_shadow_raven", "Shadow Raven", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (20, 20, 30), "A raven of pure shadow.", 2),
    ("pet_light_spirit", "Light Spirit", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 240, 200), "A gentle spirit of light.", 3),
    ("pet_dark_wisp", "Dark Wisp", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (30, 20, 40), "A wisp of pure darkness.", 2),
    ("pet_rainbow_parrot", "Rainbow Parrot", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 200, 200), "A colorful parrot.", 2),
    ("pet_neon_lizard", "Neon Lizard", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 40, 180), "A glowing neon lizard.", 2),
    ("pet_crystal_crab", "Crystal Crab", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (180, 160, 255), "A crab with a crystal shell.", 2),
    ("pet_frost_wolf", "Frost Wolf", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (140, 200, 255), "A wolf of ice and snow.", 3),
    ("pet_inferno_hound", "Inferno Hound", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 60, 20), "A hound from the inferno.", 4),
    ("pet_magma_slug", "Magma Slug", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (220, 80, 20), "A slow magma slug.", 1),
    ("pet_phantom_cat", "Phantom Cat", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (160, 140, 200), "A ghostly phantom cat.", 2),
    ("pet_void_bunny", "Void Bunny", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (100, 60, 180), "A cute void bunny.", 3),
    ("pet_ember_wolf", "Ember Wolf", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 160, 40), "A wolf of smoldering embers.", 3),
    ("pet_coral_dragon", "Coral Dragon", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (255, 120, 140), "A tiny coral dragon.", 2),
    ("pet_clockwork_bird", "Clockwork Bird", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (180, 160, 120), "A mechanical clockwork bird.", 2),
    ("pet_voidfire_salamander", "Voidfire Salamander", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (120, 40, 180), "A salamander of voidfire.", 4),
    ("pet_iron_golemling", "Iron Golemling", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (120, 120, 130), "A tiny iron golem.", 2),
    ("pet_wisdom_turtle", "Wisdom Turtle", "cosmetic", {"type": "cosmetic", "subtype": "pet"}, (100, 160, 100), "An ancient wise turtle.", 1),
]

# ─── SHIELD (20) ──────────────────────────────────────────────────
_SHIELD = [
    ("barrier_light", "Light Barrier", "shield", {"type": "shield", "hp": 20}, (180, 220, 255), "Absorbs 20 damage.", 1),
    ("barrier_arcane", "Arcane Barrier", "shield", {"type": "shield", "hp": 35}, (140, 140, 255), "Absorbs 35 damage.", 1),
    ("barrier_stone", "Stone Barrier", "shield", {"type": "shield", "hp": 50}, (160, 140, 100), "Absorbs 50 damage.", 2),
    ("barrier_iron", "Iron Barrier", "shield", {"type": "shield", "hp": 70}, (140, 140, 150), "Absorbs 70 damage.", 2),
    ("barrier_crystal", "Crystal Barrier", "shield", {"type": "shield", "hp": 90}, (180, 140, 220), "Absorbs 90 damage.", 3),
    ("ward_bone", "Bone Ward", "shield", {"type": "shield", "hp": 40}, (200, 180, 160), "Absorbs 40 damage.", 1),
    ("ward_frost", "Frost Ward", "shield", {"type": "shield", "hp": 60}, (140, 200, 255), "Absorbs 60 damage.", 2),
    ("ward_flame", "Flame Ward", "shield", {"type": "shield", "hp": 55}, (255, 140, 60), "Absorbs 55 damage.", 2),
    ("ward_void", "Void Ward", "shield", {"type": "shield", "hp": 80}, (120, 60, 180), "Absorbs 80 damage.", 3),
    ("aegis_silver", "Silver Aegis", "shield", {"type": "shield", "hp": 100}, (200, 210, 220), "Absorbs 100 damage.", 3),
    ("aegis_golden", "Golden Aegis", "shield", {"type": "shield", "hp": 130}, (255, 215, 0), "Absorbs 130 damage.", 4),
    ("aegis_crystal", "Crystal Aegis", "shield", {"type": "shield", "hp": 160}, (200, 160, 255), "Absorbs 160 damage.", 4),
    ("aegis_obsidian", "Obsidian Aegis", "shield", {"type": "shield", "hp": 200}, (60, 50, 80), "Absorbs 200 damage.", 5),
    ("aegis_primordial", "Primordial Aegis", "shield", {"type": "shield", "hp": 250}, (255, 180, 100), "Absorbs 250 damage.", 5),
    ("aegis_divine", "Divine Aegis", "shield", {"type": "shield", "hp": 350}, (255, 240, 200), "Absorbs 350 damage.", 6),
    ("barrier_thorn", "Thorn Barrier", "shield", {"type": "shield", "hp": 45}, (100, 180, 60), "Absorbs 45 damage.", 2),
    ("barrier_blood", "Blood Barrier", "shield", {"type": "shield", "hp": 75}, (180, 40, 40), "Absorbs 75 damage.", 3),
    ("ward_spirit", "Spirit Ward", "shield", {"type": "shield", "hp": 110}, (160, 200, 220), "Absorbs 110 damage.", 3),
    ("aegis_star", "Star Aegis", "shield", {"type": "shield", "hp": 180}, (200, 180, 255), "Absorbs 180 damage.", 4),
    ("barrier_absolute", "Absolute Barrier", "shield", {"type": "shield", "hp": 500}, (100, 80, 180), "Absorbs 500 damage.", 6),
]

# ─── REGEN (20) ───────────────────────────────────────────────────
_REGEN = [
    ("regen_minor", "Minor Regen Tonic", "tonic", {"type": "regen", "hp": 30, "duration": 6}, (80, 200, 120), "Heals 30 HP over 6s.", 1),
    ("regen_leaf", "Regen Leaf", "herb", {"type": "regen", "hp": 20, "duration": 8}, (120, 180, 100), "Heals 20 HP over 8s.", 1),
    ("regen_moss", "Rejuvenating Moss", "herb", {"type": "regen", "hp": 40, "duration": 6}, (100, 160, 80), "Heals 40 HP over 6s.", 1),
    ("regen_potion", "Regeneration Potion", "potion", {"type": "regen", "hp": 60, "duration": 6}, (60, 200, 100), "Heals 60 HP over 6s.", 2),
    ("regen_strong", "Strong Regen Potion", "potion", {"type": "regen", "hp": 90, "duration": 6}, (60, 220, 120), "Heals 90 HP over 6s.", 2),
    ("regen_superior", "Superior Regen Potion", "potion", {"type": "regen", "hp": 130, "duration": 6}, (60, 240, 140), "Heals 130 HP over 6s.", 3),
    ("regen_grand", "Grand Regen Elixir", "elixir", {"type": "regen", "hp": 180, "duration": 6}, (80, 255, 160), "Heals 180 HP over 6s.", 4),
    ("regen_royal", "Royal Regen Elixir", "elixir", {"type": "regen", "hp": 250, "duration": 6}, (100, 255, 180), "Heals 250 HP over 6s.", 5),
    ("regen_void", "Void Regen", "essence", {"type": "regen", "hp": 400, "duration": 6}, (160, 100, 255), "Heals 400 HP over 6s.", 6),
    ("regen_mana_minor", "Minor Mana Regen", "tonic", {"type": "regen", "mp": 25, "duration": 6}, (80, 120, 200), "Restores 25 MP over 6s.", 1),
    ("regen_mana", "Mana Regen Tonic", "tonic", {"type": "regen", "mp": 50, "duration": 6}, (80, 140, 220), "Restores 50 MP over 6s.", 2),
    ("regen_mana_strong", "Strong Mana Regen", "potion", {"type": "regen", "mp": 80, "duration": 6}, (100, 160, 240), "Restores 80 MP over 6s.", 3),
    ("regen_mana_grand", "Grand Mana Regen", "elixir", {"type": "regen", "mp": 130, "duration": 6}, (120, 180, 255), "Restores 130 MP over 6s.", 4),
    ("regen_mana_royal", "Royal Mana Regen", "elixir", {"type": "regen", "mp": 200, "duration": 6}, (140, 200, 255), "Restores 200 MP over 6s.", 5),
    ("regen_hybrid", "Vitality Tonic", "tonic", {"type": "regen", "hp": 30, "mp": 20, "duration": 6}, (160, 200, 180), "Heals 30 HP and 20 MP over 6s.", 2),
    ("regen_hybrid_strong", "Greater Vitality", "elixir", {"type": "regen", "hp": 70, "mp": 50, "duration": 6}, (180, 220, 200), "Heals 70 HP and 50 MP over 6s.", 4),
    ("regen_nectar", "Regen Nectar", "drop", {"type": "regen", "hp": 50, "duration": 5}, (255, 220, 80), "Heals 50 HP over 5s.", 2),
    ("regen_dew", "Morning Dew", "drop", {"type": "regen", "hp": 20, "mp": 15, "duration": 5}, (180, 220, 240), "Heals 20 HP and 15 MP over 5s.", 1),
    ("regen_blossom", "Regen Blossom", "herb", {"type": "regen", "hp": 100, "duration": 8}, (220, 160, 200), "Heals 100 HP over 8s.", 3),
    ("regen_embers", "Ember Regen", "essence", {"type": "regen", "mp": 160, "duration": 6}, (255, 160, 60), "Restores 160 MP over 6s.", 5),
]

# ─── CLEANSE (12) ─────────────────────────────────────────────────
_CLEANSE = [
    ("cleanse_herb", "Cleansing Herb", "herb", {"type": "cleanse"}, (140, 200, 140), "Removes all debuffs.", 1),
    ("cleanse_potion", "Cleansing Potion", "potion", {"type": "cleanse"}, (180, 220, 180), "Removes all debuffs.", 2),
    ("cleanse_elixir", "Cleansing Elixir", "elixir", {"type": "cleanse"}, (160, 240, 160), "Removes all debuffs.", 3),
    ("cleanse_tea", "Purifying Tea", "food", {"type": "cleanse"}, (200, 180, 140), "A calming tea that cleanses.", 1),
    ("cleanse_incense", "Purifying Incense", "tool", {"type": "cleanse"}, (160, 140, 200), "Clears the mind and body.", 2),
    ("cleanse_water", "Holy Water", "liquid", {"type": "cleanse"}, (200, 220, 255), "Blessed water that cleanses.", 2),
    ("cleanse_salve", "Cleansing Salve", "ointment", {"type": "cleanse"}, (180, 200, 160), "A soothing cleansing salve.", 1),
    ("cleanse_rune", "Cleansing Rune", "rune", {"type": "cleanse"}, (140, 180, 200), "A rune of purification.", 3),
    ("cleanse_powder", "Purifying Powder", "powder", {"type": "cleanse"}, (200, 180, 200), "A fine cleansing powder.", 2),
    ("cleanse_tear", "Tear of Purification", "drop", {"type": "cleanse"}, (200, 220, 255), "A pure tear that cleanses all.", 4),
    ("cleanse_flame", "Purifying Flame", "essence", {"type": "cleanse"}, (255, 200, 100), "Burns away all impurities.", 4),
    ("cleanse_void", "Void Purge", "cursed", {"type": "cleanse"}, (120, 60, 180), "Void energy that purges debuffs.", 5),
]

# ─── XP (10) ──────────────────────────────────────────────────────
_XP = [
    ("xp_tome_small", "Minor Tome of Knowledge", "tome", {"type": "xp", "xp": 30}, (180, 180, 200), "Grants 30 XP.", 1),
    ("xp_tome", "Tome of Knowledge", "tome", {"type": "xp", "xp": 70}, (200, 200, 220), "Grants 70 XP.", 2),
    ("xp_tome_greater", "Greater Tome of Knowledge", "tome", {"type": "xp", "xp": 140}, (220, 220, 240), "Grants 140 XP.", 3),
    ("xp_scroll", "Scroll of Wisdom", "scroll", {"type": "xp", "xp": 50}, (200, 180, 140), "Grants 50 XP.", 2),
    ("xp_scroll_ancient", "Ancient Scroll", "scroll", {"type": "xp", "xp": 100}, (180, 160, 120), "Grants 100 XP.", 3),
    ("xp_crystal", "Crystal of Insight", "crystal", {"type": "xp", "xp": 200}, (160, 140, 220), "Grants 200 XP.", 4),
    ("xp_orb", "Orb of Experience", "orb", {"type": "xp", "xp": 300}, (200, 180, 255), "Grants 300 XP.", 5),
    ("xp_elixir", "Elixir of Enlightenment", "elixir", {"type": "xp", "xp": 500}, (255, 220, 160), "Grants 500 XP.", 6),
    ("xp_leaf", "Enchanted Leaf", "herb", {"type": "xp", "xp": 20}, (100, 180, 120), "Grants 20 XP.", 1),
    ("xp_star", "Starlight Fragment", "artifact", {"type": "xp", "xp": 150}, (200, 200, 255), "Grants 150 XP.", 3),
]

# ─── MATERIALS / SUBSTANCES (6) ──────────────────────────────────
_MATERIALS = [
    ("ruby_substance", "Ruby Substance", "gem", {"type": "material", "gem": "ruby"}, (220, 40, 60), "A fiery red essence.", 3),
    ("sapphire_substance", "Sapphire Substance", "gem", {"type": "material", "gem": "sapphire"}, (40, 80, 220), "A deep blue essence.", 3),
    ("emerald_substance", "Emerald Substance", "gem", {"type": "material", "gem": "emerald"}, (40, 200, 100), "A verdant green essence.", 3),
    ("diamond_substance", "Diamond Substance", "gem", {"type": "material", "gem": "diamond"}, (200, 200, 255), "A brilliant white essence.", 4),
    ("gold_substance", "Gold Substance", "metal", {"type": "material", "gem": "gold"}, (255, 200, 40), "A lustrous golden essence.", 4),
    ("void_substance", "Void Substance", "orb", {"type": "material", "gem": "void"}, (140, 60, 220), "A primordial void essence.", 5),
]

# ─── SCROLL (15) ──────────────────────────────────────────────────
_SCROLL = [
    ("scroll_sparks", "Scroll of Sparks", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (255, 200, 80), "Fills the air with golden sparks.", 1),
    ("scroll_echo", "Scroll of Echoes", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (140, 180, 255), "Releases echoing sound waves.", 1),
    ("scroll_mist", "Scroll of Mist", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (180, 200, 200), "Veils you in magical mist.", 2),
    ("scroll_butterfly", "Scroll of Butterflies", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (255, 180, 200), "Summons a swirl of butterflies.", 2),
    ("scroll_storm", "Scroll of Storms", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (100, 140, 200), "A miniature storm surrounds you.", 3),
    ("scroll_stars", "Scroll of Stars", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (200, 200, 255), "A cascade of falling stars.", 3),
    ("scroll_voidgate", "Scroll of Voidgates", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (120, 60, 180), "Rips open tiny void portals.", 4),
    ("scroll_pheonix", "Scroll of the Phoenix", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (255, 160, 60), "A phoenix feather bursts into flame.", 4),
    ("scroll_time", "Scroll of Time", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (180, 180, 200), "Temporal distortion in a scroll.", 5),
    ("scroll_genesis", "Scroll of Genesis", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (255, 220, 180), "A burst of primordial light.", 6),
    ("scroll_frost", "Scroll of Frost", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (180, 220, 255), "Surrounds you in frost.", 2),
    ("scroll_flame", "Scroll of Flame", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (255, 120, 40), "Engulfs you in harmless flames.", 2),
    ("scroll_shadow", "Scroll of Shadows", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (40, 30, 60), "Shadows writhe around you.", 3),
    ("scroll_rainbow", "Scroll of Rainbows", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (255, 200, 200), "A brilliant rainbow erupts.", 2),
    ("scroll_voidlight", "Scroll of Voidlight", "scroll", {"type": "cosmetic", "subtype": "scroll"}, (160, 80, 220), "A beautiful void light display.", 4),
]

# Build CONSUMABLES dict from all item lists (tuples)
# Format: (key, name, item_type, effect, color, desc, tier)
CONSUMABLES = {}
all_items = _HEAL + _POISON + _DEATH + _BUFF + _MONEY + _COSMETIC + _SHIELD + _REGEN + _CLEANSE + _XP + _MATERIALS + _SCROLL
for item in all_items:
    k, name, itype, effect, color, desc, tier = item
    CONSUMABLES[k] = {
        "name": name, "item_type": itype, "effect": effect,
        "color": color, "desc": desc, "tier": tier,
    }

ALL_ITEM_KEYS = list(CONSUMABLES.keys())

# Tier-based drop pools
ITEM_POOLS = {
    1: [k for k, v in CONSUMABLES.items() if v["tier"] <= 1],
    2: [k for k, v in CONSUMABLES.items() if v["tier"] <= 2],
    3: [k for k, v in CONSUMABLES.items() if v["tier"] <= 3],
    4: [k for k, v in CONSUMABLES.items() if v["tier"] <= 4],
    5: [k for k, v in CONSUMABLES.items() if v["tier"] <= 5],
    6: [k for k, v in CONSUMABLES.items() if v["tier"] <= 6],
}


def get_consumable_drop(tier):
    tier = max(1, min(6, tier))
    pool = ITEM_POOLS.get(tier, ITEM_POOLS[1])
    return random.choice(pool) if pool else "health_potion"


# ─── Inventory System ─────────────────────────────────────────────
class InventoryItem:
    def __init__(self, item_type, data, quantity=1):
        self.type = item_type
        self.data = data
        self.quantity = quantity

    @property
    def name(self):
        if self.type == "weapon":
            return self.data["name"]
        return self.data["name"]

    @property
    def tier(self):
        if self.type == "weapon":
            return self.data["tier"]
        return 0

    @property
    def color(self):
        if self.type == "weapon":
            return self.data["color"]
        return self.data.get("color", (200, 200, 200))


class Inventory:
    MAX_WEAPONS = 999

    MAX_CONSUMABLES = 999
    def __init__(self):
        self.weapons = []
        self.consumables = []
        self.equipped_index = 0
        self.selected_weapon_idx = 0
        self.selected_cons_idx = 0
        self.notify_timer = 0
        self.notify_text = ""

    def add_weapon(self, weapon_def):
        if not weapon_def:
            return False
        for item in self.weapons:
            if item.data and item.data.get("key") == weapon_def.get("key") and item.data.get("tier") == weapon_def.get("tier"):
                item.quantity += 1
                return True
        if len(self.weapons) < self.MAX_WEAPONS:
            self.weapons.append(InventoryItem("weapon", weapon_def))
            return True
        return False

    def remove_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self.weapons[index].quantity -= 1
            if self.weapons[index].quantity <= 0:
                self.weapons.pop(index)
                if self.selected_weapon_idx >= len(self.weapons):
                    self.selected_weapon_idx = max(0, len(self.weapons) - 1)
                if self.equipped_index >= len(self.weapons):
                    self.equipped_index = max(0, len(self.weapons) - 1)

    def equip_weapon(self, index, player):
        if 0 <= index < len(self.weapons):
            wdef = self.weapons[index].data
            from game.weapons_inf import get_weapon
            new_w = get_weapon(wdef["key"])
            old_w = player.weapon
            player.weapon = new_w
            self.equipped_index = index
            self.notify_timer = 1.5
            self.notify_text = f"Equipped: {new_w['name']}"
            return True
        return False

    def add_consumable(self, key):
        cdef = CONSUMABLES.get(key)
        if not cdef:
            return False
        for item in self.consumables:
            if item.data == cdef:
                item.quantity += 1
                return True
        if len(self.consumables) < self.MAX_CONSUMABLES:
            self.consumables.append(InventoryItem("consumable", cdef))
            return True
        return False

    def use_consumable(self, index, player):
        if 0 <= index < len(self.consumables):
            item = self.consumables[index]
            cdef = item.data
            effect = cdef.get("effect", {})
            etype = effect.get("type", "")
            used = False

            if etype == "heal":
                hp = effect.get("hp", 0)
                mp = effect.get("mp", 0)
                if hp > 0 and player.hp < player.max_hp:
                    player.heal(hp)
                    used = True
                if mp > 0 and player.mp < player.max_mp:
                    player.recharge_mp(mp)
                    used = True

            elif etype == "poison":
                dmg = effect.get("damage", 5)
                dur = effect.get("duration", 3)
                from game.status import PoisonEffect
                player.status.add("Poison", PoisonEffect(dmg, dur))
                self.notify_text = f"Poisoned! {cdef['name']}"
                used = True

            elif etype == "death":
                chance = effect.get("chance", 0.5)
                if random.random() < chance:
                    player.take_damage(player.hp)
                    self.notify_text = f"💀 {cdef['name']} killed you!"
                else:
                    self.notify_text = f"Survived {cdef['name']}!"
                used = True

            elif etype == "buff":
                stat = effect.get("stat", "str")
                amount = effect.get("amount", 2)
                dur = effect.get("duration", 10)
                player.apply_item_buff(stat, amount, dur)
                used = True

            elif etype == "cosmetic":
                from game.status import CosmeticEffect
                color = cdef.get("color", (200, 200, 200))
                player.status.add(CosmeticEffect(cdef['name'], color, 8.0))
                self.notify_text = f"✨ {cdef['name']}"
                used = True

            elif etype == "money":
                coins = effect.get("coins", 10)
                player.coins += coins
                self.notify_text = f"+{coins} coins!"
                used = True

            elif etype == "shield":
                hp = effect.get("hp", 30)
                player.temp_hp += hp
                self.notify_text = f"Shield: +{hp} absorption!"
                used = True
                from game.constants import FONT_PATH
                notify_font = pygame.font.Font(FONT_PATH, 12)

            elif etype == "regen":
                hp_total = effect.get("hp", 0)
                mp_total = effect.get("mp", 0)
                dur = effect.get("duration", 6)
                if hp_total > 0:
                    player.apply_item_buff("regen_hp", hp_total / dur, dur)
                if mp_total > 0:
                    player.apply_item_buff("regen_mp", mp_total / dur, dur)
                self.notify_text = f"Regeneration: {cdef['name']}"
                used = True

            elif etype == "cleanse":
                player.status.clear()
                self.notify_text = "Debuffs cleansed!"
                used = True

            elif etype == "xp":
                xp_amt = effect.get("xp", 50)
                player.add_xp(xp_amt)
                self.notify_text = f"+{xp_amt} XP!"
                used = True

            if used:
                item.quantity -= 1
                if item.quantity <= 0:
                    self.consumables.pop(index)
                self.notify_timer = 1.5
                if not self.notify_text:
                    self.notify_text = f"Used: {cdef['name']}"
                return True
        return False

    def count_consumable(self, key):
        for item in self.consumables:
            if item.data.get("key") == key or item.data.get("name", "").lower() == key.lower().replace("_", " "):
                return item.quantity
        return 0

    def sell_weapon(self, index, player):
        if 0 <= index < len(self.weapons):
            item = self.weapons[index]
            price = max(1, item.tier * 15 + 5)
            player.coins += price
            self.notify_text = f"Sold {item.name} for {price} coins!"
            self.notify_timer = 2.0
            self.remove_weapon(index)
            return True
        return False

    def sell_consumable(self, index, player):
        if 0 <= index < len(self.consumables):
            item = self.consumables[index]
            price = max(1, item.tier * 3)
            player.coins += price
            self.notify_text = f"Sold {item.name} for {price} coins!"
            self.notify_timer = 2.0
            item.quantity -= 1
            if item.quantity <= 0:
                self.consumables.pop(index)
            return True
        return False


# ─── Vaporwave Inventory UI ──────────────────────────────────────
class VaporwaveInventory:
    VAPOR_COLORS = {
        "bg": (8, 6, 18),
        "panel": (16, 12, 30),
        "grid": (255, 40, 160),
        "grid_dim": (50, 20, 60),
        "cyan": (0, 220, 255),
        "pink": (255, 40, 180),
        "purple": (160, 80, 255),
        "magenta": (200, 40, 255),
        "gold": (255, 215, 0),
        "text": (220, 210, 240),
        "text_dim": (120, 110, 160),
        "selected": (255, 60, 200),
        "border_pulse": (255, 50, 180),
    }

    def __init__(self):
        self.open = False
        self.anim_t = 0.0
        self.animating = False
        self.open_direction = 1
        self.time = 0.0
        self.font_large = pygame.font.Font(FONT_PATH, 28)
        self.font_med = pygame.font.Font(FONT_PATH, 20)
        self.font_small = pygame.font.Font(FONT_PATH, 16)
        self.font_title = pygame.font.Font(FONT_PATH, 36)
        self.slot_size = 72
        self.grid_cols = 5
        self.grid_rows = 4
        self.tab = "weapons"

    def toggle(self):
        self.open_direction = 1 if not self.open else -1
        self.animating = True
        self.open = not self.open

    def update(self, dt, inventory):
        self.time += dt
        if self.animating:
            self.anim_t += dt * 4 * self.open_direction
            if self.anim_t <= 0 or self.anim_t >= 1:
                self.anim_t = max(0, min(1, self.anim_t))
                self.animating = False

    def handle_event(self, event, inventory, player):
        if not self.open:
            return False
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos

        c = self.VAPOR_COLORS
        panel_x, panel_y = 50, 50
        panel_w = WINDOW_WIDTH - 100
        panel_h = WINDOW_HEIGHT - 100
        tab_y = panel_y + 55

        # ── Tab click ──
        tabs = [("weapons", "WEAPONS"), ("consumables", "ITEMS")]
        for idx, (tkey, tlabel) in enumerate(tabs):
            tx = panel_x + 20 + idx * 130
            tab_rect = pygame.Rect(tx, tab_y, 110, 24)
            if tab_rect.collidepoint(mx, my):
                self.tab = tkey
                return True

        if self.tab == "weapons":
            return self._handle_weapons_click(mx, my, inventory, player, panel_x, panel_y, panel_w, panel_h, tab_y)
        else:
            return self._handle_consumables_click(mx, my, inventory, player, panel_x, panel_y, panel_w, panel_h, tab_y)

    def _handle_weapons_click(self, mx, my, inventory, player, panel_x, panel_y, panel_w, panel_h, tab_y):
        inv = inventory
        grid_x = panel_x + 20
        grid_y = tab_y + 35
        slot_gap = 8
        ss = self.slot_size

        # ── Grid slot click ──
        for i in range(self.grid_cols * self.grid_rows):
            col = i % self.grid_cols
            row = i // self.grid_cols
            sx = grid_x + col * (ss + slot_gap)
            sy = grid_y + row * (ss + slot_gap)
            slot_rect = pygame.Rect(sx, sy, ss, ss)
            if slot_rect.collidepoint(mx, my) and i < len(inv.weapons):
                inv.selected_weapon_idx = i
                return True

        # ── Info panel equip/sell click ──
        info_x = panel_x + panel_w - 220
        info_y = grid_y
        info_w = 200
        info_h = 260

        sel_idx = inv.selected_weapon_idx
        if 0 <= sel_idx < len(inv.weapons):
            equip_rect = pygame.Rect(info_x + 10, info_y + info_h - 70, 180, 20)
            if equip_rect.collidepoint(mx, my):
                inv.equip_weapon(sel_idx, player)
                return True
            sell_rect = pygame.Rect(info_x + 10, info_y + info_h - 46, 180, 20)
            if sell_rect.collidepoint(mx, my):
                inv.sell_weapon(sel_idx, player)
                return True

        return False

    def _handle_consumables_click(self, mx, my, inventory, player, panel_x, panel_y, panel_w, panel_h, tab_y):
        inv = inventory
        list_x = panel_x + 30
        list_y = tab_y + 45
        slot_h = 50
        slot_gap = 6

        # ── Consumable list click ──
        for i, item in enumerate(inv.consumables):
            sy = list_y + i * (slot_h + slot_gap)
            slot_rect = pygame.Rect(list_x, sy, panel_w - 260, slot_h)
            if slot_rect.collidepoint(mx, my):
                inv.selected_cons_idx = i
                return True

        # ── Info panel use/sell click ──
        info_x = panel_x + panel_w - 220
        info_y = tab_y + 35
        info_w = 200
        info_h = 180

        sel_idx = inv.selected_cons_idx
        if 0 <= sel_idx < len(inv.consumables):
            use_rect = pygame.Rect(info_x + 10, info_y + info_h - 70, 180, 20)
            if use_rect.collidepoint(mx, my):
                item = inv.consumables[sel_idx]
                eff = item.data.get("effect", {})
                was_cosmetic = eff.get("type") == "cosmetic"
                ccolor = item.data.get("color", (200, 200, 255))
                if inv.use_consumable(sel_idx, player) and was_cosmetic and hasattr(player, '_game_scene') and player._game_scene:
                    player._game_scene.emitter.burst(player.x, player.y, ccolor, count=25, speed=120, lifetime=0.8, size=4)
                return True
            sell_rect = pygame.Rect(info_x + 10, info_y + info_h - 46, 180, 20)
            if sell_rect.collidepoint(mx, my):
                inv.sell_consumable(sel_idx, player)
                return True

        return False

    def _lerp_color(self, c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    def _draw_grid_bg(self, surface, rect):
        for x in range(rect.left, rect.right, 32):
            alpha = 20 + 10 * math.sin(self.time * 0.5 + x * 0.01)
            c = (*self.VAPOR_COLORS["grid"], int(alpha))
            if x == rect.left or x + 32 > rect.right:
                continue
            pygame.draw.line(surface, c, (x, rect.top), (x, rect.bottom), 1)
        for y in range(rect.top, rect.bottom, 32):
            alpha = 20 + 10 * math.sin(self.time * 0.5 + y * 0.01)
            c = (*self.VAPOR_COLORS["grid"], int(alpha))
            if y == rect.top or y + 32 > rect.bottom:
                continue
            pygame.draw.line(surface, c, (rect.left, y), (rect.right, y), 1)

    def _draw_triangle_accent(self, surface, rect):
        cx = rect.right - 40
        cy = rect.top + 30
        size = 20 + 5 * math.sin(self.time * 1.5)
        pts = [(cx, cy - size), (cx - size, cy + size), (cx + size, cy + size)]
        glow_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        gp = [(size * 1.5, size * 1.5 - size), (size * 1.5 - size, size * 1.5 + size),
              (size * 1.5 + size, size * 1.5 + size)]
        alpha = int(15 + 10 * math.sin(self.time * 2))
        pygame.draw.polygon(glow_surf, (*self.VAPOR_COLORS["pink"][:3], alpha), gp)
        surface.blit(glow_surf, (cx - size * 1.5, cy - size * 1.5))
        pygame.draw.polygon(surface, self.VAPOR_COLORS["pink"], pts, 2)

    def render_weapons_tab(self, surface, inventory):
        c = self.VAPOR_COLORS
        inv = inventory
        weapons = inv.weapons

        panel_x = 50
        panel_y = 50
        panel_w = WINDOW_WIDTH - 100
        panel_h = WINDOW_HEIGHT - 100

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        overlay.fill((*c["bg"], 220))
        surface.blit(overlay, (panel_x, panel_y))

        border_pulse = 0.6 + 0.4 * math.sin(self.time * 1.5)
        border_color = tuple(int(a * border_pulse + b * (1 - border_pulse))
                            for a, b in zip(c["pink"], c["magenta"]))
        pygame.draw.rect(surface, border_color, panel_rect, 2, border_radius=6)

        self._draw_grid_bg(surface, panel_rect)

        title_text = self.font_title.render("◇ I N V E N T O R Y ◇", True, c["pink"])
        surface.blit(title_text, (panel_x + 20, panel_y + 12))

        stats_line = f"  Weapons: {len(weapons)}/{Inventory.MAX_WEAPONS}"
        st = self.font_small.render(stats_line, True, c["text_dim"])
        surface.blit(st, (panel_x + panel_w - st.get_width() - 20, panel_y + 18))

        self._draw_triangle_accent(surface, panel_rect)

        # ── Tab buttons ──
        tab_y = panel_y + 55
        tabs = [("weapons", "WEAPONS"), ("consumables", "ITEMS")]
        for tkey, tlabel in tabs:
            tx = panel_x + 20 + (tabs.index((tkey, tlabel))) * 130
            is_active = self.tab == tkey
            tc = c["cyan"] if is_active else c["text_dim"]
            pygame.draw.line(surface, tc, (tx, tab_y + 22), (tx + 110, tab_y + 22), 2)
            tl = self.font_med.render(tlabel, True, tc)
            surface.blit(tl, (tx + 55 - tl.get_width() // 2, tab_y))

        grid_x = panel_x + 20
        grid_y = tab_y + 35
        slot_gap = 8

        for i in range(self.grid_cols * self.grid_rows):
            col = i % self.grid_cols
            row = i // self.grid_cols
            sx = grid_x + col * (self.slot_size + slot_gap)
            sy = grid_y + row * (self.slot_size + slot_gap)
            slot_rect = pygame.Rect(sx, sy, self.slot_size, self.slot_size)

            is_occupied = i < len(weapons)
            is_selected = is_occupied and i == inv.selected_weapon_idx
            is_equipped = is_occupied and i == inv.equipped_index

            if is_occupied:
                item = weapons[i]
                pygame.draw.rect(surface, (25, 20, 45), slot_rect, border_radius=4)

                if is_selected:
                    sel_pulse = 0.5 + 0.5 * math.sin(self.time * 4)
                    sel_color = tuple(int(a * sel_pulse + b * (1 - sel_pulse))
                                    for a, b in zip(c["selected"], c["cyan"]))
                    pygame.draw.rect(surface, sel_color, slot_rect, 2, border_radius=4)
                else:
                    glow = c["text_dim"] if not is_equipped else c["gold"]
                    pygame.draw.rect(surface, glow, slot_rect, 1, border_radius=4)

                if is_equipped:
                    eq_surf = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
                    eq_alpha = int(30 + 20 * math.sin(self.time * 2))
                    pygame.draw.rect(eq_surf, (*c["gold"][:3], eq_alpha),
                                    (0, 0, self.slot_size, self.slot_size), border_radius=4)
                    surface.blit(eq_surf, (sx, sy))

                tier_names = {1: "C", 2: "U", 3: "R", 4: "E", 5: "L", 6: "M"}
                tier_str = tier_names.get(item.tier, "?")
                tc = (160, 160, 160) if item.tier == 1 else \
                     (120, 200, 120) if item.tier == 2 else \
                     (100, 100, 220) if item.tier == 3 else \
                     (180, 100, 220) if item.tier == 4 else \
                     (220, 180, 80) if item.tier == 5 else (220, 100, 200)
                tw = self.font_small.render(tier_str, True, tc)
                surface.blit(tw, (sx + 4, sy + 4))

                wcolor = item.data.get("color", (200, 200, 200))
                eye_size = 6
                eye_rect = pygame.Rect(sx + self.slot_size // 2 - eye_size // 2,
                                       sy + self.slot_size // 2 - eye_size // 2,
                                       eye_size, eye_size)
                pygame.draw.rect(surface, wcolor, eye_rect)
                pygame.draw.rect(surface, (255, 255, 255), eye_rect, 1)

                if item.quantity > 1:
                    qty = self.font_small.render(f"x{item.quantity}", True, c["text_dim"])
                    surface.blit(qty, (sx + self.slot_size - qty.get_width() - 4,
                                      sy + self.slot_size - qty.get_height() - 2))
            else:
                slot_alpha = 20 + 10 * math.sin(self.time * 2 + i * 0.5)
                empty_surf = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
                pygame.draw.rect(empty_surf, (*c["grid_dim"][:3], int(slot_alpha)),
                                (0, 0, self.slot_size, self.slot_size), 1, border_radius=4)
                surface.blit(empty_surf, (sx, sy))

        # ── Selected item info panel ──
        info_x = panel_x + panel_w - 220
        info_y = grid_y
        info_w = 200
        info_h = 260
        info_rect = pygame.Rect(info_x, info_y, info_w, info_h)
        info_bg = pygame.Surface((info_w, info_h), pygame.SRCALPHA)
        info_bg.fill((*c["panel"], 160))
        surface.blit(info_bg, (info_x, info_y))
        pygame.draw.rect(surface, c["cyan"], info_rect, 1, border_radius=4)

        sel_idx = inv.selected_weapon_idx if self.tab == "weapons" else inv.selected_cons_idx
        sel_list = weapons if self.tab == "weapons" else inv.consumables
        sel_item = sel_list[sel_idx] if 0 <= sel_idx < len(sel_list) else None

        if sel_item:
            name_color = sel_item.color
            nlabel = self.font_med.render(sel_item.name, True, name_color)
            surface.blit(nlabel, (info_x + 10, info_y + 12))

            if sel_item.type == "weapon":
                w = sel_item.data
                desc = w.get("description", "")
                dl = self.font_small.render(desc, True, c["text_dim"])
                surface.blit(dl, (info_x + 10, info_y + 38))

                lines = [
                    f"DMG: {w.get('damage', 0)}",
                    f"MAG: {w.get('magic', 0)}",
                    f"DEF: {w.get('defense', 0)}",
                    f"SPD: {w.get('speed_bonus', 0):+.1f}",
                    f"Type: {w.get('type', '?').title()}",
                ]
                for li, line in enumerate(lines):
                    lc = c["cyan"] if li < 3 else c["text_dim"]
                    ll = self.font_small.render(line, True, lc)
                    surface.blit(ll, (info_x + 10, info_y + 62 + li * 20))

                is_eq = sel_idx == inv.equipped_index
                equip_text = "[E]  Equipped" if is_eq else "[E]  Equip"
                ec = c["gold"] if is_eq else c["pink"]
                el = self.font_small.render(equip_text, True, ec)
                surface.blit(el, (info_x + 10, info_y + info_h - 70))
                sell_price = max(1, sel_item.tier * 15 + 5)
                sell_text = f"[S]  Sell ({sell_price})"
                sl = self.font_small.render(sell_text, True, (255, 180, 80))
                surface.blit(sl, (info_x + 10, info_y + info_h - 46))
            else:
                cdef = sel_item.data
                dl = self.font_small.render(cdef.get("desc", ""), True, c["text_dim"])
                surface.blit(dl, (info_x + 10, info_y + 38))
                ql = self.font_small.render(f"Qty: {sel_item.quantity}", True, c["text_dim"])
                surface.blit(ql, (info_x + 10, info_y + 58))
                ul = self.font_small.render("[U]  Use Item", True, c["pink"])
                surface.blit(ul, (info_x + 10, info_y + info_h - 70))
                sell_price = max(1, sel_item.tier * 3)
                sell_text = f"[S]  Sell ({sell_price})"
                sl = self.font_small.render(sell_text, True, (255, 180, 80))
                surface.blit(sl, (info_x + 10, info_y + info_h - 46))
        else:
            nl = self.font_small.render("No item selected", True, c["text_dim"])
            surface.blit(nl, (info_x + 10, info_y + 12))

        # ── Controls hint ──
        controls_y = panel_y + panel_h - 30
        controls = "[Tab] Close  [E] Equip / [U] Use  [S] Sell  [Q] Drop  [←→] Navigate"
        cl = self.font_small.render(controls, True, c["text_dim"])
        surface.blit(cl, (panel_x + 20, controls_y))

    def render_consumables_tab(self, surface, inventory):
        c = self.VAPOR_COLORS
        inv = inventory
        consumables = inv.consumables

        panel_x = 50
        panel_y = 50
        panel_w = WINDOW_WIDTH - 100
        panel_h = WINDOW_HEIGHT - 100

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        overlay.fill((*c["bg"], 220))
        surface.blit(overlay, (panel_x, panel_y))

        border_pulse = 0.6 + 0.4 * math.sin(self.time * 1.5)
        border_color = tuple(int(a * border_pulse + b * (1 - border_pulse))
                            for a, b in zip(c["pink"], c["magenta"]))
        pygame.draw.rect(surface, border_color, panel_rect, 2, border_radius=6)

        self._draw_grid_bg(surface, panel_rect)

        title_text = self.font_title.render("◇ I T E M S ◇", True, c["cyan"])
        surface.blit(title_text, (panel_x + 20, panel_y + 12))

        # ── Tab buttons ──
        tab_y = panel_y + 55
        tabs = [("weapons", "WEAPONS"), ("consumables", "ITEMS")]
        for tkey, tlabel in tabs:
            tx = panel_x + 20 + (tabs.index((tkey, tlabel))) * 130
            is_active = self.tab == tkey
            tc = c["cyan"] if is_active else c["text_dim"]
            pygame.draw.line(surface, tc, (tx, tab_y + 22), (tx + 110, tab_y + 22), 2)
            tl = self.font_med.render(tlabel, True, tc)
            surface.blit(tl, (tx + 55 - tl.get_width() // 2, tab_y))

        # ── Consumable list ──
        list_x = panel_x + 30
        list_y = tab_y + 45
        slot_h = 50
        slot_gap = 6

        for i, item in enumerate(consumables):
            sy = list_y + i * (slot_h + slot_gap)
            slot_rect = pygame.Rect(list_x, sy, panel_w - 260, slot_h)
            is_selected = i == inv.selected_cons_idx

            pygame.draw.rect(surface, (25, 20, 45), slot_rect, border_radius=4)
            if is_selected:
                sel_pulse = 0.5 + 0.5 * math.sin(self.time * 4)
                sel_color = tuple(int(a * sel_pulse + b * (1 - sel_pulse))
                                for a, b in zip(c["selected"], c["cyan"]))
                pygame.draw.rect(surface, sel_color, slot_rect, 2, border_radius=4)
            else:
                pygame.draw.rect(surface, c["text_dim"], slot_rect, 1, border_radius=4)

            # Color swatch
            swatch_rect = pygame.Rect(list_x + 8, sy + 8, 34, 34)
            pygame.draw.rect(surface, item.data.get("color", c["purple"]), swatch_rect, border_radius=3)

            # Effect badge
            effect = item.data.get("effect", {})
            etype = effect.get("type", "")
            badge_colors = {"heal": (80, 200, 100), "poison": (100, 200, 60),
                           "death": (200, 40, 40), "buff": (100, 140, 255),
                           "money": (255, 215, 0), "cosmetic": (255, 100, 255)}
            badge_color = badge_colors.get(etype, c["text_dim"])
            badge_rect = pygame.Rect(list_x + 8, sy + 30, 34, 14)
            pygame.draw.rect(surface, badge_color, badge_rect, border_radius=2)
            badge_label = etype[:4].upper()
            bt = self.font_small.render(badge_label, True, (0, 0, 0))
            surface.blit(bt, (list_x + 17 - bt.get_width() // 2, sy + 30))

            nl = self.font_med.render(item.name, True, c["text"])
            surface.blit(nl, (list_x + 52, sy + 5))

            dl = self.font_small.render(item.data.get("desc", ""), True, c["text_dim"])
            surface.blit(dl, (list_x + 52, sy + 28))

            ql = self.font_small.render(f"x{item.quantity}", True, c["text_dim"])
            surface.blit(ql, (list_x + panel_w - 340, sy + 15))

        if not consumables:
            el = self.font_med.render("No items — enemies drop potions!", True, c["text_dim"])
            surface.blit(el, (list_x, list_y + 20))

        # ── Info panel (reuse) ──
        info_x = panel_x + panel_w - 220
        info_y = tab_y + 35
        info_w = 200
        info_h = 180
        info_rect = pygame.Rect(info_x, info_y, info_w, info_h)
        info_bg = pygame.Surface((info_w, info_h), pygame.SRCALPHA)
        info_bg.fill((*c["panel"], 160))
        surface.blit(info_bg, (info_x, info_y))
        pygame.draw.rect(surface, c["cyan"], info_rect, 1, border_radius=4)

        sel_item = consumables[inv.selected_cons_idx] if 0 <= inv.selected_cons_idx < len(consumables) else None
        if sel_item:
            nl = self.font_med.render(sel_item.name, True, sel_item.data.get("color", c["text"]))
            surface.blit(nl, (info_x + 10, info_y + 12))

            effect = sel_item.data.get("effect", {})
            etype = effect.get("type", "?")
            badge_colors = {"heal": (80, 200, 100), "poison": (100, 200, 60),
                           "death": (200, 40, 40), "buff": (100, 140, 255),
                           "money": (255, 215, 0), "cosmetic": (255, 100, 255)}
            badge_color = badge_colors.get(etype, c["text_dim"])
            bt = self.font_small.render(f"[{etype.upper()}]", True, badge_color)
            surface.blit(bt, (info_x + 10, info_y + 34))

            dl = self.font_small.render(sel_item.data.get("desc", ""), True, c["text_dim"])
            surface.blit(dl, (info_x + 10, info_y + 54))
            ul = self.font_small.render("[U] Use Item", True, c["pink"])
            surface.blit(ul, (info_x + 10, info_y + info_h - 70))
            sell_price = max(1, sel_item.tier * 3)
            sell_text = f"[S] Sell ({sell_price})"
            sl = self.font_small.render(sell_text, True, (255, 180, 80))
            surface.blit(sl, (info_x + 10, info_y + info_h - 46))
        else:
            nl = self.font_small.render("No item selected", True, c["text_dim"])
            surface.blit(nl, (info_x + 10, info_y + 12))

        controls_y = panel_y + panel_h - 30
        controls = "[Tab] Close  [U] Use  [S] Sell  [Q] Drop  [←→] Navigate"
        cl = self.font_small.render(controls, True, c["text_dim"])
        surface.blit(cl, (panel_x + 20, controls_y))

    def render(self, surface, inventory):
        if not self.open and self.anim_t == 0:
            return

        fade = self.anim_t
        fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        fade_surf.fill((0, 0, 0, int(60 * fade)))
        surface.blit(fade_surf, (0, 0))

        scanline_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for y in range(0, WINDOW_HEIGHT, 3):
            scanline_surf.fill((0, 0, 0, int(12 * fade)), (0, y, WINDOW_WIDTH, 1))
        surface.blit(scanline_surf, (0, 0))

        if self.tab == "weapons":
            self.render_weapons_tab(surface, inventory)
        else:
            self.render_consumables_tab(surface, inventory)

        if inventory.notify_timer > 0:
            alpha = min(255, int(255 * min(1.0, inventory.notify_timer * 2)))
            nt = self.font_small.render(inventory.notify_text, True, self.VAPOR_COLORS["gold"])
            nt.set_alpha(alpha)
            nx = (WINDOW_WIDTH - nt.get_width()) // 2
            ny = 20
            surface.blit(nt, (nx, ny))
