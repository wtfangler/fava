$scoreboard players set #requested tempered.data $(n)
execute if entity @s unless score #requested tempered.data matches 1..7 run tellraw @s {"translate":"tempered.msg.set_age.usage","color":"red"}
execute unless score #requested tempered.data matches 1..7 run return 0
scoreboard players operation #age tempered.data = #requested tempered.data
scoreboard players set #done tempered.data 0
scoreboard players add #generation tempered.data 1
execute as @a run function tempered:core/reset_player
$tellraw @a ["",{"translate":"tempered.msg.set_age.done","with":["$(n)"],"color":"yellow","bold":false}]
