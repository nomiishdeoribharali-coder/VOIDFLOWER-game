# Voidflower

A top-down action RPG built with Pygame by **Nomiish Deori Bharali**. Fight through hordes of enemies, craft weapons, infuse them with rare gem substances, and survive boss encounters.

## Features

- Real-time combat with melee attacks and spell casting
- Dynamic enemy spawning with multiple AI types and boss fights
- Crafting system with 80+ recipes (weapons, consumables, permanent upgrades, special items)
- Gem weapon infusion — upgrade any craftable weapon with Ruby, Sapphire, Emerald, Diamond, Gold, or Void substances for unique stat boosts
- Inventory management with 999-slot capacity for weapons and consumables
- Cosmetic shop for skin and aura purchases
- Wood-chopping and resource gathering
- Killzone mode — defeat a wave of enemies for bonus rewards
- Particle effects, screen shake, bloom, and dynamic music/audio

## Requirements

- Python 3.12+
- Pygame 2.6.1

## Running

```bash
python3 main.py
```

## Controls

| Key | Action |
|-----|--------|
| WASD | Move |
| Mouse | Aim |
| Left Click | Cast selected spell |
| Right Click | Melee attack |
| 1–5 | Select spell slot |
| Space | Dash |
| C | Chop nearby tree (requires Level 5) |
| V | Open crafting menu |
| I | Open inventory |
| Q | Quick-item radial menu |
| G | Interact / Open shop |
| F | Pickup nearest weapon |
| R | Ultimate ability |
| M | Toggle music |
| Esc | Close menus / Pause |
| Tab | Toggle shop/radial menu |

## Crafting

Press `V` to open the crafting menu.

- **Wood** is gathered by chopping trees with `C` at Level 5+
- **Coins** are dropped by enemies or earned from quests/chests
- **Gem substances** can be purchased from traveling dealers

### Gem Weapon Tiers

| Gem | Damage | Magic | Crit | Speed | Defense |
|-----|--------|-------|------|-------|---------|
| Ruby | +40% | +10% | +10% | — | — |
| Sapphire | +30% | +25% | +5% | +1% | — |
| Emerald | +20% | +40% | +5% | +1% | — |
| Diamond | +50% | +20% | +15% | +2% | +1 |
| Gold | +60% | +10% | +10% | +3% | +1 |
| Void | +100% | +80% | +30% | +4% | +2 |

## Soundtrack

Music and themes featured or inspired by:

- **I Really Want to Stay at Your House** — *Cyberpunk 2077*
- **The Sorrow Theme** — *Metal Gear Solid 3: Snake Eater*
- **Cyberia (B-Side)** — Nicopatty
- **Dark Skies** — *Metal Gear Rising: Revengeance*
- **If YouTube Serves You This Song You're Iconic**
- **Impatience** — *Jujutsu Kaisen*
- **JJK Phantom Parade** — Gacha Theme
- **Maki vs Naoya, The Zenin Fight** — *Jujutsu Kaisen*
- **No Hesitation S2** — *Jujutsu Kaisen*
- **Self-Embodiment of Perfection** — *Jujutsu Kaisen*
- **The Pain of Recalling Memories of an Empty Life**
- **Working Overtime** — *Jujutsu Kaisen*

## Credits

Built with Pygame. Sound effects from FreeSFX GameSFX library. Fonts: SF Arborcrest Medium, VCR OSD Mono.

## Author

**Nomiish Deori Bharali** — Game design, programming, and art direction.

## Update Timeline

**v0.9.0 — The Void Awakens** *(Current)*
- Added gem weapon infusion system (Ruby, Sapphire, Emerald, Diamond, Gold, Void)
- Expanded crafting to 250+ recipes with full gem variant support
- Dealer shops now sell gem substances
- Inventory cap increased to 999 slots
- Boss limit enforced (single boss at a time)
- Added Killzone mode with wave clears and rewards
- Implemented domain expansion ultimate ability
- Wood-chopping mechanic (Level 5+)
- Cosmetic shop overhaul with skins and auras

**v0.8.5 — Wood & Crafting**
- Complete crafting system implementation (80+ recipes)
- Wood resource gathering from trees
- Crafting menu bound to `V` key
- Added weapon, consumable, upgrade, and special item recipes
- Pause menu integration for crafting

**v0.8.0 — Combat Refined**
- Spell casting system with 5 spell slots
- Melee attack overhaul with arc detection
- Parry mechanics with visual feedback
- Dash ability with cooldown
- Particle emitter for spell/hit effects
- Screen shake on impacts

**v0.7.2 — Audio Overhaul**
- Full sound effect integration via AudioManager
- Dynamic music crossfading (explore, battle, boss, shop, ultimate)
- Spell, explosion, pickup, and UI click sfx
- Volume balancing and sfx toggle support

**v0.7.0 — Progression**
- Level-up system with stat scaling
- Mutation/evolution system for weapons
- Quest system with NPC interactions
- XP tomes and permanent stat upgrades
- Radial quick-item menu

**v0.6.0 — The World**
- Tile-based world with biome transitions
- Camera system with smooth follow
- Enemy spawning with difficulty scaling
- Boss encounters with unique themes
- Multiple enemy AI types (ranged, melee, burst, spores, beams)

**v0.5.0 — Inventory & UI**
- Full inventory management system
- Dealer shop with randomized stock
- HUD with health/mana bars and minimap
- Vaporwave-styled UI panels
- Equipment and consumable slots

**v0.4.0 — Weapons**
- 25 unique base weapons across tiers 1–6
- Weapon drop system with rarity colors
- Melee attack arcs and knockback
- Magic and physical damage types
- Critical hit system

**v0.3.0 — Entities**
- Player movement and collision
- Enemy types with varied stats
- NPC and merchant entities
- Tree chopping and world objects
- Death/respawn system with typewriter effect

**v0.2.0 — Engine**
- Scene management system
- Input handling abstraction
- Particle system foundation
- Camera and viewport system
- Bloom post-processing effect

**v0.1.0 — Genesis**
- Initial Pygame setup
- Window and game loop
- Basic tile rendering
- Player movement prototype
- First enemy spawn test
