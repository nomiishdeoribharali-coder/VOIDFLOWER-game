import math
import random

MUTATION_THRESHOLD = 20
CHAIN_WINDOW = 2.0
LOW_HP_RATIO = 0.3
FULL_HP_RATIO = 0.95
HAZARD_DISTANCE = 60

MUTATION_NAMES = {
    ("duelist", "combo"): "Rapid Precision",
    ("duelist", "slow"): "Judgment Edge",
    ("cleave", "combo"): "Crowd Bloom",
    ("cleave", "slow"): "Executioner's Sweep",
    ("duelist", "combo", "berserker"): "Berserker Precision",
    ("cleave", "combo", "berserker"): "Frenzy Swarm",
    ("duelist", "slow", "berserker"): "Void Reckoning",
    ("cleave", "slow", "berserker"): "Ruin Cleaver",
    ("duelist", "combo", "terrain"): "Corrupted Fang",
    ("cleave", "combo", "terrain"): "Bloom of Decay",
    ("duelist", "slow", "terrain"): "Abyssal Judgment",
    ("cleave", "slow", "terrain"): "Plague Sweep",
    ("duelist", "combo", "pure"): "Radiant Edge",
    ("cleave", "combo", "pure"): "Bloom of Light",
    ("duelist", "slow", "pure"): "Divine Verdict",
    ("cleave", "slow", "pure"): "Purifying Sweep",
    ("berserker",): "Berserker Relic",
    ("berserker", "terrain"): "Void Corrupted",
    ("berserker", "pure"): "Unstable Divinity",
    ("terrain",): "Corruption Core",
    ("pure",): "Pure Form",
    ("stable",): "Mythic Stable",
}

EFFECT_MAP = {
    "duelist": "crit_up",
    "cleave": "chain",
    "combo": None,
    "slow": "armor_pierce",
    "berserker": "life_steal",
    "stable": "defense_up",
    "terrain": "void_brand",
    "pure": "magic_boost",
}


class MutationTracker:
    def __init__(self):
        self.per_weapon = {}

    def get_stats(self, weapon_key):
        if weapon_key not in self.per_weapon:
            self.per_weapon[weapon_key] = {
                "single_kills": 0,
                "multi_kills": 0,
                "chain_kills": 0,
                "slow_kills": 0,
                "low_hp_kills": 0,
                "full_hp_kills": 0,
                "hazard_kills": 0,
                "pure_kills": 0,
                "last_kill_time": -999.0,
                "total_kills": 0,
            }
        return self.per_weapon[weapon_key]

    def record_kill(self, weapon_key, num_hit, time_since_last, hp_ratio, near_hazard, game_time):
        s = self.get_stats(weapon_key)
        s["total_kills"] += 1

        if num_hit <= 1:
            s["single_kills"] += 1
        else:
            s["multi_kills"] += 1

        if time_since_last < CHAIN_WINDOW:
            s["chain_kills"] += 1
        else:
            s["slow_kills"] += 1

        if hp_ratio < LOW_HP_RATIO:
            s["low_hp_kills"] += 1
        elif hp_ratio >= FULL_HP_RATIO:
            s["full_hp_kills"] += 1

        if near_hazard:
            s["hazard_kills"] += 1
        else:
            s["pure_kills"] += 1

        s["last_kill_time"] = game_time

    def should_mutate(self, weapon_key):
        s = self.per_weapon.get(weapon_key)
        return s and s["total_kills"] >= MUTATION_THRESHOLD and s["total_kills"] % MUTATION_THRESHOLD == 0

    def get_mutation_profile(self, weapon_key):
        s = self.per_weapon.get(weapon_key)
        if not s or s["total_kills"] == 0:
            return {}
        total = s["total_kills"]
        profile = {}
        # Aggression: single vs multi
        sr = s["single_kills"] / max(s["single_kills"] + s["multi_kills"], 1)
        if sr > 0.6:
            profile["aggression"] = "duelist"
        elif sr < 0.4:
            profile["aggression"] = "cleave"

        # Rhythm: chain vs slow
        cr = s["chain_kills"] / max(s["chain_kills"] + s["slow_kills"], 1)
        if cr > 0.6:
            profile["rhythm"] = "combo"
        elif cr < 0.4:
            profile["rhythm"] = "slow"

        # Risk: low hp vs full hp
        lr = s["low_hp_kills"] / max(s["low_hp_kills"] + s["full_hp_kills"], 1)
        if lr > 0.6:
            profile["risk"] = "berserker"
        elif lr < 0.4 and s["full_hp_kills"] > 0:
            profile["risk"] = "stable"

        # Environment: hazard vs pure
        hr = s["hazard_kills"] / max(s["hazard_kills"] + s["pure_kills"], 1)
        if hr > 0.6:
            profile["env"] = "terrain"
        elif hr < 0.4:
            profile["env"] = "pure"

        return profile

    def get_mutation_name(self, profile):
        traits = [v for v in profile.values() if v]
        if not traits:
            return "Evolved"
        traits.sort()
        for key in (
            tuple(traits),
            traits[-1:] and tuple(traits[-1:]),
            (traits[0],) if traits else None,
        ):
            if key and key in MUTATION_NAMES:
                return MUTATION_NAMES[key]
        return traits[0].title() + " Evolved"


def evolve_weapon(base_weapon, profile, player_level):
    w = dict(base_weapon)
    tier_boost = min(6, w["tier"] + 1)
    w["tier"] = tier_boost
    scale = 1.0 + (player_level - 1) * 0.05

    for axis, pole in profile.items():
        if pole == "duelist":
            w["crit"] = w.get("crit", 0) + 10 + player_level // 2
            w["damage"] = int(w["damage"] * (1.1 + 0.02 * player_level))
            if "effect" not in w or not w["effect"]:
                w["effect"] = "crit_up"
        elif pole == "cleave":
            w["damage"] = int(w["damage"] * (1.05 + 0.02 * player_level))
            if "effect" not in w or not w["effect"]:
                w["effect"] = "chain"
        elif pole == "combo":
            w["speed_bonus"] = w["speed_bonus"] + 0.08 + player_level * 0.003
        elif pole == "slow":
            w["damage"] = int(w["damage"] * (1.2 + 0.03 * player_level))
            w["speed_bonus"] = max(0.05, w["speed_bonus"] - 0.03)
            if "effect" not in w or not w["effect"]:
                w["effect"] = "armor_pierce"
        elif pole == "berserker":
            w["damage"] = int(w["damage"] * (1.15 + 0.03 * player_level))
            if "effect" not in w or not w["effect"]:
                w["effect"] = "life_steal"
        elif pole == "stable":
            w["defense"] = w["defense"] + 3 + player_level // 2
            if "effect" not in w or not w["effect"]:
                w["effect"] = "defense_up"
        elif pole == "terrain":
            w["damage"] = int(w["damage"] * (1.1 + 0.02 * player_level))
            w["magic"] = int(w["magic"] + 5 + player_level // 2)
            if "effect" not in w or not w["effect"]:
                w["effect"] = "void_brand"
        elif pole == "pure":
            w["damage"] = int(w["damage"] * (1.08 + 0.02 * player_level))
            w["magic"] = int(w["magic"] + 3 + player_level // 3)
            if "effect" not in w or not w["effect"]:
                w["effect"] = "magic_boost"

    w["damage"] = max(1, w["damage"])
    w["magic"] = max(0, w["magic"])
    w["speed_bonus"] = min(0.5, max(0.0, w["speed_bonus"]))
    w["defense"] = max(0, w["defense"])
    w["crit"] = min(80, max(0, w.get("crit", 0)))

    colorshift = _shift_color(w["color"], profile)
    w["color"] = colorshift

    return w


def _shift_color(base_color, profile):
    r, g, b = base_color
    for pole in profile.values():
        if pole in ("duelist", "combo"):
            r = min(255, r + 30)
            b = min(255, b + 20)
        elif pole == "cleave":
            g = min(255, g + 40)
        elif pole == "slow":
            r = min(255, r + 40)
        elif pole == "berserker":
            r = min(255, r + 50)
            g = max(0, g - 20)
        elif pole == "stable":
            b = min(255, b + 30)
            g = min(255, g + 20)
        elif pole == "terrain":
            r = min(255, r + 20)
            g = max(0, g - 30)
            b = max(0, b - 20)
        elif pole == "pure":
            r = min(255, r + 20)
            g = min(255, g + 20)
            b = min(255, b + 40)
    return (r, g, b)


def reset_weapon_stats(tracker, weapon_key):
    if weapon_key in tracker.per_weapon:
        del tracker.per_weapon[weapon_key]
