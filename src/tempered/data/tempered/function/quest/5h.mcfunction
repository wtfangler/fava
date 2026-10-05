execute if score #q.5h tempered.data matches 1 run return 0
scoreboard players set #q.5h tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/5/5h
experience add @a 400 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"gold","bold":true,"translate":"tempered.quest.5h.title"},{"text":"   +400 XP","color":"green","bold":false}]
