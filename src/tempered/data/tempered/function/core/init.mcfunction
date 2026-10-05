# AGES :: setup (odpala sie przy kazdym /reload i starcie swiata)
scoreboard objectives add tempered.data dummy
scoreboard objectives add tempered.n dummy
scoreboard objectives add tempered.n2 dummy
scoreboard objectives add tempered.lock dummy
scoreboard objectives add tempered.lockn dummy
scoreboard objectives add tempered.gen dummy
scoreboard objectives add tempered.bonusgen dummy
scoreboard objectives add tempered.menu trigger
scoreboard objectives add tempered.left minecraft.custom:minecraft.leave_game
scoreboard objectives add tempered.1b minecraft.crafted:minecraft.crafting_table
scoreboard objectives add tempered.1c minecraft.crafted:minecraft.wooden_pickaxe
scoreboard objectives add tempered.1e minecraft.crafted:minecraft.chest
scoreboard objectives add tempered.1f minecraft.custom:minecraft.sleep_in_bed
scoreboard objectives add tempered.1g minecraft.custom:minecraft.mob_kills
scoreboard objectives add tempered.1h minecraft.custom:minecraft.fall_one_cm
scoreboard objectives add tempered.1i minecraft.custom:minecraft.interact_with_campfire
scoreboard objectives add tempered.2b minecraft.crafted:minecraft.furnace
scoreboard objectives add tempered.2c minecraft.crafted:minecraft.stone_pickaxe
scoreboard objectives add tempered.2e minecraft.crafted:minecraft.torch
scoreboard objectives add tempered.2f minecraft.mined:minecraft.stone
scoreboard objectives add tempered.2h minecraft.crafted:minecraft.stone_axe
scoreboard objectives add tempered.2i minecraft.custom:minecraft.interact_with_furnace
scoreboard objectives add tempered.2j minecraft.custom:minecraft.interact_with_stonecutter
scoreboard objectives add tempered.2k minecraft.custom:minecraft.deaths
scoreboard objectives add tempered.2m1 minecraft.mined:minecraft.copper_ore
scoreboard objectives add tempered.2m2 minecraft.mined:minecraft.deepslate_copper_ore
scoreboard objectives add tempered.2n minecraft.crafted:minecraft.lightning_rod
scoreboard objectives add tempered.2o minecraft.crafted:minecraft.spyglass
scoreboard objectives add tempered.3b minecraft.crafted:minecraft.iron_pickaxe
scoreboard objectives add tempered.3c minecraft.crafted:minecraft.shield
scoreboard objectives add tempered.3d minecraft.crafted:minecraft.bucket
scoreboard objectives add tempered.3e minecraft.crafted:minecraft.iron_chestplate
scoreboard objectives add tempered.3f minecraft.killed:minecraft.zombie
scoreboard objectives add tempered.3g minecraft.crafted:minecraft.shears
scoreboard objectives add tempered.3i minecraft.broken:minecraft.stone_pickaxe
scoreboard objectives add tempered.3j minecraft.custom:minecraft.fish_caught
scoreboard objectives add tempered.3k minecraft.custom:minecraft.animals_bred
scoreboard objectives add tempered.3l minecraft.custom:minecraft.traded_with_villager
scoreboard objectives add tempered.3m minecraft.custom:minecraft.damage_blocked_by_shield
scoreboard objectives add tempered.4b minecraft.crafted:minecraft.diamond_pickaxe
scoreboard objectives add tempered.4d minecraft.crafted:minecraft.enchanting_table
scoreboard objectives add tempered.4e minecraft.custom:minecraft.enchant_item
scoreboard objectives add tempered.4f minecraft.crafted:minecraft.diamond_sword
scoreboard objectives add tempered.4h minecraft.crafted:minecraft.anvil
scoreboard objectives add tempered.4i minecraft.custom:minecraft.interact_with_grindstone
scoreboard objectives add tempered.4j minecraft.custom:minecraft.enchant_item
scoreboard objectives add tempered.4k minecraft.custom:minecraft.target_hit
scoreboard objectives add tempered.4l minecraft.custom:minecraft.walk_under_water_one_cm
scoreboard objectives add tempered.4m minecraft.custom:minecraft.interact_with_anvil
scoreboard objectives add tempered.5a minecraft.crafted:minecraft.flint_and_steel
scoreboard objectives add tempered.5d minecraft.crafted:minecraft.brewing_stand
scoreboard objectives add tempered.5f minecraft.killed:minecraft.ghast
scoreboard objectives add tempered.5i minecraft.custom:minecraft.interact_with_brewingstand
scoreboard objectives add tempered.5j minecraft.custom:minecraft.damage_taken
scoreboard objectives add tempered.5k minecraft.killed:minecraft.wither_skeleton
scoreboard objectives add tempered.5l minecraft.custom:minecraft.strider_one_cm
scoreboard objectives add tempered.5m minecraft.custom:minecraft.interact_with_cartography_table
scoreboard objectives add tempered.6b minecraft.crafted:minecraft.ender_eye
scoreboard objectives add tempered.6d minecraft.killed:minecraft.enderman
scoreboard objectives add tempered.6e minecraft.killed:minecraft.ender_dragon
scoreboard objectives add tempered.6i minecraft.custom:minecraft.aviate_one_cm
scoreboard objectives add tempered.6j minecraft.used:minecraft.firework_rocket
scoreboard objectives add tempered.6k minecraft.used:minecraft.ender_pearl
scoreboard objectives add tempered.6l minecraft.custom:minecraft.play_record
scoreboard objectives add tempered.7a minecraft.killed:minecraft.wither
scoreboard objectives add tempered.7c minecraft.crafted:minecraft.beacon
scoreboard objectives add tempered.7e minecraft.custom:minecraft.raid_win
scoreboard objectives add tempered.7g minecraft.custom:minecraft.mob_kills
scoreboard objectives add tempered.7h minecraft.custom:minecraft.walk_one_cm
scoreboard objectives add tempered.7i minecraft.custom:minecraft.interact_with_beacon
scoreboard objectives add tempered.7j minecraft.custom:minecraft.interact_with_smithing_table
scoreboard objectives add tempered.7k minecraft.custom:minecraft.traded_with_villager
scoreboard objectives add tempered.7l minecraft.custom:minecraft.damage_taken

execute unless score #age tempered.data matches 1.. run function tempered:core/firstrun

# Persistent administrator settings, including after /reload and server restart.
execute unless score #gate tempered.data matches 0..1 run scoreboard players set #gate tempered.data 1
execute unless score #generation tempered.data matches 0.. run scoreboard players set #generation tempered.data 0
execute unless score #bonus_generation tempered.data matches 0.. run scoreboard players set #bonus_generation tempered.data 0
execute if score #gate tempered.data matches 1 run gamerule minecraft:limited_crafting true
execute if score #gate tempered.data matches 0 run gamerule minecraft:limited_crafting false
execute as @a run function tempered:recipe/resync

tellraw @a ["",{"text":"[TEMPERED] ","color":"gold","bold":true},{"color":"gray","bold":false,"translate":"tempered.ui.loaded"},{"text":"/trigger tempered.menu","color":"white","bold":false,"click_event":{"action":"run_command","command":"/trigger tempered.menu"}},{"color":"gray","bold":false,"translate":"tempered.ui.status_hint"}]
