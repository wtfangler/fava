execute if score #q.6e tempered.data matches 1 run return 0
scoreboard players set #q.6e tempered.data 1
scoreboard players add #done tempered.data 1
advancement grant @a only tempered:quest/6/6e
experience add @a 400 points
execute as @a at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6
tellraw @a ["",{"color":"dark_gray","bold":false,"translate":"tempered.ui.quest_done"},{"color":"gold","bold":true,"translate":"tempered.quest.6e.title"},{"text":"   +400 XP","color":"green","bold":false}]
