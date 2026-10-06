# Modrinth listing: fava

Everything to paste into the project settings. Nothing here has been sent anywhere.

## Summary (General → Summary, 227/256)

```
Vanilla Minecraft, polished: full visual and sound overhaul, a performance core, a 7-age progression with 200+ quests (TEMPERED), a modern journal on J and its own loader. No new blocks or mobs. Fabric, Minecraft 26.2 and 26.3.
```

## Environment (when uploading a version)

**Client and server → Required on both.** Players need the pack on the client (journal, loader, translations) and the server needs TEMPERED (ages, recipes, locks).

## License (License)

- Select **All Rights Reserved/No License** and **leave the License URL empty**. A link to Wikipedia is what Modrinth flags: the URL must point at the licence text itself, and "All rights reserved" has no text to link to.
- The licence covers your own content in the pack (Fancy Vanilla resource pack, artwork, configuration). TEMPERED stays MIT in its own repo/jar; the downloaded mods keep their authors' licences.
- If you make the GitHub repo public with code under MIT, you may instead pick **MIT** for the pack and put the link to the repo's `LICENSE` file as URL. Artwork can stay all-rights-reserved in `brand/`.

## Links (Links)

- **Source code:** https://github.com/wtfangler/fava (the repository is public). Your website is not source code.
- **Wiki page:** your website (https://fava.netlify.app/).
- Issue tracker: https://github.com/wtfangler/fava/issues

## Disclosures (Disclosures)

- **Contains AI-generated content:** enable it and tick **Code** and **Text**. The mod code (TEMPERED, Fancy Journal, loader), quest texts and tooling were written with Claude Code, and Modrinth requires this to be declared when AI wrote a substantial part of the code. Artwork is yours (leave Assets unticked).
- Generative AI functionality, advertisements, paid features, telemetry: leave off (none of them applies).

## Gallery (Gallery)

Upload in this order, set number 1 as featured. Files are in `brand/modrinth-gallery/`.

| # | File | Title | Description |
|---|------|-------|-------------|
| 1 | `brand/modrinth-gallery/01-banner-1920x1080.jpg` | Fancy Vanilla | Main banner (set as featured) |
| 2 | `brand/modrinth-gallery/02-loader-start.png` | Own loading screen | Fancy Vanilla loader at game start |
| 3 | `brand/modrinth-gallery/03-loader-saving.png` | Saving the world | The same loader while saving on exit |
| 4 | `brand/modrinth-gallery/04-journal-epilog.png` | Fancy Journal: Epilogue | Journal on the J key with the post-dragon Epilogue tab |
| 5 | `brand/modrinth-gallery/05-journal-fj_1_wide.png` | Fancy Journal: ages | Tabs per age with progress bars |
| 6 | `brand/modrinth-gallery/06-journal-fj_5_pause_menu.png` | One progress screen | Pause menu with the single journal entry |
| 7 | `brand/modrinth-gallery/07-track-fj_t1_pin.png` | Quest tracking | A pin on every quest; the tracked one gets a frame |
| 8 | `brand/modrinth-gallery/08-track-fj_t5_hud_multi.png` | Tracker panel | What to do and how far you are: checklist with counters |

Shots 2 to 8 come from the automated test on the real game, not staged screenshots. Add a few of your own from normal play (menu, a build with shaders) when you have them; they sell the pack better than test shots.

## Description (Description)

Paste everything between the lines. The banner at the top is your existing image on cdn.modrinth.com.

---
![Fancy Vanilla Banner](https://cdn.modrinth.com/data/cached_images/50ed80c237c4a70634c52b59643f9cb7e70da268.jpeg)

**Fancy Vanilla** keeps Minecraft vanilla and makes it look, sound and run better. There are no new blocks, mobs or biomes: you get the game you know, carefully polished, plus a progression system and a reason to keep playing after the Ender Dragon.

Available for **Minecraft 26.2** and **26.3** on **Fabric**. Built for singleplayer first, with a server-compatible setup for small groups of friends.

## What is inside

### Visual and sound polish
- Curated resource packs for foliage, leaves, crops, animations, mob models, fonts, GUI and sound, ordered so they do not fight each other.
- Particle, water and weather effects (a few of them are available on 26.2 only), a tidied interface and a Fancy Vanilla title screen.
- Two optional shader packs (via Iris). The pack is tuned to look good without them.

### Performance core
- The optimisation set from **Streamline Master**: rendering, chunk loading and generation, memory use, networking and fast game exit.
- Client-only mods are marked as client-only, so a server built from this pack does not load them.
- Note: I have not published FPS benchmarks. Results depend on your hardware, render distance and shader choice.

### TEMPERED, the seven-age progression
TEMPERED is my own mod. The world moves through seven ages, and each one unlocks recipes and gear:

| Age | Name | Quests needed to advance |
|-----|------|--------------------------|
| 1 | Wood | 6 of 9 |
| 2 | Stone | 9 of 15 |
| 3 | Iron | 8 of 13 |
| 4 | Diamond | 8 of 13 |
| 5 | Nether | 9 of 14 |
| 6 | End | 8 of 13 |
| 7 | Post-End | 8 of 12 |

- **89 original quests** make up the ages. You do not have to finish everything: only the number in the table is needed to advance.
- **63 optional personal quests** (9 per age) with small XP rewards. They never change how many quests an age needs.
- **55 Epilogue quests** that appear after you defeat the Ender Dragon, for the long game: elytra, dragon egg, navigation, rockets and more.
- Progress is shared by the world, so it also works on a server.

#### What the locks do
- Crafting of recipes from a higher age is blocked until that age is reached.
- *Holding or wearing* gear from a higher age gives **Mining Fatigue and Weakness** while it is held or worn. Take it off or put it away and the effect is cleared right away.
- **Items are never taken from you.** Anything you find in chests, loot, trades or drops stays in your inventory; it is only the use that is limited.
- Creative and spectator mode are not affected.

#### Commands
- `/trigger tempered.menu` opens the in-game menu with your status.
- Admins (`/function tempered:admin/...`): `help`, `diag`, `skip` (next age), `set_age {n:3}`, `reset`, `gate_off` and `gate_on` to disable or enable all locks and debuffs.
- Commands and messages are translated into English and Polish.

### Fancy Journal
One modern progress screen on **J** (rebindable) that replaces the two vanilla ones.
- Tabs per age with progress bars, search, and filters: all, remaining, completed.
- Optional quests are kept apart from the required count, and the Epilogue tab unlocks after the dragon.
- **Quest tracking:** a pin on every quest tracks it. A small panel in the bottom-right corner of the screen (movable in `config/fancy_journal.json`) shows the quest name, what to do, a checklist of the requirements with counters such as *Get: Any planks 20/32* (items are counted from your inventory, the rest from your statistics) and a progress bar, even with the journal closed. It disappears a few seconds after you finish the quest.
- Hold Shift while opening it for the classic vanilla view. If the journal ever fails, the game falls back to the classic screen on its own.

### Own loading screen
A dark screen with the Fancy Vanilla wordmark and a thin progress line replaces the Mojang logo at game start and resource reload, and is also shown while the world is saving on exit. The game still runs and fades loading as usual; the overlay only draws on top, and if it cannot load you simply get the vanilla screen.

### Languages
Quests, achievements, the journal, admin commands and the mod descriptions in Mod Menu come in **English** and **Polish**. There is no separate switch: they follow the game language (Options > Language).

## Installation
1. Install **Modrinth App** (or Prism Launcher) and use **Java 25** (the launcher can download it).
2. Search for Fancy Vanilla and install the version that matches your Minecraft version, or import the `.mrpack` file.
3. Give the client **6 GB of RAM** (the pack has over 100 mods) and launch the profile. Fabric, all mods and all settings are applied automatically.

## Servers
The pack is server-compatible. Startup, `/reload` and restart were tested on dedicated servers for 26.2 and 26.3 with no data-pack errors; I have not load-tested it with many players. Players need the pack installed on the client so that quests, the journal and the translations show up correctly.

## Good to know
- Only three files are bundled in the pack and they are all my own: TEMPERED, Fancy Journal and the Fancy Vanilla resource pack. Everything else is downloaded from Modrinth when you install.
- This is an **alpha** release. Quests were validated against the game registries and only a handful were completed in-game so far; long play sessions are still to be tested. Please report problems.
- **Mods built for another game version** (their authors tag them as compatible): 26.2: Chat Heads (26.1), Falling Leaves (26.1), Fast IP Ping (26.1.2), Visuality (26.3); 26.3: Async Logger (26.1.2), Entity View Distance (26.2), Explosive Enhancement (26.2), FastQuit (26.2), Glowing Torchflower (26.2), Main Menu Credits (26.2), Make Bubbles Pop (26.2).
- **Beta and alpha mods:** 26.2: Concurrent Chunk Management Engine (Fabric) (beta), EclipseUI (beta), OptiGUI (beta), Particle Rain (beta), Smooth Swapping (beta), Sound Physics Remastered (beta), Sounds (beta), Very Many Players (Fabric) (alpha), Visuality (beta), Wakes (beta); 26.3: Better Clouds (beta), Better Statistics Screen (beta), EclipseUI (beta), OptiGUI (beta), Smooth Swapping (beta), Sound Physics Remastered (beta), TCDCommons API (beta), Visuality (beta). Before long server sessions, check FastBack and world re-creation.

## Perfect for
- Players who want vanilla survival with better visuals, sound and performance
- Small groups who want a shared progression without learning a new game
- Players who finished the game and want goals for the long run

## Changelog highlights (0.2.0)
- 26.3: new base, Streamline Master 1.6.2-beta (the author's own 26.3 build).
- Quest tracking with a pin and a small HUD panel that shows what to do and how far you are.
- New TEMPERED icon; mod descriptions in Mod Menu follow the game language.
- Own loading screen (start, reload, saving).
- Commands and messages available in English and Polish.
- More optional quests, including 55 in the Epilogue.
- One journal on J instead of two progress screens.

<details>
<summary>Included content and credits (Minecraft 26.2)</summary>

All of this is downloaded from Modrinth when you install the pack. Thank you to every author.

**Mods (96)**

- [AmbientEnvironment-fabric-26.2-26.2.1](https://modrinth.com/project/DyTvM1dv)
- [AmbientSounds_FABRIC_v6.3.6_mc26.2](https://modrinth.com/project/fM515JnW)
- [BadOptimizations-2.4.1-26.2-fabric](https://modrinth.com/project/g96Z4WVZ)
- [BetterF3-19.0.0-Fabric-26.2](https://modrinth.com/project/8shC1gFX)
- [BetterGrassify-1.8.7+fabric.26.2](https://modrinth.com/project/m5T5xmUy)
- [Chunky-Fabric-1.5.3](https://modrinth.com/project/fALzjamp)
- [Clumps-fabric-26.2-26.2.1](https://modrinth.com/project/Wnxd13zP)
- [Controlling-fabric-26.2-26.2.4](https://modrinth.com/project/xv94TkTM)
- [CreativeCore_FABRIC_v2.14.16_mc26.2](https://modrinth.com/project/OsZiaDHq)
- [DetailArmorBarReconstructed-5.3.2-26.2-fabric](https://modrinth.com/project/Si9Uim4y)
- [EclipseUI-fabric-1.0.5+mc26.2-rc-2](https://modrinth.com/project/99cGtHRy)
- [ForgeConfigAPIPort-v26.2.1-mc26.2.x-Fabric](https://modrinth.com/project/ohNO6lps)
- [ImmediatelyFast-Fabric-1.16.4+26.2](https://modrinth.com/project/5ZwdcRci)
- [Ixeris-4.6.5+26.2-fabric](https://modrinth.com/project/p8RJPJIC)
- [Jade-mc26.2-Fabric-26.2.11](https://modrinth.com/project/nvQzSEkH)
- [MouseTweaks-fabric-mc26.2-2.31](https://modrinth.com/project/aC3cM3Vq)
- [NoChatReports-FABRIC-26.2-v2.20.2](https://modrinth.com/project/qQyHxfxd)
- [PacketFixer-fabric-3.3.6](https://modrinth.com/project/c7m1mi73)
- [ParticleEffects-1.6.0+26.2+fabric](https://modrinth.com/project/PLAGcSFJ)
- [Searchables-fabric-26.2-1.0.1](https://modrinth.com/project/fuuu3xnx)
- [ShoulderSurfing-Fabric-26.2-5.2.0](https://modrinth.com/project/kepjj2sy)
- [SubtleEffects-fabric-26.2-1.14.3](https://modrinth.com/project/4q8UOK1d)
- [almanac-fabric-26.2-1.26.7.3](https://modrinth.com/project/Gi02250Z)
- [animatica-0.6.3+26.2](https://modrinth.com/project/xEyZuswh)
- [appleskin-fabric-mc26.2-3.0.10](https://modrinth.com/project/EsAfCjCV)
- [baguettelib-26.2-Fabric-2.0.7](https://modrinth.com/project/OfKzpbRU)
- [bbe-fabric-1.3.7+mc26.2](https://modrinth.com/project/ONZm0H7Y)
- [better-clouds-1.14.4+26.2-fabric](https://modrinth.com/project/5srFLIaK)
- [bettermounthud-1.3.1](https://modrinth.com/project/kqJFAPU9)
- [betterstats-5.5.6+fn-26.2](https://modrinth.com/project/n6PXGAoM)
- [bookshelfinspector-fabric-2.4+26.2](https://modrinth.com/project/rOrXjyPb)
- [capes-1.5.11+26.2](https://modrinth.com/project/89Wsn8GD)
- [chat_heads-1.3.1-fabric-26.1](https://modrinth.com/project/Wb5oqrBJ)
- [cherishedworlds-fabric-17.0.0+26.2](https://modrinth.com/project/3azQ6p0W)
- [chloride-FABRIC-mc26.2-v1.8.1](https://modrinth.com/project/yD9qW65f)
- [cloth-config-26.2.155](https://modrinth.com/project/9s6osm5g)
- [continuity-3.0.1+26.2](https://modrinth.com/project/1IjD5062)
- [controlify-3.5.3+mc26.2-universal](https://modrinth.com/project/DOUdJVEm)
- [debugify-26.2.0.0](https://modrinth.com/project/QwxR6Gcd)
- [durabilitytooltip-1.2.0a-fabric-mc26.2](https://modrinth.com/project/smUP7V3r)
- [dynamic-fps-3.11.9+minecraft-26.2.0-fabric](https://modrinth.com/project/LQ3K71Q1)
- [dynamiccrosshair-9.14+26.2-fabric](https://modrinth.com/project/ZcR9weSm)
- [entity_model_features-3.3.10-26.2-fabric](https://modrinth.com/project/4I1XuqiY)
- [entity_texture_features-7.2.5-26.2-fabric](https://modrinth.com/project/BVzZfTc1)
- [entityculling-fabric-1.10.5-mc26.2](https://modrinth.com/project/NNAgCjsB)
- [explosive-enhancement-1.4.2-26.2](https://modrinth.com/project/OSQ8mw2r)
- [fabric-api-0.161.0+26.2](https://modrinth.com/project/P7dR8mSH)
- [fabric-language-kotlin-1.14.1+kotlin.2.4.20](https://modrinth.com/project/Ha28R6CL)
- [fallingleaves-2.0.7+26.1](https://modrinth.com/project/WhbRG4iK)
- [fast-ip-ping-v1.0.11-mc26.1.2](https://modrinth.com/project/9mtu0sUO)
- [fastback-fabric-0.34.0+26.2.0](https://modrinth.com/project/ZHKrK8Rp)
- [fastquit-3.1.5+mc26.2](https://modrinth.com/project/x1hIzbuY)
- [ferritecore-9.0.0-fabric](https://modrinth.com/project/uXXizFIs)
- [fzzy_config-0.7.6+26.2](https://modrinth.com/project/hYykXjDp)
- [glowing-torchflower-fabric-mc26.2-1.4.1](https://modrinth.com/project/1S4LxcvL)
- [inventorysorter-fabric-3.0.1+mc26.2](https://modrinth.com/project/5ibSyLAz)
- [iris-fabric-1.11.2+mc26.2](https://modrinth.com/project/YL57xq9U)
- [krypton-0.3.1](https://modrinth.com/project/fQEb0iXm)
- [lambdynamiclights-4.12.4+26.2](https://modrinth.com/project/yBW8D80W)
- [language-reload-1.7.7+26.2](https://modrinth.com/project/uLbm7CG6)
- [letmedespawn-fabric-26.2-1.26.7.3](https://modrinth.com/project/vE2FN5qn)
- [lithium-fabric-0.25.3+mc26.2](https://modrinth.com/project/gvQqBUqZ)
- [main-menu-credits-1.4.0+26.2-universal](https://modrinth.com/project/qJDfP7WN)
- [make_bubbles_pop-0.3.4-fabric-mc26.2.x](https://modrinth.com/project/gPCdW0Wr)
- [modernfix-5.27.19-build.1](https://modrinth.com/project/TjSm1wrD)
- [modmenu-20.0.1](https://modrinth.com/project/mOgUt4GM)
- [morechathistory-2.0.0](https://modrinth.com/project/8qkXwOnk)
- [moreculling-fabric-26.2-1.8.1](https://modrinth.com/project/51shyZVL)
- [mru-1.0.41+26.2-fabric](https://modrinth.com/project/SNVQ2c0g)
- [notenoughanimations-fabric-1.12.5-mc26.2](https://modrinth.com/project/MPCX6s5C)
- [nowplaying-fabric-2.103.1+26.2](https://modrinth.com/project/eNF4Bfla)
- [optigui-2.3.0-beta.10+26.2](https://modrinth.com/project/JuksLGBQ)
- [particle_core-0.3.3+26.2](https://modrinth.com/project/RSeLon5O)
- [particlerain-4.0.0-beta.11+26.2-fabric](https://modrinth.com/project/nrikgvxm)
- [particular-26.2-Fabric-1.5.7](https://modrinth.com/project/pYFUU6cq)
- [puzzle-fabric-2.3.1+26.2](https://modrinth.com/project/3IuO68q1)
- [reeses-sodium-options-fabric-2.2.3+mc26.2](https://modrinth.com/project/Bh37bMuy)
- [skinlayers3d-fabric-1.11.3-mc26.2](https://modrinth.com/project/zV5r3pPn)
- [smoothgui-fabric-2.0.5+mc26.2](https://modrinth.com/project/j6yrZogB)
- [smoothscroll-2.9.2](https://modrinth.com/project/CllP7wW0)
- [smoothswapping-0.9.10-26.2-fabric](https://modrinth.com/project/ydZic5r4)
- [sodium-extra-fabric-0.9.3+mc26.2](https://modrinth.com/project/PtjYWJkn)
- [sodium-fabric-0.9.1+mc26.2](https://modrinth.com/project/AANobbMI)
- [sodium-shadowy-path-blocks-fabric-7.0.0](https://modrinth.com/project/EIa1eiMm)
- [sound-physics-remastered-fabric-1.5.1+26.2](https://modrinth.com/project/qyVF9oeo)
- [sounds-2.5.1+edge+26.2-fabric](https://modrinth.com/project/ZouiUX7t)
- [spark-1.10.187-fabric](https://modrinth.com/project/l6YH9Als)
- [status-effect-bars-1.0.12](https://modrinth.com/project/x02cBj9Y)
- [supermartijn642configlib-1.1.8a-fabric-mc26.2](https://modrinth.com/project/LN9BxssP)
- [tcdcommons-5.5.6+fn-26.2](https://modrinth.com/project/Eldc1g37)
- [visuality-0.7.15+26.3](https://modrinth.com/project/rI0hvYcd)
- [wakes-0.7.1+26.2](https://modrinth.com/project/dlNu0RQY)
- [xaerominimap-fabric-26.2-26.5.1](https://modrinth.com/project/1bokaNcj)
- [xaeroworldmap-fabric-26.2-1.46.1](https://modrinth.com/project/NcUtCpym)
- [yet_another_config_lib_v3-3.9.6+26.2-fabric](https://modrinth.com/project/1eAoo2KR)
- [zoomify-2.16.1+26.2](https://modrinth.com/project/w7ThoJFB)

**Resource packs (26)**

- [AL's Creepers Revamped 2.0](https://modrinth.com/project/d2srP5t3)
- [AL's Enderman Revamped+FA 2.0](https://modrinth.com/project/ERTkxp3u)
- [AL's Scorpions & Crabs+FA 2.0](https://modrinth.com/project/6vTt8GmW)
- [AL's Skeletons Revamped+FA 2.0](https://modrinth.com/project/Q1DELmr6)
- [Better Lanterns v1.4.0 - 26.2+26.3](https://modrinth.com/project/PGGrfcvL)
- [Better-Leaves-9.6](https://modrinth.com/project/uvpymuxq)
- [Clearer Slot Highlight](https://modrinth.com/project/NITh4Uod)
- [Eggs N Eyes 1.0.7](https://modrinth.com/project/Fn2kXmlX)
- [EvenBetterEnchants_v3_1.21.5+](https://modrinth.com/project/6udpuGCH)
- [Fancy Crops v1.3](https://modrinth.com/project/UGEVQ6t9)
- [Fast Better Grass](https://modrinth.com/project/dspVZXKP)
- [FreshAnimations_v1.10.5](https://modrinth.com/project/50dA9Sha)
- [LowOnFire v26.2§8](https://modrinth.com/project/RRxvWKNC)
- [Os' Colorful Grasses (Tall)](https://modrinth.com/project/O2zhH8n8)
- [PDB3D's Blocky Armor Stands AV](https://modrinth.com/project/v7QpjqDY)
- [RAYs_3D_Ladders_v2.4](https://modrinth.com/project/Uupo7yGf)
- [RAYs_3D_Rails_v3.6](https://modrinth.com/project/jKa9Ievs)
- [Re-covered](https://modrinth.com/project/6gN7YVi7)
- [Recolourful Containers DARK 3.1.3 (1.19.4+)](https://modrinth.com/project/sQCUH0Mr)
- [Simple Grass Flowers v2.0.0](https://modrinth.com/project/ti9KkMHm)
- [Theone's Eating Animation Pack v1.0](https://modrinth.com/project/OhzX8kDf)
- [better_flame_particles-v3.1-mc1.21.9+-resourcepack](https://modrinth.com/project/ivUZsvzp)
- [qrafty's-capitalized-font-4.0](https://modrinth.com/project/FA4ebMMU)
- [visual_armor_trims_4.2](https://modrinth.com/project/tPtjib62)
- [§3Fresh §bFlower Pots](https://modrinth.com/project/CmEN0T1m)
- [§6Bushier Bushes§r](https://modrinth.com/project/ukVOzUX4)

**Shader packs (2)**

- [ComplementaryReimagined_r5.9.3](https://modrinth.com/project/HVnmMxH1)
- [miniature-shader-2.19](https://modrinth.com/project/UaS8ROxa)

</details>

<details>
<summary>Included content and credits (Minecraft 26.3)</summary>

**Mods (102)**

- [AmbientEnvironment-fabric-26.3-26.3.2](https://modrinth.com/project/DyTvM1dv)
- [AmbientSounds_FABRIC_v6.3.6_mc26.3](https://modrinth.com/project/fM515JnW)
- [BadOptimizations-2.4.1-26.3-fabric](https://modrinth.com/project/g96Z4WVZ)
- [BetterF3-20.0.0-Fabric-26.3](https://modrinth.com/project/8shC1gFX)
- [BetterGrassify-1.8.8+fabric.26.3](https://modrinth.com/project/m5T5xmUy)
- [Chunky-Fabric-1.5.3](https://modrinth.com/project/fALzjamp)
- [Clumps-fabric-26.3-26.3.2](https://modrinth.com/project/Wnxd13zP)
- [Controlling-fabric-26.3-26.3.3](https://modrinth.com/project/xv94TkTM)
- [CreativeCore_FABRIC_v2.14.19_mc26.3](https://modrinth.com/project/OsZiaDHq)
- [DetailArmorBarReconstructed-5.3.2-26.3-fabric](https://modrinth.com/project/Si9Uim4y)
- [EclipseUI-fabric-1.0.5-fabric-26.3](https://modrinth.com/project/99cGtHRy)
- [ForgeConfigAPIPort-v26.3.1-mc26.3.x-Fabric](https://modrinth.com/project/ohNO6lps)
- [ImmediatelyFast-Fabric-1.17.1+26.3](https://modrinth.com/project/5ZwdcRci)
- [Ixeris-4.6.8+26.3-fabric](https://modrinth.com/project/p8RJPJIC)
- [Jade-mc26.3-Fabric-26.3.5](https://modrinth.com/project/nvQzSEkH)
- [Ksyxis-1.4.5](https://modrinth.com/project/2ecVyZ49)
- [MouseTweaks-fabric-mc26.3-2.31](https://modrinth.com/project/aC3cM3Vq)
- [NoChatReports-FABRIC-26.3-v2.21.0](https://modrinth.com/project/qQyHxfxd)
- [PacketFixer-fabric-3.3.6](https://modrinth.com/project/c7m1mi73)
- [ParticleEffects-1.6.0+26.3+fabric](https://modrinth.com/project/PLAGcSFJ)
- [Searchables-fabric-26.3-1.0.2](https://modrinth.com/project/fuuu3xnx)
- [ShoulderSurfing-Fabric-26.3-5.2.0](https://modrinth.com/project/kepjj2sy)
- [SubtleEffects-fabric-26.3-1.14.3](https://modrinth.com/project/4q8UOK1d)
- [almanac-fabric-26.3-1.26.10.1](https://modrinth.com/project/Gi02250Z)
- [alternate-current-mc26.3-1.9.0](https://modrinth.com/project/r0v8vy1s)
- [animatica-0.6.2+26.3](https://modrinth.com/project/xEyZuswh)
- [appleskin-fabric-mc26.3-3.0.10](https://modrinth.com/project/EsAfCjCV)
- [asynclogger-2.2.2+26.1.2-fabric](https://modrinth.com/project/zvNzKfGF)
- [audiothrottle-1.0.1-26.3](https://modrinth.com/project/KEwZNpc5)
- [baguettelib-26.3-Fabric-2.0.7](https://modrinth.com/project/OfKzpbRU)
- [bbe-fabric-1.3.9+mc26.3-mod](https://modrinth.com/project/ONZm0H7Y)
- [better-clouds-1.15.0-beta.4+26.3-fabric](https://modrinth.com/project/5srFLIaK)
- [betterstats-5.6.0-beta.2+fn-26.3](https://modrinth.com/project/n6PXGAoM)
- [bookshelfinspector-fabric-2.4+26.3](https://modrinth.com/project/rOrXjyPb)
- [capes-1.5.10+26.3](https://modrinth.com/project/89Wsn8GD)
- [chat_heads-1.3.2-fabric-26.3](https://modrinth.com/project/Wb5oqrBJ)
- [cherishedworlds-fabric-18.0.0+26.3](https://modrinth.com/project/3azQ6p0W)
- [cloth-config-fabric-26.3.159](https://modrinth.com/project/9s6osm5g)
- [continuity-3.0.1+26.3](https://modrinth.com/project/1IjD5062)
- [controlify-3.5.3+mc26.3-universal](https://modrinth.com/project/DOUdJVEm)
- [debugify-26.3.0.0](https://modrinth.com/project/QwxR6Gcd)
- [durabilitytooltip-1.2.0a-fabric-mc26.3](https://modrinth.com/project/smUP7V3r)
- [dynamic-fps-3.11.10+minecraft-26.3.0-fabric](https://modrinth.com/project/LQ3K71Q1)
- [dynamiccrosshair-9.15+26.3-fabric](https://modrinth.com/project/ZcR9weSm)
- [entity-view-distance-1.9.0+26.2](https://modrinth.com/project/ihnBJ6on)
- [entity_model_features-3.3.10-26.3-fabric](https://modrinth.com/project/4I1XuqiY)
- [entity_texture_features-7.2.5-26.3-fabric](https://modrinth.com/project/BVzZfTc1)
- [entityculling-fabric-1.11.2-mc26.3](https://modrinth.com/project/NNAgCjsB)
- [explosive-enhancement-1.4.2-26.2](https://modrinth.com/project/OSQ8mw2r)
- [fabric-api-0.161.0+26.3](https://modrinth.com/project/P7dR8mSH)
- [fabric-language-kotlin-1.14.1+kotlin.2.4.20](https://modrinth.com/project/Ha28R6CL)
- [fallingleaves-2.0.8+26.3](https://modrinth.com/project/WhbRG4iK)
- [fast-ip-ping-v1.0.12-mc26.3](https://modrinth.com/project/9mtu0sUO)
- [fastback-fabric-0.35.0+26.3.0](https://modrinth.com/project/ZHKrK8Rp)
- [fastquit-3.1.5+mc26.2](https://modrinth.com/project/x1hIzbuY)
- [ferritecore-9.0.0-fabric](https://modrinth.com/project/uXXizFIs)
- [forcecloseloadingscreen-2.3.7](https://modrinth.com/project/blWBX5n1)
- [fzzy_config-0.7.7+fix3+26.3](https://modrinth.com/project/hYykXjDp)
- [glowing-torchflower-fabric-mc26.2-1.4.1](https://modrinth.com/project/1S4LxcvL)
- [inventorysorter-fabric-3.0.1+mc26.3](https://modrinth.com/project/5ibSyLAz)
- [iris-fabric-1.11.7+mc26.3](https://modrinth.com/project/YL57xq9U)
- [krypton-0.3.2](https://modrinth.com/project/fQEb0iXm)
- [lambdynamiclights-4.13.0+26.3](https://modrinth.com/project/yBW8D80W)
- [language-reload-1.7.8+26.3](https://modrinth.com/project/uLbm7CG6)
- [letmedespawn-fabric-26.3-1.26.9.2](https://modrinth.com/project/vE2FN5qn)
- [lithium-fabric-0.26.2+mc26.3](https://modrinth.com/project/gvQqBUqZ)
- [main-menu-credits-1.4.0+26.2-universal](https://modrinth.com/project/qJDfP7WN)
- [make_bubbles_pop-0.3.4-fabric-mc26.2.x](https://modrinth.com/project/gPCdW0Wr)
- [modernfix-5.27.20-build.2](https://modrinth.com/project/TjSm1wrD)
- [modmenu-21.0.0](https://modrinth.com/project/mOgUt4GM)
- [morechathistory-2.0.0](https://modrinth.com/project/8qkXwOnk)
- [moreculling-fabric-26.3-1.9.0](https://modrinth.com/project/51shyZVL)
- [mru-1.0.41+26.3-fabric](https://modrinth.com/project/SNVQ2c0g)
- [notenoughanimations-fabric-1.12.6-mc26.3](https://modrinth.com/project/MPCX6s5C)
- [nowplaying-fabric-2.104.0+26.3](https://modrinth.com/project/eNF4Bfla)
- [optigui-2.3.0-beta.10+26.3](https://modrinth.com/project/JuksLGBQ)
- [particular-26.3-Fabric-1.5.7](https://modrinth.com/project/pYFUU6cq)
- [placeholder-api-3.2.0+26.3](https://modrinth.com/project/eXts2L7r)
- [puzzle-fabric-2.3.1+26.3](https://modrinth.com/project/3IuO68q1)
- [quick-pack-fabric-1.5.1+26.3](https://modrinth.com/project/pSISfJ4O)
- [reeses-sodium-options-fabric-2.2.5+mc26.3](https://modrinth.com/project/Bh37bMuy)
- [rsls-1.4.0](https://modrinth.com/project/SKW62Pht)
- [skinlayers3d-fabric-1.11.3-mc26.3](https://modrinth.com/project/zV5r3pPn)
- [smoothgui-fabric-2.0.7+mc26.3](https://modrinth.com/project/j6yrZogB)
- [smoothscroll-3.0.0](https://modrinth.com/project/CllP7wW0)
- [smoothswapping-0.9.11-26.3-fabric](https://modrinth.com/project/ydZic5r4)
- [sodium-extra-fabric-0.9.4+mc26.3](https://modrinth.com/project/PtjYWJkn)
- [sodium-fabric-0.9.2+mc26.3](https://modrinth.com/project/AANobbMI)
- [sodium-shadowy-path-blocks-fabric-8.0.0](https://modrinth.com/project/EIa1eiMm)
- [sound-physics-remastered-fabric-1.5.1+26.3](https://modrinth.com/project/qyVF9oeo)
- [sounds-2.6.0+26.3-fabric](https://modrinth.com/project/ZouiUX7t)
- [spark-1.10.187-fabric](https://modrinth.com/project/l6YH9Als)
- [status-effect-bars-1.0.12](https://modrinth.com/project/x02cBj9Y)
- [supermartijn642configlib-1.1.8a-fabric-mc26.3](https://modrinth.com/project/LN9BxssP)
- [tcdcommons-5.6.0-beta.2+fn-26.3](https://modrinth.com/project/Eldc1g37)
- [visuality-0.7.15+26.3](https://modrinth.com/project/rI0hvYcd)
- [xaerominimap-fabric-26.3-26.5.3](https://modrinth.com/project/1bokaNcj)
- [xaeroworldmap-fabric-26.3-1.46.4](https://modrinth.com/project/NcUtCpym)
- [yet_another_config_lib_v3-3.9.7+26.3-fabric](https://modrinth.com/project/1eAoo2KR)
- [zconfig-1.0.0+26.x](https://modrinth.com/project/4qmvXRB9)
- [zfastnoise-1.1.1+26.3](https://modrinth.com/project/OnlVIpq5)
- [zoomify-2.16.3+26.3](https://modrinth.com/project/w7ThoJFB)

**Resource packs (26)**

- [AL's Creepers Revamped 2.0](https://modrinth.com/project/d2srP5t3)
- [AL's Enderman Revamped+FA 2.0](https://modrinth.com/project/ERTkxp3u)
- [AL's Scorpions & Crabs+FA 2.0](https://modrinth.com/project/6vTt8GmW)
- [AL's Skeletons Revamped+FA 2.0](https://modrinth.com/project/Q1DELmr6)
- [Better Lanterns v1.4.0 - 26.2+26.3](https://modrinth.com/project/PGGrfcvL)
- [Better-Leaves-9.6](https://modrinth.com/project/uvpymuxq)
- [Clearer Slot Highlight](https://modrinth.com/project/NITh4Uod)
- [Eggs N Eyes 1.0.7](https://modrinth.com/project/Fn2kXmlX)
- [EvenBetterEnchants_v3_1.21.5+](https://modrinth.com/project/6udpuGCH)
- [Fancy Crops v1.3](https://modrinth.com/project/UGEVQ6t9)
- [Fast Better Grass](https://modrinth.com/project/dspVZXKP)
- [FreshAnimations_v1.10.5](https://modrinth.com/project/50dA9Sha)
- [LowOnFire v26.2§8](https://modrinth.com/project/RRxvWKNC)
- [Os' Colorful Grasses (Tall)](https://modrinth.com/project/O2zhH8n8)
- [PDB3D's Blocky Armor Stands AV](https://modrinth.com/project/v7QpjqDY)
- [RAYs_3D_Ladders_v2.4](https://modrinth.com/project/Uupo7yGf)
- [RAYs_3D_Rails_v3.6](https://modrinth.com/project/jKa9Ievs)
- [Re-covered](https://modrinth.com/project/6gN7YVi7)
- [Recolourful Containers DARK 3.1.4 (1.19.4+)](https://modrinth.com/project/sQCUH0Mr)
- [Simple Grass Flowers v2.0.0](https://modrinth.com/project/ti9KkMHm)
- [Theone's Eating Animation Pack v1.0](https://modrinth.com/project/OhzX8kDf)
- [better_flame_particles-v3.1-mc1.21.9+-resourcepack](https://modrinth.com/project/ivUZsvzp)
- [qrafty's-capitalized-font-4.1](https://modrinth.com/project/FA4ebMMU)
- [visual_armor_trims_4.3](https://modrinth.com/project/tPtjib62)
- [§3Fresh §bFlower Pots](https://modrinth.com/project/CmEN0T1m)
- [§6Bushier Bushes§r](https://modrinth.com/project/ukVOzUX4)

**Shader packs (2)**

- [ComplementaryReimagined_r5.9.3](https://modrinth.com/project/HVnmMxH1)
- [miniature-shader-2.19](https://modrinth.com/project/UaS8ROxa)

</details>

---

## Before you click "Resubmit"

1. Versions: upload the `.mrpack` from `releases/26.2/` with version number `0.2.0+26.2` and the one from `releases/26.3/` with `0.2.0+26.3`, loader Fabric, channel **alpha**. The file name carries the number (`Fancy Vanilla 0.2.0 for 26.2.mrpack`).
2. In the moderation thread write that the pack has no third-party files in overrides, that every other file comes from cdn.modrinth.com, and that the description lists every included project with a link.
3. Use the first section of `docs/CHANGELOG.md` as the version changelog.
