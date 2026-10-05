execute if score #q.2o tempered.data matches 1 run return 0
scoreboard players set #q.2o tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/2/2o
experience add @a 150 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"light_purple","bold":true,"translate":"tempered.quest.2o.title"},{"text":"   +150 XP","color":"green","bold":false}]
