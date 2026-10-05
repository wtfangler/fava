scoreboard players set #gate tempered.data 0
gamerule minecraft:limited_crafting false
recipe give @a *
execute as @a[scores={tempered.lock=1..}] run function tempered:core/release_now
scoreboard players set @a tempered.lock 0
scoreboard players set @a tempered.lockn 0
tellraw @a ["",{"translate":"tempered.msg.gate.off","color":"yellow","bold":false}]
