scoreboard players set #gate tempered.data 1
gamerule minecraft:limited_crafting true
execute as @a run function tempered:recipe/resync
function tempered:core/locks
tellraw @a ["",{"translate":"tempered.msg.gate.on","color":"yellow","bold":false}]
