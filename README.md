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

## Characters

### NPCs

| Name | Role | Description |
|------|------|-------------|
| **Fruit Girl** | Healer | Sells fresh fruits that restore HP. Cheerful and always has a basket of sunshine for travelers. |
| **Good Witch** | Healer | Brews health potions under full moons. Her cauldron bubbles with nothing but good intentions. |
| **Herb Lady** | Healer | Forages deep woods for healing herbs. Knows every plant by its scent and secret. |
| **Milk Maid** | Healer | Sells fresh milk and dairy. A simple farm life, but she wouldn't trade it for anything. |
| **Dealer** | Merchant | Sells weapons, consumables, and gem substances. Robed figure with golden eyes. |
| **Quest Giver** | Quest NPC | Assigns bounties and rewards coins for completed tasks. |

### Enemies

#### Tier 1 — Basic Void Wildlife
| Name | AI | Attack | Traits |
|------|----|--------|--------|
| Void Mite | Wander | Touch | — |
| Ash Crawler | Ambush | Touch | — |
| Hollow Sprout | Stationary | Spores | — |
| Drift Slime | Chase | Touch | Splits on death |
| Static Rat | Teleport | Touch | — |

#### Tier 2 — Hunter Creatures
| Name | AI | Attack | Traits |
|------|----|--------|--------|
| Void Hound | Chase | Melee | — |
| Lantern Leech | Ambush | Leech | — |
| Echo Stalker | Chase | Melee | Invisible |
| Thorn Wisp | Kite | Projectile | — |
| Broken Sentinel | Chase | Melee | — |

#### Tier 3 — Corrupted Entities
| Name | AI | Attack | Traits |
|------|----|--------|--------|
| Petal Reaper | Chase | Melee | — |
| Memory Husk | Copy | Touch | — |
| Rift Walker | Teleport | Melee | — |
| Ink Parasite | Burst | Leech | — |
| Bloom Wraith | Phase Wander | Touch | Phases through walls |

#### Tier 4 — Void Intelligence
| Name | AI | Attack | Traits |
|------|----|--------|--------|
| Void Strategist | Kite | None | Buff aura |
| Fragment Clone | Copy | Melee | — |
| Data Leech | Chase | Slow | — |
| Silent Executioner | Burst | Burst | — |
| Root Network Node | Stationary | Summon | Spawns minions |

#### Tier 5 — Elite / Mini-Bosses
| Name | AI | Attack | Traits |
|------|----|--------|--------|
| Withered Gardener | Kite | Summon | Regenerates |
| Hollow Bloom Beast | Chase | Poison | — |
| Rift Colossus | Chase | AoE | — |
| Mirror Warden | Orbit | Beam | Illusions |
| Seedless King | Teleport | Pulse | — |

#### Tier 6 — World Events / Rare Entities
| Name | AI | Attack | Traits |
|------|----|--------|--------|
| Void Bloom Storm | Hazard | Poison | — |
| Wanderer of Nothing | Flee | None | Rare |
| Broken God Shard | Orbit | Beam | Rare |
| Glitch Angel | Teleport | Touch | Heal aura, Rare |
| Quiet Root | Stationary | None | Rare, Invincible |

### Bosses (Emotion Bosses)

| Name | Tier | HP | Attack | Theme |
|------|------|----|--------|-------|
| **Sorrow** | 5 | 1,000 | Tears | *The Sorrow Theme* — MGS3 |
| **Joy** | 5 | 1,200 | Laugh | Battle Theme 2 |
| **Fear** | 5 | 1,500 | Tendrils | Battle Theme 3 |
| **Pain** | 5 | 2,500 | Thorns | Battle Theme 4 |
| **Rage** | 6 | 4,000 | Rage | Battle Theme 5 |
| **Envy** | 6 | 3,000 | Copy | Battle Theme 6 |
| **Disgust** | 6 | 5,000 | Ooze | Battle Theme 7 |
| **Grief** | 6 | 4,500 | Sob | Battle Theme 8 |
| **Hope** | 6 | 7,000 | Heal | Battle Theme 9 |
| **Despair** | 6 | 9,000 | Void | Battle Theme 10 |

## Credits

Built with Pygame. Sound effects from FreeSFX GameSFX library. Fonts: SF Arborcrest Medium, VCR OSD Mono.
## Weapons

60 unique weapons across 7 categories and tiers 1–6, plus 300+ gem-infused variants.

### Weapon Types

| Type | Category | Examples |
|------|----------|----------|
| Dagger | Melee | Rusty Dagger, Shadow Dagger, Widowmaker |
| Sword | Melee | Worn Shortsword, Katana, Red Blade |
| Greatsword | Melee | Battle Axe, Soul Render, Godslayer |
| Spear | Melee | Broken Spear, Void Spear, Worldsplitter |
| Scythe | Melee | Scythe of Thorns, Twilight Scythe, Quietus |
| Staff | Magic | Cracked Staff, Eldritch Staff, Infinite Staff |
| Wand | Magic | Twig Wand, Flame Wand, Eternal Wand |
| Bow | Ranged | Makebow, Storm Bow, Phoenix Bow |
| Chakram | Ranged | Chipped Chakram, Chaos Chakram, Infinity Chakram |
| Void Blade | Melee | Void Arbiter, Voidheart, Heretic's Blade |
| Cursed Blade | Melee | Cursed Blade, Soul Eater |
| Forbidden Fruit | Magic | Forbidden Fruit |

### Tiers & Scaling

| Tier | Rarity | Damage Range | Magic Range |
|------|--------|--------------|-------------|
| 1 | Common | 2–7 | 0–4 |
| 2 | Uncommon | 8–16 | 0–8 |
| 3 | Rare | 15–24 | 2–14 |
| 4 | Epic | 26–40 | 4–24 |
| 5 | Legendary | 38–64 | 6–34 |
| 6 | Mythic | 52–100 | 8–52 |

### Special Effects

| Effect | Description |
|--------|-------------|
| `life_steal` | Heals the wielder on hit |
| `void_brand` | Leaves void damage over time |
| `magic_boost` | Amplifies spell damage |
| `crit_up` | Increases critical hit chance |
| `armor_pierce` | Ignores a portion of enemy defense |
| `burn` | Applies fire damage over time |
| `chain` | Attacks chain to nearby enemies |
| `defense_up` | Grants temporary defense buff |

### Gem Infusion System

Any craftable weapon can be infused with 6 gem types via crafting:

| Gem | Damage | Magic | Crit | Speed | Defense |
|-----|--------|-------|------|-------|---------|
| Ruby | +40% | +10% | +10% | — | — |
| Sapphire | +30% | +25% | +5% | +1% | — |
| Emerald | +20% | +40% | +5% | +1% | — |
| Diamond | +50% | +20% | +15% | +2% | +1 |
| Gold | +60% | +10% | +10% | +3% | +1 |
| Void | +100% | +80% | +30% | +4% | +2 |

Requires matching gem substance (purchased from dealers) + wood + coins.

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

'''
In the sacred realm of VOIDFLOWER lore, where gravity is optional and common sense has been permanently patched out, there exists a prophecy spoken only in lag spikes: “he who presses E in confusion shall ascend without permission.” Nobody knows what it means, but everyone agrees it goes hard.

The ancient NPC known as “Sus Sage #404” once whispered: “bro i was built different but the build got nerfed in the tutorial stage 💀.” After saying this, he immediately clipped through reality and became a background texture.

Legends say the sky is actually just a giant loading screen that never finishes because someone somewhere is speedrunning existence with airplane mode on. If you stare at it too long, you can hear the UI yelling “PLEASE WAIT…” in 240p audio.

There is also a forbidden weapon called the “Scroll of Mid Energy.” Whoever equips it instantly gains +50 aura loss but +100 comedic timing. Side effects include speaking exclusively in lowercase and accidentally emoting in real life.

In the deep zones of the map, players report encountering the entity known as “Rizzler of the Void,” who approaches slowly and says only: “u good?” If you answer, your save file becomes emotionally unavailable.

The economy of the world is based entirely on vibes and expired motivation. One coin equals approximately three braincells and a dream. Trading is prohibited unless both parties are actively confused.

At random intervals, the game triggers an event called “Group Chat Judgment Day,” where all enemies stop attacking and instead start rating your gameplay like it’s a TikTok comment section from hell.

The final boss is rumored to be your own past self, but with better aim, better sleep schedule, and significantly worse internet connection. Defeating it unlocks the achievement: “I survived my own delulu arc.”

And at the very end of everything, the system displays one final message in glitching neon text: “skill issue detected… but honestly same.”
'''

**v0.1.0 — Genesis**
- Initial Pygame setup
- Window and game loop
- Basic tile rendering
- Player movement prototype
- First enemy spawn test
