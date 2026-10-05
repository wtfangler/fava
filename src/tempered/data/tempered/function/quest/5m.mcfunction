execute if score #q.5m tempered.data matches 1 run return 0
scoreboard players set #q.5m tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/5/5m
experience add @a 20 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"gray","bold":true,"translate":"tempered.quest.5m.title"},{"text":"   +20 XP","color":"green","bold":false}]
