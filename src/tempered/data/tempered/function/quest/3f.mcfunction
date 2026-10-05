execute if score #q.3f tempered.data matches 1 run return 0
scoreboard players set #q.3f tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/3/3f
experience add @a 60 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"aqua","bold":true,"translate":"tempered.quest.3f.title"},{"text":"   +60 XP","color":"green","bold":false}]
